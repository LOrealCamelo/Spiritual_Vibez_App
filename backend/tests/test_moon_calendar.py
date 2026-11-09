from datetime import datetime, timezone
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.moon_calendar import monthly_moon_calendar
import pytest

client=TestClient(app)


def test_november_calendar_all_days_and_exact_phase_events():
    calendar=monthly_moon_calendar(2026,11,'America/New_York')
    assert len(calendar['days'])==30 and calendar['first_weekday']==6
    assert [d['date'] for d in calendar['days']]==[f'2026-11-{n:02d}' for n in range(1,31)]
    assert {e['phase'] for e in calendar['events']}=={'New Moon','First Quarter','Full Moon','Last Quarter'}
    new=next(e for e in calendar['events'] if e['phase']=='New Moon')
    # Existing independent conjunction reference, in UTC and local EST.
    assert abs((datetime.fromisoformat(new['at_utc'])-datetime(2026,11,9,7,2,tzinfo=timezone.utc)).total_seconds())<90
    assert new['at_local'].startswith('2026-11-09T02:02') and new['at_local'].endswith('-05:00')
    assert calendar['days'][7]['phase']=='Waning Crescent'
    assert calendar['days'][8]['events'][0]['phase']=='New Moon'
    assert all(d['snapshot_at'].split('T')[1].startswith('12:00') for d in calendar['days'])


def test_month_lengths_leap_year_and_year_boundary():
    assert len(monthly_moon_calendar(2024,2)['days'])==29
    assert len(monthly_moon_calendar(2025,2)['days'])==28
    assert monthly_moon_calendar(2026,12)['days'][-1]['date']=='2026-12-31'
    assert monthly_moon_calendar(2027,1)['days'][0]['date']=='2027-01-01'


def test_event_date_uses_local_zone_and_sidereal_only_changes_zodiac():
    utc=monthly_moon_calendar(2026,11,'UTC')
    hawaii=monthly_moon_calendar(2026,11,'Pacific/Honolulu')
    assert next(e for e in utc['events'] if e['phase']=='New Moon')['date']=='2026-11-09'
    assert next(e for e in hawaii['events'] if e['phase']=='New Moon')['date']=='2026-11-08'
    sidereal=monthly_moon_calendar(2026,11,'UTC','sidereal')
    assert utc['events']==sidereal['events']
    assert [d['illumination_percent'] for d in utc['days']]==[d['illumination_percent'] for d in sidereal['days']]
    assert utc['days'][0]['moon_position']!=sidereal['days'][0]['moon_position']


def test_skipped_historical_civil_date_is_not_given_a_fabricated_snapshot():
    day=monthly_moon_calendar(2011,12,'Pacific/Apia')['days'][29]
    assert day['date']=='2011-12-30' and not day['available']
    assert 'skipped' in day['note'] and 'phase' not in day


@pytest.mark.parametrize('params',[{'month':13},{'year':1800},{'month':0},{'timezone':'Bad/Zone'},{'zodiac':'bad'}])
def test_month_calendar_http_validation(params):
    assert client.get('/api/astrology/moon-calendar',params=params).status_code==422


def test_calendar_http_and_removed_draconic_chart():
    r=client.get('/api/astrology/moon-calendar',params={'year':2026,'month':11,'timezone':'America/New_York'})
    assert r.status_code==200 and len(r.json()['days'])==30
    r=client.post('/api/astrology/natal-chart',json={'birth_date':'1996-11-05','birth_time':'14:30','place_id':'5142056','chart_system':'draconic'})
    assert r.status_code==422


def test_ingresses_match_supplied_reference_minutes_and_cover_entire_civil_day():
    c=monthly_moon_calendar(2026,11,'UTC')
    # Minute-level fixtures transcribed from the owner's Astro-Seek screenshot.
    reference=[('Leo','2026-11-01T04:18:00+00:00'),('Virgo','2026-11-03T08:28:00+00:00'),
               ('Libra','2026-11-05T14:38:00+00:00'),('Scorpio','2026-11-07T22:40:00+00:00')]
    for event,(sign,at) in zip(c['ingresses'],reference):
        assert event['sign']==sign
        assert abs((datetime.fromisoformat(event['at_utc'])-datetime.fromisoformat(at)).total_seconds())<60
    assert [x['sign'] for x in c['days'][0]['sign_intervals']]==['Cancer','Leo']
    for day in c['days']:
        intervals=day['sign_intervals']
        assert intervals[0]['from_local'].split('T')[1].startswith('00:00')
        assert intervals[-1]['until_local'].split('T')[1].startswith('00:00')
        assert all(a['until_utc']==b['from_utc'] for a,b in zip(intervals,intervals[1:]))
        assert all(x['traditional_body_associations'] for x in intervals)
        assert day['moon_image_svg'].startswith('<svg')
        assert 'surgical team' in day['surgery_guidance']
    assert 'not established medical effects' in c['health_note']


def test_ingress_dates_dst_day_length_and_sidereal_sign_boundaries():
    utc=monthly_moon_calendar(2026,11)
    ny=monthly_moon_calendar(2026,11,'America/New_York')
    first=ny['days'][0]['sign_intervals']
    assert (datetime.fromisoformat(first[-1]['until_utc'])-datetime.fromisoformat(first[0]['from_utc'])).total_seconds()==25*3600
    # New York is still on daylight time at this ingress, before the clock change.
    assert first[0]['sign']=='Cancer' and first[1]['sign']=='Leo'
    assert ny['days'][0]['ingresses'][0]['at_local'].startswith('2026-11-01T00:18')
    assert ny['days'][0]['ingresses'][0]['at_local'].endswith('-04:00')
    hawaii=monthly_moon_calendar(2026,11,'Pacific/Honolulu')
    assert hawaii['days'][0]['sign_intervals'][0]['sign']=='Leo'
    sidereal=monthly_moon_calendar(2026,11,'UTC','sidereal')
    assert sidereal['ingresses'][0]['at_utc']!=utc['ingresses'][0]['at_utc']


def test_all_principal_phases_agree_with_independent_swiss_ephemeris_fixtures():
    # Development-only Swiss Ephemeris 2.10.03/Moshier root solving; no runtime dependency.
    reference={'Last Quarter':'2026-11-01T20:28:00+00:00','New Moon':'2026-11-09T07:02:00+00:00',
               'First Quarter':'2026-11-17T11:48:00+00:00','Full Moon':'2026-11-24T14:54:00+00:00'}
    for event in monthly_moon_calendar(2026,11)['events']:
        assert abs((datetime.fromisoformat(event['at_utc'])-datetime.fromisoformat(reference[event['phase']])).total_seconds())<120
