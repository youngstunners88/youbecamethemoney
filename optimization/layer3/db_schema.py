"""
Database schema for Layer 3 insights storage.

Uses SQLite for:
- Call records
- Lead outcomes
- Learned patterns
- Improvement logs
"""

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS call_records (
  id TEXT PRIMARY KEY,
  lead_id TEXT NOT NULL,
  timestamp DATETIME NOT NULL,
  duration_seconds INTEGER,
  lead_temperature VARCHAR(10),
  lead_source VARCHAR(20),
  service_type VARCHAR(50),
  transcript TEXT,
  outcome VARCHAR(20),
  agent_sentiment_score REAL,
  prospect_sentiment_score REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lead_outcomes (
  id TEXT PRIMARY KEY,
  lead_id TEXT NOT NULL,
  lead_temp_at_call VARCHAR(10),
  status_before VARCHAR(20),
  status_after VARCHAR(20),
  case_value DECIMAL(10,2),
  days_to_close INTEGER,
  service_type VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learned_patterns (
  id TEXT PRIMARY KEY,
  module VARCHAR(30) NOT NULL,
  pattern_type VARCHAR(50),
  pattern_data TEXT,
  confidence REAL,
  samples_count INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME
);

CREATE TABLE IF NOT EXISTS improvement_log (
  id TEXT PRIMARY KEY,
  week_number INTEGER,
  module VARCHAR(30),
  insight TEXT,
  action_taken TEXT,
  impact_metric REAL,
  impact_confirmed BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cache (
  key TEXT PRIMARY KEY,
  value TEXT,
  expires_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_call_records_lead_id ON call_records(lead_id);
CREATE INDEX IF NOT EXISTS idx_call_records_timestamp ON call_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_call_records_outcome ON call_records(outcome);
CREATE INDEX IF NOT EXISTS idx_lead_outcomes_lead_id ON lead_outcomes(lead_id);
CREATE INDEX IF NOT EXISTS idx_learned_patterns_module ON learned_patterns(module);
CREATE INDEX IF NOT EXISTS idx_improvement_log_week ON improvement_log(week_number);
"""

# SQL to create tables
def init_database(db_path):
    """Initialize database with schema."""
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute all statements in schema
    for statement in DB_SCHEMA.split(';'):
        if statement.strip():
            cursor.execute(statement)

    conn.commit()
    conn.close()
