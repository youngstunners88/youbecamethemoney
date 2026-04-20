"""
Skill: Email Drafter (Jarvis-enabled)
Context-aware legal emails + confidence scoring.
Learns optimal timing + language from outcomes.
"""

import logging
from datetime import datetime
from typing import Dict, Any

log = logging.getLogger(__name__)


class EmailDrafter:
    """Draft professional legal emails with confidence scoring."""

    EMAIL_TEMPLATES = {
        "initial_response": """Dear {client_name},

Thank you for reaching out regarding your {case_type} matter.

I appreciate you taking the time to share your situation with us. Based on what you've described, this appears to involve {key_issues}, which is an area where we have significant experience representing commercial clients.

Before we proceed, I'd like to schedule a brief consultation to:
1. Understand the full scope of your situation
2. Identify any time-sensitive issues that require immediate attention
3. Discuss our approach and fee structure
4. Determine if this is the right fit for our firm

Next steps: Please reply with 2-3 times that work best for a 30-minute call this week.

Looking forward to speaking with you.

Best regards,
Daniel Garcia, Attorney at Law
""",
        "demand_letter": """{date}

{defendant_name}
{defendant_address}

Re: Demand for {remedy} - {case_title}

Dear {defendant_contact}:

This letter is written on behalf of our client, {client_name}, regarding {case_description}.

Our client has made a good faith effort to resolve this matter directly, but despite {resolution_attempts}, the dispute remains unresolved.

FACTS:
{facts_summary}

LEGAL BASIS:
{legal_basis}

RELIEF DEMANDED:
{relief_requested}

DEADLINE:
You have until {deadline_date} to respond in writing to this demand. Failure to respond within this timeframe will result in the filing of legal action, which may expose you to additional damages including attorney's fees and court costs.

This letter is made in an attempt to resolve this matter before litigation. All communications herein are made in an attempt to settle and are protected by {applicable_privilege}.

Sincerely,

Daniel Garcia
Attorney at Law
{firm_details}
""",
        "follow_up_warm": """Dear {client_name},

I hope this message finds you well. I wanted to follow up on our recent conversation about your {case_type} matter.

I've had a chance to think more about your situation, and I believe there are several strategies we could pursue that might be advantageous given {specific_circumstances}.

The key issue here is {key_issue}, and here's why it matters for your case:

{issue_explanation}

I think it would be valuable to discuss this further. I'm available for a call {proposed_times}.

Looking forward to continuing our conversation.

Best regards,
Daniel Garcia
""",
        "referral": """Dear {client_name},

Thank you for contacting our office regarding your {case_type} matter.

After careful consideration, I believe your situation may be better served by a specialist in {referral_specialty}. While {reason_for_referral}, I want to ensure you have the best possible representation.

I'm referring you to {referral_attorney_name} at {referral_firm}, who specializes in this area and has an excellent track record.

{referral_attorney_name} is expecting to hear from you, and I've given them a heads up that you'll be calling.

Best of luck with your matter.

Best regards,
Daniel Garcia
""",
    }

    def draft_email(self, lead: Dict[str, Any], email_type: str, similar_leads: list = None) -> Dict[str, Any]:
        """
        Draft email + return confidence + reasoning.

        Args:
            lead: Lead data
            email_type: 'initial_response' | 'demand_letter' | 'follow_up_warm' | 'referral'
            similar_leads: Past leads matching this pattern

        Returns: {
            "email": "draft text",
            "email_type": "...",
            "confidence": 0-100,
            "reasoning": "Why this email + timing",
            "recommended_timing": "2pm | 9am | ...",
            "key_elements": ["trust questions", "urgency signal", ...],
            "predicted_open_rate": 0-100
        }
        """
        template = self.EMAIL_TEMPLATES.get(email_type, self.EMAIL_TEMPLATES["initial_response"])

        # Extract data
        client_name = lead.get("name", "Client")
        case_type = lead.get("service_type", "matter")
        key_issues = lead.get("key_issues", "commercial law matters")

        # Confidence base
        confidence = 60  # Starting point

        # Check similar leads for timing + language effectiveness
        recommended_timing = "2pm"  # Default
        key_elements = []
        predicted_open_rate = 45  # Default

        if similar_leads:
            for sl in similar_leads[:3]:
                if sl.get("outcome") == "conversion":
                    recommended_timing = sl.get("best_email_time", "2pm")
                    confidence += 15
                    predicted_open_rate = sl.get("open_rate", 45)
                    key_elements.append(sl.get("best_question", ""))

        # Warmth-based confidence boost
        warmth = lead.get("warmth_score", 50)
        if warmth >= 80:
            confidence += 20
            predicted_open_rate += 25
        elif warmth >= 60:
            confidence += 10
            predicted_open_rate += 10

        # Email type confidence adjustments
        if email_type == "initial_response":
            confidence = min(95, confidence)
        elif email_type == "demand_letter":
            confidence = min(90, confidence)
        elif email_type == "referral":
            confidence = min(80, confidence)

        # Build email text
        try:
            email_text = template.format(
                client_name=client_name,
                case_type=case_type,
                key_issues=key_issues,
                date=datetime.now().strftime("%B %d, %Y"),
                **lead
            )
        except KeyError:
            email_text = template  # Fallback if missing vars

        return {
            "email": email_text,
            "email_type": email_type,
            "confidence": round(confidence, 1),
            "reasoning": f"Email type '{email_type}' matches {client_name}'s warmth ({warmth}) and pattern history.",
            "recommended_timing": recommended_timing,
            "key_elements": list(set([k for k in key_elements if k]))[:3],
            "predicted_open_rate": min(95, predicted_open_rate),
            "ready_to_send": confidence >= 60,
        }

    def get_email_type(self, context: Dict[str, Any]) -> str:
        """Recommend email type based on lead/case context."""
        urgency = context.get("urgency_score", 5)
        fit = context.get("fit_score", 50)
        status = context.get("status", "new")

        if status == "new" and fit > 60:
            return "initial_response"
        elif status == "engaged" and urgency > 6:
            return "follow_up_warm"
        elif status == "demand" and fit > 70:
            return "demand_letter"
        elif fit < 40:
            return "referral"
        else:
            return "follow_up_warm"


def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point."""
    action = context.get("action", "")
    lead_or_case = context.get("lead") or context.get("case", {})
    email_type = context.get("email_type")
    similar_leads = context.get("similar_leads", [])

    drafter = EmailDrafter()

    if action == "draft":
        if not email_type:
            email_type = drafter.get_email_type(context)
        result = drafter.draft_email(lead_or_case, email_type, similar_leads)
    else:
        email_type = drafter.get_email_type(context)
        result = drafter.draft_email(lead_or_case, email_type, similar_leads)

    return {
        "skill": "email_drafter",
        "result": result,
    }
