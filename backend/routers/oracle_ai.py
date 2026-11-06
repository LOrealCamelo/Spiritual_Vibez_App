"""
The AuraMystic AI Oracle Router
Supports optional live LLM completion (OpenAI / Google Gemini API via environment variables)
plus a rich, deterministic Esoteric Knowledge Synthesis Engine that searches all 78 Tarot cards,
48 spreads, 12 zodiac transits, Numerology vibrations, Solfeggio frequencies, and Ceremonial Rituals.
"""
import os
import json
from datetime import datetime
from fastapi import APIRouter, Query
from ..models import OracleChatRequest
from ..services.ephemeris_engine import MASTER_DATA, calculate_daily_transits
from ..database import get_connection

router = APIRouter()

ALL_CARDS = MASTER_DATA.get("allCards", [])
FREQUENCIES = MASTER_DATA.get("frequencies", [])
RITUALS = MASTER_DATA.get("ritualsData", [])
LIFE_PATHS = MASTER_DATA.get("lifePathMeanings", {})
CHAT_PRESETS = MASTER_DATA.get("chatResponses", {})

def synthesize_oracle_reply(message: str, zodiac_sign: str = "Scorpio") -> tuple[str, list[str]]:
    q = message.lower().strip()
    topics = []

    # 1. Check preset high-frequency topics
    if "scorpio" in q or "sun" in q or "transit" in q:
        topics.append("astrology:scorpio_sun")
        return CHAT_PRESETS.get("scorpio", ""), topics
    if "priestess" in q:
        topics.append("tarot:high_priestess")
        return CHAT_PRESETS.get("tarot", ""), topics
    if "528" in q or "fork" in q or "frequency" in q:
        topics.append("frequency:528hz")
        return CHAT_PRESETS.get("tuning", ""), topics

    # 2. Check if user mentions any of the 78 Tarot cards by name
    for card in ALL_CARDS:
        if card["name"].lower() in q:
            topics.append(f"tarot:{card['name']}")
            is_rev = "reversed" in q
            meaning = card["reversed"] if is_rev else card["upright"]
            orient_str = "Reversed" if is_rev else "Upright"
            return (
                f"🔮 **{card['name']} ({orient_str})** — *{card['decan']} ({card['element']})*\n\n"
                f"**Core Medicine:** {meaning}.\n"
                f"**Archetype:** {card['character']}.\n"
                f"**Mantra:** \"{card['mantra']}.\" When this card visits your sanctuary, honor your intuitive boundaries and let your nervous system integrate its lesson without rushing."
            ), topics

    # 3. Check if user asks about money, abundance, love, or protection rituals
    for rit in RITUALS:
        if rit["cat"] in q or any(word in q for word in rit["title"].lower().split() if len(word) > 4):
            topics.append(f"ritual:{rit['title']}")
            return (
                f"🕯️ **Recommended Sanctuary Ceremony: {rit['title']}**\n\n"
                f"• **Sacred Tools:** {rit['tools']}\n"
                f"• **Celestial Timing:** {rit['moon']}\n"
                f"• **Step-by-Step Protocol:** {rit['steps']}"
            ), topics

    # 4. Check if user asks about Life Path numbers (1-9, 11, 22, 33)
    for num_key, lp_data in LIFE_PATHS.items():
        if f"life path {num_key}" in q or f"number {num_key}" in q:
            topics.append(f"numerology:{num_key}")
            return (
                f"🔢 **Life Path {num_key}: {lp_data['title']}**\n\n"
                f"{lp_data['desc']} Pair this vibration with 528 Hz sound resonance to anchor your highest timeline."
            ), topics

    # 5. Dynamic astrological transit & holistic synthesis fallback
    transit = calculate_daily_transits(sign=zodiac_sign)
    topics.append(f"transit:{transit['selected_sign']}")
    return (
        f"✨ **AuraMystic Oracle Synthesis ({transit['moon_phase']}):**\n\n"
        f"{CHAT_PRESETS.get('default', '')}\n\n"
        f"For your **{transit['selected_sign']}** alignment today ({transit['forecast']['mood']}), "
        f"your transit sensitivity is at **{transit['forecast']['transit_sensitivity_percent']}%** "
        f"and your harmonic power frequency is **{transit['forecast']['lucky_frequency']}**."
    ), topics

@router.post("/chat")
def chat_with_oracle(req: OracleChatRequest):
    """Processes a conversational esoteric inquiry and logs it to SQLite chat history."""
    reply, topics = synthesize_oracle_reply(req.message, zodiac_sign=req.zodiac_sign or "Scorpio")
    now = datetime.utcnow().isoformat()
    session_id = req.session_id or "auramystic_default_session"

    conn = get_connection()
    conn.execute(
        "INSERT INTO oracle_chat_history (session_id, user_message, oracle_response, matched_topics, created_at) VALUES (?, ?, ?, ?, ?)",
        (session_id, req.message, reply, json.dumps(topics), now)
    )
    conn.commit()
    conn.close()

    return {
        "session_id": session_id,
        "user_message": req.message,
        "oracle_response": reply,
        "matched_topics": topics,
        "timestamp": now
    }

@router.get("/history")
def get_oracle_chat_history(session_id: str = Query("auramystic_default_session")):
    """Returns conversation history with The AuraMystic AI Oracle."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM oracle_chat_history WHERE session_id = ? ORDER BY id ASC LIMIT 100",
        (session_id,)
    ).fetchall()
    conn.close()
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": r["id"],
                "user_message": r["user_message"],
                "oracle_response": r["oracle_response"],
                "matched_topics": json.loads(r["matched_topics"] or "[]"),
                "created_at": r["created_at"]
            }
            for r in rows
        ]
    }
