"""
Module 1: Conversion Predictor

Learns: "Which lead profiles close fastest?"

Input: Historical call + outcome data
Output: Probability that a lead will close + recommended action
"""

from dataclasses import dataclass
from typing import List, Optional
import json
from collections import defaultdict


@dataclass
class PredictionRequest:
    """Request to predict close probability"""
    lead_temperature: str          # hot, warm, luke, cold
    service_type: str              # UCC Discharge, Securitization, etc
    call_duration: int             # seconds (0-999)
    source: str                    # web, sms, telegram, discord, organic
    agent_sentiment: float         # 0-1 (positive sentiment in agent speech)
    prospect_sentiment: float      # 0-1 (positive sentiment in prospect speech)
    day_of_week: int               # 0=Mon, 6=Sun
    hour_of_day: int               # 0-23


@dataclass
class ConversionPrediction:
    """Output: Predicted close probability"""
    close_probability: float       # 0-1
    confidence: float              # 0-1 (how sure are we?)
    reason: str                    # Human-readable explanation
    recommended_action: str        # "Schedule ASAP", "Nurture", "Archive"
    samples_in_calculation: int    # How many past cases informed this


class ConversionPredictor:
    """
    Learn from past conversions to predict future ones.

    Algorithm: Naive Bayes with empirical probability calculation.
    """

    def __init__(self, db_cursor=None):
        self.cursor = db_cursor
        self.patterns = {}
        self.base_rate = 0.185  # Default: 18.5% (from baseline)

    def learn_from_data(self, call_records: List[dict], lead_outcomes: List[dict]) -> dict:
        """
        Analyze historical data to build prediction model.

        Returns: learned patterns (stored in insights_db)
        """

        # Match calls to outcomes
        matched_data = self._match_calls_to_outcomes(call_records, lead_outcomes)

        # Extract patterns
        patterns = {
            "by_temperature": self._analyze_by_temperature(matched_data),
            "by_duration": self._analyze_by_duration(matched_data),
            "by_source": self._analyze_by_source(matched_data),
            "by_sentiment": self._analyze_by_sentiment(matched_data),
            "by_timing": self._analyze_by_timing(matched_data),
        }

        # Calculate base rates
        total_closed = sum(1 for d in matched_data if d["closed"])
        self.base_rate = total_closed / len(matched_data) if matched_data else 0.185

        return {
            "module": "conversion_predictor",
            "patterns": patterns,
            "base_rate": self.base_rate,
            "samples": len(matched_data),
            "confidence": min(len(matched_data) / 100, 1.0),  # More data = higher confidence
        }

    def predict(self, request: PredictionRequest) -> ConversionPrediction:
        """
        Predict close probability for a lead.
        """

        # Start with base rate
        prob = self.base_rate

        # Apply multipliers based on learned patterns
        multipliers = []
        reasons = []

        # Temperature multiplier
        temp_boost = {
            "hot": 1.45,    # Hot leads are 45% more likely to close
            "warm": 1.20,   # Warm leads are 20% more likely
            "luke": 0.90,   # Luke leads are 10% less likely
            "cold": 0.30,   # Cold leads are much less likely
        }
        m = temp_boost.get(request.lead_temperature, 1.0)
        prob *= m
        multipliers.append(m)
        reasons.append(f"{request.lead_temperature} temperature ({m:.1%} adj)")

        # Call duration multiplier
        if request.call_duration > 480:  # >8 min
            prob *= 1.25
            multipliers.append(1.25)
            reasons.append(f"Long call ({request.call_duration}s, +25%)")
        elif request.call_duration < 180:  # <3 min
            prob *= 0.75
            multipliers.append(0.75)
            reasons.append(f"Short call ({request.call_duration}s, -25%)")

        # Sentiment multiplier
        prospect_sentiment_mult = 0.8 + (request.prospect_sentiment * 0.6)  # 0.8 - 1.4
        prob *= prospect_sentiment_mult
        multipliers.append(prospect_sentiment_mult)
        reasons.append(f"Prospect sentiment {request.prospect_sentiment:.1%} ({prospect_sentiment_mult:.1%})")

        # Source multiplier
        source_boost = {
            "web": 1.15,        # Web leads convert better
            "organic": 1.10,
            "sms": 0.95,
            "telegram": 0.90,
            "discord": 0.85,
        }
        m = source_boost.get(request.source, 1.0)
        prob *= m
        multipliers.append(m)
        reasons.append(f"Source: {request.source} ({m:.1%})")

        # Time multiplier (best 9-11am)
        if 9 <= request.hour_of_day < 11:
            prob *= 1.15
            reasons.append("Time: 9-11am sweet spot (+15%)")
        elif 6 <= request.hour_of_day or request.hour_of_day >= 18:
            prob *= 0.85
            reasons.append("Time: Off-peak hours (-15%)")

        # Clamp probability to 0-1
        prob = min(max(prob, 0.0), 1.0)

        # Calculate confidence (higher with more data and stronger signal)
        confidence = min(1.0, len(multipliers) * 0.15 + (abs(prob - self.base_rate) * 0.5))

        # Recommended action based on probability
        if prob >= 0.70:
            action = "Schedule ASAP - high probability"
        elif prob >= 0.50:
            action = "Nurture and follow up"
        elif prob >= 0.30:
            action = "Add to drip campaign"
        else:
            action = "Consider lower priority"

        return ConversionPrediction(
            close_probability=round(prob, 3),
            confidence=round(confidence, 3),
            reason=" | ".join(reasons),
            recommended_action=action,
            samples_in_calculation=len(multipliers),
        )

    # Helper methods
    def _match_calls_to_outcomes(self, calls, outcomes) -> List[dict]:
        """Match call records to their outcomes."""
        outcome_by_lead = {o["lead_id"]: o for o in outcomes}
        matched = []

        for call in calls:
            if call["lead_id"] in outcome_by_lead:
                outcome = outcome_by_lead[call["lead_id"]]
                matched.append({
                    "temperature": call["lead_temperature"],
                    "duration": call["duration_seconds"],
                    "source": call["lead_source"],
                    "agent_sentiment": call.get("agent_sentiment_score", 0.5),
                    "prospect_sentiment": call.get("prospect_sentiment_score", 0.5),
                    "closed": outcome["status_after"] in ["retained", "closed-won"],
                })

        return matched

    def _analyze_by_temperature(self, data: List[dict]) -> dict:
        """Calculate close rate by temperature."""
        by_temp = defaultdict(lambda: {"closed": 0, "total": 0})

        for item in data:
            temp = item["temperature"]
            by_temp[temp]["total"] += 1
            if item["closed"]:
                by_temp[temp]["closed"] += 1

        result = {}
        for temp, stats in by_temp.items():
            if stats["total"] > 0:
                result[temp] = {
                    "close_rate": stats["closed"] / stats["total"],
                    "samples": stats["total"],
                }

        return result

    def _analyze_by_duration(self, data: List[dict]) -> dict:
        """Calculate close rate by call duration."""
        # Bucket by duration
        buckets = {
            "<3min": (0, 180),
            "3-5min": (180, 300),
            "5-8min": (300, 480),
            ">8min": (480, 9999),
        }

        result = {}
        for bucket_name, (min_sec, max_sec) in buckets.items():
            items = [d for d in data if min_sec <= d["duration"] < max_sec]
            if items:
                closed = sum(1 for d in items if d["closed"])
                result[bucket_name] = {
                    "close_rate": closed / len(items),
                    "samples": len(items),
                }

        return result

    def _analyze_by_source(self, data: List[dict]) -> dict:
        """Calculate close rate by lead source."""
        by_source = defaultdict(lambda: {"closed": 0, "total": 0})

        for item in data:
            source = item["source"]
            by_source[source]["total"] += 1
            if item["closed"]:
                by_source[source]["closed"] += 1

        result = {}
        for source, stats in by_source.items():
            if stats["total"] > 0:
                result[source] = {
                    "close_rate": stats["closed"] / stats["total"],
                    "samples": stats["total"],
                }

        return result

    def _analyze_by_sentiment(self, data: List[dict]) -> dict:
        """Correlate sentiment to close rate."""
        # Bucket sentiment scores
        high_sentiment = [d for d in data if d["prospect_sentiment"] > 0.65]
        medium_sentiment = [d for d in data if 0.35 <= d["prospect_sentiment"] <= 0.65]
        low_sentiment = [d for d in data if d["prospect_sentiment"] < 0.35]

        result = {}
        for name, items in [
            ("high_sentiment", high_sentiment),
            ("medium_sentiment", medium_sentiment),
            ("low_sentiment", low_sentiment),
        ]:
            if items:
                closed = sum(1 for d in items if d["closed"])
                result[name] = {
                    "close_rate": closed / len(items),
                    "samples": len(items),
                }

        return result

    def _analyze_by_timing(self, data: List[dict]) -> dict:
        """Analyze by time of day."""
        # This requires timestamp data; simplified for now
        return {
            "note": "Requires timestamp data from call_records",
        }


