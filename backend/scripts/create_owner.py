"""Run on the server with its persistent membership DB configured. Never accepts a password on the command line."""
import argparse
import getpass
from pathlib import Path
from dotenv import load_dotenv
from backend.services import memberships as m
from backend.routers.accounts import email_address


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--email', required=True)
    parser.add_argument('--env-file', type=Path, help='Optional private local environment file; existing server variables take precedence.')
    parser.add_argument('--recover', action='store_true', help='Issue a one-time recovery code for an existing owner; run only in a private server shell.')
    args = parser.parse_args()
    if args.env_file:
        if not args.env_file.is_file():
            raise SystemExit('Private environment file not found. No account was changed.')
        load_dotenv(args.env_file, override=False)
    email = email_address(args.email)
    if args.recover:
        with m.database() as db:
            row = db.execute('SELECT id FROM members WHERE email=? AND admin=1', (email,)).fetchone()
            if not row:
                raise SystemExit('Existing owner not found. No account was changed.')
            code = m.create_reset(db, row['id'])
            m.audit(db, row['id'], 'server-owner-recovery', row['id'])
        print('Private one-time recovery code (30 minutes): ' + code)
        return
    password = getpass.getpass('New owner password (at least 12 characters): ')
    if len(password) < 12 or len(password) > 256 or password != getpass.getpass('Repeat password: '):
        raise SystemExit('Passwords must match and contain 12–256 characters.')
    with m.database() as db:
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT id FROM members WHERE email=?', (email,)).fetchone():
            raise SystemExit('This address already exists. No account was changed. Use verified recovery instead.')
        db.execute('INSERT INTO members(email,password,admin,created) VALUES(?,?,1,?)', (email, m.password_hash(password), m.now()))
    print('Owner created. Sign in through the app; no credentials were printed or emailed.')


if __name__ == '__main__':
    main()
