-- Fix short_term_messages structure
ALTER TABLE short_term_messages
    ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

ALTER TABLE short_term_messages
    ALTER COLUMN metadata TYPE JSONB
    USING
        CASE
            WHEN jsonb_typeof(metadata::jsonb) IS NOT NULL THEN metadata::jsonb
            ELSE to_jsonb(metadata)
        END;

-- Add created_at if missing
ALTER TABLE short_term_messages
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
