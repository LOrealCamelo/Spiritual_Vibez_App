"""Verify the actual FastAPI application against Neon using isolated test schemas.

--websocket is a verification-only transport for workspaces that block TCP 5432.
The PostgreSQL wire protocol is carried inside a certificate-verified TLS WebSocket.
Production continues using Psycopg/TLS and Neon's pooled TCP URL.
"""
import argparse
import asyncio
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode

import httpx
import psycopg
from psycopg import sql
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]


def start_tunnel(host):
    from websockets.asyncio.client import connect
    ready=threading.Event();state={}
    async def serve():
        async def handle(reader,writer):
            try:
                async with connect('wss://'+host+'/v2',max_size=None,open_timeout=20) as ws:
                    async def to_db():
                        while data:=await reader.read(65536):await ws.send(data)
                    async def from_db():
                        async for data in ws:
                            writer.write(data if isinstance(data,bytes) else data.encode());await writer.drain()
                    tasks=[asyncio.create_task(to_db()),asyncio.create_task(from_db())]
                    done,pending=await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
                    for task in pending:task.cancel()
                    for task in done:task.result()
            finally:
                writer.close()
        server=await asyncio.start_server(handle,'127.0.0.1',0)
        state['port']=server.sockets[0].getsockname()[1];ready.set()
        async with server:await server.serve_forever()
    thread=threading.Thread(target=lambda:asyncio.run(serve()),daemon=True);thread.start()
    if not ready.wait(10):raise RuntimeError('Verification tunnel did not start.')
    return state['port']


def tunneled_url(url,port):
    parts=urlsplit(url);params=dict(parse_qsl(parts.query));params.update(sslmode='disable',channel_binding='disable')
    # This local hop stays on loopback. The outer WebSocket uses verified TLS.
    return urlunsplit(parts._replace(netloc=parts.netloc.rsplit('@',1)[0]+'@127.0.0.1:'+str(port),query=urlencode(params)))


