"""12-hour input must change the actual UTC instant and computed chart.

Fixed chart references use Swiss Ephemeris 2.10.03 / Moshier, independently of
the application's Astronomy Engine. Swiss Ephemeris is not a runtime dependency.
"""
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import BirthDataRequest
from backend.services.birth_locations import resolve_birth
from backend.services.sky_engine import signed

client = TestClient(app)
BIRTH = dict(birth_date='1996-11-05', birth_time='02:30', place_id='5142056')


@pytest.mark.parametrize('hour', range(1, 13))
@pytest.mark.parametrize('period', ['AM', 'PM'])
def test_every_am_pm_hour_resolves_to_the_correct_instant(hour, period):
    # Utica was UTC-5 on this date. Enumerate midnight and noon independently.
    expected_hour = ({12: 0}.get(hour, hour) if period == 'AM'
                     else {12: 12}.get(hour, hour + 12))
    data = BirthDataRequest(**{**BIRTH, 'birth_time': f'{hour:02d}:59', 'birth_period': period})
    utc, place, local = resolve_birth(data)
    assert datetime.fromisoformat(local).hour == expected_hour
    assert utc == datetime(1996, 11, 5, expected_hour, 59,
                           tzinfo=timezone(timedelta(hours=-5))).astimezone(timezone.utc)
    assert place['timezone'] == 'America/New_York'


@pytest.mark.parametrize('route', ['natal-chart', 'moon-phase'])
def test_am_pm_changes_results_and_matches_existing_24h_api(route):
    charts = []
    for period, clock, utc in [('AM', '02:30', '07:30'), ('PM', '14:30', '19:30')]:
        response = client.post('/api/astrology/' + route, json={**BIRTH, 'birth_period': period})
        assert response.status_code == 200
        chart = response.json()
        legacy = client.post('/api/astrology/' + route, json={**BIRTH, 'birth_time': clock}).json()
        assert chart == legacy
        assert chart['birth_time'] == clock
        assert chart['birth_time_12h'] == '02:30 ' + period
        assert chart['birth_utc'] == f'1996-11-05T{utc}:00+00:00'
        charts.append(chart)
    am, pm = charts
    if route == 'natal-chart':
        assert am['ascendant'] != pm['ascendant']
        assert am['midheaven'] != pm['midheaven']
        assert am['houses'] != pm['houses']
        assert am['wheel_svg'] != pm['wheel_svg']
        assert am['placements'][1]['house'] != pm['placements'][1]['house']
    else:
        assert am['illumination_percentage'] != pm['illumination_percentage']
        assert am['moon_position'] != pm['moon_position']


@pytest.mark.parametrize('period,moon,asc,mc,houses', [
    ('AM', 154.740827, 173.858484, 82.723833,
     [173.858484,198.885511,228.839924,262.723833,296.961247,327.718046,
      353.858484,18.885511,48.839924,82.723833,116.961247,147.718046]),
    ('PM', 160.729074, 346.475083, 263.177268,
     [346.475083,32.689772,61.497801,83.177268,103.696418,128.193499,
      166.475083,212.689772,241.497801,263.177268,283.696418,308.193499]),
])
def test_am_pm_chart_against_independent_ephemeris(period, moon, asc, mc, houses):
    chart = client.post('/api/astrology/natal-chart', json={**BIRTH, 'birth_period': period}).json()
    assert abs(signed(chart['placements'][1]['longitude'] - moon)) < .02
    assert abs(signed(chart['ascendant_longitude'] - asc)) < .001
    assert abs(signed(chart['midheaven_longitude'] - mc)) < .001
    assert all(abs(signed(h['longitude'] - ref)) < .001 for h, ref in zip(chart['houses'], houses))


@pytest.mark.parametrize('date,period,clock,expected_status,expected', [
    ('2024-03-10', 'AM', '02:30', 422, 'did not exist'),
    ('2024-03-10', 'PM', '02:30', 200, '2024-03-10T18:30:00+00:00'),
    ('2024-11-03', 'AM', '01:30', 422, 'occurred twice'),
    ('2024-11-03', 'PM', '01:30', 200, '2024-11-03T18:30:00+00:00'),
    ('1996-07-05', 'PM', '02:30', 200, '1996-07-05T18:30:00+00:00'),
])
def test_am_pm_uses_historical_timezone_and_dst(date, period, clock, expected_status, expected):
    response = client.post('/api/astrology/natal-chart', json={
        **BIRTH, 'birth_date': date, 'birth_time': clock, 'birth_period': period})
    assert response.status_code == expected_status
    assert expected in response.json().get('detail', response.json().get('birth_utc', ''))


def test_am_pm_repeated_hour_requires_explicit_occurrence():
    for fold, utc in [(0, '05:30'), (1, '06:30')]:
        response = client.post('/api/astrology/natal-chart', json={
            **BIRTH, 'birth_date': '2024-11-03', 'birth_time': '01:30',
            'birth_period': 'AM', 'time_fold': fold})
        assert response.status_code == 200
        assert response.json()['birth_utc'] == f'2024-11-03T{utc}:00+00:00'


@pytest.mark.parametrize('clock,period', [('00:30','AM'), ('13:30','PM'), ('02:60','AM'), ('02:30','XX')])
def test_invalid_12h_times_do_not_fall_back_to_noon(clock, period):
    assert client.post('/api/astrology/natal-chart', json={
        **BIRTH, 'birth_time': clock, 'birth_period': period}).status_code == 422


def test_same_local_time_in_different_birthplaces_uses_each_timezone_and_coordinates():
    new_york = client.post('/api/astrology/natal-chart', json={**BIRTH, 'birth_period': 'PM'}).json()
    london = client.post('/api/astrology/natal-chart', json={
        **BIRTH, 'birth_period': 'PM', 'place_id': '2643743'}).json()
    assert london['location']['timezone'] == 'Europe/London'
    assert london['birth_utc'] == '1996-11-05T14:30:00+00:00'
    assert london['birth_utc'] != new_york['birth_utc']
    assert london['ascendant_longitude'] != new_york['ascendant_longitude']
