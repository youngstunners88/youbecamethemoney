"""
Data Collector: Pulls data from Retell API and PostgreSQL.

IMPORTANT: Runs once per week only to minimize API calls.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List
import logging

logger = logging.getLogger(__name__)


class DataCollector:
    """Fetch call and outcome data from production systems."""

    def __init__(self):
        self.retell_api_key = os.getenv("RETELL_API_KEY")
        self.pg_url = os.getenv("DATABASE_URL")

    def fetch_calls(self, days: int = 7) -> List[dict]:
        """
        Fetch call records from Retell API.

        ONE API CALL per week (all 7 days in one request).
        """
        if not self.retell_api_key:
            logger.warning("RETELL_API_KEY not set, returning mock data")
            return self._mock_calls()

        try:
            # Fetch last N days of calls
            start_date = (datetime.now() - timedelta(days=days)).isoformat()

            response = requests.get(
                "https://api.retellai.com/v2/calls",
                headers={"Authorization": f"Bearer {self.retell_api_key}"},
                params={
                    "start_date": start_date,
                    "limit": 500,
                },
                timeout=30,
            )

            if response.status_code == 200:
                calls = response.json().get("calls", [])
                logger.info(f"✅ Fetched {len(calls)} calls from Retell")
                return calls
            else:
                logger.error(f"Retell API error: {response.status_code}")
                return self._mock_calls()

        except Exception as e:
            logger.error(f"Error fetching calls: {e}")
            return self._mock_calls()

    def fetch_outcomes(self, days: int = 7) -> List[dict]:
        """
        Fetch lead outcome data from PostgreSQL.

        ONE QUERY per week.
        """
        if not self.pg_url:
            logger.warning("DATABASE_URL not set, returning mock data")
            return self._mock_outcomes()

        try:
            import psycopg2

            conn = psycopg2.connect(self.pg_url)
            cursor = conn.cursor()

            # Query: leads that have outcomes in last N days
            query = """
            SELECT
                l.id as lead_id,
                l.lead_temperature,
                l.status as status_before,
                c.status_after,
                c.case_value,
                c.days_to_close,
                c.service_type,
                c.created_at
            FROM cases c
            JOIN leads l ON c.lead_id = l.id
            WHERE c.created_at >= NOW() - INTERVAL '%d days'
            ORDER BY c.created_at DESC
            """ % days

            cursor.execute(query)
            outcomes = [
                {
                    "lead_id": row[0],
                    "lead_temp_at_call": row[1],
                    "status_before": row[2],
                    "status_after": row[3],
                    "case_value": row[4],
                    "days_to_close": row[5],
                    "service_type": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                }
                for row in cursor.fetchall()
            ]

            cursor.close()
            conn.close()

            logger.info(f"✅ Fetched {len(outcomes)} outcomes from PostgreSQL")
            return outcomes

        except Exception as e:
            logger.error(f"Error fetching outcomes: {e}")
            return self._mock_outcomes()

    def _mock_calls(self) -> List[dict]:
        """Mock call data for testing."""
        return [
            {
                "id": "call_1",
                "lead_id": "lead_001",
                "timestamp": "2026-04-07T09:30:00Z",
                "duration_seconds": 540,
                "lead_temperature": "hot",
                "lead_source": "web",
                "service_type": "UCC Discharge",
                "transcript": "What's your current situation? The force of nature is with you. Let me show you...",
                "outcome": "completed",
                "agent_sentiment_score": 0.85,
                "prospect_sentiment_score": 0.82,
            },
        ]

    def _mock_outcomes(self) -> List[dict]:
        """Mock outcome data for testing."""
        return [
            {
                "lead_id": "lead_001",
                "lead_temp_at_call": "hot",
                "status_before": "new",
                "status_after": "retained",
                "case_value": 3200,
                "days_to_close": 2,
                "service_type": "UCC Discharge",
                "created_at": "2026-04-09T00:00:00",
            },
        ]
