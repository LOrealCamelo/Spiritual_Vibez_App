"""
AuraMystic Sacred Solfeggio Frequencies, Searchable Ritual & Ceremony Finder, and Ancient Fertility Practices Router
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ..models import RitualCompleteRequest, JonasFertilityRequest
from ..services.ephemeris_engine import MASTER_DATA, compute_planetary_positions
from ..database import get_connection

router = APIRouter()

FREQUENCIES = MASTER_DATA.get("frequencies", [])
RITUALS = [
    {**r, "id": f"ritual-{i+1}", "legacy_id": str(r.get("id", i+1))}
    for i, r in enumerate(MASTER_DATA.get("ritualsData", []))
]

ANCIENT_FERTILITY_PRACTICES = [
    {
        "id": "botanical-infusions",
        "title": "Red Clover & Raspberry Leaf Infusions",
        "category": "Ancestral Botanical Tonic",
        "summary": "Traditional mineral-rich herbal infusions revered in ancestral midwifery for uterine tone, calcium-magnesium nourishment, and endocrine harmony.",
        "protocol": "Steep 1 tbsp organic dried red clover blossoms and 1 tbsp red raspberry leaf in 16 oz boiled spring water for 4 hours (covered) during the Follicular and Ovulatory lunar phases.",
        "clinical_disclaimer": "Always consult qualified healthcare practitioners for clinical guidance."
    },
    {
        "id": "eugen-jonas-lunar-charting",
        "title": "Lunar Conception Charting (Eugen Jonas Method)",
        "category": "Cosmobiological Fertility",
        "summary": "Discovered by Dr. Eugen Jonas in 1956, this method calculates the exact monthly recurrence of the Sun-Moon angular phase present at the mother's moment of birth as a secondary peak fertility window alongside biological ovulation.",
        "protocol": "Identify the natal Sun-Moon phase angle at birth; track the 29.53-day lunar return of that exact angle each month.",
        "clinical_disclaimer": "Always consult qualified healthcare practitioners for clinical guidance."
    },
    {
        "id": "sacral-castor-grounding",
        "title": "Sacral Chakra Grounding & Warm Castor Packs",
        "category": "Somatic Womb Sanctuary",
        "summary": "Gentle topical cold-pressed castor oil packs paired with 417 Hz / 528 Hz sound baths to encourage pelvic lymphatic flow and parasympathetic nervous system relaxation.",
        "protocol": "Apply warm organic hexane-free castor oil over the lower abdomen for 30 minutes during the Follicular phase (avoid during active menstruation or pregnancy).",
        "clinical_disclaimer": "Always consult qualified healthcare practitioners for clinical guidance."
    }
]

@router.get("/frequencies")
def get_solfeggio_frequencies():
    """Returns all 8 Sacred Solfeggio frequencies with Hz, somatic benefits, and tuning fork pairing notes."""
    return {
        "brand": "NeuroSpicy Mystic",
        "store_pairing": "Pairs with 528Hz Weighted & Unweighted Biosonic Tuning Forks at https://www.neurospicymystic.com",
        "frequencies": FREQUENCIES
    }

@router.get("/search")
@router.get("/")
def search_rituals(
    category: Optional[str] = Query("all", description="all | money | love | protection"),
    query: Optional[str] = Query(None, description="Keyword search across ritual title, tools, timing, and steps")
):
    """Searches and filters the AuraMystic Ritual & Ceremony Finder database."""
    results = RITUALS
    if category and category.lower() != "all":
        results = [r for r in results if r["cat"].lower() == category.lower()]
    if query:
        q = query.lower().strip()
        results = [
            r for r in results
            if q in r["title"].lower()
            or q in r["tools"].lower()
            or q in r["moon"].lower()
            or q in r["steps"].lower()
        ]
    conn = get_connection()
    completed_rows = conn.execute("SELECT ritual_id, completed_at FROM ritual_completions ORDER BY id DESC").fetchall()
    conn.close()
    completed_map = {row["ritual_id"]: row["completed_at"] for row in completed_rows}

    enriched = [
        {**r, "is_completed": r["id"] in completed_map, "last_completed_at": completed_map.get(r["id"])}
        for r in results
    ]
    return {"count": len(enriched), "rituals": enriched}

@router.post("/{ritual_id}/complete")
def mark_ritual_complete(ritual_id: str, req: Optional[RitualCompleteRequest] = None):
    """Logs a completed ceremony or ritual in SQLite."""
    ritual = next((r for r in RITUALS if str(r["id"]) == str(ritual_id) or str(r.get("legacy_id")) == str(ritual_id) or r["title"].lower() == str(ritual_id).lower()), None)
    if not ritual:
        raise HTTPException(status_code=404, detail=f"Ritual '{ritual_id}' not found.")
    now = datetime.utcnow().isoformat()
    notes = req.intention_notes if req else ""
    conn = get_connection()
    conn.execute(
        "INSERT INTO ritual_completions (ritual_id, ritual_title, category, intention_notes, completed_at) VALUES (?, ?, ?, ?, ?)",
        (ritual["id"], ritual["title"], ritual["cat"], notes, now)
    )
    conn.commit()
    conn.close()
    return {
        "status": "completed",
        "ritual_id": ritual["id"],
        "ritual_title": ritual["title"],
        "completed_at": now,
        "message": f"Ritual '{ritual['title']}' logged to your personal sanctuary history."
    }

@router.get("/fertility-practices")
def get_ancient_fertility_practices():
    """Returns Ancient Fertility Practices with botanical, cosmobiological, and somatic protocols."""
    return {
        "practices": ANCIENT_FERTILITY_PRACTICES,
        "footnote": "Always consult qualified healthcare practitioners for clinical guidance."
    }

@router.post("/fertility-jonas-calc")
def calculate_jonas_lunar_fertility(req: JonasFertilityRequest):
    """Calculates both biological ovulation and Dr. Eugen Jonas Natal Lunar Phase Return windows."""
    b_dt = datetime.strptime(req.birth_date, "%Y-%m-%d").replace(hour=14, minute=30)
    natal_pos = compute_planetary_positions(b_dt)
    natal_angle = natal_pos["LunarPhase"]["phase_angle_deg"]
    natal_phase_name = natal_pos["LunarPhase"]["phase_name"]

    lmp_dt = datetime.strptime(req.last_period_date, "%Y-%m-%d")
    bio_ovulation_dt = lmp_dt + timedelta(days=max(10, req.cycle_length - 14))

    # Find the next date within 30 days where Sun-Moon angle matches natal_angle
    now = datetime.utcnow()
    best_dt = now
    min_diff = 360.0
    for day_offset in range(0, 30):
        candidate = now + timedelta(days=day_offset)
        pos = compute_planetary_positions(candidate)
        angle = pos["LunarPhase"]["phase_angle_deg"]
        diff = abs((angle - natal_angle + 180) % 360 - 180)
        if diff < min_diff:
            min_diff = diff
            best_dt = candidate

    return {
        "birth_date": req.birth_date,
        "natal_lunar_phase": natal_phase_name,
        "natal_sun_moon_angle_deg": natal_angle,
        "biological_ovulation_window": {
            "peak_date": bio_ovulation_dt.strftime("%Y-%m-%d"),
            "fertile_window_start": (bio_ovulation_dt - timedelta(days=3)).strftime("%Y-%m-%d"),
            "fertile_window_end": (bio_ovulation_dt + timedelta(days=1)).strftime("%Y-%m-%d")
        },
        "jonas_cosmobiology_window": {
            "exact_lunar_return_date": best_dt.strftime("%Y-%m-%d"),
            "window_start": (best_dt - timedelta(days=2)).strftime("%Y-%m-%d"),
            "window_end": (best_dt + timedelta(days=1)).strftime("%Y-%m-%d"),
            "dominant_moon_sign": compute_planetary_positions(best_dt)["Moon"]["sign"]
        },
        "clinical_disclaimer": "Educational & cosmobiological reference only. Always consult qualified healthcare practitioners for clinical guidance."
    }
