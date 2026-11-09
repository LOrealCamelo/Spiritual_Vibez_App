"""
AuraMystic Astrology, Ephemeris, Natal/Placidus Charts, 13-Month Calendar, BaZi & Astrocartography Router
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from ..models import BirthDataRequest, BaZiRequest, RelocationRequest
from ..services.ephemeris_engine import (
    compute_planetary_positions,
    calculate_13_month_calendar,
    calculate_bazi_four_pillars,
    calculate_astrocartography,
    MASTER_DATA
)
from ..services.birth_locations import resolve_birth, search_places, catalog
from ..services.sky_engine import daily_transits, natal_chart
from ..services.moon_calendar import monthly_moon_calendar

router = APIRouter()

@router.get("/daily-transits")
def get_daily_transits(
    sign: str = 'Scorpio', date: Optional[str] = None,
    timezone: str = 'UTC', zodiac: str = 'tropical'
):
    """Returns real-time daily moon phase, planetary alignments, and personalized zodiac mood forecast."""
    try:
        return daily_transits(sign=sign, date_str=date, timezone_name=timezone, zodiac=zodiac)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get('/locations/countries')
def birth_countries():
    return {'countries': sorted([{'code': k, 'name': v['name']} for k,v in catalog().get_countries().items()], key=lambda c:c['name'])}


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
        "birth_time": data.birth_time,
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
        "moon_position": lp["moon_formatted"]
    }

@router.post("/natal-chart")
def generate_natal_chart(data: BirthDataRequest):
    """Calculates Placidus, Tropical, or Secondary Progression chart placements, 12 houses, and asteroids."""
    try:
        dt, location, local_time = resolve_birth(data)
        chart = natal_chart(dt, location['latitude'], location['longitude'], name=data.name,
                            zodiac=data.zodiac, house_system=data.house_system, rulership=data.rulership,
                            chart_system=data.chart_system or 'natal')
        chart.update(birth_date=data.birth_date, birth_time=data.birth_time,
                     birth_local_time=local_time, birth_utc=dt.isoformat(), location=location)
        return chart
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("/houses")
def get_twelve_houses():
    """Returns the 12 Sacred Astrological Houses encyclopedia with ruling planets and meanings."""
    return {"houses": MASTER_DATA.get("housesData", [])}

@router.get("/asteroids")
def get_major_asteroids():
    """Returns Chiron, Black Moon Lilith, Ceres, Pallas Athena, Juno, and Vesta placements and interpretations."""
    return {"asteroids": MASTER_DATA.get("asteroids", [])}

@router.get("/lunar-calendar/{month_num}")
def get_lunar_calendar(month_num: int = 13):
    """Returns the 13-Month Natural Lunar Calendar (28-day harmonic cycle + Day Out of Time)."""
    return calculate_13_month_calendar(month_num=month_num)

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

@router.get("/astrocartography")
def get_astrocartography_city(city: str = Query("Utica, NY")):
    """Returns planetary power lines and relocated chart dynamics for a target city."""
    return calculate_astrocartography(city=city)

@router.post("/astrocartography/relocate")
def post_astrocartography_relocation(req: RelocationRequest):
    """Calculates relocated chart dynamics and planetary power lines for custom coordinates or city."""
    return calculate_astrocartography(city=req.city, lat=req.latitude, lon=req.longitude)
