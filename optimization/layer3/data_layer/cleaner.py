"""Data cleaning and normalization."""

import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class DataCleaner:
    """Normalize and validate data from collectors."""

    VALID_TEMPERATURES = ["hot", "warm", "luke", "cold"]
    VALID_SOURCES = ["web", "sms", "telegram", "discord", "organic"]
    VALID_OUTCOMES = ["completed", "failed", "pending"]

    def clean_calls(self, calls: List) -> Tuple[List[Dict], int]:
        """Clean and normalize call records."""
        cleaned = []
        errors = 0

        for call in calls:
            try:
                cleaned_call = {
                    "call_id": str(call.call_id),
                    "timestamp": str(call.timestamp),
                    "duration_seconds": max(0, int(call.duration_seconds or 0)),
                    "temperature": self._normalize_temperature(call.temperature),
                    "source": self._normalize_source(call.source),
                    "service_type": str(call.service_type or "inquiry").lower(),
                    "transcript": str(call.transcript or ""),
                    "outcome": self._normalize_outcome(call.outcome),
                    "sentiment_score": self._clamp_sentiment(float(call.sentiment_score or 0.5))
                }
                cleaned.append(cleaned_call)
            except Exception as e:
                logger.warning(f"Error cleaning call {call}: {e}")
                errors += 1

        logger.info(f"Cleaned {len(cleaned)} calls, {errors} errors")
        return cleaned, errors

    def clean_outcomes(self, outcomes: List[Dict]) -> Tuple[List[Dict], int]:
        """Clean and normalize outcome records."""
        cleaned = []
        errors = 0

        for outcome in outcomes:
            try:
                cleaned_outcome = {
                    "lead_id": str(outcome.get("lead_id", "")),
                    "status": str(outcome.get("status", "in_progress")).lower(),
                    "case_value": max(0, float(outcome.get("case_value", 0))),
                    "days_to_close": max(0, int(outcome.get("days_to_close", 0)))
                }
                cleaned.append(cleaned_outcome)
            except Exception as e:
                logger.warning(f"Error cleaning outcome {outcome}: {e}")
                errors += 1

        logger.info(f"Cleaned {len(cleaned)} outcomes, {errors} errors")
        return cleaned, errors

    def _normalize_temperature(self, temp: str) -> str:
        """Normalize temperature to valid values."""
        if not temp:
            return "luke"
        temp_lower = str(temp).lower()
        return temp_lower if temp_lower in self.VALID_TEMPERATURES else "luke"

    def _normalize_source(self, source: str) -> str:
        """Normalize source to valid values."""
        if not source:
            return "web"
        source_lower = str(source).lower()
        return source_lower if source_lower in self.VALID_SOURCES else "organic"

    def _normalize_outcome(self, outcome: str) -> str:
        """Normalize outcome to valid values."""
        if not outcome:
            return "pending"
        outcome_lower = str(outcome).lower()
        return outcome_lower if outcome_lower in self.VALID_OUTCOMES else "pending"

    def _clamp_sentiment(self, score: float) -> float:
        """Clamp sentiment score to 0-1 range."""
        return max(0.0, min(1.0, float(score)))
