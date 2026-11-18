-- Additive PostgreSQL schema, version 1. Applied within the app-owned namespace.
CREATE TABLE IF NOT EXISTS shadow_journal_entries (
            id BIGSERIAL PRIMARY KEY,
            prompt TEXT NOT NULL,
            entry_text TEXT NOT NULL,
            moon_phase TEXT DEFAULT 'Waxing Gibbous in Pisces',
            tags TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        );
CREATE TABLE IF NOT EXISTS saved_tarot_readings (
            id BIGSERIAL PRIMARY KEY,
            spread_id TEXT NOT NULL,
            spread_title TEXT NOT NULL,
            category TEXT NOT NULL,
            cards_json TEXT NOT NULL,
            synthesis TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
CREATE TABLE IF NOT EXISTS cycle_tracking_logs (
            id BIGSERIAL PRIMARY KEY,
            last_period_date TEXT NOT NULL,
            cycle_length BIGINT NOT NULL,
            current_day BIGINT NOT NULL,
            phase_name TEXT NOT NULL,
            inner_season TEXT NOT NULL,
            moon_archetype TEXT NOT NULL,
            next_period_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
CREATE TABLE IF NOT EXISTS ritual_completions (
            id BIGSERIAL PRIMARY KEY,
            ritual_id TEXT NOT NULL,
            ritual_title TEXT NOT NULL,
            category TEXT NOT NULL,
            intention_notes TEXT DEFAULT '',
            completed_at TEXT NOT NULL
        );
CREATE TABLE IF NOT EXISTS study_quiz_progress (
            user_id TEXT PRIMARY KEY,
            cards_studied BIGINT DEFAULT 0,
            correct_answers BIGINT DEFAULT 0,
            current_streak BIGINT DEFAULT 0,
            best_streak BIGINT DEFAULT 0,
            mastered_card_ids TEXT DEFAULT '[]',
            updated_at TEXT NOT NULL
        );
CREATE TABLE IF NOT EXISTS oracle_chat_history (
            id BIGSERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            oracle_response TEXT NOT NULL,
            matched_topics TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        );
CREATE TABLE IF NOT EXISTS store_cart_items (
            id BIGSERIAL PRIMARY KEY,
            session_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            product_title TEXT NOT NULL,
            unit_price REAL NOT NULL,
            quantity BIGINT NOT NULL DEFAULT 1,
            added_at TEXT NOT NULL
        );
