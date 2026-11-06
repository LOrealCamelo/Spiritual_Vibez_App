"""
AuraMystic Divination Hub Router: Interactive Amethyst Crystal Pendulum Dowsing & Elder Futhark Rune Casting
"""
import random
from fastapi import APIRouter
from ..models import PendulumRequest, RuneCastRequest
from ..services.ephemeris_engine import MASTER_DATA

router = APIRouter()

PENDULUM_ANSWERS = MASTER_DATA.get("pendulumAnswers", [])
RUNES_DATA = MASTER_DATA.get("runesData", [])

@router.post("/pendulum")
def dowse_amethyst_pendulum(req: PendulumRequest):
    """Simulates Amethyst Crystal Pendulum dowsing response with directional swing geometry."""
    chosen = random.choice(PENDULUM_ANSWERS)
    swing_patterns = {
        "Yes": "Clockwise Circular Orbit (Solar Affirmative)",
        "No": "Counter-Clockwise Shielding Arc (Protective Boundary)",
        "Recalibrate": "Diagonal Oscillation (Stillness & Nervous System Reset)"
    }
    key = "Yes" if "Yes" in chosen["ans"] else ("No" if "No" in chosen["ans"] else "Recalibrate")
    return {
        "question": req.question,
        "answer": chosen["ans"],
        "guidance": chosen["sub"],
        "swing_geometry": swing_patterns[key],
        "crystal": "Charged Uruguayan Amethyst Point"
    }

@router.get("/runes")
def list_elder_futhark_runes():
    """Returns the Elder Futhark rune stones dataset."""
    return {"runes": RUNES_DATA}

@router.post("/runes/cast")
def cast_elder_futhark_runes(req: RuneCastRequest):
    """Casts 3 Elder Futhark Norse runes (Origin, Present Challenge, Sacred Outcome)."""
    count = max(1, min(req.rune_count, len(RUNES_DATA)))
    drawn = random.sample(RUNES_DATA, count)
    positions = ["1. Urd (Ancestral Root / Past)", "2. Verdandi (Living Present / Action)", "3. Skuld (Becoming / Destiny)"]
    cast_result = []
    for i, r in enumerate(drawn):
        cast_result.append({
            "position": positions[i] if i < len(positions) else f"Rune {i+1}",
            "symbol": r.get("symbol") or r.get("sym", "ᚠ"),
            "name": r["name"],
            "meaning": r["meaning"]
        })
    names = ", ".join(r["name"] for r in drawn)
    return {
        "focus_intention": req.focus_intention,
        "cast_runes": cast_result,
        "synthesis": f"The Norns reveal {names} for your inquiry: align with {drawn[0]['meaning'].lower()} and trust {drawn[-1]['meaning'].lower()}."
    }
