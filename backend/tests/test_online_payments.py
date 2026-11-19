"""No live charges: real webhook signatures, account binding and provider verification."""
import copy
import hashlib
import hmac
import json
from datetime import datetime, timezone
from urllib.parse import urlencode
import pytest
from backend.services import memberships as m, online_payments as o, paypal_memberships as p
from backend.tests.test_memberships import setup, signup, gift


@pytest.fixture
def online(setup,monkeypatch):
    client,owner=setup
    for key,value in {'STRIPE_CHECKOUT_ENABLED':'true','STRIPE_SECRET_KEY':'sk_live_fixture',
        'STRIPE_WEBHOOK_SECRET':'whsec_fixture','STRIPE_MONTH_PRICE_ID':'price_month',
        'STRIPE_YEAR_PRICE_ID':'price_year','STRIPE_LIFETIME_PRICE_ID':'price_lifetime',
        'PAYPAL_API_ENABLED':'true','PAYPAL_CLIENT_SECRET':'private-fixture',
        'PAYPAL_WEBHOOK_ID':'WH-fixture','PAYPAL_SUBSCRIPTIONS_ENABLED':'true',
        'PAYPAL_LIFETIME_ENABLED':'true','PAYPAL_IPN_URL':'https://example.test/api/account/paypal/ipn'}.items():
        monkeypatch.setenv(key,value)
    return client,owner,signup(client)


def price(plan):
    return {'id':'price_'+plan,'active':True,'livemode':True,'currency':'usd','unit_amount':m.PLANS[plan]['price_cents'],
            'recurring':None if plan=='lifetime' else {'interval':'month' if plan=='month' else 'year','interval_count':1,'trial_period_days':None}}


def stripe_mock(monkeypatch,objects):
    async def request(method,path,data=None,params=None):
        if path.startswith('prices/'):return price(path.removeprefix('prices/price_'))
        if method=='POST' and path.startswith('subscriptions/'):
            assert data=={'cancel_at_period_end':'true'}
            objects[path]['cancel_at_period_end']=True
        assert path in objects,path
        return copy.deepcopy(objects[path])
    monkeypatch.setattr(o,'stripe_request',request)


def stripe_event(client,kind,identifier,*,secret='whsec_fixture',age=0,livemode=True):
    event={'id':'evt_fixture','object':'event','livemode':livemode,'type':kind,'data':{'object':{'id':identifier}}}
    raw=json.dumps(event).encode();t=m.now()-age
    signature=hmac.new(secret.encode(),str(t).encode()+b'.'+raw,hashlib.sha256).hexdigest()
    return client.post('/api/account/stripe/webhook',content=raw,headers={'stripe-signature':f't={t},v1={signature}','content-type':'application/json'})


def stripe_checkout(client,customer,monkeypatch,plan='lifetime'):
    objects={};stripe_mock(monkeypatch,objects)
    response=client.post('/api/account/stripe/context',headers=customer,json={})
    assert response.status_code==200,response.text
    context=response.json();assert context['table_id']==o.STRIPE_TABLE and context['publishable_key'].startswith('pk_live_')
    assert 'sk_live_' not in str(context)
    now=m.now()
    objects['checkout/sessions/cs_fixture']={'id':'cs_fixture','livemode':True,'client_reference_id':context['client_reference_id'],
        'mode':'payment' if plan=='lifetime' else 'subscription','payment_status':'paid','created':now,
        'currency':'usd','amount_subtotal':m.PLANS[plan]['price_cents'],'amount_total':m.PLANS[plan]['price_cents'],'payment_intent':'pi_fixture','customer':'cus_fixture',
        'subscription':'sub_fixture','line_items':{'data':[{'quantity':1,'price':price(plan)}]}}
    if plan!='lifetime':
        objects['subscriptions/sub_fixture']={'id':'sub_fixture','customer':'cus_fixture','status':'active','trial_start':None,'trial_end':None,
             'items':{'data':[{'quantity':1,'price':price(plan)}]},'latest_invoice':'in_fixture'}
        until=m.month_after(now) if plan=='month' else m.year_after(now)
        objects['invoices/in_fixture']={'id':'in_fixture','subscription':'sub_fixture','customer':'cus_fixture','paid':True,'status':'paid','currency':'usd',
             'amount_paid':m.PLANS[plan]['price_cents'],'payment_intent':'pi_fixture','status_transitions':{'paid_at':now},
             'lines':{'data':[{'quantity':1,'price':price(plan),'amount':m.PLANS[plan]['price_cents'],'proration':False,'period':{'start':now,'end':until}}]}}
    return objects


