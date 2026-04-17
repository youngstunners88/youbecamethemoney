"""
Skill: Intake Commercial Law
Asks the right questions to qualify commercial law leads
Embeds Mr. Garcia's domain knowledge in the conversation
"""

import json
import logging
from typing import Dict, Any, List

log = logging.getLogger(__name__)

class IntakeCommercialLaw:
    """Intelligent lead intake for commercial law cases."""

    def __init__(self):
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
        """
        Generate tailored intake questions based on lead info.

        Returns questions most relevant to this lead's situation.
        """
        questions = []

        # Always ask jurisdiction (foundational)
        questions.extend(self.questions["jurisdiction"])

        # Determine what to ask based on lead info
        service_type = lead_data.get("service_type", "").lower()

        if "contract" in service_type or "agreement" in service_type:
            questions.extend(self.questions["contract_type"])

        if "business" in service_type or "commercial" in service_type:
            questions.extend(self.questions["complexity"])

        # Always assess urgency and amount
        questions.extend(self.questions["amount_in_dispute"])
        questions.extend(self.questions["urgency"])

        log.info(f"Generated {len(questions)} intake questions for lead")
        return questions

    def analyze_intake_responses(self, responses: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze intake responses to score lead quality + identify risks.

        Returns analysis with:
        - fit_score (0-100): How well this fits Garcia's practice
        - risk_factors: Legal/commercial risks identified
        - recommended_action: Next steps
        """
        fit_score = 50  # Base score

        risk_factors = []
        strengths = []

        # Analyze jurisdiction
        jurisdiction = responses.get("jurisdiction", "").lower()
        if any(state in jurisdiction for state in ["texas", "new york", "california"]):
            fit_score += 15
            strengths.append("Lead in strong jurisdiction for commercial law")
        else:
            risk_factors.append("Jurisdiction outside typical service areas")
            fit_score -= 10

        # Analyze contract/agreement
        has_contract = "yes" in responses.get("contract_type", "").lower()
        if has_contract:
            fit_score += 20
            strengths.append("Written contract exists (stronger case)")
        else:
            risk_factors.append("No written agreement - harder to litigate")
            fit_score -= 15

        # Analyze amount in dispute
        try:
            amount = float(responses.get("amount_in_dispute", "0").replace("$", "").replace(",", ""))
            if amount > 50000:
                fit_score += 25
                strengths.append(f"High-value matter (${amount:,.0f})")
            elif amount > 10000:
                fit_score += 10
                strengths.append(f"Reasonable value (${amount:,.0f})")
            else:
                fit_score -= 20
                risk_factors.append("Low-value matter - may not be economically viable")
        except:
            risk_factors.append("Could not parse amount in dispute")

        # Analyze urgency
        urgency = responses.get("urgency", "").lower()
        if "urgent" in urgency or "deadline" in urgency:
            fit_score += 10
            strengths.append("Urgent timeline - higher priority")
        elif "no rush" in urgency:
            risk_factors.append("Low urgency - may indicate low priority for client")
            fit_score -= 5

        # Analyze complexity
        complexity = responses.get("complexity", "").lower()
        if "multiple" in complexity or "parties" in complexity:
            risk_factors.append("Multiple parties increases complexity")
            fit_score -= 10
        elif "ucc" in complexity or "securitization" in complexity:
            fit_score += 15
            strengths.append("UCC/securitization issue - Garcia's specialty")

        fit_score = max(0, min(100, fit_score))  # Clamp to 0-100

        return {
            "fit_score": fit_score,
            "risk_factors": risk_factors,
            "strengths": strengths,
            "recommended_action": self._recommend_action(fit_score),
            "next_steps": self._next_steps(fit_score),
        }

    def _recommend_action(self, fit_score: int) -> str:
        """Recommend action based on fit score."""
        if fit_score >= 75:
            return "ACCEPT - Strong fit for Garcia's practice"
        elif fit_score >= 60:
            return "CONSIDER - Discuss with Garcia before committing"
        elif fit_score >= 40:
            return "REFER - Recommend to specialist or outside counsel"
        else:
            return "DECLINE - Not a good fit for Garcia's practice"

    def _next_steps(self, fit_score: int) -> List[str]:
        """Define next steps based on fit score."""
        if fit_score >= 75:
            return [
                "Schedule consultation with Mr. Garcia",
                "Request detailed case documents",
                "Prepare engagement letter",
                "Discuss fee structure"
            ]
        elif fit_score >= 60:
            return [
                "Present case summary to Mr. Garcia",
                "Request clarification on key issues",
                "Get Garcia's input before commitment"
            ]
        else:
            return [
                "Send polite decline email",
                "Provide referral recommendations",
                "Keep in database for future opportunities"
            ]

def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Hermes skill."""
    skill = IntakeCommercialLaw()

    if "generate_questions" in context.get("action", ""):
        lead_data = context.get("lead_data", {})
        questions = skill.generate_intake_questions(lead_data)
        return {
            "skill": "intake_commercial_law",
            "questions": questions,
            "count": len(questions),
        }

    elif "analyze_responses" in context.get("action", ""):
        responses = context.get("responses", {})
        analysis = skill.analyze_intake_responses(responses)
        return {
            "skill": "intake_commercial_law",
            "analysis": analysis,
        }

    else:
        return {"error": "Unknown action for intake_commercial_law skill"}
