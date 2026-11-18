"""Opaque sessions, manually verified memberships and atomic single-use gifts.

Uses Neon PostgreSQL when DATABASE_URL is configured; local SQLite remains supported.
A PostgreSQL failure never falls back to local storage.
PayPal notifications are verified separately before granting subscription access.
"""
import calendar
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone


def enabled():
    return os.getenv('MEMBERSHIP_REQUIRED', 'false').lower() == 'true'


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def now():
    return int(time.time())


def month_after(timestamp):
    d = datetime.fromtimestamp(timestamp, timezone.utc)
    year, month = (d.year + 1, 1) if d.month == 12 else (d.year, d.month + 1)
    return int(d.replace(year=year, month=month, day=min(d.day, calendar.monthrange(year, month)[1])).timestamp())


def password_hash(password):
    salt = secrets.token_hex(16)
    value = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 600000).hex()
    return 'pbkdf2-sha256$600000$' + salt + '$' + value


def password_matches(password, stored):
    _, iterations, salt, expected = stored.split('$')
    value = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(iterations)).hex()
    return hmac.compare_digest(value, expected)


def private_path(value):
    if not os.path.isabs(value):
        raise RuntimeError('Membership storage requires an absolute private path.')
    target = Path(value).resolve()
    repo = Path(__file__).resolve().parents[2]
    if any(target == root or root in target.parents for root in [repo/'frontend', repo/'mobile'/'assets']):
        raise RuntimeError('Membership storage cannot be inside publicly served artwork or frontend files.')
    return str(target)


@contextmanager
def database():
    from .. import postgres
    if postgres.configured():
        conn=postgres.connect(membership=True)
        try:
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()
        return
    path = os.getenv('MEMBERSHIP_DB_PATH')
    if not path:
        raise RuntimeError('MEMBERSHIP_DB_PATH must point to durable private storage.')
    path = private_path(path)
    if os.getenv('MEMBERSHIP_USER_DATA_DIR'):
        private_path(os.environ['MEMBERSHIP_USER_DATA_DIR'])
    os.makedirs(os.path.dirname(os.path.abspath(path)), mode=0o700, exist_ok=True)
    conn = sqlite3.connect(path, timeout=20)
    os.chmod(path, 0o600)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    try:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS members(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL, admin INTEGER NOT NULL DEFAULT 0, expires INTEGER NOT NULL DEFAULT 0,
          lifetime INTEGER NOT NULL DEFAULT 0, disabled INTEGER NOT NULL DEFAULT 0, created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES members(id), expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS resets(hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES members(id), expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES members(id),
          provider TEXT NOT NULL, reference TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created INTEGER NOT NULL,
          reviewed INTEGER, reviewer INTEGER REFERENCES members(id), note TEXT NOT NULL DEFAULT '', verified_reference TEXT, UNIQUE(provider, reference));
        CREATE UNIQUE INDEX IF NOT EXISTS unique_verified_receipt ON payments(provider,verified_reference) WHERE status='approved';
        CREATE UNIQUE INDEX IF NOT EXISTS one_pending_payment ON payments(user_id) WHERE status='pending';
        CREATE TABLE IF NOT EXISTS gifts(hash TEXT PRIMARY KEY, kind TEXT NOT NULL, created INTEGER NOT NULL,
          created_by INTEGER NOT NULL REFERENCES members(id), expires INTEGER NOT NULL, redeemed_by INTEGER REFERENCES members(id),
          redeemed INTEGER, revoked INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, actor INTEGER, action TEXT NOT NULL,
          target TEXT NOT NULL, created INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS paypal_checkouts(hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES members(id),
          created INTEGER NOT NULL, subscription TEXT);
        CREATE TABLE IF NOT EXISTS paypal_subscriptions(id TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES members(id),
          signup INTEGER NOT NULL DEFAULT 0, trial_until INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS paypal_receipts(txn TEXT PRIMARY KEY, subscription TEXT NOT NULL REFERENCES paypal_subscriptions(id),
          paid INTEGER NOT NULL, expires INTEGER NOT NULL, refunded INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS limits(key TEXT PRIMARY KEY, started INTEGER NOT NULL, count INTEGER NOT NULL);
        ''')
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()


def public_user(row, db=None):
    result = {key: row[key] for key in ['id', 'email', 'admin', 'expires', 'lifetime', 'disabled']}
    if db is not None:
        coverage = db.execute("""SELECT MAX(until) FROM (
          SELECT trial_until AS until FROM paypal_subscriptions WHERE user_id=?
          UNION ALL SELECT r.expires AS until FROM paypal_receipts r JOIN paypal_subscriptions s
          ON s.id=r.subscription WHERE s.user_id=? AND r.refunded=0)""", (row['id'],row['id'])).fetchone()[0]
        result['expires'] = max(result['expires'], coverage or 0)
    result['active'] = bool(not row['disabled'] and (row['admin'] or row['lifetime'] or result['expires'] > now()))
    return result


def session_user(token):
    if not token or len(token) > 200:
        return None
    with database() as db:
        row = db.execute('SELECT m.* FROM sessions s JOIN members m ON m.id=s.user_id WHERE s.hash=? AND s.expires>? AND m.disabled=0',
                         (digest(token), now())).fetchone()
        return public_user(row, db) if row else None


def create_session(db, user_id):
    token = secrets.token_urlsafe(32)
    db.execute('INSERT INTO sessions VALUES(?,?,?)', (digest(token), user_id, now() + 86400))
    return token


def rate_limit(key, maximum=20, seconds=900):
    with database() as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT * FROM limits WHERE key=?', (digest(key),)).fetchone()
        if row and row['started'] > now() - seconds:
            if row['count'] >= maximum:
                return False
            db.execute('UPDATE limits SET count=count+1 WHERE key=?', (digest(key),))
        else:
            db.execute('INSERT OR REPLACE INTO limits VALUES(?,?,1)', (digest(key), now()))
        return True


def audit(db, actor, action, target):
    db.execute('INSERT INTO audit(actor,action,target,created) VALUES(?,?,?,?)', (actor, action, str(target), now()))


def grant_month(db, user_id):
    row = db.execute('SELECT * FROM members WHERE id=?', (user_id,)).fetchone()
    expiry = public_user(row, db)['expires']
    db.execute('UPDATE members SET expires=? WHERE id=?', (month_after(max(now(), expiry)), user_id))


def create_reset(db, user_id):
    token = secrets.token_urlsafe(32)
    db.execute('DELETE FROM resets WHERE user_id=?', (user_id,))
    db.execute('INSERT INTO resets VALUES(?,?,?)', (digest(token), user_id, now() + 1800))
    return token
