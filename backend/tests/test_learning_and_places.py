from fastapi.testclient import TestClient
from backend.main import app
from backend.services.moon_calendar import moon_disc_svg

client = TestClient(app)


def test_birthplace_dropdowns_resolve_country_region_city_and_timezone():
    countries = client.get('/api/astrology/locations/countries').json()['countries']
    assert {'code': 'US', 'name': 'United States'} in countries
    regions = client.get('/api/astrology/locations/regions', params={'country': 'US'}).json()['regions']
    assert {'code': 'NY', 'name': 'New York'} in regions
    cities = client.get('/api/astrology/locations/cities', params={'country': 'US', 'state': 'NY', 'query': 'Utica'}).json()
    assert cities['places'][0]['place_id'] == '5142056'
    assert cities['places'][0]['timezone'] == 'America/New_York'
    assert all(p['state_code'] == 'NY' for p in cities['places'])
    assert 'America/New_York' in client.get('/api/astrology/locations/timezones').json()['timezones']
    assert client.get('/api/astrology/locations/cities', params={'country': 'XX'}).status_code == 422
    assert client.get('/api/astrology/locations/cities', params={'country': 'US'}).json()['limited']


def test_general_houses_are_education_and_not_a_personal_chart():
    guide = client.get('/api/astrology/houses').json()
    assert len(guide['houses']) == 12 and len(guide['planets']) == 10
    assert guide['houses'][0]['natural_sign'] == 'Aries'
    assert guide['houses'][-1]['natural_sign'] == 'Pisces'
    assert 'do not determine your actual house rulers' in guide['note']
    assert not any('longitude' in h for h in guide['houses'])


def test_learning_library_covers_tarot_numbers_courts_and_master_numbers():
    guide = client.get('/api/astrology/learning-library').json()
    assert [n['number'] for n in guide['numbers']] == [1,2,3,4,5,6,7,8,9,11,22,33]
    assert len(guide['tarot_numbers']) == 10 and len(guide['court_cards']) == 4
    assert all(n['strengths'] and n['shadow'] for n in guide['numbers'])
    mercury = next(p for p in guide['planets'] if p['name'] == 'Mercury')
    assert mercury['tarot_card'] == 'The Magician'
    assert len(client.get('/api/synastry/numerology-lessons').json()['tarot_numbers']) == 10
    assert client.post('/api/synastry/life-path', json={'birth_year':2000,'birth_month':2,'birth_day':30}).status_code == 422


def test_silver_moon_shapes_replace_yellow_emoji_in_calculated_sky():
    shapes = [moon_disc_svg(a) for a in (0,90,180,270)]
    assert len(set(shapes)) == 4
    assert all('#e2e7ed' in s and '#ffedc5' not in s for s in shapes)
    sky = client.get('/api/astrology/daily-transits', params={'date':'2026-11-10'}).json()
    assert '<svg' in sky['moon']['image_svg']