@pytest.mark.parametrize('plan',['month','year','lifetime'])
def test_stripe_verified_payment_replay_refund_and_account_binding(online,monkeypatch,plan):
    client,owner,customer=online;objects=stripe_checkout(client,customer,monkeypatch,plan)
    assert not client.get('/api/account/me',headers=customer).json()['active']
    assert stripe_event(client,'checkout.session.completed','cs_fixture',secret='wrong').status_code==400
    assert stripe_event(client,'checkout.session.completed','cs_fixture',age=600).status_code==400
    assert stripe_event(client,'checkout.session.completed','cs_fixture',livemode=False).status_code==422
    assert not client.get('/api/account/me',headers=customer).json()['active']
    assert stripe_event(client,'checkout.session.completed','cs_fixture').status_code==200
    account=client.get('/api/account/me',headers=customer).json();assert account['active']
    assert bool(account['lifetime'])==(plan=='lifetime')
    assert stripe_event(client,'checkout.session.completed','cs_fixture').status_code==200
    assert client.get('/api/account/me',headers=customer).json()['expires']==account['expires']
    other=signup(client,'other@example.test')
    assert not client.get('/api/account/me',headers=other).json()['active']
    if plan!='lifetime':
        assert client.post('/api/account/stripe/cancel',headers=other,json={}).status_code==404
        assert client.post('/api/account/stripe/cancel',headers=customer,json={}).status_code==200
        assert objects['subscriptions/sub_fixture']['cancel_at_period_end'] is True
        assert client.get('/api/account/me',headers=customer).json()['expires']==account['expires']
    objects['charges/ch_fixture']={'refunded':True,'currency':'usd','amount_refunded':m.PLANS[plan]['price_cents'],
                                  'amount':m.PLANS[plan]['price_cents'],'payment_intent':'pi_fixture'}
    assert stripe_event(client,'charge.refunded','ch_fixture').status_code==200
    assert not client.get('/api/account/me',headers=customer).json()['active']
    assert stripe_event(client,'checkout.session.completed','cs_fixture').status_code==200
    assert not client.get('/api/account/me',headers=customer).json()['active']


@pytest.mark.parametrize('change', ['price','currency','quantity','unbound','trial','unpaid','underpaid','discount'])
def test_stripe_invalid_or_unpaid_checkout_never_unlocks(online,monkeypatch,change):
    client,_,customer=online;objects=stripe_checkout(client,customer,monkeypatch,'year')
    session=objects['checkout/sessions/cs_fixture']
    if change=='price':session['amount_subtotal']=1
    if change=='underpaid':session['amount_total']=1
    if change=='discount':session['total_details']={'amount_discount':100}
    if change=='currency':session['currency']='eur'
    if change=='quantity':session['line_items']['data'][0]['quantity']=2
    if change=='unbound':session['client_reference_id']='someone-elses-account'
    if change=='trial':objects['subscriptions/sub_fixture']['trial_end']=m.now()+86400
    if change=='unpaid':session['payment_status']='unpaid'
    result=stripe_event(client,'checkout.session.completed','cs_fixture')
    assert result.status_code==(200 if change=='unpaid' else 422)
    assert not client.get('/api/account/me',headers=customer).json()['active']


def test_stripe_out_of_order_invoice_retries_and_renewal_extends_exact_period(online,monkeypatch):
    client,_,customer=online;objects=stripe_checkout(client,customer,monkeypatch,'year')
    assert stripe_event(client,'invoice.paid','in_fixture').status_code==503
    assert stripe_event(client,'checkout.session.completed','cs_fixture').status_code==200
    invoice=copy.deepcopy(objects['invoices/in_fixture']);old=invoice['lines']['data'][0]['period']['end']
    invoice['id']='in_renewal';invoice['lines']['data'][0]['period']={'start':old,'end':m.year_after(old)}
    # A real future renewal arrives at that future date, with existing sessions renewed too.
    monkeypatch.setattr(m,'now',lambda:old)
    invoice['status_transitions']['paid_at']=old;objects['invoices/in_renewal']=invoice
    assert stripe_event(client,'invoice.paid','in_renewal').status_code==200
    with m.database() as db:
        row=db.execute("SELECT * FROM online_receipts WHERE provider='stripe' AND txn='in_renewal'").fetchone()
        assert row['expires']==m.year_after(old)


