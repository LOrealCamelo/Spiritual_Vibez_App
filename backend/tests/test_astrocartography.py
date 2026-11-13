import math
import xml.etree.ElementTree as ET
from functools import lru_cache
import astronomy as ae
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import AstrocartographyRequest
from backend.services.astrocartography import astrocartography_report, distance_to_line
from backend.services.sky_engine import astro_time
from datetime import datetime

client=TestClient(app)
BASE=dict(birth_date='1996-11-05',birth_time='14:30',place_id='5142056')


@lru_cache(maxsize=4)
def report(time='14:30',focus='home'):
    return astrocartography_report(AstrocartographyRequest(**{**BASE,'birth_time':time},focus=focus))


def test_real_birth_details_drive_map_and_all_four_angles():
    data=report();assert data['birth_utc']=='1996-11-05T19:30:00+00:00'
    assert len(data['planets'])==10
    t=astro_time(datetime.fromisoformat(data['birth_utc']))
    for planet in data['planets']:
        assert set(planet['lines'])=={'ASC','DSC','MC','IC'}
        for angle in ['ASC','DSC']:
            points=planet['lines'][angle]
            assert len(points)>50
            for lat,lon in points[1:-1:17]:
                horizon=ae.Horizon(t,ae.Observer(lat,lon,0),planet['right_ascension_hours'],planet['declination'],ae.Refraction.Airless)
                assert abs(horizon.altitude)<1e-7
                assert (0<=horizon.azimuth<=180) if angle=='ASC' else (180<=horizon.azimuth<=360)
                assert distance_to_line(lat,lon,planet,angle)<1e-6
        assert abs(abs(planet['lines']['MC'][0][1]-planet['lines']['IC'][0][1])-180)<1e-8
        assert distance_to_line(0,planet['mc_longitude'],planet,'MC')<1e-6
        assert distance_to_line(0,planet['mc_longitude'],planet,'IC')>9900
    root=ET.fromstring(data['map_svg']);assert root.attrib['viewBox']=='0 0 1200 600'
    assert len([n for n in root.iter() if n.attrib.get('class')=='astro-line'])==40
    assert len(data['places'])==8
    assert all(p['distance_km']>=0 and p['planet'] in ['Moon','Venus','Jupiter','Sun'] for p in data['places'])


def test_fifteen_minutes_changes_lines_and_focus_changes_suggestions_only():
    original=report();later=report('14:45');career=report(focus='career')
    shift=abs(original['planets'][0]['mc_longitude']-later['planets'][0]['mc_longitude'])
    assert 3<shift<4.5
    assert original['places']!=later['places']
    assert original['planets']==career['planets'] and original['places']!=career['places']


def test_same_utc_instant_with_explicit_coordinates_produces_same_lines():
    other=astrocartography_report(AstrocartographyRequest(birth_date='1996-11-05',birth_time='19:30',latitude=51.5,longitude=0,timezone='UTC'))
    assert other['planets']==report()['planets']


def test_crossings_lie_on_both_named_lines_and_city_lists_include_all_nearby_lines():
    data=report();lookup={p['planet']:p for p in data['planets']}
    assert len(data['crossings'])>100
    for point in data['crossings']:
        for name,angle in [(point['planet_a'],point['angle_a']),(point['planet_b'],point['angle_b'])]:
            assert distance_to_line(point['latitude'],point['longitude'],lookup[name],angle)<1e-5
    for city in data['places']:
        expected={(p['planet'],angle) for p in data['planets'] for angle in ['ASC','DSC','MC','IC']
                  if distance_to_line(city['latitude'],city['longitude'],p,angle)<=500}
        assert {(p['planet'],p['angle']) for p in city['nearby_lines']}==expected


@pytest.mark.parametrize('script',['equinox-calendar.js','astro-map-tools.js','astrocartography.js'])
def test_new_web_modules_are_actually_served(script):
    r=client.get('/'+script)
    assert r.status_code==200 and 'javascript' in r.headers['content-type']
    assert len(r.content)>1000


@pytest.mark.parametrize('payload',[{}, {'birth_date':'1996-11-05','birth_time':'14:30'}, {**BASE,'birth_time':'25:99'}, {**BASE,'focus':'unknown'}, {**BASE,'place_id':'bad'}])
def test_missing_or_invalid_birth_details_never_return_preset_city_results(payload):
    assert client.post('/api/astrology/astrocartography',json=payload).status_code==422


def test_city_only_legacy_request_is_rejected_with_actionable_message():
    r=client.get('/api/astrology/astrocartography?city=Utica')
    assert r.status_code==422 and 'birth date' in r.json()['detail']


def test_global_map_city_search_returns_real_locations_with_country_and_region():
    r=client.get('/api/astrology/astrocartography/places?query=Paris')
    assert r.status_code==200
    places=r.json()['places']
    assert any(p['country_code']=='FR' and p['city']=='Paris' for p in places)
    assert all('latitude' in p and 'longitude' in p and p['country'] in p['label'] for p in places)
    assert client.get('/api/astrology/astrocartography/places?query=P').status_code==422
