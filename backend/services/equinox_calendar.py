"""A custom 13 x 28-day calendar anchored to the local March equinox date.

This is a contemporary spiritual calendar, not the Ethiopian calendar or a
claim about astronomical lunar months. Intercalary days belong to no month/week.
"""
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import astronomy


@lru_cache(maxsize=512)
def march_equinox(year):
    return astronomy.Seasons(year).mar_equinox.Utc().replace(tzinfo=timezone.utc)


def equinox_calendar(date_str=None, timezone_name='UTC', calendar_year=None, month_number=None):
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError, TypeError) as exc:
        raise ValueError('Choose a valid IANA timezone.') from exc
    today = datetime.now(zone).date()
    try:
        selected = date.fromisoformat(date_str) if date_str else today
    except (ValueError, TypeError) as exc:
        raise ValueError('Enter a valid Gregorian date (YYYY-MM-DD).') from exc
    if not 1601 <= selected.year <= 2400:
        raise ValueError('Choose a date from 1601 through 2400.')
    start_date = lambda y: march_equinox(y).astimezone(zone).date()
    selected_year = selected.year if selected >= start_date(selected.year) else selected.year - 1
    offset = (selected - start_date(selected_year)).days
    extra = offset >= 364
    converted = dict(year=selected_year, month_number=None if extra else offset // 28 + 1,
                     day=None if extra else offset % 28 + 1,
                     week=None if extra else offset % 28 // 7 + 1,
                     weekday=None if extra else offset % 7 + 1,
                     extra_day=offset - 363 if extra else None)
    converted['label'] = (('Year Day' if offset == 364 else 'Leap Day') if extra
                          else f'Month {converted["month_number"]}, Day {converted["day"]}') + f' · Equinox year {selected_year}'
    year = selected_year if calendar_year is None else calendar_year
    month = (converted['month_number'] or 13) if month_number is None else month_number
    if not isinstance(year, int) or not 1600 <= year <= 2400:
        raise ValueError('Choose an equinox year from 1600 through 2400.')
    if not isinstance(month, int) or not 1 <= month <= 13:
        raise ValueError('Choose a month from 1 through 13.')
    start, end = start_date(year), start_date(year + 1)
    span = (end - start).days
    if span not in (365, 366):
        raise ValueError('This timezone/year has an unsupported civil-date discontinuity.')
    months = [dict(number=m, name=f'Month {m}', start_date=(start + timedelta(days=(m-1)*28)).isoformat(),
                   end_date=(start + timedelta(days=m*28-1)).isoformat()) for m in range(1,14)]
    days = []
    for d in range(1,29):
        civil = start + timedelta(days=(month-1)*28+d-1)
        days.append(dict(day=d, week=(d-1)//7+1, weekday=(d-1)%7+1, gregorian_date=civil.isoformat(),
                         is_selected=civil == selected, is_today=civil == today))
    extras = []
    for index in range(span - 364):
        civil = start + timedelta(days=364+index)
        extras.append(dict(label='Year Day' if index == 0 else 'Leap Day', gregorian_date=civil.isoformat(),
                           is_selected=civil == selected, is_today=civil == today))
    def adjacent(delta):
        index = (year*13+month-1) + delta
        y, m = divmod(index,13)
        return dict(year=y,month=m+1) if 1600 <= y <= 2400 else None
    return dict(calendar_system='spring-equinox-13-month', title='13-Month Equinox Calendar',
                timezone=timezone_name, selected_date=selected.isoformat(), today=today.isoformat(),
                converted_date=converted, year=year, year_start=start.isoformat(), next_year_start=end.isoformat(),
                spring_equinox_utc=march_equinox(year).isoformat(), next_spring_equinox_utc=march_equinox(year+1).isoformat(),
                year_days=span, days_in_cycle=28, total_cycles=13, month_number=month,
                month_name=f'Month {month}', months=months, days=days, extra_days=extras,
                previous=adjacent(-1), next=adjacent(1),
                note='Month 1 begins on the local civil date of the March spring equinox (Northern Hemisphere). '
                     'Thirteen months of 28 days are followed by Year Day and, when needed, Leap Day, outside the months and weeks. '
                     'This custom spiritual calendar is separate from actual lunar phases.')
