"""Authorization, payment review, transaction reuse and atomic gifts with isolated databases."""
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services import memberships as m

PASSWORD = 'correct horse cloud garden 77'


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv('MEMBERSHIP_REQUIRED', 'true')
    monkeypatch.setenv('MEMBERSHIP_DB_PATH', str(tmp_path/'accounts.db'))
    monkeypatch.setenv('MEMBERSHIP_USER_DATA_DIR', str(tmp_path/'private'))
    monkeypatch.setenv('MEMBERSHIP_PUBLIC_URL', 'https://example.test')
    monkeypatch.setenv('MEMBERSHIP_SUPPORT_EMAIL', 'owner@example.test')
    monkeypatch.delenv('SMTP_HOST', raising=False)
    with m.database() as db:
        owner = db.execute('INSERT INTO members(email,password,admin,created) VALUES(?,?,1,?)',
                           ('owner@example.test', m.password_hash(PASSWORD), m.now())).lastrowid
        token = m.create_session(db, owner)
    with TestClient(app) as client:
        yield client, {'Authorization': 'Bearer '+token}


def signup(client, email='customer@example.test'):
    data = {'email': email, 'password': PASSWORD}
    assert client.post('/api/account/register', json={**data, 'admin': True, 'lifetime': True}).status_code == 200
    response = client.post('/api/account/login', json=data)
    assert response.status_code == 200
    assert not response.json()['user']['admin']
    return {'Authorization': 'Bearer '+response.json()['token']}


def gift(client, owner, kind='month'):
    r = client.post('/api/account/admin/gifts', headers=owner, json={'kind': kind})
    assert r.status_code == 200
    return r.json()['code']


def test_gate_rejects_anonymous_and_unpaid_and_prevents_privilege_escalation(setup):
    client, owner = setup
    assert client.get('/api/health').status_code == 200
    assert client.get('/api/tarot/cards').status_code == 401
    customer = signup(client)
    assert client.get('/api/tarot/cards', headers=customer).status_code == 403
    assert client.get('/api/account/admin/payments', headers=customer).status_code == 403
    config = client.get('/api/account/config').json()
    assert config['price_cents'] == 599 and config['renewal'] == 'manual'
    assert config['cashapp'] == 'https://cash.app/$lvcenterprise'
    assert config['venmo'] == 'https://venmo.com/lvcenterprise'


def test_payment_claim_does_not_unlock_and_owner_approval_is_idempotent(setup):
    client, owner = setup
    customer = signup(client)
    r = client.post('/api/account/payments', headers=customer, json={'provider': 'cashapp', 'reference': 'cash-123'})
    payment = r.json()['id']
    assert client.get('/api/tarot/cards', headers=customer).status_code == 403
    review = {'approve': True, 'note': 'Receipt verified in Cash App', 'verified_reference': 'ACTUAL-123'}
    assert client.post(f'/api/account/admin/payments/{payment}/review', headers=customer, json=review).status_code == 403
    assert client.post(f'/api/account/admin/payments/{payment}/review', headers=owner, json=review).status_code == 200
    expiry = client.get('/api/account/me', headers=customer).json()['expires']
    assert client.get('/api/tarot/cards', headers=customer).status_code == 200
    assert client.post(f'/api/account/admin/payments/{payment}/review', headers=owner, json=review).status_code == 409
    assert client.get('/api/account/me', headers=customer).json()['expires'] == expiry
    other = signup(client, 'other@example.test')
    r = client.post('/api/account/payments', headers=other, json={'provider': 'cashapp', 'reference': 'fake-new-ref'})
    assert client.post(f'/api/account/admin/payments/{r.json()["id"]}/review', headers=owner, json=review).status_code == 409
    assert not client.get('/api/account/me', headers=other).json()['active']


@pytest.mark.parametrize('kind', ['month', 'lifetime'])
def test_single_use_gifts_are_unique_and_cannot_be_redeemed_twice(setup, kind):
    client, owner = setup
    a, b = signup(client), signup(client, 'other@example.test')
    code = gift(client, owner, kind)
    assert gift(client, owner, kind) != code
    assert client.post('/api/account/redeem', headers=a, json={'code': code.lower()}).status_code == 200
    assert client.post('/api/account/redeem', headers=b, json={'code': code}).status_code == 400
    account = client.get('/api/account/me', headers=a).json()
    assert account['active']
    assert bool(account['lifetime']) == (kind == 'lifetime')
    with m.database() as db:
        assert db.execute('SELECT hash FROM gifts WHERE redeemed_by IS NOT NULL').fetchone()['hash'] != code


