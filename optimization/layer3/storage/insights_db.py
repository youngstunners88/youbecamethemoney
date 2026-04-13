"""
Insights Database: Stores learned patterns for later reuse.
"""

import sqlite3
import json
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class InsightsDB:
    """Store and retrieve learned insights."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def store_improvements(self, insights: List, impact: dict):
        """
        Store improvement outcomes.

        Called after weekly learning cycle to log what happened.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            week_number = datetime.now().isocalendar()[1]

            for insight in insights:
                cursor.execute("""
                    INSERT INTO improvement_log
                    (id, week_number, module, insight, action_taken, impact_metric, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"improvement_{week_number}_{insight.module}",
                    week_number,
                    insight.module,
                    insight.finding,
                    insight.action,
                    insight.impact_estimate,
                    datetime.now().isoformat(),
                ))

            conn.commit()
            conn.close()

            logger.info(f"✅ Stored {len(insights)} improvements to database")

        except Exception as e:
            logger.error(f"Error storing improvements: {e}")

    def get_learned_pattern(self, module: str, pattern_type: str):
        """
        Retrieve a previously learned pattern.

        Example: Get best-performing phrases from script_optimizer
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT pattern_data, confidence, samples_count
                FROM learned_patterns
                WHERE module = ? AND pattern_type = ?
                ORDER BY last_updated DESC
                LIMIT 1
            """, (module, pattern_type))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    "data": json.loads(result[0]) if result[0] else {},
                    "confidence": result[1],
                    "samples": result[2],
                }
            return None

        except Exception as e:
            logger.error(f"Error retrieving pattern: {e}")
            return None

    def store_pattern(self, module: str, pattern_type: str, pattern_data: dict, confidence: float, samples: int):
        """Store a newly learned pattern."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO learned_patterns
                (id, module, pattern_type, pattern_data, confidence, samples_count, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{module}_{pattern_type}",
                module,
                pattern_type,
                json.dumps(pattern_data),
                confidence,
                samples,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ))

            conn.commit()
            conn.close()

            logger.info(f"✅ Stored pattern: {module}/{pattern_type}")

        except Exception as e:
            logger.error(f"Error storing pattern: {e}")
