-- Migration 002: skills_audit table
-- Logs every FastMCP skill execution for debugging and compliance

CREATE TABLE IF NOT EXISTS skills_audit (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_name    VARCHAR(100) NOT NULL,
  lead_id       UUID,
  interview_id  UUID,
  input_payload JSONB NOT NULL DEFAULT '{}',
  output_payload JSONB NOT NULL DEFAULT '{}',
  success       BOOLEAN NOT NULL DEFAULT TRUE,
  error_message TEXT,
  duration_ms   INTEGER,
  executed_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_skills_audit_skill ON skills_audit(skill_name);
CREATE INDEX IF NOT EXISTS idx_skills_audit_lead  ON skills_audit(lead_id);
CREATE INDEX IF NOT EXISTS idx_skills_audit_time  ON skills_audit(executed_at DESC);
