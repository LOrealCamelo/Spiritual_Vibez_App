"""
AuraMystic Lunar Menstrual Cycle Tracker & Subconscious Shadow Work Sanctuary Router
"""
import json
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from ..models import MenstrualCycleRequest, ShadowJournalCreateRequest
from ..services.ephemeris_engine import MASTER_DATA, compute_planetary_positions
from ..database import get_connection

router = APIRouter()

SHADOW_PROMPTS = MASTER_DATA.get("shadowPrompts", [])

@router.post("/menstrual-cycle")
def calculate_lunar_menstrual_cycle(req: MenstrualCycleRequest):
    """Syncs biological menstrual cycle rhythms with the 29.5-day synodic moon cycle."""
    lmp = datetime.strptime(req.last_period_date, "%Y-%m-%d")
    today = datetime(2026, 11, 5)
    days_since = (today - lmp).days
    current_day = (days_since % req.cycle_length) + 1 if days_since >= 0 else 1
    next_period = lmp + timedelta(days=((max(0, days_since) // req.cycle_length) + 1) * req.cycle_length)
    next_moon = compute_planetary_positions(next_period)["LunarPhase"]

    if current_day <= 5:
        phase = "Menstrual"
        inner_season = "Inner Winter"
        archetype = "Red Moon / Wise Woman Cycle Archetype"
        desc = "Sacred rest, cellular release, and heightened dream-state intuition. Honor low-sensory boundaries and restorative stillness."
    elif current_day <= 12:
        phase = "Follicular"
        inner_season = "Inner Spring"
        archetype = "Pink Moon / Maiden Renewal Archetype"
        desc = "Rising estrogen and fresh mental curiosity. Ideal window for brainstorming, initiating new projects, and playful exploration."
    elif current_day <= 17:
        phase = "Ovulatory"
        inner_season = "Inner Summer"
        archetype = "White Moon Cycle Archetype"
        desc = "Ovulation is aligning near the Full Moon. Energy, confidence, and social magnetism are at peak. Ideal window for creative launches, networking, and intimate bonding."
    else:
        phase = "Luteal"
        inner_season = "Inner Autumn"
        archetype = "Purple Moon / Enchantress Archetype"
        desc = "Progesterone rises and intuition turns inward. Discernment is razor-sharp—complete unfinished tasks, edit workflows, and prepare your sanctuary."

    conn = get_connection()
    conn.execute(
        """INSERT INTO cycle_tracking_logs
           (last_period_date, cycle_length, current_day, phase_name, inner_season, moon_archetype, next_period_date, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (req.last_period_date, req.cycle_length, current_day, phase, inner_season, archetype, next_period.strftime("%Y-%m-%d"), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    return {
        "last_period_date": req.last_period_date,
        "cycle_length": req.cycle_length,
        "current_day": current_day,
        "day_badge": f"Day {current_day} of {req.cycle_length}",
        "phase_name": phase,
        "inner_season": inner_season,
        "phase_header": f"Current Phase: {phase} ({inner_season})",
        "moon_cycle_archetype": archetype,
        "description": desc,
        "next_predicted_menstruation": {
            "date": next_period.strftime("%B %d, %Y"),
            "iso_date": next_period.strftime("%Y-%m-%d"),
            "moon_phase": next_moon["phase_name"],
            "formatted": f"{next_period.strftime('%B %d, %Y')} ({next_moon['phase_name']})"
        }
    }

@router.get("/shadow-prompts")
def list_shadow_prompts():
    """Returns all deep reflection shadow work prompts."""
    return {"count": len(SHADOW_PROMPTS), "prompts": SHADOW_PROMPTS}

@router.get("/shadow-prompts/random")
def get_random_shadow_prompt():
    """Returns a single randomized shadow work prompt for daily reflection."""
    return {"prompt": random.choice(SHADOW_PROMPTS)}

@router.get("/journal")
def list_shadow_journal_entries():
    """Retrieves saved shadow work reflections and tarot journal notes from SQLite."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM shadow_journal_entries ORDER BY id DESC").fetchall()
    conn.close()
    return {
        "entries": [
            {
                "id": r["id"],
                "prompt": r["prompt"],
                "entry_text": r["entry_text"],
                "moon_phase": r["moon_phase"],
                "tags": json.loads(r["tags"] or "[]"),
                "created_at": r["created_at"]
            }
            for r in rows
        ]
    }

@router.post("/journal")
def create_shadow_journal_entry(req: ShadowJournalCreateRequest):
    """Saves a private shadow work reflection or spiritual note to SQLite."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO shadow_journal_entries (prompt, entry_text, moon_phase, tags, created_at) VALUES (?, ?, ?, ?, ?)",
        (req.prompt, req.entry_text, req.moon_phase or "Waxing Gibbous in Pisces", json.dumps(req.tags or []), now)
    )
    entry_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": entry_id,
        "prompt": req.prompt,
        "entry_text": req.entry_text,
        "moon_phase": req.moon_phase,
        "created_at": now,
        "status": "saved"
    }

@router.delete("/journal/{entry_id}")
def delete_shadow_journal_entry(entry_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM shadow_journal_entries WHERE id = ?", (entry_id,))
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Journal entry not found.")
    conn.commit()
    conn.close()
    return {"status": "deleted", "id": entry_id}