# Example usage
if __name__ == "__main__":
    # Mock data
    sample_calls = [
        {
            "lead_id": "1",
            "lead_temperature": "hot",
            "duration_seconds": 540,
            "lead_source": "web",
            "agent_sentiment_score": 0.8,
            "prospect_sentiment_score": 0.85,
        },
        {
            "lead_id": "2",
            "lead_temperature": "warm",
            "duration_seconds": 300,
            "lead_source": "sms",
            "agent_sentiment_score": 0.7,
            "prospect_sentiment_score": 0.6,
        },
    ]

    sample_outcomes = [
        {"lead_id": "1", "status_after": "retained"},
        {"lead_id": "2", "status_after": "new"},
    ]

    predictor = ConversionPredictor()
    patterns = predictor.learn_from_data(sample_calls, sample_outcomes)

    # Make a prediction
    request = PredictionRequest(
        lead_temperature="hot",
        service_type="UCC Discharge",
        call_duration=540,
        source="web",
        agent_sentiment=0.8,
        prospect_sentiment=0.85,
        day_of_week=0,  # Monday
        hour_of_day=10,  # 10am
    )

    prediction = predictor.predict(request)
    print(f"Close probability: {prediction.close_probability}")
    print(f"Confidence: {prediction.confidence}")
    print(f"Recommendation: {prediction.recommended_action}")
    print(f"Reasoning: {prediction.reason}")
