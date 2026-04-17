"""
Skill: Lead Urgency Scorer
Scores leads 1-10 based on commercial law patterns
Learns from Garcia's past case outcomes
"""

import logging
from typing import Dict, Any

log = logging.getLogger(__name__)

class LeadUrgencyScorer:
    """Score lead urgency based on case characteristics + historical patterns."""

    def __init__(self, learned_patterns: Dict[str, Any] = None):
        """
        Initialize scorer with learned patterns from closed cases.

        Args:
            learned_patterns: Dict of {case_type: success_rate} from Layer 3
        """
        self.learned_patterns = learned_patterns or {}

    def score_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score lead urgency (1-10) and conversion likelihood.

        Returns:
        - urgency_score (1-10): How quickly to follow up
        - confidence: How confident we are in this score
        - reasoning: Why this score
        """
        score = 5  # Base score (medium urgency)
        confidence = 0.5

        reasoning = []

        # Factor 1: Amount in dispute (value signal)
        amount = lead.get("case_value", 0)
        if amount > 100000:
            score += 3
            confidence += 0.2
            reasoning.append(f"High value case (${amount:,.0f})")
        elif amount > 50000:
            score += 2
            confidence += 0.15
            reasoning.append(f"Medium-high value (${amount:,.0f})")
        elif amount > 10000:
            score += 1
            confidence += 0.1
            reasoning.append(f"Moderate value (${amount:,.0f})")
        else:
            score -= 1
            confidence -= 0.1
            reasoning.append(f"Low value (${amount:,.0f}) - lower priority")

        # Factor 2: Service type
        service_type = lead.get("service_type", "").lower()

        # Garcia specializes in these areas
        high_priority_types = ["securitization", "ucc", "commercial", "contract", "business"]
        for ptype in high_priority_types:
            if ptype in service_type:
                score += 2
                confidence += 0.15
                reasoning.append(f"Specialization match: {ptype}")
                break

        # Factor 3: Time-sensitive signals
        has_deadline = "deadline" in lead.get("notes", "").lower()
        if has_deadline:
            score += 2
            confidence += 0.15
            reasoning.append("Deadline present - time-sensitive")

        # Factor 4: Lead warmth/temperature (from intake)
        warmth = lead.get("warmth_score", 5)
        if warmth >= 80:
            score += 2
            confidence += 0.2
            reasoning.append(f"Hot lead (warmth: {warmth})")
        elif warmth >= 60:
            score += 1
            confidence += 0.1
            reasoning.append(f"Warm lead (warmth: {warmth})")
        else:
            score -= 1
            confidence -= 0.1
            reasoning.append(f"Cold lead (warmth: {warmth})")

        # Factor 5: Learned patterns (from Layer 3)
        pattern_boost = self._get_pattern_boost(service_type)
        if pattern_boost:
            score += pattern_boost["boost"]
            confidence += pattern_boost["confidence"]
            reasoning.append(pattern_boost["reason"])

        # Clamp score to 1-10
        score = max(1, min(10, score))

        # Clamp confidence to 0-1
        confidence = max(0, min(1, confidence))

        return {
            "urgency_score": score,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "follow_up_action": self._recommend_follow_up(score),
        }

    def _get_pattern_boost(self, service_type: str) -> Dict[str, Any]:
        """Check learned patterns for this service type."""
        if not self.learned_patterns:
            return None

        pattern_data = self.learned_patterns.get(service_type, {})
        if not pattern_data:
            return None

        success_rate = pattern_data.get("success_rate", 0)
        avg_case_value = pattern_data.get("avg_case_value", 0)

        if success_rate > 0.8:  # >80% success rate
            return {
                "boost": 3,
                "confidence": 0.25,
                "reason": f"Strong pattern: {service_type} has {success_rate*100:.0f}% success rate"
            }
        elif success_rate > 0.6:  # 60-80% success
            return {
                "boost": 1,
                "confidence": 0.15,
                "reason": f"Moderate pattern: {service_type} has {success_rate*100:.0f}% success rate"
            }
        else:
            return None

    def _recommend_follow_up(self, score: int) -> Dict[str, str]:
        """Recommend follow-up timing based on score."""
        if score >= 9:
            return {
                "action": "Call immediately",
                "timing": "Within 2 hours",
                "priority": "CRITICAL"
            }
        elif score >= 7:
            return {
                "action": "Call today",
                "timing": "Within 4 hours",
                "priority": "HIGH"
            }
        elif score >= 5:
            return {
                "action": "Email inquiry",
                "timing": "Within 24 hours",
                "priority": "MEDIUM"
            }
        elif score >= 3:
            return {
                "action": "Automated follow-up",
                "timing": "Within 3 days",
                "priority": "LOW"
            }
        else:
            return {
                "action": "Archive for future reference",
                "timing": "No immediate action",
                "priority": "ARCHIVED"
            }

def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Hermes skill."""
    lead = context.get("lead", {})
    learned_patterns = context.get("learned_patterns", {})

    scorer = LeadUrgencyScorer(learned_patterns)
    result = scorer.score_lead(lead)

    return {
        "skill": "lead_urgency_scorer",
        "lead_id": lead.get("id"),
        "result": result,
    }
