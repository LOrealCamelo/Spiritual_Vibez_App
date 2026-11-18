-- Additive paid-plan metadata. Existing requests retain their monthly terms.
ALTER TABLE payments ADD COLUMN IF NOT EXISTS plan TEXT NOT NULL DEFAULT 'month';
ALTER TABLE payments ADD COLUMN IF NOT EXISTS price_cents BIGINT NOT NULL DEFAULT 599;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS verified_amount_cents BIGINT;
