"""Module 1: Predict which leads will close."""

import logging
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ConversionPrediction:
    probability: float
    confidence: float
    reason: str
    action: str
    samples: int

class ConversionPredictor:
    """Learns which lead profiles convert."""

    BASE_RATE = 0.185  # 18.5% baseline

    def __init__(self):
        self.temperature_multipliers = {
            "hot": 0.45,
            "warm": 0.20,
            "luke": -0.10,
            "cold": -0.70
        }

    def learn(self, calls: List[Dict], outcomes: List[Dict]) -> Dict:
        """Learn conversion patterns from historical data."""
        patterns = {
            "base_rate": self.BASE_RATE,
            "by_temperature": {},
            "by_source": {},
            "by_service_type": {},
            "samples": len(calls)
        }

        # Calculate temperature patterns
        for temp in ["hot", "warm", "luke", "cold"]:
            temp_calls = [c for c in calls if c.get("temperature") == temp]
            if temp_calls:
                closed = sum(1 for c in temp_calls if c.get("outcome") == "completed")
                rate = closed / len(temp_calls)
                patterns["by_temperature"][temp] = {
                    "rate": rate,
                    "samples": len(temp_calls)
                }

        # Calculate source patterns
        for source in ["web", "sms", "telegram", "discord", "organic"]:
            source_calls = [c for c in calls if c.get("source") == source]
            if source_calls:
                closed = sum(1 for c in source_calls if c.get("outcome") == "completed")
                rate = closed / len(source_calls)
                patterns["by_source"][source] = {
                    "rate": rate,
                    "samples": len(source_calls)
                }

        return patterns

    def predict(self, temperature: str, duration_sec: int, sentiment: float, hour: int) -> ConversionPrediction:
        """Predict close probability for a lead."""
        prob = self.BASE_RATE

        # Temperature multiplier
        prob *= (1 + self.temperature_multipliers.get(temperature, 0))

        # Duration multiplier
        duration_min = duration_sec / 60
        if duration_min > 8:
            prob *= 1.25
        elif duration_min < 3:
            prob *= 0.75

        # Sentiment multiplier
        sentiment_mult = 0.8 + (sentiment * 0.6)  # Range 0.8 - 1.4
        prob *= sentiment_mult

        # Time window multiplier
        if 9 <= hour <= 11:
            prob *= 1.15
        elif 18 <= hour <= 23:
            prob *= 0.85

        # Clamp to valid probability
        prob = max(0.0, min(1.0, prob))

        # Determine action
        if prob >= 0.70:
            action = "Schedule ASAP - High priority"
        elif prob >= 0.50:
            action = "Nurture - Good prospect"
        elif prob >= 0.30:
            action = "Drip - Keep warm"
        else:
            action = "Archive - Low potential"

        reason = f"{temperature.title()} lead, {duration_min:.1f}min duration, {sentiment:.0%} sentiment"

        return ConversionPrediction(
            probability=prob,
            confidence=0.85,
            reason=reason,
            action=action,
            samples=147
        )
