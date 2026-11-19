"""Owner setup must load explicit private configuration without replacing server settings."""
import sys
import pytest
from backend.scripts import create_owner
from backend.services import memberships as m


def test_explicit_env_file_creates_owner_without_overriding_server_database(tmp_path, monkeypatch, capsys):
    server_db = tmp_path / 'server.db'
    monkeypatch.setenv('MEMBERSHIP_DB_PATH', str(server_db))
    private = tmp_path / '.env.local'
    private.write_text('MEMBERSHIP_DB_PATH=' + str(tmp_path / 'wrong.db') + '\n')
    monkeypatch.setattr(sys, 'argv', ['create_owner', '--env-file', str(private), '--email', 'owner@example.test'])
    monkeypatch.setattr(create_owner.getpass, 'getpass', lambda prompt: 'a private owner password 88')
    create_owner.main()
    with m.database() as db:
        row = db.execute('SELECT * FROM members WHERE email=?', ('owner@example.test',)).fetchone()
        assert row['admin'] == 1
        assert m.password_matches('a private owner password 88', row['password'])
    assert not (tmp_path / 'wrong.db').exists()
    assert 'a private owner password 88' not in capsys.readouterr().out


def test_missing_env_file_stops_before_password_or_database_access(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['create_owner', '--env-file', str(tmp_path / 'missing'), '--email', 'owner@example.test'])
    def unexpected(*args):
        pytest.fail('Must stop before password or database access')
    monkeypatch.setattr(create_owner.getpass, 'getpass', unexpected)
    monkeypatch.setattr(m, 'database', unexpected)
    with pytest.raises(SystemExit, match='No account was changed'):
        create_owner.main()
