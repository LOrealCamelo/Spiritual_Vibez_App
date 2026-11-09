"""
AuraMystic 78-Card Tarot Studio, Interactive Study Quiz, Tap-and-Hold Peek & 48 NeuroSpicy Mystic Spreads Router
"""
import json
import random
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from ..models import DealSlotRequest, DealSpreadRequest, SynthesizeSpreadRequest, StudyAnswerRequest
from ..services.ephemeris_engine import MASTER_DATA
from ..database import get_connection

router = APIRouter()

from pathlib import Path
IMAGE_FILES = {c['id']: c['file'] for c in json.loads(Path(__file__).parents[1].joinpath('data/tarot_images.json').read_text())}
ALL_CARDS: List[Dict[str, Any]] = [{**c, 'image_url': '/assets/tarot/' + IMAGE_FILES[c['id']]} for c in MASTER_DATA.get('allCards', [])]
STUDY_DETAILS: Dict[str, Any] = MASTER_DATA.get("cardStudyDetails", {})
MASTER_SPREADS: List[Dict[str, Any]] = MASTER_DATA.get("masterSpreadsData", [])
CAT_TITLES: Dict[str, str] = MASTER_DATA.get("catTitles", {})
CAT_DESCRIPTIONS: Dict[str, str] = MASTER_DATA.get("catDescriptions", {})

DISTRACTOR_KEYWORDS = [
    "VICTORY", "AMBITION", "RESTLESSNESS", "SURRENDER", "ILLUSION",
    "ABUNDANCE", "SOLITUDE", "CELEBRATION", "HEARTBREAK", "AUTHORITY",
    "INTUITION", "PATIENCE", "REBIRTH", "CLARITY", "SOVEREIGNTY"
]

def enrich_card_study_data(card: Dict[str, Any]) -> Dict[str, Any]:
    cid = str(card["id"])
    override = STUDY_DETAILS.get(cid, {})
    up_kw = override.get("keywordsUpright") or [s.strip().upper() for s in card["upright"].split(",") if s.strip()]
    rev_kw = override.get("keywordsReversed") or [s.strip().upper() for s in card["reversed"].split(",") if s.strip()]
    return {
        **card,
        "keywords_upright": up_kw,
        "keywords_reversed": rev_kw,
        "affirmation_upright": override.get(
            "affirmationUpright",
            f"I embody the highest wisdom of {card['name']} and trust my sovereign path: {card['mantra']}."
        ),
        "affirmation_reversed": override.get(
            "affirmationReversed",
            f"I gently release resistance around {card['name']} and honor my nervous system's timing."
        ),
        "description_upright": override.get(
            "descriptionUpright",
            f"{card['name']} ({card['decan']}) represents {card['upright'].lower()}. Archetype: {card['character']}. Mantra: {card['mantra']}."
        ),
        "description_reversed": override.get(
            "descriptionReversed",
            f"When reversed, {card['name']} invites introspection around {card['reversed'].lower()}. Realign with your inner authority."
        )
    }

@router.get("/cards")
def list_tarot_cards(
    suit: Optional[str] = Query(None, description="Major | Wands | Cups | Swords | Coins | all"),
    search: Optional[str] = Query(None, description="Search by card name, keyword, decan, or mantra")
):
    """Returns all 78 Tarot cards in the Sacred Tarot Encyclopedia, filterable by suit and search query."""
    results = ALL_CARDS
    if suit and suit.lower() != "all":
        results = [c for c in results if c["suit"].lower() == suit.lower()]
    if search:
        q = search.lower().strip()
        results = [
            c for c in results
            if q in c["name"].lower()
            or q in c["mantra"].lower()
            or q in c["upright"].lower()
            or q in c["reversed"].lower()
            or q in c["decan"].lower()
        ]
    return {"count": len(results), "cards": [enrich_card_study_data(c) for c in results]}

@router.get("/cards/{card_id}")
def get_card_detail(card_id: int):
    """Returns full Tap-and-Hold Peek details (Upright/Reversed keywords, affirmation, decan, and description)."""
    for c in ALL_CARDS:
        if c["id"] == card_id:
            return enrich_card_study_data(c)
    raise HTTPException(status_code=404, detail=f"Card ID {card_id} not found in 78-card deck.")

