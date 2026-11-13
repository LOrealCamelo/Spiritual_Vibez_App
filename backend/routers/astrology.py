"""
AuraMystic Astrology, Ephemeris, Natal/Placidus Charts, 13-Month Calendar, BaZi & Astrocartography Router
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import available_timezones
from ..models import BirthDataRequest, AsteroidBirthRequest, AstrocartographyRequest, BaZiRequest, RelocationRequest
from ..services.asteroid_charts import search_asteroids, asteroid_chart, EphemerisUnavailable
from ..services.ephemeris_engine import (
    compute_planetary_positions,
    calculate_13_month_calendar,
    calculate_bazi_four_pillars,
    MASTER_DATA
)
from ..services.birth_locations import birth_time_24h, resolve_birth, search_places, catalog, region_choices, city_choices
from ..services.sky_engine import daily_transits, natal_chart
from ..services.moon_calendar import monthly_moon_calendar, moon_disc_svg

router = APIRouter()
LEARNING_LIBRARY = json.loads(Path(__file__).parents[1].joinpath('data/learning_library.json').read_text(encoding='utf-8'))

@router.get("/daily-transits")
def get_daily_transits(
    sign: str = 'Scorpio', date: Optional[str] = None,
    timezone: str = 'UTC', zodiac: str = 'tropical'
):
    """Returns real-time daily moon phase, planetary alignments, and personalized zodiac mood forecast."""
    try:
        result = daily_transits(sign=sign, date_str=date, timezone_name=timezone, zodiac=zodiac)
        result['moon']['image_svg'] = moon_disc_svg(result['moon']['phase_angle_deg'])
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get('/locations/countries')
def birth_countries():
    return {'countries': sorted([{'code': k, 'name': v['name']} for k,v in catalog().get_countries().items()], key=lambda c:c['name'])}


@router.get('/locations/regions')
def birth_regions(country: str):
    try:
        return {'regions': region_choices(country)}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get('/locations/timezones')
def birth_timezones():
    return {'timezones': sorted(available_timezones())}


@router.get('/locations/cities')
def birth_cities(country: str, state: str = '', query: str = ''):
    try:
        return city_choices(country, state, query)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get('/moon-calendar')
def get_monthly_moon_calendar(year: Optional[int] = None, month: Optional[int] = None,
                              timezone: str = 'UTC', zodiac: str = 'tropical'):
    try:
        return monthly_moon_calendar(year,month,timezone,zodiac)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc)) from exc


@router.get('/locations/search')
def birth_city_search(city: str, country: str, state: str = ''):
    try:
        return {'places': search_places(city, country, state), 'source': 'GeoNames (CC BY 4.0)',
                'note': 'Cities and towns with population of at least 1,000. If yours is absent, choose a nearby listed town and note that houses may differ slightly.'}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.post("/moon-phase")
def calculate_natal_moon_phase(data: BirthDataRequest):
    """Calculates exact natal lunar phase, illumination percentage, moon sign, and soul archetype."""
    try:
        dt, location, local_time = resolve_birth(data)
        pos = compute_planetary_positions(dt, data.zodiac)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    lp = pos["LunarPhase"]
    return {
        "birth_date": data.birth_date,
        "birth_time": birth_time_24h(data),
        'birth_time_12h': datetime.fromisoformat(local_time).strftime('%I:%M %p'),
        'birth_local_time': local_time,
        'birth_utc': dt.isoformat(),
        'location': location,
        "natal_moon_phase": lp["phase_name"],
        "emoji": lp["emoji"],
        "archetype_title": lp["archetype"],
        "description": lp["description"],
        "spiritual_gifts": lp["gifts"],
        "illumination_percentage": lp["illumination_percent"],
        "moon_sign": lp["moon_sign"],
        "moon_position": lp["moon_formatted"],
        'moon_image_svg': moon_disc_svg(lp['phase_angle_deg'])
    }

@router.post("/natal-chart")
def generate_natal_chart(data: BirthDataRequest):
    """Calculates Placidus, Tropical, or Secondary Progression chart placements, 12 houses, and asteroids."""
    try:
        dt, location, local_time = resolve_birth(data)
        chart = natal_chart(dt, location['latitude'], location['longitude'], name=data.name,
                            zodiac=data.zodiac, house_system=data.house_system, rulership=data.rulership,
                            chart_system=data.chart_system or 'natal')
        chart.update(birth_date=data.birth_date, birth_time=birth_time_24h(data),
                     birth_time_12h=datetime.fromisoformat(local_time).strftime('%I:%M %p'),
                     birth_local_time=local_time, birth_utc=dt.isoformat(), location=location)
        return chart
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("/houses")
def get_twelve_houses():
    """Returns the 12 Sacred Astrological Houses encyclopedia with ruling planets and meanings."""
    return {"houses": LEARNING_LIBRARY['houses'], 'note': LEARNING_LIBRARY['house_note'],
            'planets': LEARNING_LIBRARY['planets'], 'tarot_note': LEARNING_LIBRARY['planet_note']}


@router.get('/learning-library')
def learning_library():
    return LEARNING_LIBRARY

@router.get("/asteroids")
def get_major_asteroids(query: str = '', offset: int = 0):
    """Search/page the full JPL numbered-asteroid catalog."""
    try:
        return search_asteroids(query, offset)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except EphemerisUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post('/asteroids/natal-chart')
def calculate_asteroid_birth_chart(data: AsteroidBirthRequest):
    try:
        return asteroid_chart(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except EphemerisUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.get('/calendar-13-month')
def get_equinox_calendar(date: Optional[str] = None, timezone: str = 'UTC', year: Optional[int] = None, month: Optional[int] = None):
    """Convert a civil date and browse thirteen 28-day months anchored to the March equinox."""
    try:
        return calculate_13_month_calendar(month, date, timezone, year)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get('/lunar-calendar/{month_num}', deprecated=True)
def get_lunar_calendar(month_num: int = 13, date: Optional[str] = None, timezone: str = 'UTC', year: Optional[int] = None):
    """Legacy URL; now returns the corrected solar/equinox calendar, without invented Moon phases."""
    return get_equinox_calendar(date, timezone, year, month_num)

@router.post("/bazi")
@router.get("/bazi")
def get_bazi_pillars(
    birth_year: int = Query(1996),
    birth_month: int = Query(11),
    birth_day: int = Query(5),
    birth_hour: int = Query(14),
    polarity: str = Query("Yin Feminine"),
    body: Optional[BaZiRequest] = None
):
    """Calculates Four Pillars of Destiny (BaZi), Chinese Zodiac animal, elemental balance, and Day Master."""
    if body is not None:
        return calculate_bazi_four_pillars(
            year=body.birth_year,
            month=body.birth_month or 11,
            day=body.birth_day or 5,
            hour=body.birth_hour or 14,
            polarity=body.polarity or "Yin Feminine"
        )
    return calculate_bazi_four_pillars(year=birth_year, month=birth_month, day=birth_day, hour=birth_hour, polarity=polarity)

@router.post('/astrocartography')
def calculate_astrocartography_map(data: AstrocartographyRequest):
    from ..services.astrocartography import astrocartography_report
    try:
        return astrocartography_report(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get('/astrocartography/places')
def search_map_places(query: str = Query(..., min_length=2, max_length=80)):
    """Offline global city lookup for inspecting places after a personal map exists."""
    from ..services.birth_locations import city_records, place_record, normalized
    term=normalized(query)
    found=[c for c in city_records().values() if normalized(c['name']).startswith(term)]
    found.sort(key=lambda c:(normalized(c['name'])!=term,-c['population'],c['countrycode']))
    return {'places':[place_record(c) for c in found[:20]]}

@router.get('/astrocartography', deprecated=True)
def get_astrocartography_city(city: Optional[str] = None):
    raise HTTPException(status_code=422, detail='A destination alone cannot calculate your map. Submit your birth date, exact birth time and birthplace to this endpoint using POST.')

@router.post('/astrocartography/relocate', deprecated=True)
def post_astrocartography_relocation(req: RelocationRequest):
    """Legacy URL now uses real birth data; it no longer returns a preset city score."""
    return calculate_astrocartography_map(req)
