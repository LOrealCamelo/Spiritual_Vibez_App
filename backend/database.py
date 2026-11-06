"""
AuraMystic Production SQLite Persistence Layer
Manages all user data: Shadow Work journal entries, saved Tarot spread readings,
Lunar Menstrual Cycle logs, Ritual completions, Study Quiz streaks, AI Oracle chat history,
and NeuroSpicy Mystic Storefront shopping bag sessions.
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.environ.get(
    "AURAMYSTIC_DB_PATH",
    os.path.join(os.path.dirname(__file__), "data", "auramystic.db")
)

_ACTIVE_DB_PATH: Optional[str] = None

def get_connection() -> sqlite3.Connection:
    global _ACTIVE_DB_PATH
    if _ACTIVE_DB_PATH is None:
        try:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            test_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            test_conn.execute("CREATE TABLE IF NOT EXISTS _lock_check (id INT)")
            test_conn.close()
            _ACTIVE_DB_PATH = DB_PATH
        except sqlite3.OperationalError:
            _ACTIVE_DB_PATH = "/tmp/auramystic.db"
    conn = sqlite3.connect(_ACTIVE_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS shadow_journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            entry_text TEXT NOT NULL,
            moon_phase TEXT DEFAULT 'Waxing Gibbous in Pisces',
            tags TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_tarot_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spread_id TEXT NOT NULL,
            spread_title TEXT NOT NULL,
            category TEXT NOT NULL,
            cards_json TEXT NOT NULL,
            synthesis TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cycle_tracking_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_period_date TEXT NOT NULL,
            cycle_length INTEGER NOT NULL,
            current_day INTEGER NOT NULL,
            phase_name TEXT NOT NULL,
            inner_season TEXT NOT NULL,
            moon_archetype TEXT NOT NULL,
            next_period_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ritual_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ritual_id TEXT NOT NULL,
            ritual_title TEXT NOT NULL,
            category TEXT NOT NULL,
            intention_notes TEXT DEFAULT '',
            completed_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_quiz_progress (
            user_id TEXT PRIMARY KEY,
            cards_studied INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            mastered_card_ids TEXT DEFAULT '[]',
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS oracle_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            oracle_response TEXT NOT NULL,
            matched_topics TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS store_cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_title TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            added_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# Initialize tables on module load
init_db()
