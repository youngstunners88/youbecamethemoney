"""Data collection from Retell API and PostgreSQL."""

import requests
import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CallRecord:
    call_id: str
    timestamp: str
    duration_seconds: int
    temperature: str
    source: str
    service_type: str
    transcript: str
    outcome: str
    sentiment_score: float

class DataCollector:
    def __init__(self, retell_api_key: str, retell_base: str, use_mock: bool = False):
        self.api_key = retell_api_key
        self.base_url = retell_base
        self.use_mock = use_mock

    def fetch_calls(self, days: int = 7) -> List[CallRecord]:
        """Fetch call records from Retell API."""
        if self.use_mock:
            return self._generate_mock_calls(days)

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {"days": days, "limit": 500}
            response = requests.get(
                f"{self.base_url}/calls",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            calls = []
            for call_data in response.json().get("calls", []):
                calls.append(CallRecord(
                    call_id=call_data.get("call_id"),
                    timestamp=call_data.get("timestamp"),
                    duration_seconds=call_data.get("duration_seconds", 0),
                    temperature=call_data.get("temperature", "luke"),
                    source=call_data.get("source", "web"),
                    service_type=call_data.get("service_type", "inquiry"),
                    transcript=call_data.get("transcript", ""),
                    outcome=call_data.get("outcome", "pending"),
                    sentiment_score=call_data.get("sentiment_score", 0.5)
                ))
            return calls
        except Exception as e:
            logger.error(f"Error fetching calls: {e}. Using mock data.")
            return self._generate_mock_calls(days)

    def fetch_outcomes(self, days: int = 7) -> List[Dict]:
        """Fetch lead outcomes from PostgreSQL."""
        if self.use_mock:
            return self._generate_mock_outcomes(days)

        try:
            import psycopg2
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cursor = conn.cursor()

            query = """
            SELECT lead_id, status, case_value, days_to_close
            FROM cases
            WHERE created_at > NOW() - INTERVAL '%d days'
            """ % days

            cursor.execute(query)
            outcomes = []
            for row in cursor.fetchall():
                outcomes.append({
                    "lead_id": row[0],
                    "status": row[1],
                    "case_value": row[2],
                    "days_to_close": row[3]
                })
            cursor.close()
            conn.close()
            return outcomes
        except Exception as e:
            logger.error(f"Error fetching outcomes: {e}. Using mock data.")
            return self._generate_mock_outcomes(days)

    def _generate_mock_calls(self, days: int) -> List[CallRecord]:
        """Generate mock call data for testing."""
        import random
        calls = []
        base_time = datetime.utcnow() - timedelta(days=days)

        temperatures = ["hot", "warm", "luke", "cold"]
        sources = ["web", "sms", "telegram", "discord", "organic"]
        service_types = ["inquiry", "consultation", "follow_up", "closing"]
        outcomes = ["completed", "failed", "pending"]

        for i in range(147):
            call_time = base_time + timedelta(
                hours=random.randint(0, days*24),
                minutes=random.randint(0, 59)
            )
            calls.append(CallRecord(
                call_id=f"call_{i:04d}",
                timestamp=call_time.isoformat(),
                duration_seconds=random.randint(120, 1200),
                temperature=random.choice(temperatures),
                source=random.choice(sources),
                service_type=random.choice(service_types),
                transcript=f"Mock transcript {i}",
                outcome=random.choice(outcomes),
                sentiment_score=random.uniform(0.2, 0.95)
            ))
        return calls

    def _generate_mock_outcomes(self, days: int) -> List[Dict]:
        """Generate mock outcome data for testing."""
        import random
        outcomes = []
        for i in range(32):
            outcomes.append({
                "lead_id": f"lead_{i:04d}",
                "status": random.choice(["closed_won", "closed_lost", "in_progress"]),
                "case_value": random.choice([0, 3200, 6400, 9600, 12800]),
                "days_to_close": random.randint(1, 60)
            })
        return outcomes
