"""
Skill: Email Drafter
Context-aware legal responses that teach + qualify leads
Generates professional, persuasive correspondence
"""

import logging
from typing import Dict, Any

log = logging.getLogger(__name__)

class EmailDrafter:
    """Draft professional legal emails that educate and qualify."""

    EMAIL_TEMPLATES = {
        "initial_response": """
Dear {client_name},

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
        "demand_letter": """
{date}

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
        "follow_up_warm": """
Dear {client_name},

I hope this message finds you well. I wanted to follow up on our recent conversation about your {case_type} matter.

I've had a chance to think more about your situation, and I believe there are several strategies we could pursue that might be advantageous given {specific_circumstances}.

The key issue here is {key_issue}, and here's why it matters for your case:

{issue_explanation}

I think it would be valuable to discuss this further. I'm available for a call {proposed_times}.

Looking forward to continuing our conversation.

Best regards,
Daniel Garcia
""",
        "referral": """
Dear {client_name},

Thank you for contacting our office regarding your {case_type} matter.

After careful consideration, I believe your situation may be better served by a specialist in {referral_specialty}. While {reason_for_referral}, I want to ensure you have the best possible representation.

I'm referring you to {referral_attorney_name} at {referral_firm}, who specializes in this area and has an excellent track record.

{referral_attorney_name} is expecting to hear from you, and I've given them a heads up that you'll be calling.

Best of luck with your matter.

Best regards,
Daniel Garcia
""",
    }

    def draft_initial_response(self, lead: Dict[str, Any]) -> str:
        """Draft initial response to new lead inquiry."""
        template = self.EMAIL_TEMPLATES["initial_response"]

        # Extract key information
        client_name = lead.get("name", "Client")
        case_type = lead.get("service_type", "legal matter")
        key_issues = lead.get("key_issues", "commercial law issues")

        return template.format(
            client_name=client_name,
            case_type=case_type,
            key_issues=key_issues,
        )

    def draft_demand_letter(self, case: Dict[str, Any]) -> str:
        """Draft formal demand letter."""
        from datetime import datetime, timedelta

        template = self.EMAIL_TEMPLATES["demand_letter"]

        deadline = datetime.now() + timedelta(days=30)

        return template.format(
            date=datetime.now().strftime("%B %d, %Y"),
            defendant_name=case.get("defendant_name", "[Defendant Name]"),
            defendant_address=case.get("defendant_address", "[Address]"),
            defendant_contact=case.get("defendant_contact", "Sir or Madam"),
            client_name=case.get("client_name", "Client"),
            case_title=case.get("title", "Matter"),
            case_description=case.get("description", "[Case Description]"),
            resolution_attempts=case.get("resolution_attempts", "multiple good faith attempts"),
            facts_summary=case.get("facts", "[Facts Summary]"),
            legal_basis=case.get("legal_basis", "[Legal Basis]"),
            relief_requested=case.get("relief", "[Relief Requested]"),
            deadline_date=deadline.strftime("%B %d, %Y"),
            applicable_privilege=case.get("privilege", "applicable privilege"),
            firm_details=case.get("firm_details", "Daniel Garcia, Attorney at Law"),
        )

    def draft_follow_up(self, lead: Dict[str, Any], context: str = "") -> str:
        """Draft warm follow-up to engaged lead."""
        template = self.EMAIL_TEMPLATES["follow_up_warm"]

        client_name = lead.get("name", "Client")
        case_type = lead.get("service_type", "matter")
        specific_circumstances = lead.get("circumstances", "the circumstances of your case")
        key_issue = lead.get("key_issue", "the central legal issue")
        issue_explanation = lead.get("issue_explanation", "[Issue Explanation]")

        return template.format(
            client_name=client_name,
            case_type=case_type,
            specific_circumstances=specific_circumstances,
            key_issue=key_issue,
            issue_explanation=issue_explanation,
            proposed_times=lead.get("proposed_times", "at your earliest convenience"),
        )

    def draft_referral(self, lead: Dict[str, Any], reason: str = "") -> str:
        """Draft polite referral to another attorney."""
        template = self.EMAIL_TEMPLATES["referral"]

        client_name = lead.get("name", "Client")
        case_type = lead.get("service_type", "matter")
        referral_specialty = lead.get("referral_specialty", "your specific legal issue")
        referral_attorney = lead.get("referral_attorney", "[Attorney Name]")
        referral_firm = lead.get("referral_firm", "[Firm Name]")

        return template.format(
            client_name=client_name,
            case_type=case_type,
            referral_specialty=referral_specialty,
            reason_for_referral=reason or "this is outside our current focus areas",
            referral_attorney_name=referral_attorney,
            referral_firm=referral_firm,
        )

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
    """Main entry point for Hermes skill."""
    action = context.get("action", "")
    lead_or_case = context.get("lead") or context.get("case", {})

    drafter = EmailDrafter()

    if "initial_response" in action:
        email = drafter.draft_initial_response(lead_or_case)
        email_type = "initial_response"
    elif "demand_letter" in action:
        email = drafter.draft_demand_letter(lead_or_case)
        email_type = "demand_letter"
    elif "follow_up" in action:
        email = drafter.draft_follow_up(lead_or_case, context.get("context", ""))
        email_type = "follow_up"
    elif "referral" in action:
        email = drafter.draft_referral(lead_or_case, context.get("reason", ""))
        email_type = "referral"
    else:
        # Auto-detect type
        email_type = drafter.get_email_type(context)
        if email_type == "initial_response":
            email = drafter.draft_initial_response(lead_or_case)
        elif email_type == "demand_letter":
            email = drafter.draft_demand_letter(lead_or_case)
        elif email_type == "follow_up_warm":
            email = drafter.draft_follow_up(lead_or_case)
        else:
            email = drafter.draft_referral(lead_or_case)

    return {
        "skill": "email_drafter",
        "email_type": email_type,
        "draft": email,
        "ready_to_send": True,
    }
