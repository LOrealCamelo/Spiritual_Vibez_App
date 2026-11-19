"""Paid access duration, exact receipts, legacy preservation and plan tampering."""
from datetime import datetime, timezone
import calendar
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import pytest
from backend.services import memberships as m
from backend.tests.test_memberships import setup, signup


def submit(client, customer, plan, reference='PLAN-RECEIPT', provider='cashapp', **extra):
    response = client.post('/api/account/payments', headers=customer,
                           json={'provider': provider, 'reference': reference, 'plan': plan, **extra})
    assert response.status_code == 200, response.text
    return response.json()


def approve(client, owner, payment, amount, reference='ACTUAL-PLAN-RECEIPT'):
    return client.post(f'/api/account/admin/payments/{payment}/review', headers=owner,
                       json={'approve': True, 'note': 'Verified receipt in payment app',
                             'verified_reference': reference, 'verified_amount_cents': amount})


@pytest.mark.parametrize('plan,cents', [('month',599),('year',4500),('lifetime',6000)])
@pytest.mark.parametrize('provider', ['cashapp','venmo'])
def test_each_paid_plan_requires_exact_owner_verified_receipt(setup,plan,cents,provider):
    client,owner=setup;customer=signup(client)
    data=submit(client,customer,plan,provider=provider,price_cents=1,lifetime=True)
    assert data['price_cents']==cents and data['plan']==plan
    assert not client.get('/api/account/me',headers=customer).json()['active']
    pending=client.get('/api/account/admin/payments',headers=owner).json()[0]
    assert pending['plan']==plan and pending['price_cents']==cents
    assert approve(client,customer,data['id'],cents).status_code==403
    assert approve(client,owner,data['id'],1).status_code==422
    assert not client.get('/api/account/me',headers=customer).json()['active']
    assert approve(client,owner,data['id'],cents).status_code==200
    account=client.get('/api/account/me',headers=customer).json()
    assert account['active'] and bool(account['lifetime'])==(plan=='lifetime')
    if plan!='lifetime':
        expected=m.year_after(m.now()) if plan=='year' else m.month_after(m.now())
        assert abs(account['expires']-expected)<5
    assert client.get('/api/tarot/cards',headers=customer).status_code==200
    assert approve(client,owner,data['id'],cents).status_code==409
    assert client.get('/api/account/me',headers=customer).json()['expires']==account['expires']
    row=client.get('/api/account/admin/payments',headers=owner).json()[0]
    assert row['verified_amount_cents']==cents


def test_invalid_plan_and_missing_verified_amount_cannot_unlock(setup):
    client,owner=setup;customer=signup(client)
    assert client.post('/api/account/payments',headers=customer,json={'provider':'venmo','reference':'PLAN-123','plan':'free'}).status_code==422
    data=submit(client,customer,'year')
    assert approve(client,owner,data['id'],None).status_code==422
    assert not client.get('/api/account/me',headers=customer).json()['active']


def test_yearly_renewal_starts_after_remaining_paid_access(setup):
    client,owner=setup;customer=signup(client)
    leap_year=datetime.now(timezone.utc).year+1
    while not calendar.isleap(leap_year):leap_year+=1
    future=int(datetime(leap_year,2,29,12,tzinfo=timezone.utc).timestamp())
    with m.database() as db:db.execute('UPDATE members SET expires=? WHERE email=?',(future,'customer@example.test'))
    data=submit(client,customer,'year')
    assert approve(client,owner,data['id'],4500).status_code==200
    account=client.get('/api/account/me',headers=customer).json()
    assert account['expires']==int(datetime(leap_year+1,2,28,12,tzinfo=timezone.utc).timestamp())
    # A second year is added to the existing end date, never to today's date.
    second=submit(client,customer,'year',reference='SECOND-YEAR')
    assert approve(client,owner,second['id'],4500,'SECOND-ACTUAL').status_code==200
    assert client.get('/api/account/me',headers=customer).json()['expires']==m.year_after(account['expires'])


def test_same_receipt_cannot_fund_a_different_plan_or_account(setup):
    client,owner=setup;a=signup(client);b=signup(client,'other@example.test')
    data=submit(client,a,'month')
    assert approve(client,owner,data['id'],599).status_code==200
    other=submit(client,b,'lifetime',reference='OTHER-CLAIM')
    assert approve(client,owner,other['id'],6000).status_code==409
    assert not client.get('/api/account/me',headers=b).json()['active']


