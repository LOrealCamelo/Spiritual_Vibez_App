"""PayPal hosted subscriptions: verified IPN only, never browser-return entitlement."""
import os
import secrets
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qsl

import httpx
from dateutil import parser
from fastapi import HTTPException
from . import memberships as m

BUTTON = 'QE2G8ZSPEMBBC'
MERCHANT = 'M8B5TF7XNYV24'
EMAIL = 'natture1st@gmail.com'


def enabled():
    return m.enabled() and os.getenv('PAYPAL_SUBSCRIPTIONS_ENABLED', 'false').lower() == 'true'


def money(value, expected):
    try:
        return Decimal(value).is_finite() and Decimal(value) == Decimal(expected)
    except (InvalidOperation, TypeError):
        return False


def timestamp(value):
    try:
        dt = parser.parse(value, tzinfos={'PST': -28800, 'PDT': -25200})
        if dt.tzinfo is None:
            raise ValueError()
        result = int(dt.astimezone(timezone.utc).timestamp())
        if result > m.now() + 300:
            raise ValueError()
        return result
    except (ValueError, TypeError, OverflowError):
        raise HTTPException(422, 'Invalid PayPal event date.')


def checkout(account):
    if not enabled():
        raise HTTPException(503, 'PayPal subscriptions are not enabled yet.')
    public = os.getenv('MEMBERSHIP_PUBLIC_URL', '').rstrip('/')
    notify = os.getenv('PAYPAL_IPN_URL', '')
    if not public.startswith('https://') or not notify.startswith('https://'):
        raise HTTPException(503, 'Secure checkout URLs are not configured.')
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT id FROM members WHERE admin=1 AND disabled=0').fetchone():
            raise HTTPException(503, 'The owner account must be configured first.')
        if db.execute("SELECT id FROM paypal_subscriptions WHERE user_id=? AND status NOT IN ('cancelled','ended')", (account['id'],)).fetchone():
            raise HTTPException(409, 'Manage your existing PayPal subscription before starting another.')
        if account['admin'] or account['lifetime']:
            raise HTTPException(409, 'This account does not need a paid subscription.')
        token = secrets.token_urlsafe(32)
        db.execute('INSERT INTO paypal_checkouts(hash,user_id,created) VALUES(?,?,?)', (m.digest(token), account['id'], m.now()))
    return {'action': 'https://www.paypal.com/cgi-bin/webscr', 'fields': {
        'cmd': '_s-xclick', 'hosted_button_id': BUTTON, 'currency_code': 'USD',
        'custom': token, 'notify_url': notify, 'return': public+'/#checkout',
        'cancel_return': public+'/#checkout', 'charset': 'utf-8'}}


async def verify(raw):
    # Fixed production endpoint: caller cannot redirect verification or use sandbox events.
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
            response = await client.post('https://ipnpb.paypal.com/cgi-bin/webscr',
                content=b'cmd=_notify-validate&'+raw,
                headers={'Content-Type': 'application/x-www-form-urlencoded', 'Connection': 'Close'})
            if response.status_code != 200:
                raise HTTPException(503, 'PayPal verification unavailable; retry notification.')
            return response.text.strip() == 'VERIFIED'
    except httpx.HTTPError:
        raise HTTPException(503, 'PayPal verification unavailable; retry notification.')


