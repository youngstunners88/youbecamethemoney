-- ============================================================
-- Migration 001: Client Interviews + Behavior Profiling
-- Date: 2026-04-14
-- Purpose: Lemonslice interview portal data layer
-- ============================================================

-- New table: client_interviews
CREATE TABLE IF NOT EXISTS client_interviews (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id               UUID REFERENCES leads(id) ON DELETE CASCADE,
  lemonslice_video_url  TEXT,
  interview_transcript  TEXT,

  -- Behavioral signals (0–100 unless noted)
  tone_confidence       FLOAT CHECK (tone_confidence BETWEEN 0 AND 100),
  tone_urgency          FLOAT CHECK (tone_urgency BETWEEN 0 AND 100),
  knowledge_level       INT   CHECK (knowledge_level BETWEEN 1 AND 10),
  hesitation_score      FLOAT CHECK (hesitation_score BETWEEN 0 AND 100),

  -- Extracted answers
  stated_urgency        VARCHAR(20)  CHECK (stated_urgency IN ('immediate','week','month','unknown')),
  stated_amount         INT,
  stated_jurisdiction   VARCHAR(50),

  -- Hermes analysis output
  behavior_profile      JSONB DEFAULT '{}',
  warmth_delta          FLOAT DEFAULT 0,   -- +/- applied to lead warmth_score
  analyzed_at           TIMESTAMP,
  analyzed_by           VARCHAR(50) DEFAULT 'hermes',

  created_at            TIMESTAMP DEFAULT NOW()
);

-- Add columns to leads table
ALTER TABLE leads
  ADD COLUMN IF NOT EXISTS interview_id       UUID REFERENCES client_interviews(id),
  ADD COLUMN IF NOT EXISTS hall_of_fame       BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS behavior_profile   JSONB DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS warmth_score       FLOAT DEFAULT 50;

-- Hall of Fame profiles table
CREATE TABLE IF NOT EXISTS hall_of_fame_profiles (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id         UUID REFERENCES leads(id),
  interview_id    UUID REFERENCES client_interviews(id),
  case_outcome    VARCHAR(20),           -- 'won', 'settled', 'referred'
  case_value      INT,
  key_quotes      JSONB DEFAULT '[]',    -- extracted interview quotes
  testimonial     TEXT,                 -- generated testimonial
  published       BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_interviews_lead_id    ON client_interviews(lead_id);
CREATE INDEX IF NOT EXISTS idx_interviews_created    ON client_interviews(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_interviews_urgency    ON client_interviews(stated_urgency);
CREATE INDEX IF NOT EXISTS idx_leads_hall_of_fame    ON leads(hall_of_fame) WHERE hall_of_fame = TRUE;
CREATE INDEX IF NOT EXISTS idx_leads_warmth          ON leads(warmth_score DESC);
CREATE INDEX IF NOT EXISTS idx_hof_published         ON hall_of_fame_profiles(published) WHERE published = TRUE;

-- View: enriched leads with interview data
CREATE OR REPLACE VIEW leads_enriched AS
SELECT
  l.*,
  ci.tone_confidence,
  ci.tone_urgency,
  ci.knowledge_level,
  ci.hesitation_score,
  ci.stated_urgency,
  ci.stated_amount,
  ci.stated_jurisdiction,
  ci.behavior_profile      AS interview_profile,
  ci.analyzed_at           AS interview_analyzed_at,
  hof.testimonial,
  hof.key_quotes
FROM leads l
LEFT JOIN client_interviews ci ON l.interview_id = ci.id
LEFT JOIN hall_of_fame_profiles hof ON hof.lead_id = l.id AND hof.published = TRUE;

COMMENT ON TABLE client_interviews   IS 'Lemonslice video interview records with behavioral analysis';
COMMENT ON TABLE hall_of_fame_profiles IS 'Published success stories from closed cases';
COMMENT ON VIEW  leads_enriched      IS 'Leads joined with interview and hall-of-fame data for dashboard';
