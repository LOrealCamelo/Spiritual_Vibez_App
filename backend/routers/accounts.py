"""Account access and owner-reviewed payments. Never trust a payment screenshot."""
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import quote
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from ..services import memberships as m
from ..services import paypal_memberships as paypal

router = APIRouter(prefix='/api/account', tags=['Accounts and memberships'])


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=256)


class EmailInput(BaseModel):
    email: str = Field(min_length=3, max_length=254)


class ResetInput(BaseModel):
    token: str = Field(min_length=20, max_length=200)
    password: str = Field(min_length=12, max_length=256)


class PaymentInput(BaseModel):
    provider: str
    reference: str = Field(min_length=4, max_length=150)


class ReviewInput(BaseModel):
    approve: bool
    verified_reference: str = Field(default='', max_length=150)
    note: str = Field(min_length=3, max_length=500)


class GiftInput(BaseModel):
    kind: str
    valid_days: int = Field(default=30, ge=1, le=365)


class CodeInput(BaseModel):
    code: str = Field(min_length=8, max_length=200)


def email_address(value):
    value = value.strip().lower()
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}", value):
        raise HTTPException(422, 'Enter a valid email address.')
    return value


def user(request: Request):
    token = request.headers.get('authorization', '').removeprefix('Bearer ')
    account = m.session_user(token)
    if not account:
        raise HTTPException(401, 'Please log in.')
    return account


def admin(account=Depends(user)):
    if not account['admin']:
        raise HTTPException(403, 'Administrator access required.')
    return account


def limited(request, action, subject='', maximum=20):
    source = request.client.host if request.client else 'unknown'
    if not m.rate_limit(action+':source:'+source, 200) or not m.rate_limit(action+':'+subject+':'+source, maximum):
        raise HTTPException(429, 'Too many attempts. Please try again later.')


@router.get('/config')
def config():
    configured = bool(os.getenv('MEMBERSHIP_DB_PATH') and os.getenv('MEMBERSHIP_USER_DATA_DIR'))
    owner_ready = False
    if configured:
        with m.database() as db:
            owner_ready = bool(db.execute('SELECT id FROM members WHERE admin=1 AND disabled=0').fetchone())
    return {'accounts_configured': configured, 'owner_ready': owner_ready, ** {'required': m.enabled(), 'price_cents': 599, 'currency': 'USD', 'renewal': 'paypal' if paypal.enabled() else 'manual', 'paypal_enabled': paypal.enabled(), 'trial_hours': 24,
            'cashapp': 'https://cash.app/$lvcenterprise', 'venmo': 'https://venmo.com/lvcenterprise',
            'support_email': os.getenv('MEMBERSHIP_SUPPORT_EMAIL', ''),
            'password_reset_email': bool(os.getenv('SMTP_HOST'))}}


@router.post('/register')
def register(body: Credentials, request: Request):
    email = email_address(body.email)
    limited(request, 'register', maximum=10)
    hashed = m.password_hash(body.password)
    with m.database() as db:
        # Do not reveal existing addresses through the registration response.
        db.execute('INSERT OR IGNORE INTO members(email,password,created) VALUES(?,?,?)', (email, hashed, m.now()))
    return {'message': 'If this address is new, your account is ready. Log in to continue, or use password recovery.'}


@router.post('/login')
def login(body: Credentials, request: Request):
    email = email_address(body.email)
    limited(request, 'login', email)
    with m.database() as db:
        row = db.execute('SELECT * FROM members WHERE email=?', (email,)).fetchone()
        # An unknown address still pays the same password derivation cost.
        stored = row['password'] if row else 'pbkdf2-sha256$600000$' + '00'*16 + '$' + '00'*32
        valid = m.password_matches(body.password, stored)
        if not row or not valid or row['disabled']:
            raise HTTPException(401, 'Email or password was not recognized.')
        return {'token': m.create_session(db, row['id']), 'user': m.public_user(row, db)}


@router.get('/me')
def me(account=Depends(user)):
    return account


@router.post('/logout')
def logout(request: Request, account=Depends(user)):
    token = request.headers.get('authorization', '').removeprefix('Bearer ')
    with m.database() as db:
        db.execute('DELETE FROM sessions WHERE hash=?', (m.digest(token),))
    return {'ok': True}


def send_reset(email, token):
    origin = os.getenv('MEMBERSHIP_PUBLIC_URL', '').rstrip('/')
    message = EmailMessage()
    message['From'] = os.environ['SMTP_FROM']
    message['To'] = email
    message['Subject'] = 'Reset your Spiritual Vibz password'
    message.set_content('Your password reset code expires in 30 minutes:\n\n'+token+
                        '\n\nOpen '+origin+'/#account and choose Reset password. Ignore this email if you did not request it.')
    with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.getenv('SMTP_PORT', '587')), timeout=15) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(os.environ['SMTP_USERNAME'], os.environ['SMTP_PASSWORD'])
        smtp.send_message(message)


