"""
AuraMystic Astronomical, Ephemeris, BaZi, Lunar Calendar & Astrocartography Engine
Shared astronomy calls delegate to sky_engine. The equinox calendar and birth-based
astrocartography live in dedicated services. Symbolic BaZi helpers remain below.
"""
import math
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "master_data.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    MASTER_DATA = json.load(f)

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

SIGN_MODALITIES = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable"
}

def to_julian_day(dt: datetime) -> float:
    """Compute astronomical Julian Day for any UTC datetime."""
    y = dt.year
    m = dt.month
    d = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5
    return jd

# Shared accurate ephemerides for daily sky, natal Moon and other modules.
from .sky_engine import compute_planetary_positions, daily_transits as calculate_daily_transits, sign_position as longitude_to_sign_deg, natal_chart


def calculate_multi_system_chart(birth_date, birth_time, latitude, longitude, system='placidus', timezone_name='UTC'):
    from zoneinfo import ZoneInfo
    dt = datetime.strptime(f'{birth_date} {birth_time}', '%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo(timezone_name))
    return natal_chart(dt, latitude, longitude, chart_system=system)


def calculate_13_month_calendar(month_num=None, date_str=None, timezone_name='UTC', calendar_year=None):
    """Compatibility wrapper for the corrected equinox-based 13-month calendar."""
    from .equinox_calendar import equinox_calendar
    return equinox_calendar(date_str, timezone_name, calendar_year, month_num)


def calculate_bazi_four_pillars(year: int = 1996, month: int = 11, day: int = 5, hour: int = 14, polarity: str = "Yin Feminine") -> Dict[str, Any]:
    stems = [
        ("Jia", "Yang Wood", "🌲"), ("Yi", "Yin Wood", "🌿"),
        ("Bing", "Yang Fire", "🔥"), ("Ding", "Yin Fire", "🕯️"),
        ("Wu", "Yang Earth", "⛰️"), ("Ji", "Yin Earth", "🏺"),
        ("Geng", "Yang Metal", "⚔️"), ("Xin", "Yin Metal", "💎"),
        ("Ren", "Yang Water", "🌊"), ("Gui", "Yin Water", "🌧️")
    ]
    branches = [
        ("Zi", "Rat", "🐀", "Water"), ("Chou", "Ox", "🐂", "Earth"),
        ("Yin", "Tiger", "🐅", "Wood"), ("Mao", "Rabbit", "🐇", "Wood"),
        ("Chen", "Dragon", "🐉", "Earth"), ("Si", "Snake", "🐍", "Fire"),
        ("Wu", "Horse", "🐎", "Fire"), ("Wei", "Goat", "🐐", "Earth"),
        ("Shen", "Monkey", "🐒", "Metal"), ("You", "Rooster", "🐓", "Metal"),
        ("Xu", "Dog", "🐕", "Earth"), ("Hai", "Pig", "🐖", "Water")
    ]

    y_stem = stems[(year - 4) % 10]
    y_branch = branches[(year - 4) % 12]

    m_stem = stems[((year * 12 + month) + 1) % 10]
    m_branch = branches[(month + 1) % 12]

    dt = datetime(year, max(1, min(12, month)), max(1, min(28, day)), max(0, min(23, hour)))
    jd = int(to_julian_day(dt))
    d_stem = stems[(jd + 9) % 10]
    d_branch = branches[(jd + 1) % 12]

    h_branch_idx = ((hour + 1) // 2) % 12
    h_stem = stems[(jd * 2 + h_branch_idx) % 10]
    h_branch = branches[h_branch_idx]

    element_word = y_stem[1].split()[1]
    return {
        "birth_year": year,
        "polarity": polarity,
        "animal_sign": f"{element_word} {y_branch[1]} {y_branch[2]}",
        "stem_branch_title": f"{y_stem[0]} {y_branch[0]} ({y_stem[1]} {y_branch[1]})",
        "pillars": {
            "year_pillar": {
                "title": f"{y_stem[1].split()[1]} {y_branch[1]} ({y_stem[0]} {y_branch[0]})",
                "domain": "Ancestral Lineage & Outer Persona"
            },
            "month_pillar": {
                "title": f"{m_stem[1].split()[1]} {m_branch[1]} ({m_stem[0]} {m_branch[0]})",
                "domain": "Career, Drive & Social Environment"
            },
            "day_master": {
                "title": f"{d_stem[1]} {d_branch[1]} ({d_stem[0]} {d_branch[0]})",
                "domain": "Core Soul Identity & Spouse Palace"
            },
            "hour_pillar": {
                "title": f"{h_stem[1].split()[1]} {h_branch[1]} ({h_stem[0]} {h_branch[0]})",
                "domain": "Inner Child, Creations & Legacy"
            }
        },
        "interpretation": (
            f"Born under the {y_stem[1]} {y_branch[1]} pillar ({polarity}), you possess sharp analytical instincts "
            f"and entrepreneurial magnetism. Your {d_stem[1]} Day Master grants a natural gift for timing, "
            f"community leadership, and sovereign financial navigation."
        )
    }

def calculate_astrocartography(data):
    from .astrocartography import astrocartography_report
    return astrocartography_report(data)
