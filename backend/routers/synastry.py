"""
AuraMystic Numerology (Life Path & Master Numbers 11, 22, 33) and Relationship Synastry Router
"""
from fastapi import APIRouter, HTTPException
from ..models import LifePathRequest, SynastryRequest
from ..services.ephemeris_engine import MASTER_DATA, SIGN_ELEMENTS, SIGN_MODALITIES
from datetime import date
from pathlib import Path
import json

router = APIRouter()
NUMBER_GUIDE = json.loads(Path(__file__).parents[1].joinpath('data/learning_library.json').read_text(encoding='utf-8'))

ANGEL_SYNCHRONICITIES = {
    "1": "111 — Instant manifestation portal; keep your thoughts focused on sovereign creation, not fear.",
    "2": "222 — Divine partnership, diplomatic equilibrium, and right-timing alignment.",
    "3": "333 — Ascended Masters and creative muses surround your voice and artistic expression.",
    "4": "444 — Archangelic protection and unbreakable structural foundations in business and home.",
    "5": "555 — Quantum catalyst; major liberation and life-path upgrades are underway.",
    "6": "666 — Return to heart-centered sanctuary, somatic nourishment, and domestic harmony.",
    "7": "777 — Mystic gnosis unlocked; synchronicities confirm you are walking your highest esoteric path.",
    "8": "888 — Infinite karmic abundance, financial harvest, and sovereign leadership flow.",
    "9": "999 — Sacred graduation; release completed chapters to step into your next evolutionary octave.",
    "11": "11:11 — Master Illuminator activation; heightened psychic channel and soul-mission remembrance.",
    "22": "22:22 — Master Builder blueprint; turn visionary spiritual concepts into enduring earthly empires.",
    "33": "33:33 — Master Avatar vibration; unconditional compassionate leadership and collective healing."
}

def reduce_numerology_number(num: int) -> int:
    while num > 9 and num not in (11, 22, 33):
        num = sum(int(d) for d in str(num))
    return num

@router.post("/life-path")
def calculate_life_path(req: LifePathRequest):
    """Calculates Life Path Number preserving Master Numbers (11, 22, 33) with step-by-step breakdown."""
    try:
        date(req.birth_year, req.birth_month, req.birth_day)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail='Enter a valid calendar birth date.') from exc
    m_red = reduce_numerology_number(req.birth_month)
    d_red = reduce_numerology_number(req.birth_day)
    y_sum = sum(int(d) for d in str(req.birth_year))
    y_red = reduce_numerology_number(y_sum)

    raw_total = m_red + d_red + y_red
    life_path = reduce_numerology_number(raw_total)

    info = next(n for n in NUMBER_GUIDE['numbers'] if n['number'] == life_path)
    is_master = life_path in (11, 22, 33)

    return {
        "birth_date": f"{req.birth_year:04d}-{req.birth_month:02d}-{req.birth_day:02d}",
        "life_path_number": life_path,
        "is_master_number": is_master,
        "title": info["title"],
        "description": info["strengths"],
        'shadow': info['shadow'],
        "angel_synchronicity": ANGEL_SYNCHRONICITIES.get(str(life_path), ""),
        "calculation_breakdown": {
            "month_reduced": m_red,
            "day_reduced": d_red,
            "year_reduced": y_red,
            "sum_before_final_reduction": raw_total,
            "final_vibration": life_path
        }
    }

@router.get("/numerology-lessons")
def get_all_numerology_lessons():
    """Returns core esoteric meanings for single digits (1-9) and Master Numbers (11, 22, 33)."""
    return {'lessons': [{**n, 'lesson': n['strengths']} for n in NUMBER_GUIDE['numbers']],
            'tarot_numbers': NUMBER_GUIDE['tarot_numbers'], 'court_cards': NUMBER_GUIDE['court_cards'],
            'court_note': NUMBER_GUIDE['court_note'], 'master_note': NUMBER_GUIDE['master_note']}

