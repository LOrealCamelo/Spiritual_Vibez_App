"""No real charges: exercise signed-notification boundary and durable entitlement."""
from urllib.parse import urlencode
from datetime import datetime, timezone
import pytest
from backend.services import memberships as m, paypal_memberships as p
from backend.tests.test_memberships import setup, signup


@pytest.fixture
def paypal(setup, monkeypatch):
    client, owner = setup
    monkeypatch.setenv('PAYPAL_SUBSCRIPTIONS_ENABLED', 'true')
    monkeypatch.setenv('PAYPAL_IPN_URL', 'https://example.test/api/account/paypal/ipn')
    customer = signup(client)
    checkout = client.post('/api/account/paypal/checkout', headers=customer, json={})
    assert checkout.status_code == 200
    fields = checkout.json()['fields']
    assert fields['hosted_button_id'] == p.BUTTON
    return client, customer, fields['custom']


def event(custom, **extra):
    return dict(custom=custom, receiver_id=p.MERCHANT, receiver_email=p.EMAIL,
        subscr_id='I-EXAMPLE', txn_type='subscr_signup', period3='1 M',
        mc_amount3='5.99', mc_currency='USD', recurring='1',
        subscr_date=datetime.now(timezone.utc).strftime('%H:%M:%S %b %d, %Y UTC'), **extra)


def send(client, data):
    return client.post('/api/account/paypal/ipn', content=urlencode(data), headers={'Content-Type':'application/x-www-form-urlencoded'})


def verified(monkeypatch):
    async def yes(raw):return True
    monkeypatch.setattr(p, 'verify', yes)


def test_unverified_return_and_notification_never_unlock(paypal, monkeypatch):
    client, customer, custom = paypal
    async def no(raw):return False
    monkeypatch.setattr(p, 'verify', no)
    assert client.get('/#checkout').status_code == 200
    assert send(client, event(custom)).status_code == 400
    assert not client.get('/api/account/me', headers=customer).json()['active']


def test_paid_renewal_replay_cancel_and_refund(paypal, monkeypatch):
    client, customer, custom = paypal
    verified(monkeypatch)
    assert send(client, event(custom)).status_code == 200
    expiry = client.get('/api/account/me', headers=customer).json()['expires']
    assert expiry == 0
    assert not client.get('/api/account/me', headers=customer).json()['active']
    assert client.get('/api/account/config').json()['trial_hours'] == 0
    assert send(client, event(custom)).status_code == 200
    assert client.get('/api/account/me', headers=customer).json()['expires']==expiry
    payment=event(custom);payment.update(txn_type='subscr_payment', txn_id='TXN-ONE', payment_status='Completed',mc_gross='5.99',payment_date=payment['subscr_date'])
    assert send(client,payment).status_code == 200
    paid_expiry=client.get('/api/account/me',headers=customer).json()['expires']
    assert paid_expiry > expiry+27*86400
    assert send(client,payment).status_code == 200
    assert client.get('/api/account/me',headers=customer).json()['expires']==paid_expiry
    cancel=event(custom);cancel['txn_type']='subscr_cancel'
    assert send(client,cancel).status_code==200
    assert client.get('/api/account/me',headers=customer).json()['expires']==paid_expiry
    assert client.get('/api/account/paypal/subscriptions',headers=customer).json()[0]['status']=='cancelled'
    refund=dict(receiver_id=p.MERCHANT,receiver_email=p.EMAIL,payment_status='Refunded',parent_txn_id='TXN-ONE',mc_gross='-5.99',mc_currency='USD')
    assert send(client,refund).status_code==200
    assert client.get('/api/account/me',headers=customer).json()['expires']==expiry


@pytest.mark.parametrize('changes',[
 {'receiver_id':'WRONG'}, {'receiver_email':'wrong@example.test'}, {'test_ipn':'1'},
 {'period1':'1 D'}, {'period1':'7 D'}, {'period2':'1 D'},
 {'mc_amount2':'1.00'}, {'period3':'1 Y'}, {'mc_amount3':'0.01'}, {'mc_currency':'EUR'},
 {'mc_amount1':'1.00'}, {'recurring':'0'}, {'custom':'unbound-token'},
])
def test_invalid_plan_receiver_environment_or_binding_denied(paypal,monkeypatch,changes):
    client,customer,custom=paypal;verified(monkeypatch)
    data=event(custom);data.update(changes)
    assert send(client,data).status_code==422
    assert not client.get('/api/account/me',headers=customer).json()['active']