def test_simultaneous_redemption_has_exactly_one_winner(setup):
    client, owner = setup
    a, b = signup(client), signup(client, 'other@example.test')
    code = gift(client, owner)
    def redeem(headers):
        return client.post('/api/account/redeem', headers=headers, json={'code': code}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(redeem, [a, b]))
    assert sorted(statuses) == [200, 400]


def test_expired_revoked_codes_and_expired_memberships_are_denied(setup, monkeypatch):
    client, owner = setup
    customer = signup(client)
    code = gift(client, owner)
    h = m.digest(code)
    assert client.post('/api/account/admin/gifts/'+h+'/revoke', headers=owner, json={}).status_code == 200
    assert client.post('/api/account/redeem', headers=customer, json={'code': code}).status_code == 400
    code = gift(client, owner)
    with m.database() as db:
        db.execute('UPDATE gifts SET expires=? WHERE hash=?', (m.now()-1, m.digest(code)))
    assert client.post('/api/account/redeem', headers=customer, json={'code': code}).status_code == 400
    with m.database() as db:
        db.execute('UPDATE members SET expires=? WHERE email=?', (m.now()-1, 'customer@example.test'))
    assert client.get('/api/tarot/cards', headers=customer).status_code == 403


def test_private_journal_and_export_are_isolated_between_accounts(setup):
    client, owner = setup
    a, b = signup(client), signup(client, 'other@example.test')
    for headers in [a, b]:
        assert client.post('/api/account/redeem', headers=headers, json={'code': gift(client, owner)}).status_code == 200
    response = client.post('/api/wellness/journal', headers=a, json={'prompt': 'Private', 'entry_text': 'Only customer A may read this.'})
    assert response.status_code == 200, response.text
    a_export = client.get('/api/account/export', headers=a).json()
    b_export = client.get('/api/account/export', headers=b).json()
    assert 'Only customer A' in str(a_export)
    assert 'Only customer A' not in str(b_export)
    with m.database() as db:
        db.execute('UPDATE members SET expires=0 WHERE email=?', ('customer@example.test',))
    assert client.get('/api/account/export', headers=a).status_code == 200
    assert client.get('/api/wellness/journal', headers=a).status_code == 403


def test_reset_code_is_one_time_and_revokes_existing_sessions(setup):
    client, owner = setup
    customer = signup(client)
    uid = client.get('/api/account/me', headers=customer).json()['id']
    assert client.post('/api/account/forgot-password', json={'email': 'unknown@example.test'}).status_code == 200
    code = client.post(f'/api/account/admin/members/{uid}/reset', headers=owner, json={}).json()['code']
    body = {'token': code, 'password': 'another secure garden password 88'}
    assert client.post('/api/account/reset-password', json=body).status_code == 200
    assert client.get('/api/account/me', headers=customer).status_code == 401
    assert client.post('/api/account/reset-password', json=body).status_code == 400
    assert client.post('/api/account/login', json={'email': 'customer@example.test', 'password': PASSWORD}).status_code == 401


def test_suspend_preserves_data_and_logout_invalidates_token(setup):
    client, owner = setup
    customer = signup(client)
    uid = client.get('/api/account/me', headers=customer).json()['id']
    assert client.post(f'/api/account/admin/members/{uid}/access', headers=owner, json={'disabled': True, 'reason': 'Verified refund'}).status_code == 200
    assert client.get('/api/account/me', headers=customer).status_code == 401
    assert client.post(f'/api/account/admin/members/{uid}/access', headers=owner, json={'disabled': False, 'reason': 'Resolved issue'}).status_code == 200
    response = client.post('/api/account/login', json={'email': 'customer@example.test', 'password': PASSWORD})
    headers = {'Authorization': 'Bearer '+response.json()['token']}
    assert client.post('/api/account/logout', headers=headers, json={}).status_code == 200
    assert client.get('/api/account/me', headers=headers).status_code == 401


def test_rate_limits_persist_and_month_boundary_is_defined(setup):
    client, owner = setup
    for _ in range(20):
        assert m.rate_limit('test-key')
    assert not m.rate_limit('test-key')
    from datetime import datetime, timezone
    date = int(datetime(2028, 1, 31, tzinfo=timezone.utc).timestamp())
    assert datetime.fromtimestamp(m.month_after(date), timezone.utc).isoformat().startswith('2028-02-29')


def test_public_and_relative_storage_paths_are_rejected_without_writing_files():
    from pathlib import Path
    with pytest.raises(RuntimeError):
        m.private_path('relative/accounts.db')
    repo = Path(__file__).resolve().parents[2]
    with pytest.raises(RuntimeError):
        m.private_path(str(repo/'frontend/assets/unsafe-account-data.db'))