def cleanup(url,prefix):
    with psycopg.connect(url) as db:
        rows=db.execute('SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE %s',(prefix+'_%',)).fetchall()
        for (name,) in rows:
            if name.startswith(prefix+'_'):db.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(name)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--websocket',action='store_true')
    parser.add_argument('--backend-tests',action='store_true',help='Also run the membership/PayPal suite in isolated Neon schemas.')
    parser.add_argument('--init-app',action='store_true',help='After verification, add the app-owned empty schemas if absent.')
    args=parser.parse_args()
    values=dotenv_values(ROOT/'.env.local')
    urls={k:os.getenv(k) or values.get(k) for k in ['DATABASE_URL','DATABASE_URL_UNPOOLED']}
    if not all(urls.values()):raise RuntimeError('Private pooled and unpooled database URLs are required.')
    if args.websocket:
        tunneled={}
        for key,value in urls.items():
            host=urlsplit(value).hostname
            if not host.endswith('.neon.tech'):raise RuntimeError('The verification tunnel requires a Neon endpoint.')
            tunneled[key]=tunneled_url(value,start_tunnel(host))
        urls=tunneled
    if args.backend_tests:
        test_env={k:v for k,v in os.environ.items() if k not in ('DATABASE_URL','DATABASE_URL_UNPOOLED')}
        test_env.update(POSTGRES_TEST_URL=urls['DATABASE_URL'],POSTGRES_TEST_URL_UNPOOLED=urls['DATABASE_URL_UNPOOLED'],PYTHONPATH=str(ROOT))
        subprocess.run([sys.executable,'-m','pytest','backend/tests/test_memberships.py','backend/tests/test_paypal_memberships.py','-q'],cwd=ROOT,env=test_env,check=True)
    prefix='sv_livecheck_'+secrets.token_hex(5)
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    base=f'http://127.0.0.1:{port}'
    env={**os.environ,**urls,'DATABASE_NAMESPACE':prefix,'MEMBERSHIP_REQUIRED':'true',
         'PAYPAL_SUBSCRIPTIONS_ENABLED':'false','MEMBERSHIP_PUBLIC_URL':'https://example.test',
         'MEMBERSHIP_SUPPORT_EMAIL':'owner@example.test','PORT':str(port),'HOST':'127.0.0.1',
         'PYTHON':sys.executable,'PYTHONPATH':str(ROOT)+':'+str(ROOT/'frontend/tests')}
    server=None
    with tempfile.TemporaryDirectory(prefix='sv-neon-e2e-') as temporary:
        log_path=Path(temporary)/'server.log'
        def start():
            stream=log_path.open('a')
            process=subprocess.Popen(['npm','start'],cwd=ROOT,env=env,stdout=stream,stderr=stream,start_new_session=True)
            stream.close()
            for _ in range(180):
                if process.poll() is not None:raise RuntimeError('Application startup failed; check local server output privately.')
                try:
                    if httpx.get(base+'/api/health',timeout=2).status_code==200:return process
                except httpx.HTTPError:pass
                time.sleep(.3)
            os.killpg(process.pid,signal.SIGTERM)
            raise RuntimeError('Application did not become ready.')
        def stop(process):
            os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=20)
            for _ in range(100):
                try:httpx.get(base+'/api/health',timeout=1)
                except httpx.ConnectError:return
                except httpx.HTTPError:pass
                time.sleep(.2)
            raise RuntimeError('Previous app listener did not stop.')
        try:
            server=start();print('PASS: npm start / FastAPI health with real Neon storage.',flush=True)
            screenshots=ROOT.parent/'neon-browser-evidence'
            command=[sys.executable,str(ROOT/'frontend/tests/membership_flows.py'),'--base-url',base,'--screenshots',str(screenshots)]
            subprocess.run(command,cwd=ROOT,env=env,check=True)
            with httpx.Client(base_url=base) as client:
                account=client.post('/api/account/login',json={'email':'buyer@example.test','password':'cloud garden test password 88'})
                account.raise_for_status();headers={'Authorization':'Bearer '+account.json()['token']}
                saved=client.post('/api/wellness/journal',headers=headers,json={'prompt':'Neon persistence verification','entry_text':'This isolated test entry must survive an app restart.'})
                saved.raise_for_status();entry=saved.json()['id']
                print('PASS: authenticated server journal saved in Neon.',flush=True)
            stop(server);server=None
            server=start()
            with httpx.Client(base_url=base) as client:
                account=client.post('/api/account/login',json={'email':'buyer@example.test','password':'cloud garden test password 88'})
                account.raise_for_status();headers={'Authorization':'Bearer '+account.json()['token']}
                rows=client.get('/api/wellness/journal',headers=headers);rows.raise_for_status()
                assert any(row['id']==entry for row in rows.json()['entries'])
            print('PASS: account login, gift access and server-side journal survive application restart.',flush=True)
        except Exception:
            if log_path.exists():
                safe=log_path.read_text()
                for secret in values.values():
                    if secret:safe=safe.replace(secret,'[private value redacted]')
                target=ROOT.parent/'neon-application-test.log'
                target.write_text(safe);target.chmod(0o600)
            raise
        finally:
            if server is not None:stop(server)
            cleanup(urls['DATABASE_URL_UNPOOLED'],prefix)
            print('Removed only the isolated verification schemas.',flush=True)
    if args.init_app:
        os.environ.update(urls)
        from backend import postgres
        postgres.ensure_schema(postgres.schema_for(membership=True),True)
        postgres.ensure_schema(postgres.schema_for(),False)
        print('PASS: additive application schemas initialized; existing tables and accounts preserved.',flush=True)
    print('Neon end-to-end verification passed. No live payment or hosting deployment was performed.',flush=True)


if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Do not print connection exceptions/URLs or environment values.
        print('Neon verification failed:',type(exc).__name__,file=sys.stderr)
        raise SystemExit(1)
