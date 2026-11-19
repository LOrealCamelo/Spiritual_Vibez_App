-- Additive PostgreSQL schema, version 1. Applied within the app-owned namespace.
CREATE TABLE IF NOT EXISTS members(id BIGSERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL, admin BIGINT NOT NULL DEFAULT 0, expires BIGINT NOT NULL DEFAULT 0,
          lifetime BIGINT NOT NULL DEFAULT 0, disabled BIGINT NOT NULL DEFAULT 0, created BIGINT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(hash TEXT PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES members(id), expires BIGINT NOT NULL);
        CREATE TABLE IF NOT EXISTS resets(hash TEXT PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES members(id), expires BIGINT NOT NULL);
        CREATE TABLE IF NOT EXISTS payments(id BIGSERIAL PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES members(id),
          provider TEXT NOT NULL, reference TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created BIGINT NOT NULL,
          reviewed BIGINT, reviewer BIGINT REFERENCES members(id), note TEXT NOT NULL DEFAULT '', verified_reference TEXT, UNIQUE(provider, reference));
        CREATE UNIQUE INDEX IF NOT EXISTS unique_verified_receipt ON payments(provider,verified_reference) WHERE status='approved';
        CREATE UNIQUE INDEX IF NOT EXISTS one_pending_payment ON payments(user_id) WHERE status='pending';
        CREATE TABLE IF NOT EXISTS gifts(hash TEXT PRIMARY KEY, kind TEXT NOT NULL, created BIGINT NOT NULL,
          created_by BIGINT NOT NULL REFERENCES members(id), expires BIGINT NOT NULL, redeemed_by BIGINT REFERENCES members(id),
          redeemed BIGINT, revoked BIGINT NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS audit(id BIGSERIAL PRIMARY KEY, actor BIGINT, action TEXT NOT NULL,
          target TEXT NOT NULL, created BIGINT NOT NULL);
        CREATE TABLE IF NOT EXISTS paypal_checkouts(hash TEXT PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES members(id),
          created BIGINT NOT NULL, subscription TEXT);
        CREATE TABLE IF NOT EXISTS paypal_subscriptions(id TEXT PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES members(id),
          signup BIGINT NOT NULL DEFAULT 0, trial_until BIGINT NOT NULL DEFAULT 0, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS paypal_receipts(txn TEXT PRIMARY KEY, subscription TEXT NOT NULL REFERENCES paypal_subscriptions(id),
          paid BIGINT NOT NULL, expires BIGINT NOT NULL, refunded BIGINT NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS limits(key TEXT PRIMARY KEY, started BIGINT NOT NULL, count BIGINT NOT NULL);
