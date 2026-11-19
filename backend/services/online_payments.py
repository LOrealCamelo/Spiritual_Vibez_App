"""Account-bound Stripe/PayPal checkouts. Browser approval never grants access."""
import os
import re
import secrets
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

import httpx
import stripe
from fastapi import HTTPException
from . import memberships as m

PAYPAL_CLIENT = 'BAA_khDA0lTYHUlMU_qUVbs0jUltxsS_lg0EyvVqYsnrleca-Bb8naZA9KgVLRRnP68ixUQ_C3hKjdn7Hw'
PAYPAL_PLANS = {'month': 'P-49240117EJ7400837NL7FS3Q', 'year': 'P-2CB49304GY501903DNL7FRPA'}
LIFETIME_BUTTON = 'S6M5U5P48M76G'
STRIPE_TABLE = 'prctbl_1UdJscJLFxwakDjONc9avp8H'
STRIPE_PRICES = {'month':'price_1UdJOJJLFxwakDjOkkkgfM7p', 'year':'price_1UdJi6JLFxwakDjOxl3QSEKa', 'lifetime':'price_1UdJQnJLFxwakDjOdjVHLruu'}
STRIPE_PUBLIC = 'pk_live_51UHXPrJLFxwakDjOEf8zZAk8s0HiDi7VfLSv2UZLSbfPPTFM4MYoQ9cKg8krJe6dwPOKRuTJvcSG7ElDtJGwGhLt006U1R6ivc'
ENDED = ('cancelled','canceled','ended','expired','incomplete_expired')


def flag(name):
    return m.enabled() and os.getenv(name, 'false').lower() == 'true'


def stripe_prices():
    return {key: os.getenv('STRIPE_'+key.upper()+'_PRICE_ID','').strip() or STRIPE_PRICES[key] for key in m.PLANS}


def stripe_public_key():
    return os.getenv('STRIPE_PUBLISHABLE_KEY','').strip() or STRIPE_PUBLIC


def stripe_table_id():
    return os.getenv('STRIPE_PRICING_TABLE_ID','').strip() or STRIPE_TABLE


def stripe_enabled():
    return bool(flag('STRIPE_CHECKOUT_ENABLED') and os.getenv('STRIPE_SECRET_KEY','').startswith('sk_live_')
        and os.getenv('STRIPE_WEBHOOK_SECRET','').startswith('whsec_')
        and re.fullmatch(r'pk_live_[A-Za-z0-9]{1,300}',stripe_public_key())
        and re.fullmatch(r'prctbl_[A-Za-z0-9]{1,100}',stripe_table_id())
        and all(re.fullmatch(r'price_[A-Za-z0-9]+', value) for value in stripe_prices().values())
        and len(set(stripe_prices().values())) == 3)


def paypal_enabled():
    return bool(flag('PAYPAL_API_ENABLED') and os.getenv('PAYPAL_CLIENT_SECRET') and os.getenv('PAYPAL_WEBHOOK_ID'))


def lifetime_enabled():
    return flag('PAYPAL_LIFETIME_ENABLED') and flag('PAYPAL_SUBSCRIPTIONS_ENABLED')


def public_config():
    return {'stripe_enabled': stripe_enabled(), 'paypal_api_enabled': paypal_enabled(),
            'paypal_lifetime_enabled': lifetime_enabled()}


def cents(value):
    try:
        number = Decimal(str(value)) * 100
        if not number.is_finite() or number != number.to_integral_value():raise ValueError()
        return int(number)
    except (InvalidOperation, ValueError, TypeError):
        raise HTTPException(422, 'Invalid payment amount.') from None


def stamp(value):
    try:
        result = int(value) if isinstance(value,(int,float)) else int(datetime.fromisoformat(value.replace('Z','+00:00')).timestamp())
        if result <= 0 or result > m.now()+300:raise ValueError()
        return result
    except (ValueError, TypeError, AttributeError, OverflowError):
        raise HTTPException(422, 'Invalid payment date.') from None