@router.post('/forgot-password')
def forgot(body: EmailInput, request: Request, tasks: BackgroundTasks):
    email = email_address(body.email)
    limited(request, 'recovery', email, maximum=5)
    with m.database() as db:
        row = db.execute('SELECT id FROM members WHERE email=?', (email,)).fetchone()
        if row and os.getenv('SMTP_HOST'):
            token = m.create_reset(db, row['id'])
            tasks.add_task(send_reset, email, token)
    return {'message': 'If the address is registered and email delivery is configured, a reset code will be sent. Otherwise contact support for verified account recovery.'}


@router.post('/reset-password')
def reset(body: ResetInput, request: Request):
    limited(request, 'reset', maximum=15)
    hashed = m.password_hash(body.password)
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT user_id FROM resets WHERE hash=? AND expires>?', (m.digest(body.token), m.now())).fetchone()
        if not row:
            raise HTTPException(400, 'The reset code is invalid or expired.')
        db.execute('UPDATE members SET password=? WHERE id=?', (hashed, row['user_id']))
        db.execute('DELETE FROM sessions WHERE user_id=?', (row['user_id'],))
        db.execute('DELETE FROM resets WHERE user_id=?', (row['user_id'],))
        m.audit(db, row['user_id'], 'password-reset', row['user_id'])
    return {'message': 'Password changed. Log in again.'}


@router.post('/payments')
def payment(body: PaymentInput, request: Request, account=Depends(user)):
    if account['lifetime'] or account['admin']:
        raise HTTPException(409, 'This account does not need a monthly renewal.')
    limited(request, 'payment', str(account['id']), maximum=5)
    if body.provider not in ['cashapp', 'venmo']:
        raise HTTPException(422, 'Choose Cash App or Venmo.')
    import sqlite3
    reference = body.reference.strip().upper()
    if len(reference) < 4:
        raise HTTPException(422, 'Enter the transaction reference.')
    with m.database() as db:
        try:
            cursor = db.execute('INSERT INTO payments(user_id,provider,reference,created) VALUES(?,?,?,?)',
                                (account['id'], body.provider, reference, m.now()))
        except sqlite3.IntegrityError:
            raise HTTPException(409, 'A pending request or this transaction reference already exists.')
        return {'id': cursor.lastrowid, 'status': 'pending', 'message': 'Access begins only after the owner verifies receipt of $5.99 USD and approves this request.'}


@router.get('/payments')
def own_payments(account=Depends(user)):
    with m.database() as db:
        return [dict(row) for row in db.execute('SELECT id,provider,reference,status,created,note FROM payments WHERE user_id=? ORDER BY id DESC LIMIT 100', (account['id'],))]


@router.post('/redeem')
def redeem(body: CodeInput, request: Request, account=Depends(user)):
    limited(request, 'gift', str(account['id']), maximum=10)
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        code = db.execute('SELECT * FROM gifts WHERE hash=? AND redeemed_by IS NULL AND revoked=0 AND expires>?',
                          (m.digest(body.code.strip().upper()), m.now())).fetchone()
        if not code:
            raise HTTPException(400, 'This gift code is invalid, expired, revoked or already used.')
        db.execute('UPDATE gifts SET redeemed_by=?,redeemed=? WHERE hash=?', (account['id'], m.now(), code['hash']))
        if code['kind'] == 'lifetime':
            db.execute('UPDATE members SET lifetime=1 WHERE id=?', (account['id'],))
        else:
            m.grant_month(db, account['id'])
        m.audit(db, account['id'], 'gift-redeemed', code['hash'][:12])
    return {'message': 'Your gift membership is active. No automatic charges will occur.'}


@router.get('/admin/payments')
def pending(account=Depends(admin)):
    with m.database() as db:
        return [dict(row) for row in db.execute('SELECT p.*,m.email FROM payments p JOIN members m ON m.id=p.user_id ORDER BY p.id DESC LIMIT 200')]


@router.post('/admin/payments/{payment_id}/review')
def review(payment_id: int, body: ReviewInput, account=Depends(admin)):
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT * FROM payments WHERE id=? AND status="pending"', (payment_id,)).fetchone()
        if not row:
            raise HTTPException(409, 'This request has already been reviewed or does not exist.')
        verified = body.verified_reference.strip().upper()
        if body.approve and len(verified) < 4:
            raise HTTPException(422, 'Enter the actual verified transaction reference from your payment account.')
        if body.approve and db.execute('SELECT id FROM payments WHERE provider=? AND verified_reference=? AND status="approved"', (row['provider'], verified)).fetchone():
            raise HTTPException(409, 'That verified payment has already funded a membership.')
        if body.approve:
            m.grant_month(db, row['user_id'])
        db.execute('UPDATE payments SET status=?,reviewed=?,reviewer=?,note=?,verified_reference=? WHERE id=?',
                   ('approved' if body.approve else 'rejected', m.now(), account['id'], body.note, verified if body.approve else None, payment_id))
        m.audit(db, account['id'], 'payment-approved' if body.approve else 'payment-rejected', payment_id)
    return {'ok': True}


