-- Agent Reasoning & Real-Time Learning
-- Hermes brain: every decision is justified + learns from outcomes

CREATE TABLE IF NOT EXISTS agent_reasoning_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    lead_id         UUID REFERENCES leads(id) ON DELETE SET NULL,
    skill_name      TEXT NOT NULL,
    input_snapshot  JSONB NOT NULL,
    reasoning       JSONB NOT NULL,  -- { why, similar_leads, pattern_match }
    decision        TEXT NOT NULL,
    confidence      FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    recommended_action TEXT,
    metadata        JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_agent_reasoning_ts ON agent_reasoning_log (ts DESC);
CREATE INDEX IF NOT EXISTS idx_agent_reasoning_lead ON agent_reasoning_log (lead_id);
CREATE INDEX IF NOT EXISTS idx_agent_reasoning_skill ON agent_reasoning_log (skill_name, ts DESC);

-- Outcome feedback: when lead converts/opens/replies, update confidence
CREATE TABLE IF NOT EXISTS agent_feedback (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reasoning_id    UUID NOT NULL REFERENCES agent_reasoning_log(id) ON DELETE CASCADE,
    lead_id         UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    outcome_type    TEXT NOT NULL CHECK (outcome_type IN ('email_open', 'click', 'reply', 'call_answer', 'conversion', 'no_response')),
    outcome_ts      TIMESTAMPTZ NOT NULL,
    confidence_before FLOAT,
    confidence_after FLOAT,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_feedback_reasoning ON agent_feedback (reasoning_id);
CREATE INDEX IF NOT EXISTS idx_agent_feedback_lead ON agent_feedback (lead_id, outcome_ts DESC);

-- Hermes memory: cached patterns from similar leads (real-time, not weekly)
CREATE TABLE IF NOT EXISTS hermes_memory (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_type    TEXT NOT NULL,
    jurisdiction    TEXT,
    pattern_key     TEXT,  -- "ucc_ca_creditor_pressure"

    -- Pattern statistics (updated real-time, not weekly)
    sample_size     INT DEFAULT 0,
    success_count   INT DEFAULT 0,
    success_rate    FLOAT DEFAULT 0,
    avg_warmth      FLOAT,
    avg_conversion_days FLOAT,

    -- Best practices from winners
    best_questions  JSONB,  -- ["What triggered this?", "Do you hold the original?"]
    best_email_times JSONB, -- { "open_time": "2pm", "confidence": 0.95 }
    best_actions    JSONB,  -- ["email_immediate", "schedule_call"]

    -- Metadata
    last_updated    TIMESTAMPTZ DEFAULT NOW(),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB DEFAULT '{}'::jsonb
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_hermes_pattern ON hermes_memory (service_type, jurisdiction, pattern_key);
CREATE INDEX IF NOT EXISTS idx_hermes_service ON hermes_memory (service_type, success_rate DESC);

-- Real-time pattern matching: which leads match which patterns
CREATE TABLE IF NOT EXISTS lead_pattern_match (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id         UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    pattern_id      UUID NOT NULL REFERENCES hermes_memory(id) ON DELETE CASCADE,
    match_confidence FLOAT NOT NULL CHECK (match_confidence >= 0 AND match_confidence <= 100),
    matched_at      TIMESTAMPTZ DEFAULT NOW(),
    metadata        JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_lead_pattern_lead ON lead_pattern_match (lead_id);
CREATE INDEX IF NOT EXISTS idx_lead_pattern_pattern ON lead_pattern_match (pattern_id);

-- View: agent confidence timeline (for dashboard)
CREATE OR REPLACE VIEW agent_confidence_timeline AS
SELECT
    arl.lead_id,
    arl.ts,
    arl.skill_name,
    arl.decision,
    arl.confidence AS confidence_decision_time,
    COALESCE(af.confidence_after, arl.confidence) AS confidence_current,
    af.outcome_type,
    af.outcome_ts,
    CASE
        WHEN af.outcome_type IN ('conversion', 'reply', 'click') THEN 'positive'
        WHEN af.outcome_type = 'no_response' THEN 'negative'
        ELSE 'neutral'
    END AS outcome_signal
FROM agent_reasoning_log arl
LEFT JOIN agent_feedback af ON arl.id = af.reasoning_id
ORDER BY arl.ts DESC;

-- View: pattern effectiveness (which patterns convert best)
CREATE OR REPLACE VIEW pattern_effectiveness AS
SELECT
    hm.service_type,
    hm.jurisdiction,
    hm.pattern_key,
    hm.sample_size,
    hm.success_count,
    ROUND(hm.success_rate::numeric, 3) AS success_rate,
    ROUND(hm.avg_warmth::numeric, 1) AS avg_warmth,
    ROUND(hm.avg_conversion_days::numeric, 1) AS avg_days_to_convert,
    hm.best_email_times->'open_time' AS optimal_email_time,
    hm.last_updated
FROM hermes_memory hm
WHERE hm.sample_size > 0
ORDER BY hm.success_rate DESC, hm.sample_size DESC;
