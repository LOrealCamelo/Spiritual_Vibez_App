import pytest
import io
import json
from urllib.parse import urlparse, parse_qs
from fastapi.testclient import TestClient
from backend.main import app
from backend.services import asteroid_charts as engine

client = TestClient(app)
BIRTH = dict(birth_date='1996-11-05',birth_time='02:30',birth_period='PM',place_id='5142056',chart_system='natal')


def test_horizons_csv_uses_apparent_longitude_and_measured_motion():
    # Independent NASA/JPL Horizons quantity 31, 1996-Nov-05, geocentric Ceres.
    text = '$$SOE\n1996-Nov-05 19:29, , ,267.1853459,-3.0383916,\n1996-Nov-05 19:30, , ,267.1855982,-3.0384053,\n1996-Nov-05 19:31, , ,267.1858505,-3.0384189,\n$$EOE'
    lon, lat, speed = engine.parse_horizons(text)
    assert lon == pytest.approx(267.1855982)
    assert lat == pytest.approx(-3.0384053)
    assert speed == pytest.approx(.363312)
    with pytest.raises(engine.EphemerisUnavailable):
        engine.parse_horizons('No ephemeris available')


def test_asteroids_use_actual_birth_utc_and_city_houses(monkeypatch):
    calls = []
    def position(body_id, instant):
        calls.append((body_id,instant))
        return {1:267.1855982,2:243.9,3:6,4:268.3}[body_id], -3, .36
    monkeypatch.setattr(engine,'horizons_position',position)
    pm = client.post('/api/astrology/asteroids/natal-chart',json=BIRTH)
    assert pm.status_code == 200
    chart = pm.json()
    assert [a['name'] for a in chart['asteroids']] == ['Ceres','Pallas','Juno','Vesta']
    assert all(instant == '1996-11-05T19:30:00+00:00' for _,instant in calls)
    assert chart['asteroids'][0]['longitude'] == pytest.approx(267.185598)
    assert chart['asteroids'][0]['house'] == 10
    assert '⚳' in chart['wheel_svg'] and chart['asteroid_aspects']
    assert 'NASA/JPL' in chart['ephemeris_source']
    am = client.post('/api/astrology/asteroids/natal-chart',json={**BIRTH,'birth_period':'AM'}).json()
    assert calls[-1][1] == '1996-11-05T07:30:00+00:00'
    assert am['houses'] != chart['houses']
    sidereal = client.post('/api/astrology/asteroids/natal-chart',json={**BIRTH,'zodiac':'sidereal','aspect_mode':'hide'}).json()
    assert sidereal['asteroids'][0]['longitude'] != chart['asteroids'][0]['longitude']
    assert not sidereal['asteroid_aspects']


@pytest.mark.parametrize('selected', [[],[1,1],[9999999999],list(range(1,12))])
def test_invalid_selections_are_rejected(selected):
    assert client.post('/api/astrology/asteroids/natal-chart',json={**BIRTH,'asteroid_ids':selected}).status_code == 422


def test_ephemeris_failure_never_returns_placeholder_positions(monkeypatch):
    def unavailable(*args):
        raise engine.EphemerisUnavailable('Ephemeris unavailable; please retry.')
    monkeypatch.setattr(engine,'horizons_position',unavailable)
    response = client.post('/api/astrology/asteroids/natal-chart',json=BIRTH)
    assert response.status_code == 503
    assert 'asteroids' not in response.json()


def test_full_catalog_search_and_non_major_asteroid_calculation(monkeypatch):
    engine.search_asteroids.cache_clear()
    monkeypatch.setattr(engine, '_CATALOG_RECORDS', {})
    requests = []
    def catalog_response(url, timeout):
        requests.append(parse_qs(urlparse(url).query))
        return io.BytesIO(json.dumps({'count': 1, 'data': [['1008', 'La Paz']]}).encode())
    monkeypatch.setattr(engine, 'urlopen', catalog_response)
    result = client.get('/api/astrology/asteroids', params={'query':'1008'}).json()
    assert result['asteroids'][0]['name'] == 'La Paz'
    assert requests[0]['sb-cdata'] == ['{"AND": ["pdes|EQ|1008"]}']
    assert requests[0]['sb-ns'] == ['n']
    monkeypatch.setattr(engine, 'horizons_position', lambda *args: (42.0, 1.0, .1))
    chart = client.post('/api/astrology/asteroids/natal-chart', json={**BIRTH, 'asteroid_ids':[1008]}).json()
    assert chart['asteroids'][0]['id'] == 1008
    assert chart['asteroids'][0]['name'] == 'La Paz'
    assert chart['asteroids'][0]['longitude'] == 42.0
    engine.search_asteroids.cache_clear()
