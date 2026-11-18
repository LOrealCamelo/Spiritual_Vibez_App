"""Psycopg adapter for the existing SQL repositories; credentials stay server-side.

Neon's pooled URL serves application traffic. Additive, versioned schemas use the
unpooled URL. Account schemas preserve the existing per-account SQLite isolation.
"""
import hashlib
import os
import re
import sqlite3
import threading
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

import psycopg
from psycopg import sql
from psycopg.pq import TransactionStatus
from psycopg_pool import ConnectionPool

_LOCK = threading.RLock()
_initialized = set()
class DatabaseUnavailable(RuntimeError):
    pass


ID_TABLES = {'members','payments','audit','shadow_journal_entries','saved_tarot_readings',
             'cycle_tracking_logs','ritual_completions','oracle_chat_history','store_cart_items'}


def configured():
    return bool(os.getenv('DATABASE_URL'))


def namespace():
    value=os.getenv('DATABASE_NAMESPACE','spiritual_vibz')
    if not re.fullmatch('[a-z][a-z0-9_]{0,30}',value):
        raise RuntimeError('DATABASE_NAMESPACE must be a short lowercase SQL identifier.')
    return value


def validated_url(name='DATABASE_URL'):
    value=os.getenv(name) or (os.getenv('DATABASE_URL') if name=='DATABASE_URL_UNPOOLED' else '')
    try:
        parts=urlsplit(value)
        if parts.scheme not in ('postgres','postgresql') or not parts.hostname or not parts.path.strip('/'):
            raise ValueError()
        if parts.hostname.endswith('.neon.tech') and parse_qs(parts.query).get('sslmode',[''])[0] not in ('require','verify-ca','verify-full'):
            raise ValueError()
        if name=='DATABASE_URL_UNPOOLED' and '-pooler.' in parts.hostname:
            raise RuntimeError('DATABASE_URL_UNPOOLED is required for schema initialization.')
    except (ValueError,TypeError):
        raise RuntimeError('A valid private PostgreSQL URL with TLS is required.') from None
    return value


class Record(dict):
    def __getitem__(self,key):
        return list(self.values())[key] if isinstance(key,int) else super().__getitem__(key)


def record_factory(cursor):
    names=[c.name for c in cursor.description] if cursor.description else []
    return lambda values:Record(zip(names,values))


@lru_cache(maxsize=4)
def pool_for(url):
    return ConnectionPool(url,min_size=0,max_size=5,timeout=20,max_idle=60,open=True,
        kwargs={'prepare_threshold':None,'row_factory':record_factory,'connect_timeout':20},name='spiritual-postgres')


def schema_for(account_id=None, membership=False):
    if membership:return namespace()+'_memberships'
    return namespace()+('_user_'+str(int(account_id)) if account_id is not None else '_legacy')


def ensure_schema(schema,membership):
    url=validated_url('DATABASE_URL_UNPOOLED')
    key=(url,schema)
    if key in _initialized:return
    with _LOCK:
        if key in _initialized:return
        path=Path(__file__).parent/'sql'/('memberships_v1.sql' if membership else 'user_data_v1.sql')
        try:
            with psycopg.connect(url,connect_timeout=20,prepare_threshold=None) as conn:
                lock=int.from_bytes(hashlib.sha256(schema.encode()).digest()[:8],'big',signed=True)
                conn.execute('SELECT pg_advisory_xact_lock(%s)',(lock,))
                conn.execute(sql.SQL('CREATE SCHEMA IF NOT EXISTS {}').format(sql.Identifier(schema)))
                conn.execute(sql.SQL('SET LOCAL search_path TO {}, pg_catalog').format(sql.Identifier(schema)))
                paths = [path]
                if membership:
                    paths.append(Path(__file__).parent/'sql'/'memberships_v2.sql')
                for migration in paths:
                    for statement in migration.read_text().split(';'):
                        if statement.strip():conn.execute(statement)
            _initialized.add(key)
        except psycopg.Error:
            raise DatabaseUnavailable('PostgreSQL schema initialization failed; check server-side connection settings.') from None


def translate(statement):
    statement=statement.strip()
    ignore=bool(re.match(r'INSERT OR IGNORE',statement,re.I))
    replace=bool(re.match(r'INSERT OR REPLACE INTO limits',statement,re.I))
    if replace:
        statement=re.sub(r'INSERT OR REPLACE INTO limits\s+VALUES',
            'INSERT INTO limits (key,started,count) VALUES',statement,flags=re.I)
        statement+=' ON CONFLICT(key) DO UPDATE SET started=EXCLUDED.started,count=EXCLUDED.count'
    elif ignore:
        statement=re.sub(r'INSERT OR IGNORE','INSERT',statement,flags=re.I)+' ON CONFLICT DO NOTHING'
    if 'INSERT OR ' in statement.upper():raise RuntimeError('Unsupported PostgreSQL insert operation.')
    match=re.match(r'INSERT INTO\s+([a-z_]+)\b',statement,re.I)
    returns_id=bool(match and match[1].lower() in ID_TABLES and 'RETURNING' not in statement.upper())
    if returns_id:statement+=' RETURNING id'
    # Existing repositories use parameter markers, never question marks in literals.
    return statement.replace('?','%s'),returns_id


class Cursor:
    def __init__(self,connection):self.connection=connection;self.raw=None;self.lastrowid=None
    def execute(self,statement,params=()):
        self.connection.prepare()
        if statement.strip().upper()=='BEGIN IMMEDIATE':
            # Preserve SQLite's write-transaction serialization for gifts/approvals.
            self.raw=self.connection.raw.execute('SELECT pg_advisory_xact_lock(%s)',(self.connection.write_lock,))
            return self
        statement,returns_id=translate(statement)
        try:self.raw=self.connection.raw.execute(statement,params)
        except psycopg.IntegrityError:raise sqlite3.IntegrityError('A database constraint prevented this change.') from None
        self.lastrowid=None
        if returns_id:
            row=self.raw.fetchone();self.lastrowid=row['id'] if row else None
        return self
    @property
    def rowcount(self):return self.raw.rowcount
    def fetchone(self):return self.raw.fetchone()
    def fetchall(self):return self.raw.fetchall()
    def __iter__(self):return iter(self.raw)
    def close(self):
        if self.raw:self.raw.close()


class Connection:
    def __init__(self,raw,pool,schema):
        self.raw=raw;self.pool=pool;self.schema=schema;self.closed=False
        self.write_lock=int.from_bytes(hashlib.sha256((namespace()+'_writes').encode()).digest()[:8],'big',signed=True)
    def prepare(self):
        if self.raw.info.transaction_status==TransactionStatus.IDLE:
            self.raw.execute(sql.SQL('SET LOCAL search_path TO {}, pg_catalog').format(sql.Identifier(self.schema)))
    def execute(self,statement,params=()):return Cursor(self).execute(statement,params)
    def cursor(self):return Cursor(self)
    def commit(self):self.raw.commit()
    def rollback(self):self.raw.rollback()
    def close(self):
        if not self.closed:
            try:self.raw.rollback()
            finally:self.pool.putconn(self.raw);self.closed=True


def connect(account_id=None,membership=False):
    schema=schema_for(account_id,membership)
    ensure_schema(schema,membership)
    pool=pool_for(validated_url())
    try:return Connection(pool.getconn(),pool,schema)
    except psycopg.Error:
        raise DatabaseUnavailable('PostgreSQL connection unavailable; local storage fallback is disabled.') from None
