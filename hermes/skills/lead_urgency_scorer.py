"""
Skill: Lead Urgency Scorer (Jarvis-enabled)
Scores leads 1-10 + returns confidence + reasoning.
Learns from outcomes + pattern success rates.
"""

import logging
from typing import Dict, Any, List

log = logging.getLogger(__name__)


class LeadUrgencyScorer:
    """Score lead urgency with confidence + reasoning (Jarvis mode)."""

    def __init__(self, learned_patterns: Dict[str, Any] = None, hermes_memory: List[Dict] = None):
        """
        Initialize scorer with learned patterns.

        Args:
            learned_patterns: {case_type: success_rate} from hermes_memory
            hermes_memory: List of similar leads + their outcomes
        """
        self.learned_patterns = learned_patterns or {}
        self.hermes_memory = hermes_memory or []

    def score_lead(self, lead: Dict[str, Any], similar_leads: List[Dict] = None) -> Dict[str, Any]:
        """
        Score lead urgency (1-10) with confidence + reasoning.

        Returns: {
            "urgency_score": 1-10,
            "warmth_prediction": 0-100,
            "confidence": 0-100,
            "reasoning": { "why": "...", "factors": [...], "similar_leads": [...] },
            "follow_up_action": { "action": "...", "timing": "...", "priority": "..." },
            "recommended_timing": "2pm | 9am | 24h | 48h | ..."
        }
        """
        score = 5  # Base: medium urgency
        confidence = 50  # Base: moderate confidence
        factors = []
        evidence = []

        # ── Factor 1: Amount in dispute ──
        amount = lead.get("case_value", 0)
        if amount > 100000:
            score += 3
            confidence += 15
            factors.append(f"High value: ${amount:,.0f}")
            evidence.append("value=high")
        elif amount > 50000:
            score += 2
            confidence += 10
            factors.append(f"Medium-high: ${amount:,.0f}")
            evidence.append("value=medium_high")
        elif amount > 10000:
            score += 1
            confidence += 5
            factors.append(f"Moderate: ${amount:,.0f}")
            evidence.append("value=moderate")
        else:
            score -= 1
            confidence -= 5
            factors.append(f"Low value: ${amount:,.0f}")
            evidence.append("value=low")

        # ── Factor 2: Service type (Garcia's specialties) ──
        service_type = lead.get("service_type", "").lower()
        high_priority = ["securitization", "ucc", "commercial", "contract", "business"]
        matched_specialty = next((pt for pt in high_priority if pt in service_type), None)
        if matched_specialty:
            score += 2
            confidence += 12
            factors.append(f"Specialization: {matched_specialty}")
            evidence.append(f"specialty={matched_specialty}")

        # ── Factor 3: Time-sensitive signals ──
        has_deadline = "deadline" in lead.get("notes", "").lower()
        if has_deadline:
            score += 2
            confidence += 10
            factors.append("Deadline present")
            evidence.append("deadline=yes")

        # ── Factor 4: Lead warmth (from intake) ──
        warmth = lead.get("warmth_score", 50)
        if warmth >= 80:
            score += 2
            confidence += 15
            factors.append(f"Hot lead (warmth: {warmth})")
            evidence.append("warmth=hot")
        elif warmth >= 60:
            score += 1
            confidence += 10
            factors.append(f"Warm lead (warmth: {warmth})")
            evidence.append("warmth=warm")
        else:
            score -= 1
            confidence -= 5
            factors.append(f"Cold lead (warmth: {warmth})")
            evidence.append("warmth=cold")

        # ── Factor 5: Pattern matching from similar leads ──
        similar_lead_matches = []
        if similar_leads:
            for sl in similar_leads[:3]:
                match_conf = sl.get("match_confidence", 0)
                outcome = sl.get("outcome", "unknown")
                if match_conf > 0.7:
                    if outcome == "conversion":
                        score += 1
                        confidence += 10
                        similar_lead_matches.append({
                            "id": sl.get("id"),
                            "name": sl.get("name"),
                            "confidence": round(match_conf * 100, 0),
                            "outcome": outcome,
                            "warmth": sl.get("warmth_score", "?"),
                        })
                        factors.append(f"Matched {sl.get('name')} (converted)")
                        evidence.append("pattern_match=conversion")
                    elif outcome == "no_response":
                        confidence -= 5
                        evidence.append("pattern_match=cold")

        # ── Clamp scores ──
        score = max(1, min(10, score))
        confidence = max(0, min(100, confidence))

        # ── Recommended timing (learned from patterns) ──
        recommended_timing = self._get_optimal_timing(service_type, warmth, similar_leads)

        # ── Follow-up action ──
        follow_up_action = self._recommend_follow_up(score, confidence)

        return {
            "urgency_score": score,
            "warmth_prediction": round(warmth, 1),
            "confidence": round(confidence, 1),
            "reasoning": {
                "why": f"Urgency {score}/10 (confidence: {confidence}%)",
                "factors": factors,
                "evidence": evidence,
                "similar_leads": similar_lead_matches,
            },
            "follow_up_action": follow_up_action,
            "recommended_timing": recommended_timing,
        }

    def _get_optimal_timing(self, service_type: str, warmth: float, similar_leads: List[Dict] = None) -> str:
        """Determine optimal email/call timing based on patterns."""
        if not similar_leads or len(similar_leads) == 0:
            # Default recommendations
            if warmth >= 80:
                return "2pm"  # Hot leads: afternoon
            elif warmth >= 60:
                return "9am"  # Warm leads: morning
            else:
                return "24h"  # Cold leads: next day

        # Use pattern data if available
        best_open_time = "2pm"  # Default
        for sl in similar_leads:
            if sl.get("outcome") == "conversion":
                best_open_time = sl.get("best_email_time", "2pm")
                break

        return best_open_time

    def _recommend_follow_up(self, score: int, confidence: float) -> Dict[str, str]:
        """Recommend follow-up timing + priority based on urgency + confidence."""
        if score >= 9 and confidence >= 80:
            return {
                "action": "Call immediately",
                "timing": "Within 1 hour",
                "priority": "CRITICAL",
            }
        elif score >= 7 or confidence >= 90:
            return {
                "action": "Email + schedule call",
                "timing": "Within 2 hours",
                "priority": "HIGH",
            }
        elif score >= 5 and confidence >= 70:
            return {
                "action": "Email at optimal time",
                "timing": "Within 4 hours",
                "priority": "MEDIUM",
            }
        elif score >= 3:
            return {
                "action": "Email nurture",
                "timing": "Within 24 hours",
                "priority": "LOW",
            }
        else:
            return {
                "action": "Mark cold, queue Q2",
                "timing": "No immediate action",
                "priority": "ARCHIVED",
            }


def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Hermes skill."""
    lead = context.get("lead", {})
    learned_patterns = context.get("learned_patterns", {})
    similar_leads = context.get("similar_leads", [])

    scorer = LeadUrgencyScorer(learned_patterns)
    result = scorer.score_lead(lead, similar_leads)

    return {
        "skill": "lead_urgency_scorer",
        "lead_id": lead.get("id"),
        "result": result,
    }