@router.get("/numerology-lessons/{number}")
def get_numerology_lesson_by_number(number: int):
    meanings = MASTER_DATA.get("lifePathMeanings", {})
    key = str(number)
    if key not in meanings:
        raise HTTPException(status_code=404, detail="Numerology vibration not found. Valid numbers: 1-9, 11, 22, 33.")
    return {
        "number": number,
        "is_master_number": number in (11, 22, 33),
        "title": meanings[key]["title"],
        "lesson": meanings[key]["desc"],
        "angel_number_message": ANGEL_SYNCHRONICITIES.get(key, "")
    }

@router.post("/compatibility")
def generate_synastry_report(req: SynastryRequest):
    """Generates a multi-factor Relationship & Love Compatibility report with 4 sub-scores."""
    sign_a = req.partner_a_sign.capitalize()
    sign_b = req.partner_b_sign.capitalize()
    elem_a = SIGN_ELEMENTS.get(sign_a, "Water")
    elem_b = SIGN_ELEMENTS.get(sign_b, "Earth")
    mod_a = SIGN_MODALITIES.get(sign_a, "Fixed")
    mod_b = SIGN_MODALITIES.get(sign_b, "Fixed")

    # Sister-sign (opposition polarity) check
    signs_order = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    idx_a = signs_order.index(sign_a) if sign_a in signs_order else 7
    idx_b = signs_order.index(sign_b) if sign_b in signs_order else 1
    aspect_dist = abs(idx_a - idx_b)
    if aspect_dist > 6:
        aspect_dist = 12 - aspect_dist

    if aspect_dist == 6:
        axis_label = "Magnetic Sister-Sign Polarity Axis"
        base_score = 94
        emotional, passion, comm, trust = 96, 98, 89, 93
    elif elem_a == elem_b:
        axis_label = f"Harmonic {elem_a} Trine Resonance"
        base_score = 93
        emotional, passion, comm, trust = 95, 92, 94, 91
    elif (elem_a in ("Water", "Earth") and elem_b in ("Water", "Earth")) or (elem_a in ("Fire", "Air") and elem_b in ("Fire", "Air")):
        axis_label = f"Supportive {elem_a}–{elem_b} Sextile Alchemy"
        base_score = 91
        emotional, passion, comm, trust = 92, 90, 91, 92
    elif aspect_dist == 3:
        axis_label = "Catalytic Growth Square & High Voltage"
        base_score = 86
        emotional, passion, comm, trust = 85, 95, 82, 84
    else:
        axis_label = "Karmic Mystery & Evolutionary Mirror"
        base_score = 88
        emotional, passion, comm, trust = 88, 89, 86, 88

    return {
        "partner_a": {"sign": sign_a, "element": elem_a, "modality": mod_a, "gender": req.partner_a_gender},
        "partner_b": {"sign": sign_b, "element": elem_b, "modality": mod_b, "gender": req.partner_b_gender},
        "match_title": f"{sign_a} & {sign_b}: {axis_label}",
        "overall_affinity_percent": base_score,
        "sub_scores": {
            "emotional_depth": emotional,
            "physical_passion": passion,
            "communication": comm,
            "long_term_trust": trust
        },
        "strengths": [
            f"Deep elemental interplay between {sign_a} ({elem_a}) and {sign_b} ({elem_b})",
            "Complementary nervous system co-regulation when boundaries are honored",
            "High creative and spiritual co-manifestation potential"
        ],
        "watch_outs": [
            f"Navigating {mod_a} vs. {mod_b} pacing during high-stress transits",
            "Ensuring unspoken expectations are voiced early with compassionate directness"
        ],
        "summary": (
            f"The connection between {sign_a} ({elem_a}) and {sign_b} ({elem_b}) activates a {axis_label}. "
            f"{sign_a} brings sovereign intuition and depth, while {sign_b} anchors partnership stability and magnetic reciprocity. "
            f"Overall Synastry Resonance: {base_score}%."
        )
    }
