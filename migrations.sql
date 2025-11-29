CREATE TABLE IF NOT EXISTS short_term_messages (
    id SERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    kind TEXT NOT NULL,
    meta JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS episodic_events (
    id SERIAL PRIMARY KEY,
    episode_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    kind TEXT NOT NULL,
    content TEXT NOT NULL,
    meta JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS long_term_knowledge (
    id SERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    category TEXT NOT NULL,   -- rule, mapping, style
    content TEXT NOT NULL,
    meta JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pending_corrections (
    id SERIAL PRIMARY KEY,
    user_role TEXT NOT NULL,
    correction JSONB NOT NULL,
    status TEXT DEFAULT 'pending',
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