@router.get("/study/quiz")
@router.get("/study/quiz-question")
def get_study_quiz_question(card_id: Optional[int] = Query(None, description="Specific card ID (0-77) or random")):
    """Generates a multiple-choice study quiz question with no spoilers on the card front."""
    if card_id is not None and 0 <= card_id < len(ALL_CARDS):
        card = ALL_CARDS[card_id]
    else:
        card = random.choice(ALL_CARDS)

    enriched = enrich_card_study_data(card)
    correct_kw = enriched["keywords_upright"][0] if enriched["keywords_upright"] else "TRADITION"
    if card["id"] == 5:
        correct_kw = "TRADITION"
        options = ["VICTORY", "AMBITION", "RESTLESSNESS", "TRADITION"]
    else:
        pool = [w for w in DISTRACTOR_KEYWORDS if w != correct_kw]
        distractors = random.sample(pool, 3)
        options = distractors + [correct_kw]
        random.shuffle(options)

    return {
        "brand": "NeuroSpicy Mystic",
        "card_id": card["id"],
        "card_name": card["name"],
        'image_url': card['image_url'],
        "suit": card["suit"],
        "icon": card["icon"],
        "prompt": "What idea can this card represent?",
        "options": options,
        "correct_answer": correct_kw,
        "peek_back_data": {
            "decan": card["decan"],
            "element": card["element"],
            "keywords_upright": enriched["keywords_upright"],
            "keywords_reversed": enriched["keywords_reversed"],
            "affirmation_upright": enriched["affirmation_upright"],
            "affirmation_reversed": enriched["affirmation_reversed"],
            "description_upright": enriched["description_upright"],
            "description_reversed": enriched["description_reversed"]
        }
    }

@router.post("/study/answer")
def submit_study_quiz_answer(req: StudyAnswerRequest):
    """Validates a user's study quiz answer and updates their streak & progress in SQLite."""
    card = next((c for c in ALL_CARDS if c["id"] == req.card_id), None)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    enriched = enrich_card_study_data(card)
    valid_keywords = [k.upper() for k in enriched["keywords_upright"]]
    if card["id"] == 5:
        valid_keywords.append("TRADITION")

    is_correct = req.selected_keyword.strip().upper() in valid_keywords

    conn = get_connection()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM study_quiz_progress WHERE user_id = ?", (req.user_id,)).fetchone()
    now = datetime.utcnow().isoformat()

    if not row:
        studied = 1
        correct = 1 if is_correct else 0
        streak = 1 if is_correct else 0
        best = streak
        mastered = [card["id"]] if is_correct else []
        cur.execute(
            "INSERT INTO study_quiz_progress VALUES (?, ?, ?, ?, ?, ?, ?)",
            (req.user_id, studied, correct, streak, best, json.dumps(mastered), now)
        )
    else:
        studied = row["cards_studied"] + 1
        correct = row["correct_answers"] + (1 if is_correct else 0)
        streak = (row["current_streak"] + 1) if is_correct else 0
        best = max(row["best_streak"], streak)
        mastered = json.loads(row["mastered_card_ids"] or "[]")
        if is_correct and card["id"] not in mastered:
            mastered.append(card["id"])
        cur.execute(
            """UPDATE study_quiz_progress
               SET cards_studied=?, correct_answers=?, current_streak=?, best_streak=?, mastered_card_ids=?, updated_at=?
               WHERE user_id=?""",
            (studied, correct, streak, best, json.dumps(mastered), now, req.user_id)
        )
    conn.commit()
    conn.close()

    return {
        "is_correct": is_correct,
        "card_name": card["name"],
        "selected_keyword": req.selected_keyword,
        "valid_keywords": enriched["keywords_upright"],
        "explanation": enriched["description_upright"],
        "affirmation": enriched["affirmation_upright"],
        "progress": {
            "cards_studied": studied,
            "correct_answers": correct,
            "accuracy_percent": round(correct / max(1, studied) * 100, 1),
            "current_streak": streak,
            "best_streak": best,
            "mastered_count": len(mastered)
        }
    }

