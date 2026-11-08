"""
AuraMystic Astronomical, Ephemeris, BaZi, Lunar Calendar & Astrocartography Engine
Shared astronomy calls delegate to sky_engine. Legacy symbolic calendar, BaZi and
astrocartography helpers remain below; their calculations are outside that validation.
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


def calculate_13_month_calendar(month_num: int = 13) -> Dict[str, Any]:
    month_num = max(1, min(13, month_num))
    moon_names = {
        1: ("Magnetic Bat Moon", "Purpose", "July 26 – August 22"),
        2: ("Lunar Scorpion Moon", "Challenge", "August 23 – September 19"),
        3: ("Electric Deer Moon", "Service", "September 20 – October 17"),
        4: ("Self-Existing Owl Moon", "Form", "October 18 – November 14"),
        5: ("Overtone Peacock Moon", "Radiance", "November 15 – December 12"),
        6: ("Rhythmic Lizard Moon", "Equality", "December 13 – January 9"),
        7: ("Resonant Monkey Moon", "Attunement", "January 10 – February 6"),
        8: ("Galactic Hawk Moon", "Integrity", "February 7 – March 6"),
        9: ("Solar Jaguar Moon", "Intention", "March 7 – April 3"),
        10: ("Planetary Dog Moon", "Manifestation", "April 4 – May 1"),
        11: ("Spectral Serpent Moon", "Liberation", "May 2 – May 29"),
        12: ("Crystal Rabbit Moon", "Cooperation", "May 30 – June 26"),
        13: ("Cosmic Turtle Moon", "Endurance & Presence", "June 27 – July 24")
    }
    name, totem_power, date_span = moon_names[month_num]
    days = []
    for d in range(1, 29):
        phase = "Full Moon Peak 🌕" if d == 14 else ("New Moon Seed 🌑" if d in (1, 28) else ("First Quarter 🌓" if d == 7 else ("Last Quarter 🌗" if d == 21 else "Harmonic Flow •")))
        days.append({
            "day": d,
            "week": (d - 1) // 7 + 1,
            "phase_marker": phase,
            "is_portal_day": d in (1, 7, 14, 21, 28)
        })
    return {
        "month_number": month_num,
        "moon_name": name,
        "totem_keyword": totem_power,
        "solar_date_range": date_span,
        "days_in_cycle": 28,
        "total_cycles": 13,
        "day_out_of_time": {
            "date": "July 25",
            "title": "Day Out of Time (Galactic Freedom Day)",
            "description": "Universal celebration day of artistic freedom, peace, forgiveness, and spiritual rebirth preceding the galactic new year on July 26."
        },
        "days": days
    }

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

def calculate_astrocartography(city: str = "Utica, NY", lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
    cities = MASTER_DATA.get("cityData", {})
    city_coords = {
        "Utica, NY": (43.1009, -75.2327, "9.4 / 10 Excellent", ["Sun Line (Leadership)", "Venus Line (Harmony & Love)", "Jupiter Line (Wealth & Expansion)"], "Sun Midheaven & Jupiter Trine Active"),
        "New York City": (40.7128, -74.0060, "9.1 / 10 High Acceleration", ["Mercury MC Line (Commerce)", "Sun Ascendant (Visibility)", "Mars Trine (Drive)"], "Mercury Midheaven & Venus Sextile Active"),
        "Sedona, AZ": (34.8697, -111.7610, "9.7 / 10 Psychic Vortex", ["Neptune IC Line (Mysticism)", "Pluto Trine (Alchemy)", "Moon Node (Destiny)"], "Neptune IC & Pluto Trine Active"),
        "Los Angeles, CA": (34.0522, -118.2437, "9.2 / 10 Creative Glamour", ["Venus Ascendant (Magnetism)", "Sun Trine (Cinema & Media)", "Jupiter Sextile"], "Venus Ascendant & Sun Trine Active"),
        "London, UK": (51.5074, -0.1278, "8.9 / 10 Global Expansion", ["Jupiter Descendant (Alliances)", "Saturn MC (Prestige)", "Mercury Sextile"], "Jupiter Descendant & Saturn MC Active"),
        "Tokyo, Japan": (35.6762, 139.6503, "9.0 / 10 Tech & Innovation", ["Mars Midheaven (Execution)", "Uranus Ascendant (Future AI)", "Mercury Trine"], "Mars Midheaven & Uranus Trine Active"),
        "Bali, Indonesia": (-8.4095, 115.1889, "9.6 / 10 Somatic Sanctuary", ["Moon IC Line (Rebirth)", "Venus Trine (Sacred Healing)", "Neptune Sextile"], "Moon IC & Venus Trine Active")
    }
    base = cities.get(city, cities.get("Utica, NY"))
    coords = city_coords.get(city, city_coords["Utica, NY"])
    use_lat = lat if lat is not None else coords[0]
    use_lon = lon if lon is not None else coords[1]

    return {
        "city": city,
        "latitude": use_lat,
        "longitude": use_lon,
        "coordinates_formatted": f"LAT {abs(use_lat):.4f}° {'N' if use_lat >= 0 else 'S'} • LONG {abs(use_lon):.4f}° {'E' if use_lon >= 0 else 'W'}",
        "relocated_ascendant": base["asc"],
        "dominant_planet_line": base["line"],
        "active_aspects": coords[4],
        "planetary_lines": coords[3],
        "spiritual_affinity_score": coords[2],
        "description": base["desc"],
        "available_cities": list(cities.keys())
    }