def test_pending_payment_and_out_of_order_retry(paypal,monkeypatch):
    client,customer,custom=paypal;verified(monkeypatch)
    data=event(custom);data.update(txn_type='subscr_payment',txn_id='TXN-TWO',payment_status='Completed',mc_gross='5.99',payment_date=data['subscr_date'])
    assert send(client,data).status_code==503
    assert send(client,event(custom)).status_code==200
    data['payment_status']='Pending'
    assert send(client,data).status_code==422


def test_duplicate_fields_and_oversize_denied(paypal,monkeypatch):
    client,customer,custom=paypal;verified(monkeypatch)
    assert client.post('/api/account/paypal/ipn',content=urlencode(event(custom))+'&receiver_id=evil',headers={'Content-Type':'application/x-www-form-urlencoded'}).status_code==422
    assert client.post('/api/account/paypal/ipn',content='a'*32769,headers={'Content-Type':'application/x-www-form-urlencoded'}).status_code==413


def test_verification_posts_exact_body_to_fixed_paypal_endpoint(monkeypatch):
    import asyncio
    import httpx
    actual_client=httpx.AsyncClient
    raw=b'receiver_id=M8B5TF7XNYV24&custom=opaque%2Bvalue'
    def handler(request):
        assert str(request.url)=='https://ipnpb.paypal.com/cgi-bin/webscr'
        assert request.method=='POST'
        assert request.content==b'cmd=_notify-validate&'+raw
        return httpx.Response(200,text='VERIFIED')
    monkeypatch.setattr(p.httpx,'AsyncClient',lambda **kwargs:actual_client(transport=httpx.MockTransport(handler),**kwargs))
    assert asyncio.run(p.verify(raw)) is True


def test_invalid_or_unavailable_verification_never_accepts(monkeypatch):
    import asyncio
    import httpx
    from fastapi import HTTPException
    actual_client=httpx.AsyncClient
    for status,body in [(200,'INVALID'),(500,'VERIFIED')]:
        monkeypatch.setattr(p.httpx,'AsyncClient',lambda **kwargs:actual_client(transport=httpx.MockTransport(lambda request:httpx.Response(status,text=body)),**kwargs))
        if status==200:assert not asyncio.run(p.verify(b'x=y'))
        else:
            with pytest.raises(HTTPException) as error:asyncio.run(p.verify(b'x=y'))
            assert error.value.status_code==503


def test_delayed_verified_signup_does_not_grant_access(paypal,monkeypatch):
    client,customer,custom=paypal;verified(monkeypatch)
    start=m.now()-90000
    with m.database() as db:db.execute('UPDATE paypal_checkouts SET created=?',(start-10,))
    data=event(custom);data['subscr_date']=datetime.fromtimestamp(start,timezone.utc).strftime('%H:%M:%S %b %d, %Y UTC')
    assert send(client,data).status_code==200
    assert not client.get('/api/account/me',headers=customer).json()['active']


def test_checkout_cannot_accept_payments_when_membership_gate_is_off(paypal,monkeypatch):
    client,customer,custom=paypal
    monkeypatch.setenv('MEMBERSHIP_REQUIRED','false')
    assert client.post('/api/account/paypal/checkout',headers=customer,json={}).status_code==503


@pytest.mark.parametrize('fields', [
    {'period1': '0 D', 'period2': '0 D', 'mc_amount1': '0.00', 'mc_amount2': '0.00'},
    {'period1': '', 'period2': '', 'mc_amount1': '', 'mc_amount2': ''},
])
def test_unused_trial_fields_do_not_grant_access(paypal, monkeypatch, fields):
    client, customer, custom = paypal
    verified(monkeypatch)
    data = event(custom); data.update(fields)
    assert send(client, data).status_code == 200
    account = client.get('/api/account/me', headers=customer).json()
    assert account['expires'] == 0
    assert not account['active']