def test_concurrent_approvals_only_grant_one_year(setup):
    client,owner=setup;customer=signup(client);data=submit(client,customer,'year')
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses=list(pool.map(lambda _:approve(client,owner,data['id'],4500).status_code,range(2)))
    assert sorted(statuses)==[200,409]
    assert abs(client.get('/api/account/me',headers=customer).json()['expires']-m.year_after(m.now()))<5


def test_lifetime_removes_expiry_but_never_cancels_paypal_billing(setup):
    client,owner=setup;customer=signup(client)
    uid=client.get('/api/account/me',headers=customer).json()['id']
    with m.database() as db:
        db.execute("INSERT INTO paypal_subscriptions(id,user_id,status) VALUES(?,?,'active')",('EXISTING-MONTHLY',uid))
    data=submit(client,customer,'lifetime')
    assert approve(client,owner,data['id'],6000).status_code==200
    assert client.get('/api/account/me',headers=customer).json()['lifetime']
    with m.database() as db:assert db.execute('SELECT status FROM paypal_subscriptions').fetchone()['status']=='active'
    assert client.post('/api/account/payments',headers=customer,json={'provider':'cashapp','reference':'UNNEEDED-RENEWAL','plan':'year'}).status_code==409


def test_yearly_catalog_savings_are_correct(setup):
    client,_=setup;plans={p['id']:p for p in client.get('/api/account/config').json()['plans']}
    assert plans['year']['price_cents']==4500
    assert plans['lifetime']['price_cents']==6000
    assert plans['year']['savings_cents']==plans['month']['price_cents']*12-plans['year']['price_cents']==2688


def test_sqlite_upgrade_preserves_legacy_accounts_and_payments(tmp_path,monkeypatch):
    # Run against a local disposable v1 database even during opt-in PG tests.
    monkeypatch.delenv('DATABASE_URL',raising=False)
    path=tmp_path/'legacy.db';monkeypatch.setenv('MEMBERSHIP_DB_PATH',str(path))
    original=Path(m.__file__).resolve().parents[1]/'sql'/'memberships_v1.sql'
    with sqlite3.connect(path) as db:
        db.executescript(original.read_text().replace('BIGSERIAL','INTEGER').replace('BIGINT','INTEGER'))
        db.execute('INSERT INTO members(id,email,password,created) VALUES(42,?,?,123)',('existing@example.test','existing-hash'))
        db.execute('INSERT INTO payments(id,user_id,provider,reference,created) VALUES(7,42,?,?,123)',('cashapp','PRESERVE-RECEIPT'))
    for _ in range(2):
        with m.database() as db:
            member=db.execute('SELECT * FROM members WHERE id=42').fetchone()
            row=db.execute('SELECT * FROM payments WHERE id=7').fetchone()
            assert member['email']=='existing@example.test' and member['password']=='existing-hash'
            assert row['reference']=='PRESERVE-RECEIPT' and row['status']=='pending'
            assert row['plan']=='month' and row['price_cents']==599 and row['verified_amount_cents'] is None


def test_postgres_v1_upgrade_preserves_legacy_request_when_opted_in():
    from backend import postgres
    if not postgres.configured():
        pytest.skip('Opt-in PostgreSQL test requires disposable verification schemas.')
    schema=postgres.schema_for(membership=True)
    assert schema.startswith('sv_verify_'), 'Never downgrade an application schema in tests.'
    with m.database() as db:
        uid=db.execute('INSERT INTO members(email,password,created) VALUES(?,?,?)',('legacy@example.test','existing-hash',123)).lastrowid
        pid=db.execute('INSERT INTO payments(user_id,provider,reference,created) VALUES(?,?,?,?)',(uid,'venmo','KEEP-LEGACY',123)).lastrowid
        for column in ['verified_amount_cents','price_cents','plan']:
            db.execute('ALTER TABLE payments DROP COLUMN '+column)
    postgres._initialized.discard((postgres.validated_url('DATABASE_URL_UNPOOLED'),schema))
    for _ in range(2):
        with m.database() as db:
            row=db.execute('SELECT * FROM payments WHERE id=?',(pid,)).fetchone()
            assert row['reference']=='KEEP-LEGACY' and row['user_id']==uid
            assert row['plan']=='month' and row['price_cents']==599
            assert row['verified_amount_cents'] is None
