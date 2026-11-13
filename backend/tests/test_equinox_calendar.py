from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.equinox_calendar import equinox_calendar

client=TestClient(app)


def test_today_conversion_and_equinox_boundary():
    result=equinox_calendar('2026-11-12','America/New_York')
    assert result['converted_date']['month_number']==9
    assert result['converted_date']['day']==14
    first=equinox_calendar('2026-03-20','America/New_York')
    assert (first['converted_date']['month_number'],first['converted_date']['day'])==(1,1)
    previous=equinox_calendar('2026-03-19','America/New_York')
    assert previous['converted_date']['year']==2025
    assert previous['converted_date']['month_number'] is None
    assert previous['converted_date']['extra_day']==1
    assert 'Year Day' in previous['converted_date']['label']


@pytest.mark.parametrize('year',[2023,2024,2025,2026,2027,2028,2099,2100])
@pytest.mark.parametrize('zone',['UTC','America/New_York','Pacific/Kiritimati'])
def test_every_day_occurs_once_with_thirteen_equal_months_and_extra_days(year,zone):
    result=equinox_calendar(f'{year}-07-01',zone,year,1)
    all_dates=[]
    for month in range(1,14):
        block=equinox_calendar(f'{year}-07-01',zone,year,month)
        assert len(block['days'])==28
        assert [d['day'] for d in block['days']]==list(range(1,29))
        assert [d['week'] for d in block['days']]==[w for w in range(1,5) for _ in range(7)]
        assert [d['weekday'] for d in block['days']]==list(range(1,8))*4
        all_dates.extend(d['gregorian_date'] for d in block['days'])
    all_dates.extend(d['gregorian_date'] for d in result['extra_days'])
    start=date.fromisoformat(result['year_start']);end=date.fromisoformat(result['next_year_start'])
    assert all_dates==[(start+timedelta(days=i)).isoformat() for i in range((end-start).days)]
    assert len(all_dates) in (365,366)
    assert len(result['extra_days'])==len(all_dates)-364
    for extra in result['extra_days']:
        converted=equinox_calendar(extra['gregorian_date'],zone)['converted_date']
        assert converted['month_number'] is None and converted['weekday'] is None


def test_timezone_changes_equinox_day_and_month_navigation_crosses_years():
    assert equinox_calendar('2024-06-01','UTC')['year_start']=='2024-03-20'
    assert equinox_calendar('2024-06-01','America/New_York')['year_start']=='2024-03-19'
    assert equinox_calendar('2026-03-20','UTC',2026,1)['previous']=={'year':2025,'month':13}
    assert equinox_calendar('2026-03-20','UTC',2026,13)['next']=={'year':2027,'month':1}


@pytest.mark.parametrize('params',[{'date':'2026-02-30'},{'date':'not-a-date'},{'month':14},{'month':0},{'year':1500},{'timezone':'Bad/Zone'}])
def test_invalid_calendar_inputs_are_rejected(params):
    assert client.get('/api/astrology/calendar-13-month',params=params).status_code==422


def test_legacy_endpoint_remains_available_without_fabricated_moon_phases():
    r=client.get('/api/astrology/lunar-calendar/13?date=2026-11-12&timezone=UTC')
    assert r.status_code==200
    result=r.json()
    assert len(result['days'])==28 and result['total_cycles']==13
    assert 'moon_name' not in result
    assert not any('phase_marker' in day for day in result['days'])
