CREATE TABLE IF NOT EXISTS nlp_cache (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,
    entities JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nlp_cache_input_text
    ON nlp_cache (input_text);
