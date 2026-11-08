"""Numerical regressions and HTTP journeys for the repaired astronomy routes.

Fixed comparison values were calculated independently with Swiss Ephemeris
2.10.03 / Moshier (pyswisseph 2.10.3.2), not with the application library.
Swiss Ephemeris is a development reference only; it is not an app dependency.
"""
from datetime import datetime, timezone
from xml.etree import ElementTree
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.sky_engine import compute_planetary_positions, house_cusps, daily_transits, signed, lahiri_ayanamsa, astro_time

client = TestClient(app)
UTC = timezone.utc
BIRTH = dict(name='Mystic', birth_date='1996-11-05', birth_time='14:30', place_id='5142056')


def test_ten_planets_against_independent_reference():
    expected = {'Sun':225.591083,'Moon':210.702521,'Mercury':218.075245,'Venus':203.602616,
                'Mars':142.063589,'Jupiter':145.115236,'Saturn':8.874359,'Uranus':64.411536,
                'Neptune':1.946462,'Pluto':303.192631}
    result = compute_planetary_positions(datetime(2026,11,8,tzinfo=UTC))
    for planet, lon in expected.items():
        assert abs(signed(result[planet]['longitude']-lon)) < .02, planet
    assert result['Mercury']['retrograde'] and result['Venus']['retrograde']
    assert not result['Jupiter']['retrograde']
    assert result['LunarPhase']['phase_name'] == 'Waning Crescent'
    assert result['LunarPhase']['illumination_percent'] == pytest.approx(1.84, abs=.05)
    next_new = datetime.fromisoformat(result['LunarPhase']['next_phase_at'].replace('Z','+00:00'))
    # Independent lunar conjunction: 2026-11-09, 07:02 UTC (minute precision).
    assert abs((next_new-datetime(2026,11,9,7,2,tzinfo=UTC)).total_seconds()) < 90


@pytest.mark.parametrize('dt,lat,lon,expected',[
    (datetime(1996,11,5,19,30,tzinfo=UTC),43.1009,-75.2327,[346.4750111,32.6897171,61.4977601,83.1772309,103.6963791,128.1934510,166.4750111,212.6897171,241.4977601,263.1772309,283.6963791,308.1934510]),
    (datetime(2000,1,1,12,tzinfo=UTC),51.5074,-.1278,[24.0145904,61.0129715,81.9114216,99.4932253,118.9135352,147.4854873,204.0145904,241.0129715,261.9114216,279.4932253,298.9135352,327.4854873]),
    (datetime(1990,7,15,6,tzinfo=UTC),-33.8688,151.2093,[279.8007974,301.1882126,324.7883372,353.5127139,28.5571844,66.0515220,99.8007974,121.1882126,144.7883372,173.5127139,208.5571844,246.0515220]),
])
def test_placidus_both_hemispheres_and_longitude_wrap(dt,lat,lon,expected):
    actual, asc, mc = house_cusps(dt,lat,lon)
    assert max(abs(signed(a-b)) for a,b in zip(actual,expected)) < .001
    assert actual[0] == asc and actual[9] == mc
    assert any(abs((actual[(i+1)%12]-c)%360-30)>1 for i,c in enumerate(actual))


@pytest.mark.parametrize('year,reference',[(1900,22.4605497),(2000,23.8570924),(2026,24.2322186),(2100,25.2542874)])
def test_mean_lahiri_reference(year,reference):
    month,day=(11,8) if year==2026 else (1,1)
    assert lahiri_ayanamsa(astro_time(datetime(year,month,day,12,tzinfo=UTC))) == pytest.approx(reference,abs=.0001)


def test_city_selection_chart_wheel_and_full_report():
    places = client.get('/api/astrology/locations/search',params={'city':'Utica','country':'United States','state':'New York'}).json()['places']
    assert len(places)==1 and places[0]['place_id']=='5142056'
    assert places[0]['timezone']=='America/New_York'
    response = client.post('/api/astrology/natal-chart',json=BIRTH)
    assert response.status_code == 200
    chart=response.json()
    assert chart['birth_utc']=='1996-11-05T19:30:00+00:00'
    assert len(chart['placements'])==10 and len(chart['houses'])==12
    assert all(len(p['paragraphs'])==3 and 1<=p['house']<=12 for p in chart['placements'])
    assert all(h['description'] for h in chart['houses']) and chart['aspects']
    root=ElementTree.fromstring(chart['wheel_svg'])
    assert root.tag=='{http://www.w3.org/2000/svg}svg'
    assert len(root.findall('{http://www.w3.org/2000/svg}line'))>360
    assert 'script' not in chart['wheel_svg']


def test_sidereal_and_house_choices_are_real_transformations():
    tropical=client.post('/api/astrology/natal-chart',json=BIRTH).json()
    sidereal=client.post('/api/astrology/natal-chart',json={**BIRTH,'zodiac':'sidereal','house_system':'whole_sign'}).json()
    offset=sidereal['ayanamsa_degrees']
    for a,b in zip(tropical['placements'],sidereal['placements']):
        assert abs(signed(a['longitude']-b['longitude']-offset))<.00001
    assert all(h['longitude']%30==0 for h in sidereal['houses'])
    assert tropical['ascendant'] != sidereal['ascendant']


def test_historical_dst_and_missing_location_are_not_silently_guessed():
    for changes, phrase in [({'place_id':None},'select'),({'birth_date':'2024-03-10','birth_time':'02:30'},'did not exist'),
                            ({'birth_date':'2024-11-03','birth_time':'01:30'},'occurred twice'),({'birth_date':'2024-02-30'},'valid')]:
        r=client.post('/api/astrology/natal-chart',json={**BIRTH,**changes})
        assert r.status_code==422 and phrase in r.json()['detail']
    for fold, utc in [(0,'05:30:00'),(1,'06:30:00')]:
        r=client.post('/api/astrology/natal-chart',json={**BIRTH,'birth_date':'2024-11-03','birth_time':'01:30','time_fold':fold})
        assert r.status_code==200 and utc in r.json()['birth_utc']
    summer=client.post('/api/astrology/moon-phase',json={**BIRTH,'birth_date':'1996-07-05'}).json()
    assert '18:30:00' in summer['birth_utc']


def test_current_day_rolls_over_in_requested_timezone_and_forecasts_differ():
    now=datetime(2026,11,9,2,tzinfo=UTC)  # Still Nov 8 in New York.
    virgo=daily_transits('Virgo',timezone_name='America/New_York',now=now)
    pisces=daily_transits('Pisces',timezone_name='America/New_York',now=now)
    assert virgo['date']=='2026-11-08' and virgo['as_of'].startswith('2026-11-08T21:00')
    assert virgo['planets']==pisces['planets'] and virgo['forecast']['content']!=pisces['forecast']['content']
    assert virgo['forecast']['details'][1]['solar_house']!=pisces['forecast']['details'][1]['solar_house']
    tomorrow=daily_transits('Virgo',timezone_name='America/New_York',now=datetime(2026,11,9,6,tzinfo=UTC))
    assert tomorrow['date']=='2026-11-09' and tomorrow['moon']['phase_angle_deg']!=virgo['moon']['phase_angle_deg']
    yesterday=daily_transits('Virgo','2026-11-07','America/New_York',now=now)
    assert yesterday['as_of'].startswith('2026-11-07T12:00:00')


@pytest.mark.parametrize('params',[{'date':'2026-02-30'},{'timezone':'Nowhere/Fake'},{'sign':'bad'},{'zodiac':'bad'}])
def test_bad_daily_input_is_a_useful_validation_error(params):
    assert client.get('/api/astrology/daily-transits',params=params).status_code==422
