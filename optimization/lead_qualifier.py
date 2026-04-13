#!/usr/bin/env python3
"""
FastMCP Skill: Lead Temperature Qualifier

Categorizes leads as: cold, luke, warm, hot
Based on engagement level, problem awareness, and readiness

Call this skill after initial voice call to refine temperature categorization.
"""

import json
from typing import Optional
from enum import Enum

class LeadTemperature(str, Enum):
    COLD = "cold"
    LUKE = "luke"
    WARM = "warm"
    HOT = "hot"


class LeadQualifier:
    def __init__(self):
        self.criteria = {
            "hot": {
                "engagement": 8,  # High engagement
                "problem_awareness": 9,
                "decision_readiness": 8,
                "keywords": ["ready", "hire", "next steps", "how much", "when can", "yes"],
                "voice_indicators": ["fast_speaking", "excited_tone", "asking_costs"],
            },
            "warm": {
                "engagement": 6,
                "problem_awareness": 7,
                "decision_readiness": 5,
                "keywords": ["interested", "tell me more", "makes sense", "possibly", "let me think"],
                "voice_indicators": ["engaged_questions", "positive_tone"],
            },
            "luke": {
                "engagement": 4,
                "problem_awareness": 5,
                "decision_readiness": 2,
                "keywords": ["maybe", "could be", "not sure", "interesting", "i guess"],
                "voice_indicators": ["hesitant_tone", "few_questions"],
            },
            "cold": {
                "engagement": 1,
                "problem_awareness": 2,
                "decision_readiness": 0,
                "keywords": ["not interested", "no thanks", "wrong number", "stop", "no"],
                "voice_indicators": ["dismissive", "short_answers", "frustrated"],
            },
        }

    def qualify_lead(
        self,
        transcript: str,
        engagement_score: int,  # 1-10
        problem_awareness_score: int,  # 1-10
        decision_readiness_score: int,  # 1-10
        service_type: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """
        Qualify a lead based on multiple signals

        Args:
            transcript: Full call transcript
            engagement_score: How engaged is the prospect? (1-10)
            problem_awareness_score: Do they understand their problem? (1-10)
            decision_readiness_score: Are they ready to decide? (1-10)
            service_type: Type of service interested in
            notes: Agent's notes from call

        Returns:
            Qualification result with temperature, confidence, and recommendations
        """

        # Analyze transcript for keywords
        transcript_lower = transcript.lower()
        keyword_counts = {temp: 0 for temp in LeadTemperature}

        for temperature, criteria in self.criteria.items():
            keyword_counts[temperature] = sum(
                1 for keyword in criteria["keywords"]
                if keyword in transcript_lower
            )

        # Score-based temperature
        avg_score = (engagement_score + problem_awareness_score + decision_readiness_score) / 3

        if avg_score >= 8:
            primary_temp = LeadTemperature.HOT
        elif avg_score >= 6:
            primary_temp = LeadTemperature.WARM
        elif avg_score >= 4:
            primary_temp = LeadTemperature.LUKE
        else:
            primary_temp = LeadTemperature.COLD

        # Check for contradictions (e.g., high engagement but cold keywords)
        if keyword_counts[LeadTemperature.COLD] > 2:
            primary_temp = LeadTemperature.COLD

        # Calculate confidence
        confidence = self._calculate_confidence(
            engagement_score,
            problem_awareness_score,
            decision_readiness_score,
            keyword_counts[primary_temp],
        )

        # Get next action recommendation
        next_action = self._get_next_action(primary_temp, service_type)

        return {
            "temperature": primary_temp.value,
            "confidence": confidence,
            "scores": {
                "engagement": engagement_score,
                "problem_awareness": problem_awareness_score,
                "decision_readiness": decision_readiness_score,
                "average": round(avg_score, 1),
            },
            "keyword_signals": keyword_counts,
            "service_type": service_type,
            "next_action": next_action,
            "follow_up_template": self._get_follow_up_template(primary_temp),
            "agent_notes": notes,
        }

    def _calculate_confidence(self, engagement, problem_aware, decision_ready, keyword_matches):
        """Calculate confidence score (0-1) of qualification"""

        # Score based on consistency
        score_variance = max(engagement, problem_aware, decision_ready) - min(engagement, problem_aware, decision_ready)
        consistency = 1 - (score_variance / 10)

        # Keyword match adds to confidence
        keyword_bonus = min(keyword_matches * 0.1, 0.2)

        # Base confidence from average score
        avg_score = (engagement + problem_aware + decision_ready) / 3
        base_confidence = min(avg_score / 10, 1.0)

        # Combine
        confidence = (base_confidence * 0.6 + consistency * 0.3 + keyword_bonus * 0.1)

        return round(min(confidence, 1.0), 2)

    def _get_next_action(self, temperature: str, service_type: Optional[str] = None) -> str:
        """Get recommended next action based on temperature"""

        actions = {
            "hot": f"Schedule consultation call with Daniel Garcia within 24 hours. {service_type or 'Commercial law'} specialist should handle.",
            "warm": "Send educational email with case study. Schedule follow-up in 3 days. Offer to answer questions.",
            "luke": "Send free ebook + educational materials. Low priority follow-up in 1 week. Build nurture sequence.",
            "cold": "Mark as not-ready. Add to 6-month re-engagement sequence. Monitor for re-activation signals.",
        }

        return actions.get(temperature, "Unknown action")

    def _get_follow_up_template(self, temperature: str) -> str:
        """Get follow-up email template based on temperature"""

        templates = {
            "hot": """Subject: Your Consultation is Scheduled - Daniel Garcia

Hi [FIRST_NAME],

Daniel reviewed your case and wants to help. Here's your consultation time: [CALENDAR_LINK]

He'll walk you through:
- Your specific UCC strategy
- Timeline to resolution
- What success looks like

See you then.

The YBTM Team""",

            "warm": """Subject: Next Steps in Your Commercial Law Journey

Hi [FIRST_NAME],

Thanks for the conversation. We think you're a great fit for our services.

Here's what I'd like to do:
1. Send you our case study on [SERVICE_TYPE]
2. Follow up in 3 days to answer questions
3. If you're ready, schedule a call with Daniel

Sound good?

The YBTM Team""",

            "luke": """Subject: Free Resource: [SERVICE_TYPE] Guide

Hi [FIRST_NAME],

No pressure here - just wanted to send you something valuable.

Download your free guide: [EBOOK_LINK]

This covers everything about [SERVICE_TYPE], exactly what we discussed.

Read it, and reach out if you have questions: 954-260-9327

The YBTM Team""",

            "cold": """Subject: We're Here When You're Ready

Hi [FIRST_NAME],

Understood - this isn't the right time.

But we're here when you are: 954-260-9327

From goods to GODS - we believe in your journey.

The YBTM Team""",
        }

        return templates.get(temperature, "")

    def batch_qualify(self, leads_data: list) -> list:
        """Qualify multiple leads at once"""
        results = []
        for lead in leads_data:
            result = self.qualify_lead(**lead)
            results.append({
                "lead_id": lead.get("lead_id"),
                "qualification": result,
            })
        return results


# Initialize skill
qualifier = LeadQualifier()


def main():
    """Example usage"""

    # Example call transcript
    transcript = """
    Agent: Good afternoon! This is Sarah from You Became The Money on behalf of Daniel Garcia.
    Prospect: Hi! Yeah, I was actually waiting for your call.
    Agent: Great! So tell me, what's your current situation with debt or commercial matters?
    Prospect: Well, I've been dealing with credit card debt and I've been reading about UCC Articles. That's why I was interested when you called.
    Agent: That's fantastic. So you're already problem-aware. How urgent would you say your situation is?
    Prospect: Pretty urgent. I want to resolve this within the next 90 days if possible.
    Agent: Excellent. And if we could show you a path to do that, would that be interesting?
    Prospect: Absolutely. How does your process work?
    Agent: [explains process]
    Prospect: Okay, this makes a lot of sense. What's the next step? How much would something like this cost?
    """

    # Qualify the lead
    qualification = qualifier.qualify_lead(
        transcript=transcript,
        engagement_score=9,
        problem_awareness_score=9,
        decision_readiness_score=8,
        service_type="UCC Discharge",
        notes="Prospect was waiting for call, already researched UCC, asking about pricing",
    )

    print("Lead Qualification Result:")
    print(json.dumps(qualification, indent=2))


if __name__ == "__main__":
    main()