@router.get("/categories")
@router.get("/spreads/categories")
def get_spread_categories():
    """Returns all 7 NeuroSpicy Mystic curated spread categories with counts and descriptions."""
    categories = []
    for cat_id, title in CAT_TITLES.items():
        count = sum(1 for s in MASTER_SPREADS if s["category"] == cat_id)
        categories.append({
            "id": cat_id,
            "title": title,
            "description": CAT_DESCRIPTIONS.get(cat_id, ""),
            "spread_count": count
        })
    return {
        "brand": "NeuroSpicy Mystic",
        "total_spreads": len(MASTER_SPREADS),
        "categories": categories
    }

@router.get("/spreads")
def list_spreads(
    category: Optional[str] = Query(None, description="wellbeing | daily | love | shadow | crossroads | purpose | spirit"),
    search: Optional[str] = Query(None, description="Search spread title or question text")
):
    """Returns all 48 NeuroSpicy Mystic spreads or filters by category/search."""
    results = MASTER_SPREADS
    if category and category.lower() != "all":
        results = [s for s in results if s["category"].lower() == category.lower()]
    if search:
        q = search.lower().strip()
        results = [
            s for s in results
            if q in s["title"].lower()
            or q in s["desc"].lower()
            or any(q in q_obj["q"].lower() or q in q_obj["title"].lower() for q_obj in s["questions"])
        ]
    return {"brand": "NeuroSpicy Mystic", "count": len(results), "spreads": results}

@router.get("/spreads/reset-your-energy")
def get_reset_your_energy_spread():
    """Returns the featured 4-card stepped descending diagonal Reset Your Energy spread."""
    spread = next((s for s in MASTER_SPREADS if s["id"] == "reset-energy"), MASTER_SPREADS[0])
    return {"brand": "NeuroSpicy Mystic", **spread}

@router.get("/spreads/{spread_id}")
def get_spread_by_id(spread_id: str):
    """Returns any of the 48 NeuroSpicy Mystic spreads by ID."""
    spread = next((s for s in MASTER_SPREADS if s["id"] == spread_id), None)
    if not spread:
        raise HTTPException(status_code=404, detail=f"Spread '{spread_id}' not found.")
    return {"brand": "NeuroSpicy Mystic", **spread}

@router.post("/deal-card")
@router.post("/spreads/deal-card")
@router.post("/spreads/deal-slot")
def deal_single_slot(req: DealSlotRequest):
    """Electronically draws a random card from the 78-card deck for a specific spread slot."""
    spread = next((s for s in MASTER_SPREADS if s["id"] == req.spread_id), MASTER_SPREADS[0])
    available = [c for c in ALL_CARDS if c["id"] not in req.exclude_card_ids]
    pool = available if available else ALL_CARDS
    chosen = random.choice(pool)
    is_upright = random.random() > 0.12
    orientation = "Upright" if is_upright else "Reversed"
    enriched = enrich_card_study_data(chosen)

    q_obj = next((q for q in spread["questions"] if q["slot"] == req.slot_num), spread["questions"][0])
    meaning = chosen["upright"] if is_upright else chosen["reversed"]

    return {
        "brand": "NeuroSpicy Mystic",
        "spread_id": spread["id"],
        "spread_title": spread["title"],
        "slot": req.slot_num,
        "slot_title": q_obj["title"],
        "question": q_obj["q"],
        "card": {
            "id": chosen["id"],
            'image_url': chosen['image_url'],
            "name": chosen["name"],
            "suit": chosen["suit"],
            "icon": chosen["icon"],
            "decan": chosen["decan"],
            "element": chosen["element"],
            "mantra": chosen["mantra"],
            "orientation": orientation,
            "meaning": meaning,
            "affirmation": enriched["affirmation_upright"] if is_upright else enriched["affirmation_reversed"]
        },
        "contextual_interpretation": (
            f"For '{q_obj['title']}' ({q_obj['q']}), {chosen['name']} ({orientation}) reveals: {meaning}. "
            f"Mantra: {chosen['mantra']}."
        )
    }

