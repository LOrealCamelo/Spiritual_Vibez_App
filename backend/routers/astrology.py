"""
AuraMystic Astrology, Ephemeris, Natal/Placidus/Draconic Charts, 13-Month Calendar, BaZi & Astrocartography Router
"""
from fastapi import APIRouter, Query
from typing import Optional
from ..models import BirthDataRequest, BaZiRequest, RelocationRequest
from ..services.ephemeris_engine import (
    calculate_daily_transits,
    compute_planetary_positions,
    calculate_multi_system_chart,
    calculate_13_month_calendar,
    calculate_bazi_four_pillars,
    calculate_astrocartography,
    MASTER_DATA
)
from datetime import datetime

router = APIRouter()

@router.get("/daily-transits")
def get_daily_transits(
    sign: str = Query("Scorpio", description="Zodiac sign for personalized daily mood forecast"),
    date: Optional[str] = Query(None, description="YYYY-MM-DD (defaults to today)")
):
    """Returns real-time daily moon phase, planetary alignments, and personalized zodiac mood forecast."""
    return calculate_daily_transits(sign=sign, date_str=date)

@router.post("/moon-phase")
def calculate_natal_moon_phase(data: BirthDataRequest):
    """Calculates exact natal lunar phase, illumination percentage, moon sign, and soul archetype."""
    try:
        dt = datetime.strptime(f"{data.birth_date} {data.birth_time or '14:30'}", "%Y-%m-%d %H:%M")
    except ValueError:
        dt = datetime.strptime(data.birth_date, "%Y-%m-%d").replace(hour=14, minute=30)
    pos = compute_planetary_positions(dt)
    lp = pos["LunarPhase"]
    return {
        "birth_date": data.birth_date,
        "birth_time": data.birth_time,
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
    """Calculates Placidus, Tropical, Secondary Progressions, or Draconic chart placements, 12 houses, and asteroids."""
    return calculate_multi_system_chart(
        birth_date=data.birth_date,
        birth_time=data.birth_time or "14:30",
        latitude=data.latitude or 43.1009,
        longitude=data.longitude or -75.2327,
        system=data.chart_system or "placidus"
    )

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
