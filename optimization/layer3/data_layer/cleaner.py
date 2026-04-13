"""
Data Cleaner: Formats messy data for analysis.
"""

from typing import List
import logging

logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and normalize call and outcome data."""

    def clean_calls(self, calls: List[dict]) -> List[dict]:
        """Normalize call records."""
        cleaned = []

        for call in calls:
            try:
                cleaned_call = {
                    "id": call.get("id", "unknown"),
                    "lead_id": call.get("lead_id", "unknown"),
                    "timestamp": call.get("timestamp", ""),
                    "duration_seconds": int(call.get("duration_seconds", 0)),
                    "lead_temperature": self._normalize_temp(call.get("lead_temperature", "luke")),
                    "lead_source": self._normalize_source(call.get("lead_source", "unknown")),
                    "service_type": call.get("service_type", "Unknown"),
                    "transcript": call.get("transcript", ""),
                    "outcome": self._normalize_outcome(call.get("outcome", "failed")),
                    "agent_sentiment_score": self._clamp_score(call.get("agent_sentiment_score", 0.5)),
                    "prospect_sentiment_score": self._clamp_score(call.get("prospect_sentiment_score", 0.5)),
                }

                # Skip calls with missing critical data
                if cleaned_call["timestamp"] and cleaned_call["lead_id"]:
                    cleaned.append(cleaned_call)

            except Exception as e:
                logger.warning(f"Skipped invalid call: {e}")
                continue

        logger.info(f"Cleaned {len(cleaned)}/{len(calls)} calls")
        return cleaned

    def clean_outcomes(self, outcomes: List[dict]) -> List[dict]:
        """Normalize outcome records."""
        cleaned = []

        for outcome in outcomes:
            try:
                cleaned_outcome = {
                    "lead_id": outcome.get("lead_id", "unknown"),
                    "lead_temp_at_call": self._normalize_temp(outcome.get("lead_temp_at_call", "luke")),
                    "status_before": outcome.get("status_before", "unknown"),
                    "status_after": outcome.get("status_after", "unknown"),
                    "case_value": float(outcome.get("case_value", 0)),
                    "days_to_close": int(outcome.get("days_to_close", 0)),
                    "service_type": outcome.get("service_type", "Unknown"),
                    "created_at": outcome.get("created_at", ""),
                }

                if cleaned_outcome["lead_id"]:
                    cleaned.append(cleaned_outcome)

            except Exception as e:
                logger.warning(f"Skipped invalid outcome: {e}")
                continue

        logger.info(f"Cleaned {len(cleaned)}/{len(outcomes)} outcomes")
        return cleaned

    @staticmethod
    def _normalize_temp(temp: str) -> str:
        """Normalize temperature to valid values."""
        temp = str(temp).lower().strip()
        if temp in ["hot", "warm", "luke", "cold"]:
            return temp
        elif temp in ["very hot", "excellent"]:
            return "hot"
        elif temp in ["maybe", "lukewarm"]:
            return "luke"
        else:
            return "luke"

    @staticmethod
    def _normalize_source(source: str) -> str:
        """Normalize lead source."""
        source = str(source).lower().strip()
        valid = ["web", "sms", "telegram", "discord", "organic"]
        if source in valid:
            return source
        else:
            return "unknown"

    @staticmethod
    def _normalize_outcome(outcome: str) -> str:
        """Normalize call outcome."""
        outcome = str(outcome).lower().strip()
        if outcome in ["completed", "success", "answered"]:
            return "completed"
        elif outcome in ["failed", "no_answer", "unanswered"]:
            return "failed"
        else:
            return "unknown"

    @staticmethod
    def _clamp_score(score) -> float:
        """Clamp sentiment scores to 0-1."""
        try:
            s = float(score)
            return max(0.0, min(1.0, s))
        except:
            return 0.5
