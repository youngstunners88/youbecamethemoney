"""Persistent storage for learned patterns."""

import sqlite3
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class InsightsDB:
    """Store and retrieve learned patterns."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def store_improvement(self, week: int, insights: list, impact: float) -> bool:
        """Log weekly improvement to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO improvement_log 
                (week_number, cycle_date, insights_count, expected_improvement, created_at)
                VALUES (?, datetime('now'), ?, ?, datetime('now'))
            """, (week, len(insights), impact))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error storing improvement: {e}")
            return False

    def get_learned_pattern(self, module_name: str, pattern_type: str) -> Optional[Dict]:
        """Retrieve previously learned pattern."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT pattern_data, confidence
                FROM learned_patterns
                WHERE module_name = ? AND pattern_type = ?
                ORDER BY created_at DESC LIMIT 1
            """, (module_name, pattern_type))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    "data": json.loads(result[0]),
                    "confidence": result[1]
                }
            return None
        except Exception as e:
            logger.error(f"Error retrieving pattern: {e}")
            return None

    def store_pattern(self, module_name: str, pattern_type: str, 
                     data: Dict, confidence: float, samples: int) -> bool:
        """Persist newly learned pattern."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO learned_patterns
                (module_name, pattern_type, pattern_data, confidence, samples_used, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (module_name, pattern_type, json.dumps(data), confidence, samples))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error storing pattern: {e}")
            return False

    def get_improvement_history(self, weeks: int = 8) -> list:
        """Get improvement history for trending."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT week_number, expected_improvement, created_at
                FROM improvement_log
                ORDER BY week_number DESC
                LIMIT ?
            """, (weeks,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    "week": r[0],
                    "improvement": r[1],
                    "date": r[2]
                } for r in results
            ]
        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return []
