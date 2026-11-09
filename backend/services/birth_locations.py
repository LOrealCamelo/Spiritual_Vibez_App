"""Offline GeoNames city selection and historical local-time conversion.

GeoNames data: https://www.geonames.org/, CC BY 4.0. No birth details are
sent to a geocoding service. A selected place, rather than a city-name guess,
determines the coordinates and IANA timezone.
"""
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
import unicodedata
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import geonamescache


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold()) if not unicodedata.combining(c)).strip()


@lru_cache(maxsize=1)
def catalog():
    return geonamescache.GeonamesCache(min_city_population=1000)


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
    for c in catalog().get_cities().values():
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


def resolve_birth(data):
    if data.place_id:
        city = catalog().get_cities().get(str(data.place_id))
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
    try:
        zone = ZoneInfo(location['timezone'])
        naive = datetime.strptime(f'{data.birth_date} {data.birth_time}', '%Y-%m-%d %H:%M')
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise ValueError('Enter a valid birth date and local time (24-hour hours and minutes).') from exc
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
