-- Preserve historical references and receipts; new customers identify their sender handle.
ALTER TABLE payments ADD COLUMN IF NOT EXISTS sender_handle TEXT NOT NULL DEFAULT '';
