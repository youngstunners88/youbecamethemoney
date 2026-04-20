"""
Skill: Intake Commercial Law (Jarvis-enabled)
Qualifies leads + returns confidence scores + reasoning.
Integrates with hermes_memory for pattern matching.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

log = logging.getLogger(__name__)


class IntakeCommercialLaw:
    """Intelligent lead intake with confidence scoring."""

    def __init__(self, db_connection=None):
        self.db = db_connection  # PostgreSQL connection for hermes_memory lookup
        self.questions = {
            "jurisdiction": [
                "What state/jurisdiction is your business registered in?",
                "Where is the dispute occurring?",
            ],
            "contract_type": [
                "Does this involve a contract? If so, what type (B2B, vendor agreement, etc)?",
                "Is there a written agreement in place?",
            ],
            "amount_in_dispute": [
                "What is the approximate amount in dispute?",
                "Is this a high-value or routine matter?",
            ],
            "urgency": [
                "Is there a deadline or statute of limitations concern?",
                "How quickly do you need resolution?",
            ],
            "complexity": [
                "Are there multiple parties involved?",
                "Does this involve UCC (Uniform Commercial Code) issues?",
            ],
            "prior_attempts": [
                "Have you attempted resolution already?",
                "Is this a breach of contract or ongoing dispute?",
            ],
        }

    def generate_intake_questions(self, lead_data: Dict[str, Any]) -> List[str]:
        """Generate tailored intake questions based on lead info."""
        questions = []
        questions.extend(self.questions["jurisdiction"])
        service_type = lead_data.get("service_type", "").lower()
        if "contract" in service_type or "agreement" in service_type:
            questions.extend(self.questions["contract_type"])
        if "business" in service_type or "commercial" in service_type:
            questions.extend(self.questions["complexity"])
        questions.extend(self.questions["amount_in_dispute"])
        questions.extend(self.questions["urgency"])
        log.info(f"Generated {len(questions)} intake questions for lead")
        return questions

    def analyze_intake_responses(self, responses: Dict[str, str], similar_leads: List[Dict] = None) -> Dict[str, Any]:
        """
        Analyze intake responses with confidence scoring + reasoning.

        Args:
            responses: Lead's interview answers
            similar_leads: Optional list of past leads matching this pattern

        Returns: {
            "decision": "ACCEPT | CONSIDER | REFER | DECLINE",
            "fit_score": 0-100,
            "confidence": 0-100,
            "reasoning": { "why": "...", "pattern_match": "...", "evidence": [...] },
            "risk_factors": [...],
            "strengths": [...],
            "recommended_action": "...",
            "similar_leads": [{ "id": "...", "outcome": "conversion", "confidence": 0.92 }]
        }
        """
        fit_score = 50
        confidence = 50  # Base confidence (no pattern data yet)
        risk_factors = []
        strengths = []
        evidence = []

        # ── Jurisdiction Analysis ──
        jurisdiction = responses.get("jurisdiction", "").lower()
        strong_jurisdictions = ["texas", "new york", "california"]
        if any(state in jurisdiction for state in strong_jurisdictions):
            fit_score += 15
            confidence += 10
            strengths.append(f"Strong jurisdiction: {jurisdiction.title()}")
            evidence.append(f"jurisdiction=strong")
        else:
            risk_factors.append("Jurisdiction outside typical service areas")
            fit_score -= 10
            confidence -= 5

        # ── Contract/Agreement Analysis ──
        has_contract = "yes" in responses.get("contract_type", "").lower()
        if has_contract:
            fit_score += 20
            confidence += 15
            strengths.append("Written contract exists (stronger case)")
            evidence.append("contract=documented")
        else:
            risk_factors.append("No written agreement - harder to litigate")
            fit_score -= 15
            confidence -= 10

        # ── Amount in Dispute Analysis ──
        try:
            amount = float(responses.get("amount_in_dispute", "0").replace("$", "").replace(",", ""))
            if amount > 50000:
                fit_score += 25
                confidence += 20
                strengths.append(f"High-value matter (${amount:,.0f})")
                evidence.append(f"value=high")
            elif amount > 10000:
                fit_score += 10
                confidence += 10
                strengths.append(f"Reasonable value (${amount:,.0f})")
                evidence.append(f"value=moderate")
            else:
                fit_score -= 20
                confidence -= 15
                risk_factors.append("Low-value matter")
                evidence.append(f"value=low")
        except:
            risk_factors.append("Could not parse amount")
            confidence -= 5

        # ── Urgency Analysis ──
        urgency = responses.get("urgency", "").lower()
        if "urgent" in urgency or "deadline" in urgency:
            fit_score += 10
            confidence += 10
            strengths.append("Urgent timeline - higher priority")
            evidence.append("urgency=high")
        elif "no rush" in urgency:
            risk_factors.append("Low urgency")
            fit_score -= 5

        # ── Complexity Analysis ──
        complexity = responses.get("complexity", "").lower()
        has_ucc = "ucc" in complexity or "securitization" in complexity
        has_multiple = "multiple" in complexity or "parties" in complexity

        if has_ucc:
            fit_score += 15
            confidence += 15
            strengths.append("UCC/Securitization issue - Garcia's specialty")
            evidence.append("service=ucc_specialty")
        if has_multiple:
            risk_factors.append("Multiple parties increases complexity")
            fit_score -= 10
            confidence -= 5

        # ── Pattern Matching from Similar Leads ──
        similar_lead_info = None
        if similar_leads and len(similar_leads) > 0:
            # Use the best match
            best_match = max(similar_leads, key=lambda x: x.get("match_confidence", 0))
            match_confidence = best_match.get("match_confidence", 0)
            outcome = best_match.get("outcome", "unknown")

            if match_confidence > 0.8 and outcome == "conversion":
                confidence += 25
                evidence.append(f"pattern_match=strong (like {best_match.get('name', 'past lead')}, converted)")
                similar_lead_info = best_match
            elif match_confidence > 0.6:
                confidence += 10
                evidence.append(f"pattern_match=moderate")

        # ── Clamp scores ──
        fit_score = max(0, min(100, fit_score))
        confidence = max(0, min(100, confidence))

        # ── Decision ──
        if fit_score >= 75:
            decision = "ACCEPT"
            recommended_action = "Schedule consultation with Mr. Garcia"
        elif fit_score >= 60:
            decision = "CONSIDER"
            recommended_action = "Present to Mr. Garcia for review"
        elif fit_score >= 40:
            decision = "REFER"
            recommended_action = "Recommend specialist or outside counsel"
        else:
            decision = "DECLINE"
            recommended_action = "Send polite decline, keep in follow-up"

        return {
            "decision": decision,
            "fit_score": fit_score,
            "confidence": round(confidence, 1),
            "reasoning": {
                "why": f"Lead fits Garcia's practice ({decision.lower()})",
                "pattern_match": f"Similar lead match: {similar_lead_info.get('name') if similar_lead_info else 'none'}",
                "evidence": evidence,
                "signal_count": len([e for e in evidence if "=" in e]),
            },
            "risk_factors": risk_factors,
            "strengths": strengths,
            "recommended_action": recommended_action,
            "similar_leads": [
                {
                    "id": lead.get("id"),
                    "name": lead.get("name"),
                    "confidence": round(lead.get("match_confidence", 0) * 100, 1),
                    "outcome": lead.get("outcome"),
                }
                for lead in (similar_leads or [])[:3]
            ],
        }


def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Hermes skill."""
    action = context.get("action", "")
    lead_data = context.get("lead_data", {})
    responses = context.get("responses", {})
    similar_leads = context.get("similar_leads", [])

    skill = IntakeCommercialLaw()

    if "generate_questions" in action:
        questions = skill.generate_intake_questions(lead_data)
        return {
            "skill": "intake_commercial_law",
            "questions": questions,
            "count": len(questions),
        }

    elif "analyze_responses" in action:
        analysis = skill.analyze_intake_responses(responses, similar_leads)
        return {
            "skill": "intake_commercial_law",
            "analysis": analysis,
        }

    else:
        return {"error": "Unknown action for intake_commercial_law skill"}
