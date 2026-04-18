-- Ramsees conversation log
-- Every turn through the command-center gateway is persisted here.

CREATE TABLE IF NOT EXISTS ramsees_conversations (
    id          UUID PRIMARY KEY,
    ts          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    channel     TEXT NOT NULL CHECK (channel IN ('chat', 'retell', 'embark', 'manual', 'system')),
    role        TEXT NOT NULL CHECK (role IN ('user', 'ramsees', 'system')),
    text        TEXT NOT NULL,
    meta        JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_ramsees_conv_ts       ON ramsees_conversations (ts DESC);
CREATE INDEX IF NOT EXISTS idx_ramsees_conv_channel  ON ramsees_conversations (channel, ts DESC);
CREATE INDEX IF NOT EXISTS idx_ramsees_conv_meta_gin ON ramsees_conversations USING gin (meta);

-- Retell-specific view: one row per call with latest assistant summary
CREATE OR REPLACE VIEW retell_calls AS
SELECT
    meta->>'call_id'                            AS call_id,
    MIN(ts)                                     AS started_at,
    MAX(ts)                                     AS last_seen_at,
    MAX(meta->>'caller')                        AS caller,
    MAX(CASE WHEN role = 'user'    THEN text END) AS transcript,
    MAX(CASE WHEN role = 'ramsees' THEN text END) AS ramsees_summary
FROM ramsees_conversations
WHERE channel = 'retell' AND meta ? 'call_id'
GROUP BY meta->>'call_id';