def paypal_mock(monkeypatch,objects):
    async def request(method,path,data=None):
        if path=='/v1/notifications/verify-webhook-signature':return {'verification_status':objects.get('verification','SUCCESS')}
        if path.startswith('/v1/billing/plans/'):
            plan=next(key for key,value in o.PAYPAL_PLANS.items() if path.endswith(value))
            return objects.get('plan',{'status':'ACTIVE','billing_cycles':[{'tenure_type':'REGULAR','total_cycles':0,
                'frequency':{'interval_unit':'MONTH' if plan=='month' else 'YEAR','interval_count':1},
                'pricing_scheme':{'fixed_price':{'value':str(m.PLANS[plan]['price_cents']/100),'currency_code':'USD'}}}]})
        assert path in objects,path
        return copy.deepcopy(objects[path])
    monkeypatch.setattr(o,'paypal_request',request)


def paypal_event(client,kind,obj):
    return client.post('/api/account/paypal/webhook',json={'id':'WH-event','event_type':kind,'resource':obj},headers={
        'paypal-auth-algo':'SHA256withRSA','paypal-cert-url':'https://api.paypal.com/v1/notifications/certs/fixture',
        'paypal-transmission-id':'event-id','paypal-transmission-sig':'signature','paypal-transmission-time':datetime.now(timezone.utc).isoformat()})


def paypal_checkout(client,customer,monkeypatch,plan):
    objects={};paypal_mock(monkeypatch,objects)
    response=client.post('/api/account/paypal/context',headers=customer,json={'plan':plan})
    assert response.status_code==200,response.text
    context=response.json();assert context['plan_id']==o.PAYPAL_PLANS[plan]
    assert 'private-fixture' not in str(context)
    now=datetime.now(timezone.utc).isoformat()
    objects['/v1/billing/subscriptions/I-FIXTURE']={'id':'I-FIXTURE','plan_id':context['plan_id'],'custom_id':context['custom_id'],'create_time':now,'status':'ACTIVE'}
    sale={'id':'SALE123','billing_agreement_id':'I-FIXTURE','state':'completed','create_time':now,
          'amount':{'total':str(m.PLANS[plan]['price_cents']/100),'currency':'USD'}}
    return objects,sale


@pytest.mark.parametrize('plan',['month','year'])
def test_paypal_sdk_approval_never_unlocks_but_verified_sale_does(online,monkeypatch,plan):
    client,_,customer=online;objects,sale=paypal_checkout(client,customer,monkeypatch,plan)
    assert client.post('/api/account/paypal/confirm',headers=customer,json={'subscription_id':'I-FIXTURE'}).status_code==200
    assert not client.get('/api/account/me',headers=customer).json()['active']
    objects['verification']='FAILURE'
    assert paypal_event(client,'PAYMENT.SALE.COMPLETED',sale).status_code==400
    assert not client.get('/api/account/me',headers=customer).json()['active']
    objects['verification']='SUCCESS'
    assert paypal_event(client,'BILLING.SUBSCRIPTION.ACTIVATED',{'id':'I-FIXTURE'}).status_code==200
    assert not client.get('/api/account/me',headers=customer).json()['active']
    assert paypal_event(client,'PAYMENT.SALE.COMPLETED',sale).status_code==200
    account=client.get('/api/account/me',headers=customer).json();assert account['active']
    assert abs(account['expires']-(m.month_after(m.now()) if plan=='month' else m.year_after(m.now())))<5
    assert paypal_event(client,'PAYMENT.SALE.COMPLETED',sale).status_code==200
    assert client.get('/api/account/me',headers=customer).json()['expires']==account['expires']
    objects['/v1/billing/subscriptions/I-FIXTURE']['status']='CANCELLED'
    assert paypal_event(client,'BILLING.SUBSCRIPTION.CANCELLED',{'id':'I-FIXTURE'}).status_code==200
    assert client.get('/api/account/me',headers=customer).json()['expires']==account['expires']
    objects['/v1/payments/sale/SALE123']={'state':'refunded','amount':sale['amount']}
    assert paypal_event(client,'PAYMENT.SALE.REFUNDED',{'sale_id':'SALE123'}).status_code==200
    assert not client.get('/api/account/me',headers=customer).json()['active']


