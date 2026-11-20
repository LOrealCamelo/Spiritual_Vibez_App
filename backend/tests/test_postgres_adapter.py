"""SQL portability and fail-closed configuration, without cloud credentials."""
import pytest
from backend import postgres


def test_sql_translation_preserves_conflicts_and_parameterization():
    query,returns=postgres.translate('INSERT OR IGNORE INTO members(email,password,created) VALUES(?,?,?)')
    assert query=='INSERT INTO members(email,password,created) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING RETURNING id'
    assert returns
    query,returns=postgres.translate('INSERT OR REPLACE INTO limits VALUES(?,?,1)')
    assert 'ON CONFLICT(key) DO UPDATE' in query and not returns
    assert postgres.translate('SELECT hash FROM gifts WHERE hash=?')==('SELECT hash FROM gifts WHERE hash=%s',False)


def test_private_neon_connections_require_tls_and_unpooled_migration_url(monkeypatch):
    monkeypatch.setenv('DATABASE_URL','postgresql://user:example@ep-test-pooler.neon.tech/app?sslmode=require')
    assert postgres.validated_url().startswith('postgresql://')
    with pytest.raises(RuntimeError):postgres.validated_url('DATABASE_URL_UNPOOLED')
    monkeypatch.setenv('DATABASE_URL','postgresql://user:example@ep-test.neon.tech/app?sslmode=disable')
    with pytest.raises(RuntimeError):postgres.validated_url()
    monkeypatch.setenv('DATABASE_NAMESPACE','bad; DROP SCHEMA public')
    with pytest.raises(RuntimeError):postgres.namespace()


def test_rows_support_existing_mapping_and_scalar_readers():
    row=postgres.Record(id=8,email='customer@example.test')
    assert row['id']==row[0]==8
    assert dict(row)=={'id':8,'email':'customer@example.test'}


@pytest.mark.parametrize('direct',[
    'postgresql://user:example@ep-other.neon.tech/app?sslmode=require',
    'postgresql://user:example@ep-test.neon.tech/other?sslmode=require',
])
def test_mismatched_neon_targets_stop_before_any_schema_write(monkeypatch,direct):
    monkeypatch.setenv('DATABASE_URL','postgresql://user:example@ep-test-pooler.neon.tech/app?sslmode=require')
    monkeypatch.setenv('DATABASE_URL_UNPOOLED',direct)
    def unexpected_connection(*args,**kwargs):pytest.fail('Mismatched database must not receive schema writes')
    monkeypatch.setattr(postgres.psycopg,'connect',unexpected_connection)
    with pytest.raises(postgres.DatabaseUnavailable):postgres.ensure_schema('sv_target_check_memberships',True)


def test_matching_neon_targets_allow_separate_credentials_for_migrations(monkeypatch):
    monkeypatch.setenv('DATABASE_URL','postgresql://runtime:example@ep-test-pooler.neon.tech/app?sslmode=require')
    direct='postgresql://migrator:example@ep-test.neon.tech/app?sslmode=require'
    monkeypatch.setenv('DATABASE_URL_UNPOOLED',direct)
    assert postgres.migration_url()==direct


def test_postgres_outage_returns_503_without_local_fallback(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    monkeypatch.setenv('DATABASE_URL','postgresql://user:example@ep-test.neon.tech/app?sslmode=require')
    monkeypatch.setenv('MEMBERSHIP_REQUIRED','false')
    def unavailable(*args,**kwargs):raise postgres.DatabaseUnavailable('private driver details')
    monkeypatch.setattr(postgres,'connect',unavailable)
    response=TestClient(app).get('/api/account/config')
    assert response.status_code==503
    assert response.json()=={'detail':'Account storage is temporarily unavailable.'}
    assert 'private driver details' not in response.text


def test_pytest_refuses_an_application_database_at_collection():
    import os,subprocess,sys
    result=subprocess.run([sys.executable,'-m','pytest','backend/tests/test_postgres_adapter.py','--collect-only','-q'],
        env={**os.environ,'DATABASE_URL':'postgresql://blocked.invalid/app'},capture_output=True,text=True)
    assert result.returncode==4
    assert 'Refusing tests with DATABASE_URL set' in result.stderr