def process(raw):
    try:
        pairs = parse_qsl(raw.decode('ascii'), keep_blank_values=True, max_num_fields=200)
    except (ValueError, UnicodeError):
        raise HTTPException(422, 'Invalid notification encoding.')
    if len(dict(pairs)) != len(pairs):
        raise HTTPException(422, 'Duplicate notification fields.')
    data = dict(pairs)
    if data.get('test_ipn') == '1' or data.get('receiver_id') != MERCHANT:
        raise HTTPException(422, 'Incorrect PayPal merchant or environment.')
    if data.get('receiver_email', EMAIL).lower() != EMAIL:
        raise HTTPException(422, 'Incorrect PayPal receiver.')
    if data.get('payment_status') in ('Refunded', 'Reversed'):
        with m.database() as db:
            db.execute('BEGIN IMMEDIATE')
            receipt = db.execute('SELECT * FROM paypal_receipts WHERE txn=?', (data.get('parent_txn_id',''),)).fetchone()
            if not receipt or data.get('mc_currency') != 'USD' or not money(data.get('mc_gross'), '-5.99'):
                raise HTTPException(422, 'Refund requires owner review.')
            db.execute('UPDATE paypal_receipts SET refunded=1 WHERE txn=?', (receipt['txn'],))
        return
    kind = data.get('txn_type', '')
    sub_id = data.get('subscr_id', '')
    if not sub_id or len(sub_id) > 100:
        raise HTTPException(422, 'Missing subscription identifier.')
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        sub = db.execute('SELECT * FROM paypal_subscriptions WHERE id=?', (sub_id,)).fetchone()
        custom = data.get('custom', '')
        order = db.execute('SELECT * FROM paypal_checkouts WHERE hash=?', (m.digest(custom),)).fetchone() if custom else None
        if not sub and not order:
            raise HTTPException(422, 'No matching account checkout.')
        if sub and order and sub['user_id'] != order['user_id']:
            raise HTTPException(422, 'Subscription account mismatch.')
        if kind == 'subscr_signup':
            if sub and sub['signup']:
                return
            if not order:
                raise HTTPException(422, 'Checkout has expired.')
            # Validate the saved monthly plan without granting a trial.
            # PayPal may omit unused trial fields or send zero-duration periods.
            no_trial = all(
                data.get(f'period{i}', '') in ('', '0 D', '0 W', '0 M', '0 Y')
                and money(data.get(f'mc_amount{i}', data.get(f'amount{i}', '0')) or '0', '0')
                for i in (1, 2)
            )
            if (data.get('mc_currency') != 'USD' or not no_trial
                or data.get('period3') != '1 M'
                or data.get('recurring') != '1'
                or not money(data.get('mc_amount3', data.get('amount3')), '5.99')):
                raise HTTPException(422, 'Subscription terms do not match the approved plan.')
            start = timestamp(data.get('subscr_date'))
            if not order['created']-300 <= start <= order['created']+86400:
                raise HTTPException(422, 'Subscription started outside its checkout window.')
            uid = order['user_id']
            if order['subscription'] and order['subscription'] != sub_id:
                raise HTTPException(422, 'Checkout is already linked to another subscription.')
            if sub:
                db.execute('UPDATE paypal_subscriptions SET signup=?,trial_until=? WHERE id=?', (start, 0, sub_id))
            else:
                db.execute("INSERT INTO paypal_subscriptions(id,user_id,signup,trial_until,status) VALUES(?,?,?,?,'active')", (sub_id, uid, start, 0))
            db.execute('UPDATE paypal_checkouts SET subscription=? WHERE hash=?', (sub_id, order['hash']))
            m.audit(db, uid, 'paypal_signup_verified', sub_id)
        elif kind == 'subscr_payment':
            if not sub or not sub['signup']:
                raise HTTPException(503, 'Awaiting verified signup notification; retry.')
            txn = data.get('txn_id', '')
            if (not txn or len(txn)>100 or data.get('payment_status') != 'Completed'
                or data.get('mc_currency') != 'USD' or not money(data.get('mc_gross'), '5.99')):
                raise HTTPException(422, 'Payment has not completed for the approved amount.')
            if db.execute('SELECT 1 FROM paypal_receipts WHERE txn=?', (txn,)).fetchone():
                return
            paid = timestamp(data.get('payment_date'))
            # Anchor coverage to payment date, never notification delivery/replay time.
            until = m.month_after(paid)
            db.execute('INSERT INTO paypal_receipts(txn,subscription,paid,expires) VALUES(?,?,?,?)', (txn, sub_id, paid, until))
            m.audit(db, sub['user_id'], 'paypal_payment_verified', txn)
        elif kind in ('subscr_cancel', 'subscr_eot'):
            status = 'cancelled' if kind == 'subscr_cancel' else 'ended'
            if sub:
                db.execute('UPDATE paypal_subscriptions SET status=? WHERE id=?', (status, sub_id))
            elif order:
                db.execute('INSERT INTO paypal_subscriptions(id,user_id,status) VALUES(?,?,?)', (sub_id, order['user_id'], status))
            # Cancellation stops renewal at PayPal; already purchased access remains.
        elif kind == 'subscr_failed':
            if sub:
                m.audit(db, sub['user_id'], 'paypal_payment_failed', sub_id)
        else:
            raise HTTPException(422, 'Unsupported subscription event; owner review required.')


def status(account):
    with m.database() as db:
        return [dict(row) for row in db.execute('SELECT id,status,trial_until FROM paypal_subscriptions WHERE user_id=?', (account['id'],))]
