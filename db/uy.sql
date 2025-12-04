ALTER TABLE long_term_knowledge
ALTER COLUMN content TYPE JSONB
USING to_jsonb(content);
ALTER TABLE episodic_events
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE episodic_events
ALTER COLUMN content TYPE JSONB
USING to_jsonb(content);
