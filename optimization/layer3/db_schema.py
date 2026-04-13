"""Database schema initialization for Layer 3 insights storage."""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS call_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    duration_seconds INTEGER,
    temperature TEXT,
    source TEXT,
    service_type TEXT,
    transcript TEXT,
    outcome TEXT,
    sentiment_score REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lead_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id TEXT UNIQUE NOT NULL,
    status_before TEXT,
    status_after TEXT,
    case_value REAL,
    days_to_close INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learned_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_name TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    pattern_data TEXT NOT NULL,
    confidence REAL,
    samples_used INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    expires_at TEXT
);

CREATE TABLE IF NOT EXISTS improvement_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_number INTEGER,
    cycle_date TEXT,
    insights_count INTEGER,
    expected_improvement REAL,
    expected_improvement_reason TEXT,
    actions_deployed TEXT,
    hermes_response TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    expires_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_call_timestamp ON call_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_lead_outcome_date ON lead_outcomes(created_at);
CREATE INDEX IF NOT EXISTS idx_pattern_module ON learned_patterns(module_name);
"""

def init_database(db_path: str) -> sqlite3.Connection:
    """Initialize database with schema."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for statement in SCHEMA.split(';'):
        if statement.strip():
            cursor.execute(statement)

    conn.commit()
    logger.info(f"Database initialized at {db_path}")
    return conn

def get_connection(db_path: str) -> sqlite3.Connection:
    """Get database connection."""
    return sqlite3.connect(db_path)
