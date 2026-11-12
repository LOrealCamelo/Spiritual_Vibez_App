"""Build and run the actual Render Docker image, then check its web/static/API files."""
import argparse,json,os,subprocess,time,urllib.request,uuid
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ca-bundle',type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    env={k:v for k,v in os.environ.items() if k not in {'DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'}}
    docker=['docker','--host=unix:///var/run/docker.sock']
    suffix=uuid.uuid4().hex[:10]
    image='spiritual-vibez-smoke:'+suffix
    def run(*command,**kwargs):return subprocess.run(docker+list(command),cwd=root,env=env,check=True,**kwargs)
    build=['build','-t',image]
    if args.ca_bundle:build+=['--secret','id=build_ca,src='+str(args.ca_bundle.resolve())]
    run(*build,'.')
    container=None
    container_name='sv-render-smoke-'+suffix
    try:
        # Check the injected Render port, not only the local-development default.
        container=run('run','--name',container_name,'-d','--rm','-e','PORT=9137','-p','127.0.0.1::9137',image,capture_output=True,text=True).stdout.strip()
        address='http://'+run('port',container,'9137/tcp',capture_output=True,text=True).stdout.strip()
        http=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for _ in range(90):
            try:
                with http.open(address+'/api/health',timeout=2) as response:
                    if response.status==200:break
            except OSError:time.sleep(1)
        else:raise RuntimeError('Container did not become healthy on its Render PORT.')
        paths=['/','/app.js','/liquid-glass.css','/artwork.js','/assets/cosmos-night-sky.png','/assets/illustrations/cosmic.png','/assets/tarot/00-the-fool.png','/assets/tarot/77-king-of-pentacles.png']
        for path in paths:
            with http.open(address+path,timeout=10) as response:
                content=response.read()
                assert response.status==200,path
                if path.endswith('.png'):assert content.startswith(b'\x89PNG\r\n\x1a\n'),path
                if path=='/app.js':assert b'HOME_DESIGN.heading' in content,path
                if path=='/artwork.js':assert b'Your journey starts here' in content,path
                if path=='/liquid-glass.css':assert b'cosmos-night-sky.png' in content
        with http.open(address+'/api/tarot/cards',timeout=10) as response:assert json.load(response)['count']==78
        with http.open(address+'/api/astrology/moon-calendar?year=2026&month=11&timezone=America%2FNew_York',timeout=20) as response:assert len(json.load(response)['days'])==30
        print('PASS: actual Render container starts on PORT=9137 and serves the complete deck, scenery, clear glass and lunar API.')
    except Exception as exc:
        if isinstance(exc,subprocess.CalledProcessError) and exc.stderr:print(exc.stderr)
        if container:subprocess.run(docker+['logs','--tail','35',container],cwd=root,env=env,check=False)
        raise
    finally:
        subprocess.run(docker+['rm','-f',container_name],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
        subprocess.run(docker+['image','rm',image],cwd=root,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)

if __name__=='__main__':main()