@router.post("/spreads/deal-all")
def deal_entire_spread(req: DealSpreadRequest):
    """Deals all card slots for a spread at once and produces a unified NeuroSpicy Mystic synthesis."""
    spread = next((s for s in MASTER_SPREADS if s["id"] == req.spread_id), MASTER_SPREADS[0])
    count = spread["cardCount"]
    sampled = random.sample(ALL_CARDS, min(count, len(ALL_CARDS)))
    dealt_positions = []
    for idx, q_obj in enumerate(spread["questions"]):
        card = sampled[idx]
        is_upright = random.random() > 0.12
        orientation = "Upright" if is_upright else "Reversed"
        meaning = card["upright"] if is_upright else card["reversed"]
        dealt_positions.append({
            "slot": q_obj["slot"],
            "slot_title": q_obj["title"],
            "question": q_obj["q"],
            "card_id": card["id"],
            "card_name": card["name"],
            'image_url': card['image_url'],
            "icon": card["icon"],
            "decan": card["decan"],
            "element": card["element"],
            "orientation": orientation,
            "meaning": meaning,
            "position_synthesis": f"{card['name']} ({orientation}) answers '{q_obj['q']}' through {meaning.lower()}."
        })

    card_names = ", ".join(p["card_name"] for p in dealt_positions)
    holistic_synthesis = (
        f"NeuroSpicy Mystic Unified Synthesis for '{spread['title']}': "
        f"Drawing across this layout reveals an energetic progression through {card_names}. "
        f"Honor your nervous system's natural pacing, release external urgency, and anchor the practical wisdom of "
        f"{dealt_positions[-1]['card_name']} ({dealt_positions[-1]['orientation']}) as your sovereign integration step."
    )

    if req.save_to_journal:
        conn = get_connection()
        conn.execute(
            "INSERT INTO saved_tarot_readings (spread_id, spread_title, category, cards_json, synthesis, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (spread["id"], spread["title"], spread["category"], json.dumps(dealt_positions), holistic_synthesis, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()

    return {
        "brand": "NeuroSpicy Mystic",
        "spread_id": spread["id"],
        "spread_title": spread["title"],
        "category": spread["category"],
        "card_count": count,
        "positions": dealt_positions,
        "holistic_synthesis": holistic_synthesis
    }

@router.post("/synthesize-reading")
@router.post("/spreads/synthesize")
def synthesize_custom_spread(req: SynthesizeSpreadRequest):
    """Generates a unified NeuroSpicy Mystic Oracle reading synthesis for user-drawn cards and optionally saves it."""
    spread = next((s for s in MASTER_SPREADS if s["id"] == req.spread_id), MASTER_SPREADS[0])
    positions = []
    for item in req.drawn_cards:
        card = next((c for c in ALL_CARDS if c["id"] == item.card_id), ALL_CARDS[0])
        q_obj = next((q for q in spread["questions"] if q["slot"] == item.slot), spread["questions"][0])
        meaning = card["upright"] if item.orientation == "Upright" else card["reversed"]
        positions.append({
            "slot": item.slot,
            "slot_title": q_obj["title"],
            "question": q_obj["q"],
            "card_id": card["id"],
            "card_name": card["name"],
            'image_url': card['image_url'],
            "orientation": item.orientation,
            "meaning": meaning,
            "interpretation": f"{card['name']} ({item.orientation}) illuminates '{q_obj['title']}': {meaning}."
        })

    names = ", ".join(p["card_name"] for p in positions) if positions else "The Hierophant"
    synthesis = (
        f"NeuroSpicy Mystic Unified Synthesis ({spread['title']}): "
        f"Your drawn cards ({names}) weave a cohesive roadmap of energetic reclamation. "
        f"Trust your somatic boundaries, release overgiving, and align your daily actions with sovereign clarity."
    )

    if req.save_to_journal and positions:
        conn = get_connection()
        conn.execute(
            "INSERT INTO saved_tarot_readings (spread_id, spread_title, category, cards_json, synthesis, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (spread["id"], spread["title"], spread["category"], json.dumps(positions), synthesis, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()

    return {
        "brand": "NeuroSpicy Mystic",
        "spread_id": spread["id"],
        "spread_title": spread["title"],
        "positions": positions,
        "synthesis": synthesis
    }

@router.get("/readings/saved")
def get_saved_readings():
    """Returns saved Tarot spread readings from SQLite persistence."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM saved_tarot_readings ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return {
        "readings": [
            {
                "id": r["id"],
                "spread_id": r["spread_id"],
                "spread_title": r["spread_title"],
                "category": r["category"],
                "positions": json.loads(r["cards_json"]),
                "synthesis": r["synthesis"],
                "created_at": r["created_at"]
            }
            for r in rows
        ]
    }
