"""Offline GeoNames city selection and historical local-time conversion.

GeoNames data: https://www.geonames.org/, CC BY 4.0. No birth details are
sent to a geocoding service. A selected place, rather than a city-name guess,
determines the coordinates and IANA timezone.
"""
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
import re
import unicodedata
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from threading import Lock
import geonamescache
_CITY_LOAD_LOCK = Lock()


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold()) if not unicodedata.combining(c)).strip()


@lru_cache(maxsize=1)
def catalog():
    return geonamescache.GeonamesCache(min_city_population=500)


@lru_cache(maxsize=1)
def city_records():
    # Avoid parsing the larger directory twice during concurrent first requests.
    with _CITY_LOAD_LOCK:
        return catalog().get_cities()


@lru_cache(maxsize=1)
def regions():
    result = {}
    for line in Path(__file__).parents[1].joinpath('data/geonames_admin1.tsv').read_text(encoding='utf-8').splitlines():
        key, name, *_ = line.split('\t')
        result[key] = name
    return result


def place_record(city):
    country = catalog().get_countries()[city['countrycode']]['name']
    state = regions().get(city['countrycode'] + '.' + city['admin1code'], city['admin1code'])
    return dict(place_id=str(city['geonameid']), city=city['name'], country=country,
                country_code=city['countrycode'], state=state, state_code=city['admin1code'],
                timezone=city['timezone'], latitude=city['latitude'], longitude=city['longitude'],
                label=', '.join(x for x in [city['name'], state, country] if x))


def search_places(city, country, state=''):
    query, region = normalized(city), normalized(state)
    if len(query) < 2:
        return []
    countries = catalog().get_countries()
    code = next((code for code, c in countries.items() if normalized(country) in
                 [normalized(code), normalized(c['name']), normalized(c['iso3'])]), None)
    if not code:
        raise ValueError('Choose a country name or its two-letter code, for example United States or US.')
    found = []
    for c in city_records().values():
        if c['countrycode'] != code:
            continue
        if region and region not in [normalized(c['admin1code']), normalized(regions().get(code + '.' + c['admin1code'], ''))]:
            continue
        name = normalized(c['name'])
        exact = query == name
        if exact or name.startswith(query) or any(query == normalized(n) for n in c.get('alternatenames', [])):
            found.append((not exact, -c['population'], c))
    found.sort(key=lambda row: row[:2])
    return [place_record(c) for _, _, c in found[:15]]


@lru_cache(maxsize=256)
def region_choices(country):
    code = country.upper()
    if code not in catalog().get_countries():
        raise ValueError('Choose a country from the list.')
    return sorted([{'code': key.split('.', 1)[1], 'name': name}
                   for key, name in regions().items() if key.startswith(code + '.')],
                  key=lambda item: item['name'])


@lru_cache(maxsize=128)
def city_choices(country, state='', query=''):
    code = country.upper()
    if code not in catalog().get_countries():
        raise ValueError('Choose a country from the list.')
    term = normalized(query.split(',')[0])
    matches = [c for c in city_records().values()
               if c['countrycode'] == code and (not state or c['admin1code'] == state)
               and (not term or term in normalized(c['name'])
                    or any(term in normalized(a) for a in c.get('alternatenames', [])))]
    matches.sort(key=lambda c: (normalized(c['name']) != term, normalized(c['name'])))
    return {'places': [place_record(c) for c in matches[:300]], 'total': len(matches),
            'limited': len(matches) > 300,
            'note': 'GeoNames towns and cities with population 500+. Search to narrow the dropdown. For an unlisted birthplace, use its coordinates and historical timezone below.'}


def birth_time_24h(data):
    """Normalize the recorded local clock time before applying timezone rules.

    Midnight is 12 AM -> 00:MM; noon is 12 PM -> 12:MM.
    Retain the 24-hour API contract when no AM/PM period is supplied.
    """
    match = re.fullmatch(r'(\d{1,2}):([0-5]\d)', data.birth_time)
    if not match:
        raise ValueError('Enter a valid birth time with hours and minutes (HH:MM).')
    hour, minute = map(int, match.groups())
    if data.birth_period is not None:
        if not 1 <= hour <= 12:
            raise ValueError('For AM/PM birth times, choose an hour from 1 to 12.')
        hour = hour % 12 + (12 if data.birth_period == 'PM' else 0)
    elif not 0 <= hour <= 23:
        raise ValueError('For 24-hour birth times, choose an hour from 0 to 23.')
    return f'{hour:02d}:{minute:02d}'


def resolve_birth(data):
    if data.place_id:
        city = city_records().get(str(data.place_id))
        if not city:
            raise ValueError('Select your birth city from the search results.')
        location = place_record(city)
    elif data.latitude is not None and data.longitude is not None and data.timezone:
        # Explicit coordinates remain available for existing API integrations.
        location = dict(city=data.city or 'Custom location', state=data.state or '', country=data.country or '',
                        label=data.city or 'Custom location', latitude=data.latitude,
                        longitude=data.longitude, timezone=data.timezone)
    else:
        raise ValueError('Search for and select your birth city before calculating your chart.')
    clock_time = birth_time_24h(data)
    try:
        zone = ZoneInfo(location['timezone'])
        naive = datetime.strptime(f'{data.birth_date} {clock_time}', '%Y-%m-%d %H:%M')
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise ValueError('Enter a valid birth date and local time.') from exc
    if not 1900 <= naive.year <= 2100:
        raise ValueError('Birth dates must be between 1900 and 2100.')
    candidates = []
    for fold in (0, 1):
        local = naive.replace(tzinfo=zone, fold=fold)
        utc = local.astimezone(timezone.utc)
        if utc.astimezone(zone).replace(tzinfo=None) == naive and utc not in [c[1] for c in candidates]:
            candidates.append((fold, utc, local))
    if not candidates:
        raise ValueError('That local time did not exist because the clocks moved forward. Check your birth record.')
    if len(candidates) > 1 and data.time_fold is None:
        raise ValueError('That time occurred twice when clocks moved back. Choose the first or second occurrence below.')
    chosen = next((c for c in candidates if c[0] == data.time_fold), candidates[0])
    return chosen[1], location, chosen[2].isoformat()