@router.post('/admin/gifts')
def gift(body: GiftInput, account=Depends(admin)):
    if body.kind not in ['month', 'lifetime']:
        raise HTTPException(422, 'Choose month or lifetime.')
    code = 'SV-' + m.secrets.token_hex(16).upper()
    with m.database() as db:
        db.execute('INSERT INTO gifts(hash,kind,created,created_by,expires) VALUES(?,?,?,?,?)',
                   (m.digest(code), body.kind, m.now(), account['id'], m.now() + body.valid_days * 86400))
        m.audit(db, account['id'], 'gift-created-'+body.kind, m.digest(code)[:12])
    return {'code': code, 'kind': body.kind, 'message': 'Copy now. This unique code is shown once and can be redeemed once.'}


@router.get('/admin/gifts')
def gifts(account=Depends(admin)):
    with m.database() as db:
        return [dict(row) for row in db.execute('SELECT hash,kind,created,expires,redeemed_by,redeemed,revoked FROM gifts ORDER BY created DESC LIMIT 200')]


@router.post('/admin/gifts/{code_hash}/revoke')
def revoke(code_hash: str, account=Depends(admin)):
    with m.database() as db:
        db.execute('UPDATE gifts SET revoked=1 WHERE hash=? AND redeemed_by IS NULL', (code_hash,))
        m.audit(db, account['id'], 'gift-revoked', code_hash[:12])
    return {'ok': True}


@router.get('/admin/members')
def members(account=Depends(admin)):
    with m.database() as db:
        return [m.public_user(row, db) for row in db.execute('SELECT * FROM members ORDER BY id DESC LIMIT 500')]


@router.post('/admin/members/{member_id}/reset')
def owner_reset(member_id: int, account=Depends(admin)):
    with m.database() as db:
        if not db.execute('SELECT id FROM members WHERE id=?', (member_id,)).fetchone():
            raise HTTPException(404, 'Account not found.')
        token = m.create_reset(db, member_id)
        m.audit(db, account['id'], 'owner-recovery-issued', member_id)
    return {'code': token, 'message': 'Deliver privately only after verifying the account owner. Expires in 30 minutes.'}


class AccessInput(BaseModel):
    disabled: bool
    reason: str = Field(min_length=3, max_length=500)


@router.post('/admin/members/{member_id}/access')
def manage_access(member_id: int, body: AccessInput, account=Depends(admin)):
    with m.database() as db:
        row = db.execute('SELECT * FROM members WHERE id=?', (member_id,)).fetchone()
        if not row or row['admin']:
            raise HTTPException(400, 'Only customer accounts may be suspended here.')
        db.execute('UPDATE members SET disabled=? WHERE id=?', (int(body.disabled), member_id))
        if body.disabled:
            db.execute('DELETE FROM sessions WHERE user_id=?', (member_id,))
        m.audit(db, account['id'], ('suspended: ' if body.disabled else 'restored: ')+body.reason, member_id)
    return {'ok': True}


@router.get('/export')
def export_data(account=Depends(user)):
    from ..database import ACCOUNT_ID, get_connection
    context = ACCOUNT_ID.set(account['id'])
    try:
        conn = get_connection()
        try:
            tables = ['shadow_journal_entries', 'saved_tarot_readings', 'cycle_tracking_logs', 'ritual_completions', 'study_quiz_progress', 'oracle_chat_history']
            return {table: [dict(row) for row in conn.execute('SELECT * FROM '+table)] for table in tables}
        finally:
            conn.close()
    finally:
        ACCOUNT_ID.reset(context)


@router.post('/paypal/checkout')
def paypal_checkout(request: Request, account=Depends(user)):
    limited(request, 'paypal-checkout', str(account['id']), maximum=5)
    return paypal.checkout(account)


@router.get('/paypal/subscriptions')
def paypal_subscriptions(account=Depends(user)):
    return paypal.status(account)


@router.post('/paypal/ipn')
async def paypal_ipn(request: Request):
    if not paypal.enabled():
        raise HTTPException(503, 'PayPal subscriptions are not enabled.')
    if request.headers.get('content-type', '').split(';')[0] != 'application/x-www-form-urlencoded':
        raise HTTPException(415, 'Expected PayPal form notification.')
    raw = b''
    async for chunk in request.stream():
        raw += chunk
        if len(raw) > 32768:
            raise HTTPException(413, 'Notification too large.')
    if not await paypal.verify(raw):
        raise HTTPException(400, 'Unverified notification.')
    # SQLite work is short and synchronous, matching the existing account handlers.
    from starlette.concurrency import run_in_threadpool
    await run_in_threadpool(paypal.process, raw)
    return {'received': True}
