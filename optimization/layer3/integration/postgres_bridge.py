"""
PostgreSQL Bridge for Layer 3 Learning Engine
Replaces SQLite, connects to real Garcia-Ramsees database
Enables learning from real leads, cases, and outcomes
"""

import psycopg2
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

log = logging.getLogger(__name__)

class PostgresBridge:
    """Bridge between Layer 3 and Garcia's PostgreSQL database."""

    def __init__(self, host: str, dbname: str, user: str, password: str = None, port: int = 5432):
        """
        Connect to PostgreSQL database.

        Args:
            host: Database host (e.g., localhost, zo.garcia-ramsees.local)
            dbname: Database name (e.g., garcia_ramsees)
            user: PostgreSQL user
            password: Optional password
            port: PostgreSQL port (default 5432)
        """
        self.host = host
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.conn = None
        self._connect()

    def _connect(self):
        """Establish PostgreSQL connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.dbname,
                user=self.user,
                password=self.password,
                port=self.port
            )
            log.info(f"✅ Connected to PostgreSQL: {self.host}/{self.dbname}")
        except Exception as e:
            log.error(f"❌ Failed to connect to PostgreSQL: {e}")
            raise

    def fetch_recent_calls(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch recent call records from interaction_logs table.

        Returns leads that came in last N days.
        """
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT
                    id,
                    timestamp,
                    platform,
                    message,
                    lead_id,
                    sentiment_score
                FROM interaction_logs
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                ORDER BY timestamp DESC
            """
            cursor.execute(query % days)
            rows = cursor.fetchall()

            calls = []
            for row in rows:
                calls.append({
                    "id": row[0],
                    "timestamp": row[1].isoformat() if row[1] else None,
                    "platform": row[2],
                    "message": row[3],
                    "lead_id": row[4],
                    "sentiment_score": row[5],
                })

            log.info(f"✅ Fetched {len(calls)} recent calls (last {days} days)")
            return calls

        except Exception as e:
            log.error(f"❌ Error fetching calls: {e}")
            return []

    def fetch_recent_leads(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch recent leads from leads table.

        Returns leads created in last N days with their status.
        """
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    service_type,
                    warmth_score,
                    status,
                    created_at
                FROM leads
                WHERE created_at >= NOW() - INTERVAL '%s days'
                ORDER BY created_at DESC
            """
            cursor.execute(query % days)
            rows = cursor.fetchall()

            leads = []
            for row in rows:
                leads.append({
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "service_type": row[4],
                    "warmth_score": row[5],
                    "status": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                })

            log.info(f"✅ Fetched {len(leads)} recent leads (last {days} days)")
            return leads

        except Exception as e:
            log.error(f"❌ Error fetching leads: {e}")
            return []

    def fetch_closed_cases(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch closed cases for pattern learning.

        Returns cases that closed in last N days with outcomes.
        """
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT
                    id,
                    lead_id,
                    service_type,
                    case_value,
                    intake_date,
                    close_date,
                    outcome
                FROM cases
                WHERE status = 'closed' AND close_date >= NOW() - INTERVAL '%s days'
                ORDER BY close_date DESC
            """
            cursor.execute(query % days)
            rows = cursor.fetchall()

            cases = []
            for row in rows:
                cases.append({
                    "id": row[0],
                    "lead_id": row[1],
                    "service_type": row[2],
                    "case_value": float(row[3]) if row[3] else 0,
                    "intake_date": row[4].isoformat() if row[4] else None,
                    "close_date": row[5].isoformat() if row[5] else None,
                    "outcome": row[6],
                })

            log.info(f"✅ Fetched {len(cases)} closed cases (last {days} days)")
            return cases

        except Exception as e:
            log.error(f"❌ Error fetching cases: {e}")
            return []

    def store_learned_pattern(self, module_name: str, pattern_type: str, pattern_data: Dict[str, Any], confidence: float):
        """
        Store learned pattern back to database.

        This creates feedback loop: data → learn → store → learn again
        """
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO learned_patterns
                (module_name, pattern_type, pattern_data, confidence, samples_used, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            import json
            cursor.execute(
                query,
                (module_name, pattern_type, json.dumps(pattern_data), confidence, len(pattern_data))
            )
            self.conn.commit()

            log.info(f"✅ Stored pattern: {module_name}/{pattern_type} (confidence: {confidence})")

        except Exception as e:
            log.error(f"❌ Error storing pattern: {e}")
            self.conn.rollback()

    def update_lead_score(self, lead_id: str, warmth_score: int, urgency_score: int = None):
        """
        Update lead scores based on learning results.

        Called after Hermes qualifies a lead.
        """
        try:
            cursor = self.conn.cursor()
            if urgency_score is not None:
                query = """
                    UPDATE leads
                    SET warmth_score = %s, urgency_score = %s, updated_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (warmth_score, urgency_score, lead_id))
            else:
                query = """
                    UPDATE leads
                    SET warmth_score = %s, updated_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (warmth_score, lead_id))

            self.conn.commit()
            log.info(f"✅ Updated lead {lead_id} score: {warmth_score}")

        except Exception as e:
            log.error(f"❌ Error updating lead: {e}")
            self.conn.rollback()

    def log_improvement(self, improvement_data: Dict[str, Any]):
        """
        Log improvement action (for audit trail).

        Records what Hermes learned and what it improved.
        """
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO improvement_logs
                (module_name, action, improvement_data, timestamp)
                VALUES (%s, %s, %s, NOW())
            """
            import json
            cursor.execute(
                query,
                (improvement_data.get("module"), improvement_data.get("action"), json.dumps(improvement_data))
            )
            self.conn.commit()

            log.info(f"✅ Logged improvement: {improvement_data.get('action')}")

        except Exception as e:
            log.error(f"❌ Error logging improvement: {e}")
            self.conn.rollback()

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            log.info("✅ Database connection closed")
