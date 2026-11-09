"""Build the complete source ZIP and boot the extracted app as a user would."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip-out', type=Path, required=True)
    parser.add_argument('--ref', default='HEAD')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    output = args.zip_out.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'archive', '--format=zip', '--prefix=SpiritualVibez/',
                    '-o', str(output), args.ref], cwd=root, check=True)
    with tempfile.TemporaryDirectory(prefix='spiritual vibez ') as temporary:
        unpacked = Path(temporary)
        with zipfile.ZipFile(output) as archive:
            archive.extractall(unpacked)
        app = unpacked / 'SpiritualVibez'
        for file in ['START_WEB_WINDOWS.cmd', 'run_web.py', 'frontend/index.html',
                     'frontend/app.js', 'frontend/styles.css', 'backend/main.py',
                     'mobile/App.tsx', 'mobile/android/app/build.gradle',
                     'mobile/ios/SpiritualVibez.xcodeproj/project.pbxproj']:
            assert (app / file).is_file(), 'Application source missing from ZIP: ' + file
        assert len(list((app / 'mobile/assets/illustrations').glob('*.png'))) == 4
        assert len(json.loads((app / 'mobile/src/data/uiPanels.json').read_text())) == 24
        assert (app / 'frontend/artwork.js').is_file()
        assert len(list((app / 'mobile/assets/tarot').glob('*.png'))) == 78
        assert (app / 'frontend/cosmic.js').is_file()
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        address = 'http://127.0.0.1:' + str(port)
        if os.name == 'nt':
            # /s preserves the quoted batch path, including spaces in the extracted folder.
            command = 'cmd.exe /d /s /c ""' + str(app / 'START_WEB_WINDOWS.cmd') + '" --no-browser --port ' + str(port) + '"'
        else:
            command = [sys.executable, str(app / 'run_web.py'), '--no-browser', '--port', str(port)]
        log_path = output.with_suffix('.startup.log')
        http = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with log_path.open('w+', encoding='utf-8') as log:
            process = subprocess.Popen(command, cwd=app, stdout=log, stderr=log,
                                       start_new_session=os.name != 'nt')
            try:
                deadline = time.monotonic() + 300
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        raise RuntimeError('The extracted app exited before startup.')
                    try:
                        with http.open(address + '/api/health', timeout=1) as response:
                            if response.status == 200:
                                break
                    except OSError:
                        time.sleep(.5)
                else:
                    raise RuntimeError('The extracted app did not start within five minutes.')
                for route in ['/', '/app.js', '/cosmic.js', '/artwork.js', '/styles.css', '/liquid-glass.css', '/assets/illustrations/cosmic.png', '/assets/tarot/00-the-fool.png', '/assets/ui_background.png',
                              '/assets/footer.png', '/assets/cartoon_me_transparent3.png']:
                    with http.open(address + route) as response:
                        assert response.status == 200, route
                        content = response.read()
                        if route.endswith('.png'):
                            assert content.startswith(b'\x89PNG\r\n\x1a\n'), route
                        if route == '/app.js':
                            assert b"https://neurospicymystic.com/" in content
                            assert b'.webp' not in content
                with http.open(address + '/api/tarot/cards') as response:
                    assert json.load(response)['count'] == 78
                with http.open(address + '/api/tarot/spreads') as response:
                    assert json.load(response)['count'] == 48
                with http.open(address + '/api/rituals/search?query=rosemary') as response:
                    assert json.load(response)['count'] >= 1
                with http.open(address + '/api/astrology/moon-calendar?year=2026&month=11&timezone=UTC') as response:
                    lunar=json.load(response)
                    assert len(lunar['days'])==30 and lunar['days'][0]['ingresses'][0]['sign']=='Leo'
                    assert lunar['days'][0]['moon_image_svg'].startswith('<svg')
                birth=json.dumps({'birth_date':'1996-11-05','birth_time':'14:30','place_id':'5142056'}).encode()
                request=urllib.request.Request(address+'/api/astrology/natal-chart',data=birth,headers={'Content-Type':'application/json'})
                with http.open(request) as response:
                    chart=json.load(response)
                    assert len(chart['placements'])==10 and len(chart['angles'])==4
                    assert chart['placements'][0]['glyph'] and chart['placements'][0]['sign_glyph']
                    assert chart['houses'][0]['ruler_placement'] and chart['wheel_svg']
                print('PASS: complete ZIP, extracted-folder launcher, web source, PNGs and live backend.')
                print('Platform: ' + sys.platform)
                print('ZIP: ' + str(output))
            except Exception:
                log.flush()
                log.seek(0)
                print(log.read(), file=sys.stderr)
                raise
            finally:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)


if __name__ == '__main__':
    main()