def test_paypal_cannot_bind_another_account_or_use_trial_plan(online,monkeypatch):
    client,_,customer=online;objects,sale=paypal_checkout(client,customer,monkeypatch,'year')
    other=signup(client,'other@example.test')
    assert client.post('/api/account/paypal/confirm',headers=other,json={'subscription_id':'I-FIXTURE'}).status_code==403
    objects['plan']={'status':'ACTIVE','billing_cycles':[{'tenure_type':'TRIAL','total_cycles':1}]}
    assert paypal_event(client,'PAYMENT.SALE.COMPLETED',sale).status_code==422
    assert not client.get('/api/account/me',headers=customer).json()['active']


def test_paypal_lifetime_verified_ipn_and_full_refund_preserve_manual_gift(online,monkeypatch):
    client,owner,customer=online
    response=client.post('/api/account/paypal/lifetime-checkout',headers=customer,json={})
    assert response.status_code==200 and response.json()['fields']['hosted_button_id']==o.LIFETIME_BUTTON
    fields=response.json()['fields']
    async def yes(raw):return True
    monkeypatch.setattr(p,'verify',yes)
    event={'receiver_id':p.MERCHANT,'receiver_email':p.EMAIL,'txn_type':'web_accept','txn_id':'LIFE123','custom':fields['custom'],
           'payment_status':'Completed','mc_currency':'USD','mc_gross':'60.00','payment_date':datetime.now(timezone.utc).isoformat()}
    def send(data):return client.post('/api/account/paypal/ipn',content=urlencode(data),headers={'content-type':'application/x-www-form-urlencoded'})
    wrong={**event,'mc_gross':'5.99'};assert send(wrong).status_code==422
    assert not client.get('/api/account/me',headers=customer).json()['active']
    assert send(event).status_code==200;assert send(event).status_code==200
    assert client.get('/api/account/me',headers=customer).json()['lifetime']
    assert client.get('/api/tarot/cards',headers=customer).status_code==200
    refund={'receiver_id':p.MERCHANT,'payment_status':'Refunded','parent_txn_id':'LIFE123','mc_currency':'USD','mc_gross':'-60.00'}
    assert send(refund).status_code==200
    assert not client.get('/api/account/me',headers=customer).json()['active']
    assert send(event).status_code==200
    assert not client.get('/api/account/me',headers=customer).json()['active']
    code=gift(client,owner,'lifetime');assert client.post('/api/account/redeem',headers=customer,json={'code':code}).status_code==200
    assert send(refund).status_code==200
    assert client.get('/api/account/me',headers=customer).json()['lifetime']


def test_checkout_flags_and_merchant_headers_fail_closed(online,monkeypatch):
    client,_,customer=online
    config=client.get('/api/account/config').json()
    assert config['stripe_enabled'] and config['paypal_api_enabled'] and config['paypal_lifetime_enabled']
    assert 'private-fixture' not in str(config) and 'sk_live_fixture' not in str(config) and 'whsec_fixture' not in str(config)
    monkeypatch.setenv('MEMBERSHIP_REQUIRED','false')
    assert client.post('/api/account/stripe/context',headers=customer,json={}).status_code==503
    assert client.post('/api/account/paypal/context',headers=customer,json={'plan':'year'}).status_code==503
    assert client.post('/api/account/paypal/lifetime-checkout',headers=customer,json={}).status_code==503
    assert client.post('/api/account/paypal/webhook',json={}).status_code==400
    assert client.post('/api/account/stripe/webhook',content=b'x'*262145).status_code==413


@pytest.mark.parametrize('provider',['stripe','paypal'])
def test_verification_uses_fixed_https_endpoints_and_private_auth(online,monkeypatch,provider):
    import asyncio
    import httpx
    actual=httpx.AsyncClient;seen=[]
    def handler(request):
        seen.append(str(request.url))
        if str(request.url)=='https://api-m.paypal.com/v1/oauth2/token':
            assert request.headers['authorization'].startswith('Basic ')
            return httpx.Response(200,json={'access_token':'private-access-token'})
        if provider=='stripe':
            assert str(request.url)=='https://api.stripe.com/v1/prices/price_month'
            assert request.headers['authorization']=='Bearer sk_live_fixture'
            assert request.headers['stripe-version']=='2024-06-20'
        else:
            assert str(request.url)=='https://api-m.paypal.com/v1/billing/plans/'+o.PAYPAL_PLANS['month']
            assert request.headers['authorization']=='Bearer private-access-token'
        return httpx.Response(200,json={'verified_fixture':True})
    def client(**kwargs):
        assert kwargs.get('follow_redirects') is False
        return actual(transport=httpx.MockTransport(handler),**kwargs)
    monkeypatch.setattr(o.httpx,'AsyncClient',client)
    if provider=='stripe':result=asyncio.run(o.stripe_request('GET','prices/price_month'))
    else:result=asyncio.run(o.paypal_request('GET','/v1/billing/plans/'+o.PAYPAL_PLANS['month']))
    assert result=={'verified_fixture':True}