def public_url():
    value = os.getenv('MEMBERSHIP_PUBLIC_URL','').rstrip('/')
    parsed = urlparse(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.query or parsed.fragment:
        raise HTTPException(503, 'Secure membership URL is not configured.')
    return value


def check_existing(db, uid):
    # A second automated subscription could create duplicate charges.
    legacy=db.execute("SELECT 1 FROM paypal_subscriptions WHERE user_id=? AND status NOT IN ('cancelled','ended')",(uid,)).fetchone()
    online=db.execute("SELECT 1 FROM online_subscriptions WHERE user_id=? AND lower(status) NOT IN ('cancelled','canceled','ended','expired','incomplete_expired')",(uid,)).fetchone()
    if legacy or online:raise HTTPException(409, 'Manage your existing recurring billing before starting another checkout.')


def prepare(account, provider, plan):
    public_url()
    if account['admin'] or account['lifetime']:raise HTTPException(409, 'This account does not need paid access.')
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        if not db.execute('SELECT 1 FROM members WHERE admin=1 AND disabled=0').fetchone():
            raise HTTPException(503, 'Owner setup is required before checkout.')
        check_existing(db,account['id'])
        token=secrets.token_urlsafe(32)
        db.execute('INSERT INTO online_checkouts(hash,user_id,provider,plan,created) VALUES(?,?,?,?,?)',
                   (m.digest(token),account['id'],provider,plan,m.now()))
    return token


def order_for(db, token, provider, reference, created, plan):
    order=db.execute('SELECT * FROM online_checkouts WHERE hash=?',(m.digest(token or ''),)).fetchone()
    if (not order or order['provider']!=provider or order['plan'] not in (plan,'table')
        or not order['created']-300 <= created <= order['created']+86400
        or (order['reference'] and order['reference']!=reference)):
        raise HTTPException(422,'No matching account-bound checkout.')
    bound=db.execute('SELECT hash FROM online_checkouts WHERE reference=?',(reference,)).fetchone()
    if bound and bound['hash']!=order['hash']:raise HTTPException(422,'Payment is already linked to another checkout.')
    db.execute('UPDATE online_checkouts SET reference=? WHERE hash=?',(reference,order['hash']))
    return order['user_id']


def bind_subscription(db, provider, identifier, uid, plan, status, created, customer=''):
    row=db.execute('SELECT * FROM online_subscriptions WHERE provider=? AND id=?',(provider,identifier)).fetchone()
    if row and (row['user_id']!=uid or row['plan']!=plan):raise HTTPException(422,'Subscription account mismatch.')
    if row:db.execute('UPDATE online_subscriptions SET status=?,customer=? WHERE provider=? AND id=?',(status,customer,provider,identifier))
    else:db.execute('INSERT INTO online_subscriptions(provider,id,user_id,plan,customer,status,created) VALUES(?,?,?,?,?,?,?)',
                    (provider,identifier,uid,plan,customer,status,created))


def receipt(db, provider, txn, uid, plan, paid, until, payment_id='', subscription=''):
    if not txn or len(txn)>200:raise HTTPException(422,'Missing payment reference.')
    old=db.execute('SELECT * FROM online_receipts WHERE provider=? AND txn=?',(provider,txn)).fetchone()
    if old:
        if old['user_id']!=uid or old['plan']!=plan:raise HTTPException(422,'Payment account mismatch.')
        return  # Never revive a refunded receipt or extend coverage on replay.
    db.execute('INSERT INTO online_receipts(provider,txn,user_id,plan,amount_cents,paid,expires,lifetime,payment_id,subscription) VALUES(?,?,?,?,?,?,?,?,?,?)',
               (provider,txn,uid,plan,m.PLANS[plan]['price_cents'],paid,until,int(plan=='lifetime'),payment_id,subscription))
    m.audit(db,uid,provider+'_payment_verified',txn)


async def stripe_request(method,path,data=None,params=None):
    if not os.getenv('STRIPE_SECRET_KEY','').startswith('sk_live_'):
        raise HTTPException(503,'Stripe verification is not configured.')
    try:
        async with httpx.AsyncClient(timeout=20,follow_redirects=False) as client:
            r=await client.request(method,'https://api.stripe.com/v1/'+path,
                headers={'Authorization':'Bearer '+os.environ['STRIPE_SECRET_KEY'],'Stripe-Version':'2024-06-20'},data=data,params=params)
            if r.status_code!=200:raise HTTPException(503,'Stripe verification unavailable; retry notification.')
            return r.json()
    except (httpx.HTTPError,ValueError):raise HTTPException(503,'Stripe verification unavailable; retry notification.') from None


def price_plan(price):
    identifier=price.get('id')
    plan=next((key for key,value in stripe_prices().items() if value==identifier),None)
    if not plan or price.get('currency')!='usd' or price.get('unit_amount')!=m.PLANS[plan]['price_cents']:
        raise HTTPException(422,'Stripe price does not match an approved plan.')
    recurring=price.get('recurring')
    if plan=='lifetime':
        if recurring:raise HTTPException(422,'Lifetime access must be a one-time payment.')
    elif (not recurring or recurring.get('interval')!=('month' if plan=='month' else 'year')
          or recurring.get('interval_count')!=1 or recurring.get('trial_period_days')):
        raise HTTPException(422,'Subscription must have the approved period and no trial.')
    return plan


async def stripe_context(account):
    if not stripe_enabled():raise HTTPException(503,'Stripe checkout is not configured yet.')
    for price_id in stripe_prices().values():
        price=await stripe_request('GET','prices/'+price_id)
        price_plan(price)
        if not price.get('active') or not price.get('livemode'):raise HTTPException(422,'Stripe price is not active in live mode.')
    token=prepare(account,'stripe','table')
    return {'table_id':stripe_table_id(),'publishable_key':stripe_public_key(),'client_reference_id':token}


def validate_subscription(subscription,plan):
    if subscription.get('trial_start') or subscription.get('trial_end'):
        raise HTTPException(422,'Trial subscriptions are not supported.')
    items=subscription.get('items',{}).get('data',[])
    if len(items)!=1 or items[0].get('quantity')!=1 or price_plan(items[0].get('price',{}))!=plan:
        raise HTTPException(422,'Subscription price does not match the selected plan.')


async def stripe_invoice(identifier):
    invoice=await stripe_request('GET','invoices/'+identifier)
    if invoice.get('status')!='paid' or not invoice.get('paid') or invoice.get('currency')!='usd':
        return  # Unpaid/zero invoices never unlock membership.
    sub_id=invoice.get('subscription')
    if not isinstance(sub_id,str):raise HTTPException(422,'Invoice is missing its subscription.')
    subscription=await stripe_request('GET','subscriptions/'+sub_id)
    lines=invoice.get('lines',{}).get('data',[])
    if len(lines)!=1 or lines[0].get('quantity')!=1 or lines[0].get('proration'):
        raise HTTPException(422,'Invoice needs owner review.')
    line=lines[0];plan=price_plan(line.get('price',{}));validate_subscription(subscription,plan)
    if (plan=='lifetime' or invoice.get('amount_paid',0)<m.PLANS[plan]['price_cents']
        or line.get('amount')!=m.PLANS[plan]['price_cents']
        or any(x.get('amount',0) for x in invoice.get('total_discount_amounts',[]))):
        raise HTTPException(422,'Invoice amount does not match the approved plan.')
    paid=stamp(invoice.get('status_transitions',{}).get('paid_at'))
    until=int(line.get('period',{}).get('end',0));start=int(line.get('period',{}).get('start',0))
    if start<=0 or until<=paid:
        raise HTTPException(422,'Invoice coverage requires owner review.')
    expected=m.month_after(start) if plan=='month' else m.year_after(start)
    if abs(until-expected)>86400:
        raise HTTPException(422,'Invoice coverage requires owner review.')
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        bound=db.execute('SELECT * FROM online_subscriptions WHERE provider=? AND id=?',('stripe',sub_id)).fetchone()
        if not bound:raise HTTPException(503,'Awaiting account-bound checkout notification; retry.')
        if bound['plan']!=plan or bound['customer']!=invoice.get('customer') or subscription.get('customer')!=bound['customer']:
            raise HTTPException(422,'Invoice account mismatch.')
        receipt(db,'stripe',identifier,bound['user_id'],plan,paid,until,str(invoice.get('payment_intent') or ''),sub_id)


async def stripe_process(event):
    if event.get('livemode') is not True:raise HTTPException(422,'Live Stripe notifications are required.')
    kind=event.get('type','');obj=event.get('data',{}).get('object',{});identifier=obj.get('id','')
    if not re.fullmatch(r'[A-Za-z0-9_]{1,200}',identifier):raise HTTPException(422,'Invalid Stripe resource.')
    if kind in ('checkout.session.completed','checkout.session.async_payment_succeeded'):
        session=await stripe_request('GET','checkout/sessions/'+identifier,params={'expand[]':'line_items'})
        if session.get('livemode') is not True:raise HTTPException(422,'Live Stripe checkout required.')
        items=session.get('line_items',{}).get('data',[])
        if len(items)!=1 or items[0].get('quantity')!=1:raise HTTPException(422,'Checkout quantity requires owner review.')
        plan=price_plan(items[0].get('price',{}))
        if (session.get('currency')!='usd' or session.get('amount_subtotal')!=m.PLANS[plan]['price_cents']
            or session.get('amount_total',0)<m.PLANS[plan]['price_cents']
            or session.get('total_details',{}).get('amount_discount',0)):
            raise HTTPException(422,'Checkout total does not match the approved price.')
        sub=None
        if plan!='lifetime':
            if session.get('mode')!='subscription':raise HTTPException(422,'A recurring checkout is required.')
            sub=await stripe_request('GET','subscriptions/'+session['subscription']);validate_subscription(sub,plan)
            if sub.get('customer')!=session.get('customer'):raise HTTPException(422,'Stripe customer mismatch.')
        elif session.get('mode')!='payment':raise HTTPException(422,'Lifetime must be a one-time checkout.')
        with m.database() as db:
            db.execute('BEGIN IMMEDIATE')
            uid=order_for(db,session.get('client_reference_id'),'stripe',identifier,stamp(session.get('created')),plan)
            if sub:bind_subscription(db,'stripe',sub['id'],uid,plan,sub['status'],stamp(session['created']),session['customer'])
            elif session.get('payment_status')=='paid':
                receipt(db,'stripe',identifier,uid,plan,stamp(session['created']),0,str(session.get('payment_intent') or ''))
        if sub and session.get('payment_status')=='paid':await stripe_invoice(sub['latest_invoice'])
    elif kind=='invoice.paid':await stripe_invoice(identifier)
    elif kind.startswith('customer.subscription.'):
        sub=await stripe_request('GET','subscriptions/'+identifier)
        with m.database() as db:
            db.execute('UPDATE online_subscriptions SET status=? WHERE provider=? AND id=?',(sub['status'],'stripe',identifier))
    elif kind=='charge.refunded':
        charge=await stripe_request('GET','charges/'+identifier)
        if charge.get('refunded') and charge.get('currency')=='usd' and charge.get('amount_refunded')==charge.get('amount'):
            payment=charge.get('payment_intent')
            if payment and isinstance(payment,str):
                with m.database() as db:
                    db.execute('UPDATE online_receipts SET refunded=1 WHERE provider=? AND payment_id=?',('stripe',payment))


async def stripe_cancel(account):
    if not os.getenv('STRIPE_SECRET_KEY','').startswith('sk_live_'):raise HTTPException(503,'Stripe billing is not configured.')
    with m.database() as db:
        rows=db.execute("SELECT id FROM online_subscriptions WHERE provider='stripe' AND user_id=? AND status NOT IN ('canceled','incomplete_expired')",(account['id'],)).fetchall()
    if not rows:raise HTTPException(404,'No recurring Stripe subscription was found for this account.')
    for row in rows:
        await stripe_request('POST','subscriptions/'+row['id'],data={'cancel_at_period_end':'true'})
    return {'message':'Automatic Stripe renewal is cancelled at the end of the current period. Paid access remains until its expiration.'}


async def paypal_request(method,path,data=None):
    try:
        async with httpx.AsyncClient(timeout=20,follow_redirects=False) as client:
            token=await client.post('https://api-m.paypal.com/v1/oauth2/token',
                auth=httpx.BasicAuth((os.getenv('PAYPAL_CLIENT_ID') or PAYPAL_CLIENT),os.environ['PAYPAL_CLIENT_SECRET']),data={'grant_type':'client_credentials'})
            if token.status_code!=200:raise HTTPException(503,'PayPal verification unavailable; retry notification.')
            access=token.json()['access_token']
            r=await client.request(method,'https://api-m.paypal.com'+path,headers={'Authorization':'Bearer '+access},json=data)
            if r.status_code not in (200,201,204):raise HTTPException(503,'PayPal verification unavailable; retry notification.')
            return r.json() if r.content else {}
    except (httpx.HTTPError,ValueError,KeyError):raise HTTPException(503,'PayPal verification unavailable; retry notification.') from None


async def paypal_plan(plan):
    identifier=PAYPAL_PLANS.get(plan)
    if not identifier:raise HTTPException(422,'Choose monthly or yearly PayPal billing.')
    data=await paypal_request('GET','/v1/billing/plans/'+identifier)
    cycles=data.get('billing_cycles',[])
    fee=data.get('payment_preferences',{}).get('setup_fee',{}).get('value','0')
    if data.get('status')!='ACTIVE' or len(cycles)!=1 or cycles[0].get('tenure_type')!='REGULAR' or cycles[0].get('total_cycles')!=0 or cents(fee)!=0:
        raise HTTPException(422,'PayPal plan must be active without trials or setup fees.')
    cycle=cycles[0];price=cycle.get('pricing_scheme',{}).get('fixed_price',{})
    if (cycle.get('frequency')!={'interval_unit':'MONTH' if plan=='month' else 'YEAR','interval_count':1}
        or price.get('currency_code')!='USD' or cents(price.get('value'))!=m.PLANS[plan]['price_cents']):
        raise HTTPException(422,'PayPal billing terms do not match the approved plan.')
    return identifier


async def paypal_context(account,plan):
    if not paypal_enabled():raise HTTPException(503,'PayPal subscription checkout is not configured yet.')
    identifier=await paypal_plan(plan)
    return {'client_id':(os.getenv('PAYPAL_CLIENT_ID') or PAYPAL_CLIENT),'plan_id':identifier,
            'custom_id':prepare(account,'paypal',plan)}


async def bind_paypal(identifier,account_id=None):
    if not re.fullmatch(r'I-[A-Za-z0-9]{1,100}',identifier):raise HTTPException(422,'Invalid PayPal subscription.')
    sub=await paypal_request('GET','/v1/billing/subscriptions/'+identifier)
    plan=next((key for key,value in PAYPAL_PLANS.items() if value==sub.get('plan_id')),None)
    if not plan or sub.get('plan_overridden'):raise HTTPException(422,'Unapproved PayPal plan.')
    await paypal_plan(plan)
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        uid=order_for(db,sub.get('custom_id'),'paypal',identifier,stamp(sub.get('create_time')),plan)
        if account_id is not None and uid!=account_id:raise HTTPException(403,'This subscription belongs to another account.')
        bind_subscription(db,'paypal',identifier,uid,plan,sub['status'].lower(),stamp(sub['create_time']))
    return sub,plan,uid


async def paypal_process(event):
    kind=event.get('event_type','');obj=event.get('resource',{})
    if kind.startswith('BILLING.SUBSCRIPTION.'):
        await bind_paypal(obj.get('id',''))
    elif kind=='PAYMENT.SALE.COMPLETED':
        identifier=obj.get('billing_agreement_id','');sub,plan,uid=await bind_paypal(identifier)
        amount=obj.get('amount',{})
        if obj.get('state')!='completed' or amount.get('currency')!='USD' or cents(amount.get('total'))!=m.PLANS[plan]['price_cents']:
            raise HTTPException(422,'PayPal payment has not completed for the approved price.')
        paid=stamp(obj.get('create_time'));until=m.month_after(paid) if plan=='month' else m.year_after(paid)
        with m.database() as db:
            db.execute('BEGIN IMMEDIATE')
            receipt(db,'paypal',obj.get('id',''),uid,plan,paid,until,subscription=identifier)
    elif kind=='PAYMENT.SALE.REFUNDED':
        sale_id=obj.get('sale_id','')
        if not re.fullmatch(r'[A-Za-z0-9]{1,100}',sale_id):raise HTTPException(422,'Invalid PayPal refund reference.')
        sale=await paypal_request('GET','/v1/payments/sale/'+sale_id)
        with m.database() as db:
            old=db.execute('SELECT * FROM online_receipts WHERE provider=? AND txn=?',('paypal',sale_id)).fetchone()
            if old and sale.get('state')=='refunded' and sale.get('amount',{}).get('currency')=='USD' and cents(sale['amount']['total'])==old['amount_cents']:
                db.execute('UPDATE online_receipts SET refunded=1 WHERE provider=? AND txn=?',('paypal',sale_id))


def lifetime_checkout(account):
    if not lifetime_enabled():raise HTTPException(503,'Lifetime PayPal checkout is not enabled.')
    notify=os.getenv('PAYPAL_IPN_URL','')
    if not notify.startswith('https://'):raise HTTPException(503,'PayPal payment notifications are not configured.')
    token=prepare(account,'paypal-lifetime','lifetime');public=public_url()
    return {'action':'https://www.paypal.com/cgi-bin/webscr','fields':{'cmd':'_s-xclick','hosted_button_id':LIFETIME_BUTTON,
            'currency_code':'USD','custom':token,'notify_url':notify,'return':public+'/#checkout','cancel_return':public+'/#checkout'}}


def lifetime_ipn(data):
    # The caller already verified the exact IPN body and merchant with PayPal.
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        if data.get('payment_status') in ('Refunded','Reversed'):
            old=db.execute('SELECT * FROM online_receipts WHERE provider=? AND txn=?',('paypal-lifetime',data.get('parent_txn_id',''))).fetchone()
            if not old:return False
            if data.get('mc_currency')!='USD' or cents(data.get('mc_gross'))!=-6000:raise HTTPException(422,'Refund needs owner review.')
            db.execute('UPDATE online_receipts SET refunded=1 WHERE provider=? AND txn=?',('paypal-lifetime',old['txn']))
            return True
        if data.get('txn_type')!='web_accept':return False
        if data.get('payment_status')!='Completed' or data.get('mc_currency')!='USD' or cents(data.get('mc_gross'))!=6000:
            raise HTTPException(422,'Lifetime payment must complete for $60 USD.')
        from .paypal_memberships import timestamp
        paid=stamp(timestamp(data.get('payment_date')))
        txn=data.get('txn_id','')
        uid=order_for(db,data.get('custom'),'paypal-lifetime',txn,paid,'lifetime')
        receipt(db,'paypal-lifetime',txn,uid,'lifetime',paid,0)
        return True
