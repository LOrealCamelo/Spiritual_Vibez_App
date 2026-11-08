#!/usr/bin/env python3
"""Start the complete local web app, including its Python backend."""
import argparse
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import venv
import webbrowser


ROOT = Path(__file__).resolve().parent


def choose_port(requested):
    candidates = [requested] if requested else range(8000, 8020)
    for port in candidates:
        with socket.socket() as probe:
            try:
                probe.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError('The web port is already in use. Close the other app or choose --port 8020.')


def prepare_python():
    environment = ROOT / '.venv-web'
    executable = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    requirements = ROOT / 'backend/requirements.txt'
    marker = environment / '.requirements-sha256'
    expected = hashlib.sha256(requirements.read_bytes()).hexdigest()
    if not executable.is_file():
        print('First start: creating a private Python environment in .venv-web...', flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)
    ready = subprocess.run(
        [str(executable), '-c', 'import fastapi, uvicorn, httpx, dateutil'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0
    if not ready or not marker.is_file() or marker.read_text().strip() != expected:
        print('Installing the backend packages. Internet is needed on the first start.', flush=True)
        subprocess.run([
            str(executable), '-m', 'pip', 'install', '--disable-pip-version-check',
            '-r', str(requirements),
        ], cwd=ROOT, check=True)
        marker.write_text(expected)
    return executable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--no-browser', action='store_true', help='Print the address without opening a browser.')
    parser.add_argument('--port', type=int, default=None, help='Use this port instead of selecting an available port.')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        print('Install Python 3.11 or newer, then start this file again.', file=sys.stderr)
        return 1
    for relative in ['frontend/index.html', 'frontend/app.js', 'frontend/styles.css', 'backend/main.py']:
        if not (ROOT / relative).is_file():
            print('Extract the COMPLETE project ZIP first. Missing file: ' + relative, file=sys.stderr)
            return 1
    if args.port is not None and not 1 <= args.port <= 65535:
        parser.error('--port must be between 1 and 65535')
    process = None
    try:
        port = choose_port(args.port)
        executable = prepare_python()
        address = 'http://127.0.0.1:' + str(port)
        print('\nStarting Spiritual Vibez: web app + backend', flush=True)
        print('Project folder: ' + str(ROOT), flush=True)
        print('Browser address: ' + address, flush=True)
        print('Keep this window open while testing. Press Ctrl+C to stop.\n', flush=True)
        process = subprocess.Popen([
            str(executable), '-m', 'uvicorn', 'backend.main:app',
            '--host', '127.0.0.1', '--port', str(port),
        ], cwd=ROOT)
        # Avoid a proxy or an old server on another port when checking this local app.
        local_http = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for _ in range(120):
            if process.poll() is not None:
                raise RuntimeError('The backend exited before it was ready. See the error above.')
            try:
                with local_http.open(address + '/api/health', timeout=1) as response:
                    if response.status == 200:
                        break
            except (OSError, urllib.error.URLError):
                time.sleep(.25)
        else:
            raise RuntimeError('The backend did not become ready. See the messages above.')
        if not args.no_browser and not webbrowser.open(address):
            print('Open this address in your browser: ' + address, flush=True)
        return process.wait()
    except KeyboardInterrupt:
        print('\nStopping Spiritual Vibez...', flush=True)
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print('\nCould not start the app: ' + str(error), file=sys.stderr)
        print('Use Python 3.11+ and allow the first package installation to finish.', file=sys.stderr)
        return 1
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == '__main__':
    raise SystemExit(main())
