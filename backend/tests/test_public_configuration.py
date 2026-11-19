"""Static hosts and FastAPI must expose the same public configuration."""
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
root = Path(__file__).resolve().parents[2]


def test_security_headers_and_private_api_caching():
    for path in ['/', '/api/health', '/api/not-a-route', '/assets/icons/avatar-180.png']:
        response = client.get(path)
        assert response.headers['x-content-type-options'] == 'nosniff'
        assert response.headers['x-frame-options'] == 'DENY'
        assert response.headers['referrer-policy'] == 'strict-origin-when-cross-origin'
        assert 'microphone=()' in response.headers['permissions-policy']
        if path.startswith('/api/'):
            assert response.headers['cache-control'] == 'no-store'


def test_robots_sitemap_and_browser_scripts_are_served_by_render():
    robots = client.get('/robots.txt')
    assert robots.status_code == 200
    assert 'https://app.neurospicymystic.com/sitemap.xml' in robots.text
    sitemap = client.get('/sitemap.xml')
    assert sitemap.status_code == 200
    tree = ET.fromstring(sitemap.text)
    assert [n.text for n in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')] == ['https://app.neurospicymystic.com/']
    for script in ['url-hygiene.js', 'metadata.js']:
        response = client.get('/' + script)
        assert response.status_code == 200
        assert 'javascript' in response.headers['content-type']
        assert response.content == (root / 'frontend' / script).read_bytes()


def test_every_manifest_icon_and_seo_image_is_public():
    manifest = client.get('/assets/icons/spiritual-vibz.webmanifest')
    assert manifest.status_code == 200
    for icon in manifest.json()['icons']:
        response = client.get(icon['src'])
        assert response.status_code == 200
        assert response.content.startswith(b'\x89PNG\r\n\x1a\n')
    image = client.get('/assets/home-top-with-spiritual-vibz-logo.png')
    assert image.status_code == 200


def test_existing_public_frontend_cors_contract_is_preserved():
    # This is an audit, not authorization to restrict origins or change auth.
    for origin in ['https://app.neurospicymystic.com', 'https://spiritualvibz.netlify.app']:
        response = client.options('/api/astrology/natal-chart', headers={
            'Origin': origin, 'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'})
        assert response.status_code == 200
        assert response.headers['access-control-allow-origin'] == origin
        assert 'POST' in response.headers['access-control-allow-methods']


def test_homepage_script_and_stylesheet_references_are_served():
    """Catch modules present in Netlify builds but missing from FastAPI's frontend."""
    import re
    from fastapi.testclient import TestClient
    from backend.main import app
    with TestClient(app) as client:
        document = client.get('/').text
        paths = re.findall(r'(?:src|href)="([^"?]+(?:\.js|\.css))(?:\?[^" ]*)?"', document)
        assert 'love-experience.js' in paths
        assert 'love-experience.css' in paths
        for path in paths:
            if path.startswith(('http:', 'https:')):
                continue
            response = client.get('/' + path.lstrip('/'))
            assert response.status_code == 200, path
            assert ('javascript' if path.endswith('.js') else 'text/css') in response.headers['content-type'], path
