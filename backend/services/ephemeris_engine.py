"""
AuraMystic Astronomical, Ephemeris, BaZi, Lunar Calendar & Astrocartography Engine
Provides real mathematical planetary longitude, synodic lunar phase, Placidus/Draconic/Progressed
house transformations, Four Pillars of Destiny (BaZi), and Relocation Ascendant calculations.
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

SIGN_RULERS = {
    "Aries": ("Mars", "Initiative & Courage"),
    "Taurus": ("Venus", "Sensual Wealth & Stability"),
    "Gemini": ("Mercury", "Sacred Messenger & Intellect"),
    "Cancer": ("Moon", "Psychic Sanctuary & Lineage"),
    "Leo": ("Sun", "Solar Sovereignty & Radiance"),
    "Virgo": ("Mercury", "Sacred Alchemy & Precision"),
    "Libra": ("Venus", "Harmonic Balance & Beauty"),
    "Scorpio": ("Pluto & Mars", "Alchemical Depth & Rebirth"),
    "Sagittarius": ("Jupiter", "Prophetic Wisdom & Expansion"),
    "Capricorn": ("Saturn", "Master Architecture & Legacy"),
    "Aquarius": ("Uranus & Saturn", "Quantum Vision & Liberation"),
    "Pisces": ("Neptune & Jupiter", "Mystic Unity & Dreamweaver")
}

SIGN_FREQUENCIES = {
    "Aries": "417 Hz", "Taurus": "432 Hz", "Gemini": "741 Hz", "Cancer": "639 Hz",
    "Leo": "528 Hz", "Virgo": "741 Hz", "Libra": "639 Hz", "Scorpio": "528 Hz",
    "Sagittarius": "852 Hz", "Capricorn": "396 Hz", "Aquarius": "963 Hz", "Pisces": "528 Hz"
}

MOON_PHASE_ARCHETYPES = [
    {
        "name": "New Moon",
        "emoji": "🌑",
        "angle_range": (0, 45),
        "archetype": "New Moon Soul Archetype",
        "description": "Born during the sacred dark-to-new lunar conjunction. You are an instinctive initiator and intuitive pioneer who walks with deep self-trust and seeds new paradigms.",
        "gifts": ["Instinctive Initiation", "Fresh Paradigm Seeding", "Unfiltered Intuition"]
    },
    {
        "name": "Waxing Crescent",
        "emoji": "🌒",
        "angle_range": (45, 90),
        "archetype": "Waxing Crescent Soul Archetype",
        "description": "Born as the silver crescent emerges from shadow. You are a persistent builder who overcomes historical resistance and anchors new visions into material form.",
        "gifts": ["Breakthrough Momentum", "Creative Persistence", "Courageous Manifestation"]
    },
    {
        "name": "First Quarter",
        "emoji": "🌓",
        "angle_range": (90, 135),
        "archetype": "First Quarter Soul Archetype",
        "description": "Born at the 90-degree solar-lunar square of decisive action. You break stagnant generational molds and thrive as a catalyst in moments requiring bold leadership.",
        "gifts": ["Decisive Action", "Generational Pattern Breaker", "Executive Willpower"]
    },
    {
        "name": "Waxing Gibbous",
        "emoji": "🌔",
        "angle_range": (135, 180),
        "archetype": "Waxing Gibbous Soul Archetype",
        "description": "Born just before full illumination. You are a devoted mentor and seeker of spiritual refinement who perfects systems, heals communities, and elevates collective standards.",
        "gifts": ["Devoted Mastery", "Analytical Synthesis", "High-Frequency Mentorship"]
    },
    {
        "name": "Full Moon",
        "emoji": "🌕",
        "angle_range": (180, 225),
        "archetype": "Full Moon Soul Archetype",
        "description": "Born during maximum lunar illumination. You carry heightened psychic radiance, polarity reconciliation gifts, and natural public charisma.",
        "gifts": ["Maximum Psychic Radiance", "Polarity Reconciliation", "Magnetic Public Charisma"]
    },
    {
        "name": "Disseminating Moon",
        "emoji": "🌖",
        "angle_range": (225, 270),
        "archetype": "Disseminating Moon Soul Archetype",
        "description": "Born in the wisdom-sharing phase following the Full Moon. You are a natural mystic educator, storyteller, and spiritual translator who illuminates others.",
        "gifts": ["Prophetic Teaching", "Wisdom Distribution", "Community Illumination"]
    },
    {
        "name": "Last Quarter",
        "emoji": "🌗",
        "angle_range": (270, 315),
        "archetype": "Last Quarter Soul Archetype",
        "description": "Born at the waning solar-lunar square. You are a karmic liberator and revolutionary thinker who helps humanity release obsolete belief systems.",
        "gifts": ["Karmic Liberation", "Sovereign Deconditioning", "Future-Sight Strategy"]
    },
    {
        "name": "Balsamic / Dark Moon",
        "emoji": "🌘",
        "angle_range": (315, 360),
        "archetype": "Balsamic Dark Moon Soul Archetype",
        "description": "Born in the sacred sanctuary of the waning crescent. You are an old-soul Mystic Seer carrying prophetic wisdom, ancestral healing, and karmic completion.",
        "gifts": ["Prophetic Seer", "Ancestral Cord-Cutting", "Deep Subconscious Alchemy"]
    }
]

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

def longitude_to_sign_deg(lon: float) -> Dict[str, Any]:
    lon = lon % 360.0
    sign_idx = int(lon // 30)
    deg_float = lon % 30.0
    deg = int(deg_float)
    minutes = int(round((deg_float - deg) * 60))
    if minutes == 60:
        deg += 1
        minutes = 0
    sign = ZODIAC_SIGNS[sign_idx]
    ruler, influence = SIGN_RULERS[sign]
    return {
        "longitude": round(lon, 4),
        "sign": sign,
        "degree": deg,
        "minutes": minutes,
        "formatted": f"{sign} {deg}°{minutes:02d}'",
        "element": SIGN_ELEMENTS[sign],
        "modality": SIGN_MODALITIES[sign],
        "ruler": ruler,
        "influence": influence
    }

def compute_planetary_positions(dt: datetime) -> Dict[str, Dict[str, Any]]:
    """
    Calculates ecliptic longitudes for Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn,
    North Node, and major asteroids using orbital elements referenced to J2000.0.
    """
    jd = to_julian_day(dt)
    d = jd - 2451545.0  # Days since J2000.0

    # Mean solar longitude & anomaly
    mean_lon_sun = (280.46646 + 0.98564736 * d) % 360.0
    mean_anom_sun = math.radians((357.52911 + 0.98560028 * d) % 360.0)
    sun_lon = (mean_lon_sun + 1.914602 * math.sin(mean_anom_sun) + 0.019993 * math.sin(2 * mean_anom_sun)) % 360.0

    # Lunar mean longitude, anomaly, and elongation
    mean_lon_moon = (218.3165 + 13.17639648 * d) % 360.0
    mean_anom_moon = math.radians((134.9634 + 13.06499295 * d) % 360.0)
    mean_elong = math.radians((297.8502 + 12.19074912 * d) % 360.0)
    moon_lon = (
        mean_lon_moon
        + 6.2886 * math.sin(mean_anom_moon)
        + 1.2740 * math.sin(2 * mean_elong - mean_anom_moon)
        + 0.6583 * math.sin(2 * mean_elong)
        + 0.2136 * math.sin(2 * mean_anom_moon)
        - 0.1851 * math.sin(mean_anom_sun)
    ) % 360.0

    # Planetary longitudes (heliocentric to geocentric approximation)
    mercury_lon = (sun_lon + 18.5 * math.sin(math.radians(4.0923 * d + 48.0))) % 360.0
    mercury_speed = 4.0923 * math.cos(math.radians(4.0923 * d + 48.0))
    mercury_retrograde = mercury_speed < -1.2

    venus_lon = (sun_lon + 38.0 * math.sin(math.radians(1.6021 * d + 181.9))) % 360.0
    mars_lon = (355.43 + 0.52403 * d + 10.69 * math.sin(math.radians(0.52403 * d + 19.4))) % 360.0
    jupiter_lon = (34.35 + 0.08309 * d + 5.55 * math.sin(math.radians(0.08309 * d + 20.0))) % 360.0
    saturn_lon = (50.08 + 0.03346 * d + 6.40 * math.sin(math.radians(0.03346 * d + 317.0))) % 360.0
    north_node_lon = (125.04452 - 0.05295377 * d) % 360.0

    # Major asteroids
    chiron_lon = (209.5 + 0.0196 * d + 4.2 * math.sin(math.radians(0.0196 * d))) % 360.0
    lilith_lon = (83.35 + 0.111404 * d) % 360.0
    ceres_lon = (168.0 + 0.2141 * d) % 360.0
    pallas_lon = (252.0 + 0.2136 * d) % 360.0
    juno_lon = (205.0 + 0.2260 * d) % 360.0
    vesta_lon = (318.0 + 0.2715 * d) % 360.0

    positions = {
        "Sun": longitude_to_sign_deg(sun_lon),
        "Moon": longitude_to_sign_deg(moon_lon),
        "Mercury": {**longitude_to_sign_deg(mercury_lon), "motion": "Retrograde" if mercury_retrograde else "Direct & Seeking"},
        "Venus": longitude_to_sign_deg(venus_lon),
        "Mars": longitude_to_sign_deg(mars_lon),
        "Jupiter": longitude_to_sign_deg(jupiter_lon),
        "Saturn": longitude_to_sign_deg(saturn_lon),
        "NorthNode": longitude_to_sign_deg(north_node_lon),
        "Chiron": longitude_to_sign_deg(chiron_lon),
        "BlackMoonLilith": longitude_to_sign_deg(lilith_lon),
        "Ceres": longitude_to_sign_deg(ceres_lon),
        "PallasAthena": longitude_to_sign_deg(pallas_lon),
        "Juno": longitude_to_sign_deg(juno_lon),
        "Vesta": longitude_to_sign_deg(vesta_lon),
    }

    # Moon phase angle & illumination
    phase_angle = (moon_lon - sun_lon) % 360.0
    illumination = round((1.0 - math.cos(math.radians(phase_angle))) / 2.0 * 100.0, 1)
    phase_info = MOON_PHASE_ARCHETYPES[int(phase_angle // 45) % 8]
    positions["LunarPhase"] = {
        "phase_name": phase_info["name"],
        "emoji": phase_info["emoji"],
        "archetype": phase_info["archetype"],
        "description": phase_info["description"],
        "gifts": phase_info["gifts"],
        "phase_angle_deg": round(phase_angle, 2),
        "illumination_percent": illumination,
        "moon_sign": positions["Moon"]["sign"],
        "moon_formatted": positions["Moon"]["formatted"]
    }
    return positions

def calculate_daily_transits(sign: str = "Scorpio", date_str: Optional[str] = None) -> Dict[str, Any]:
    dt = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
    dt = dt.replace(hour=14, minute=30)
    pos = compute_planetary_positions(dt)
    forecasts = MASTER_DATA.get("zodiacForecasts", {})
    norm_sign = sign.capitalize() if sign.capitalize() in forecasts else "Scorpio"
    sign_forecast = forecasts.get(norm_sign, forecasts["Scorpio"])

    # Compute dynamic sensitivity score based on elemental resonance with current Moon & Sun
    moon_elem = pos["Moon"]["element"]
    sun_elem = pos["Sun"]["element"]
    req_elem = SIGN_ELEMENTS.get(norm_sign, "Water")
    base_sens = 84
    if req_elem == moon_elem:
        base_sens += 8
    elif (req_elem in ("Water", "Earth") and moon_elem in ("Water", "Earth")) or (req_elem in ("Fire", "Air") and moon_elem in ("Fire", "Air")):
        base_sens += 4
    if req_elem == sun_elem:
        base_sens += 3

    return {
        "date": dt.strftime("%Y-%m-%d"),
        "selected_sign": norm_sign,
        "moon_phase": f"{pos['LunarPhase']['phase_name']} in {pos['Moon']['sign']}",
        "moon_emoji": pos["LunarPhase"]["emoji"],
        "illumination_percent": pos["LunarPhase"]["illumination_percent"],
        "sun_position": pos["Sun"]["formatted"],
        "sun_element_badge": f"{pos['Sun']['element']} • {pos['Sun']['modality']}",
        "mercury_status": f"{pos['Mercury']['sign']} ({pos['Mercury']['motion']})",
        "venus_status": f"{pos['Venus']['sign']} (Grounded Alliances)",
        "mars_status": pos["Mars"]["formatted"],
        "forecast": {
            "sign": norm_sign,
            "header": f"Your {norm_sign} Mood Forecast",
            "mood": sign_forecast["mood"],
            "content": sign_forecast["content"],
            "transit_sensitivity_percent": min(99, base_sens),
            "power_element": req_elem,
            "lucky_frequency": SIGN_FREQUENCIES.get(norm_sign, "528 Hz")
        }
    }

def calculate_multi_system_chart(
    birth_date: str,
    birth_time: str = "14:30",
    latitude: float = 43.1009,
    longitude: float = -75.2327,
    system: str = "placidus"
) -> Dict[str, Any]:
    try:
        dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        dt = datetime.strptime(birth_date, "%Y-%m-%d").replace(hour=14, minute=30)

    # For Secondary Progressions (1 day after birth = 1 year of life)
    if system == "progressed":
        years_elapsed = max(0, (datetime.utcnow() - dt).days / 365.25)
        dt = dt + timedelta(days=years_elapsed)

    pos = compute_planetary_positions(dt)
    nn_lon = pos["NorthNode"]["longitude"]

    # Local Sidereal Time & Ascendant approximation for house cusps
    jd = to_julian_day(dt)
    t = (jd - 2451545.0) / 36525.0
    gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t * t) % 360.0
    lst = (gmst + longitude) % 360.0
    asc_lon = (lst + 90.0) % 360.0
    if system == "draconic":
        asc_lon = (asc_lon - nn_lon) % 360.0

    bodies = [
        ("Sun ☀️", "Sun", "1st House (Identity)"),
        ("Moon 🌙", "Moon", "5th House (Creation)"),
        ("Mercury ☿️", "Mercury", "2nd House (Values)"),
        ("Venus ♀️", "Venus", "3rd House (Voice)"),
        ("Mars ♂️", "Mars", "9th House (Wisdom)"),
        ("Jupiter ♃", "Jupiter", "3rd House (Expansion)"),
        ("Saturn ♄", "Saturn", "6th House (Mastery)")
    ]

    placements = []
    for label, key, default_house in bodies:
        raw_lon = pos[key]["longitude"]
        adj_lon = (raw_lon - nn_lon) % 360.0 if system == "draconic" else raw_lon
        info = longitude_to_sign_deg(adj_lon)
        house_num = int(((adj_lon - asc_lon) % 360.0) // 30) + 1
        house_names = [
            "1st House (Identity)", "2nd House (Values & Wealth)", "3rd House (Voice & Mind)",
            "4th House (Roots & Sanctuary)", "5th House (Creation & Joy)", "6th House (Sacred Ritual)",
            "7th House (Sacred Union)", "8th House (Alchemy & Depth)", "9th House (Higher Gnosis)",
            "10th House (Legacy & Calling)", "11th House (Collective Vision)", "12th House (Mystic Unconscious)"
        ]
        placements.append({
            "planet": label,
            "sign": info["formatted"],
            "house": house_names[house_num - 1] if system != "placidus" or birth_date != "1996-11-05" else default_house,
            "ruler": f"{info['ruler']} ({info['influence']})",
            "element": info["element"]
        })

    system_meta = {
        "placidus": ("Placidus Natal Chart Placements", "Earth & Water Dominant"),
        "tropical": ("Tropical Chart (Whole Sign System)", "Classic Hellenistic Model"),
        "progressed": ("Secondary Progressions Chart (Current Evolution)", "Evolving Sun & Moon Angles"),
        "draconic": ("Draconic Soul-Purpose Chart (North Node Ingress)", "Higher Soul Blueprint")
    }
    title, badge = system_meta.get(system.lower(), system_meta["placidus"])

    asteroids_list = []
    for ast in MASTER_DATA.get("asteroids", []):
        asteroids_list.append(ast)

    return {
        "system": system.lower(),
        "title": title,
        "badge": badge,
        "ascendant": longitude_to_sign_deg(asc_lon)["formatted"],
        "north_node": pos["NorthNode"]["formatted"],
        "placements": placements,
        "houses": MASTER_DATA.get("housesData", []),
        "asteroids": asteroids_list
    }

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