def test_stripe_trial_price_rejected_before_embedding_checkout(online,monkeypatch):
    client,_,customer=online
    async def request(method,path,data=None,params=None):
        item=price('month');item['recurring']['trial_period_days']=1;return item
    monkeypatch.setattr(o,'stripe_request',request)
    assert client.post('/api/account/stripe/context',headers=customer,json={}).status_code==422
    with m.database() as db:assert not db.execute('SELECT 1 FROM online_checkouts').fetchone()


def test_automated_providers_cannot_create_duplicate_billing(online,monkeypatch):
    client,_,customer=online;objects=stripe_checkout(client,customer,monkeypatch,'month')
    assert stripe_event(client,'checkout.session.completed','cs_fixture').status_code==200
    assert client.post('/api/account/stripe/context',headers=customer,json={}).status_code==409
    paypal_mock(monkeypatch,{})
    assert client.post('/api/account/paypal/context',headers=customer,json={'plan':'year'}).status_code==409
    assert client.post('/api/account/paypal/checkout',headers=customer,json={}).status_code==409
    assert client.post('/api/account/paypal/lifetime-checkout',headers=customer,json={}).status_code==409


def test_refund_without_payment_reference_cannot_revoke_unrelated_access(online,monkeypatch):
    client,_,customer=online;objects=stripe_checkout(client,customer,monkeypatch,'month')
    objects['invoices/in_fixture']['payment_intent']=None
    assert stripe_event(client,'checkout.session.completed','cs_fixture').status_code==200
    objects['charges/ch_unrelated']={'refunded':True,'currency':'usd','amount':599,'amount_refunded':599,'payment_intent':None}
    assert stripe_event(client,'charge.refunded','ch_unrelated').status_code==200
    assert client.get('/api/account/me',headers=customer).json()['active']


def test_stripe_current_public_embed_can_be_configured_without_changing_secrets(online,monkeypatch):
    client,_,customer=online;stripe_mock(monkeypatch,{})
    monkeypatch.setenv('STRIPE_PUBLISHABLE_KEY','  pk_live_currentpublickey  ')
    monkeypatch.setenv('STRIPE_PRICING_TABLE_ID',' prctbl_currenttable ')
    response=client.post('/api/account/stripe/context',headers=customer,json={})
    assert response.status_code==200
    assert response.json()['publishable_key']=='pk_live_currentpublickey'
    assert response.json()['table_id']=='prctbl_currenttable'
    assert 'sk_live_fixture' not in response.text and 'whsec_fixture' not in response.text


@pytest.mark.parametrize('key,value',[
    ('STRIPE_PUBLISHABLE_KEY','sk_live_wrongfield'),
    ('STRIPE_PUBLISHABLE_KEY','pk_test_wrongmode'),
    ('STRIPE_PRICING_TABLE_ID','https://untrusted.example/table'),
])
def test_invalid_public_embed_settings_never_expose_secret_or_open_checkout(online,monkeypatch,key,value):
    client,_,customer=online
    monkeypatch.setenv(key,value)
    assert client.get('/api/account/config').json()['stripe_enabled'] is False
    response=client.post('/api/account/stripe/context',headers=customer,json={})
    assert response.status_code==503
    assert value not in response.text


def test_confirmed_price_defaults_preserve_environment_overrides(monkeypatch):
    for key in m.PLANS:monkeypatch.delenv('STRIPE_'+key.upper()+'_PRICE_ID',raising=False)
    assert o.stripe_prices()['year']=='price_1UdJi6JLFxwakDjOxl3QSEKa'
    assert o.stripe_prices()['lifetime']=='price_1UdJQnJLFxwakDjOdjVHLruu'
    assert o.stripe_prices()['month']=='price_1UdJOJJLFxwakDjOkkkgfM7p'
    monkeypatch.setenv('STRIPE_YEAR_PRICE_ID',' price_override ')
    assert o.stripe_prices()['year']=='price_override'
