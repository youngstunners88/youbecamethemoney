"""
Skill 7: hall_of_fame_curator.py
When a case closes successfully, creates a public Hall of Fame profile.
Extracts key quotes, generates testimonial, publishes to dashboard.
"""

import os
import json
import logging
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# ── Data models ───────────────────────────────────────────────

@dataclass
class HallOfFameProfile:
    lead_id: str
    interview_id: str
    case_outcome: str           # won | settled | referred
    case_value: int
    key_quotes: list            # 2–3 anonymized quotes from transcript
    testimonial: str            # generated 2–3 sentence testimonial
    headline: str               # short punchy headline for the card
    jurisdiction: Optional[str]
    service_type: Optional[str]
    published: bool
    created_at: str


# ── Quote extractor ───────────────────────────────────────────

def _extract_quotes_rule_based(transcript: str, n: int = 3) -> list:
    """Extract strongest sentences from transcript as key quotes."""
    sentences = re.split(r'(?<=[.!?])\s+', transcript)
    # Score by length and presence of strong signal words
    signal_words = ["urgent", "need", "resolve", "ready", "understand", "immediately",
                    "amount", "deadline", "grateful", "professional", "result"]
    scored = []
    for s in sentences:
        s = s.strip()
        if 20 < len(s) < 200 and not s.lower().startswith("interviewer"):
            score = sum(1 for w in signal_words if w in s.lower())
            scored.append((score, s))
    scored.sort(reverse=True)
    return [s for _, s in scored[:n]]


# ── Testimonial generator ─────────────────────────────────────

def _generate_testimonial_rule_based(profile_data: dict) -> tuple:
    """Rule-based testimonial when Claude API unavailable."""
    outcome = profile_data.get("case_outcome", "resolved")
    value = profile_data.get("case_value", 0)
    jurisdiction = profile_data.get("jurisdiction", "")
    service = profile_data.get("service_type", "commercial matter")

    outcome_phrases = {
        "won": f"successfully resolved their {service}",
        "settled": f"reached a favorable settlement on their {service}",
        "referred": f"was connected with the right specialist for their {service}",
    }
    outcome_phrase = outcome_phrases.get(outcome, f"resolved their {service}")

    value_str = f"${value:,}" if value > 0 else "significant"

    testimonial = (
        f"Our client {outcome_phrase} in {jurisdiction + ' ' if jurisdiction else ''}with "
        f"{value_str} at stake. From the first interview, the team understood the urgency "
        f"and moved quickly. The outcome exceeded expectations."
    )
    headline = f"${value:,} {service.title()} — {outcome.title()}" if value else f"{service.title()} — {outcome.title()}"
    return testimonial, headline


def _generate_with_claude(transcript: str, profile_data: dict) -> Optional[tuple]:
    """Use Claude to generate a polished testimonial + headline."""
    if not ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = f"""You are writing a professional testimonial for a commercial law firm's Hall of Fame.

Case outcome: {profile_data.get('case_outcome')}
Case value: ${profile_data.get('case_value', 0):,}
Service type: {profile_data.get('service_type', 'commercial')}
Jurisdiction: {profile_data.get('jurisdiction', '')}

Key quotes from client interview:
{chr(10).join(profile_data.get('key_quotes', [])[:3])}

Write:
1. A 2–3 sentence professional testimonial (anonymized, third-person)
2. A short punchy headline (max 8 words)

Return JSON only:
{{"testimonial": "...", "headline": "..."}}"""

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        data = json.loads(msg.content[0].text.strip())
        return data["testimonial"], data["headline"]
    except Exception as e:
        logger.error(f"Claude testimonial failed: {e}")
        return None


# ── Main curator ──────────────────────────────────────────────

def curate_profile(lead_id: str, case_outcome: str, interview_id: str = "",
                   transcript: str = "", case_value: int = 0,
                   service_type: str = "", jurisdiction: str = "",
                   auto_publish: bool = True) -> dict:
    """
    Skill 7 entry point. Called by Hermes when a case closes.

    Args:
        lead_id:      UUID of the lead
        case_outcome: 'won' | 'settled' | 'referred'
        interview_id: UUID of the linked interview
        transcript:   Full interview transcript (for quote extraction)
        case_value:   Dollar value of the case
        service_type: Type of legal service
        jurisdiction: State/country
        auto_publish: Whether to publish immediately

    Returns:
        dict with the hall of fame profile
    """
    if case_outcome not in ("won", "settled", "referred"):
        return {"success": False, "error": f"Invalid outcome: {case_outcome}"}

    # Extract key quotes
    key_quotes = _extract_quotes_rule_based(transcript) if transcript else []

    # Build profile data for generation
    profile_data = {
        "case_outcome": case_outcome,
        "case_value": case_value,
        "service_type": service_type or "commercial matter",
        "jurisdiction": jurisdiction,
        "key_quotes": key_quotes,
    }

    # Generate testimonial
    result = _generate_with_claude(transcript, profile_data)
    if result:
        testimonial, headline = result
    else:
        testimonial, headline = _generate_testimonial_rule_based(profile_data)

    profile = HallOfFameProfile(
        lead_id=lead_id,
        interview_id=interview_id,
        case_outcome=case_outcome,
        case_value=case_value,
        key_quotes=key_quotes,
        testimonial=testimonial,
        headline=headline,
        jurisdiction=jurisdiction or None,
        service_type=service_type or None,
        published=auto_publish,
        created_at=datetime.utcnow().isoformat()
    )

    logger.info(f"Hall of Fame profile created for lead {lead_id}: {headline}")

    return {
        "success": True,
        "lead_id": lead_id,
        "interview_id": interview_id,
        "profile": asdict(profile),
        "published": auto_publish,
    }


def save_profile_to_db(profile_data: dict, db_conn) -> bool:
    """Persist Hall of Fame profile to PostgreSQL."""
    try:
        cursor = db_conn.cursor()
        p = profile_data["profile"]

        cursor.execute("""
            INSERT INTO hall_of_fame_profiles
              (lead_id, interview_id, case_outcome, case_value,
               key_quotes, testimonial, published, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT DO NOTHING
        """, (
            p["lead_id"], p["interview_id"] or None,
            p["case_outcome"], p["case_value"],
            json.dumps(p["key_quotes"]), p["testimonial"],
            p["published"]
        ))

        cursor.execute("""
            UPDATE leads SET hall_of_fame = TRUE WHERE id = %s
        """, (p["lead_id"],))

        db_conn.commit()
        cursor.close()
        logger.info(f"Hall of Fame profile saved for lead {p['lead_id']}")
        return True
    except Exception as e:
        logger.error(f"DB save failed: {e}")
        db_conn.rollback()
        return False


# ── Example ───────────────────────────────────────────────────

if __name__ == "__main__":
    SAMPLE_TRANSCRIPT = """
    Client: I had a promissory note for $85,000 that went into default. I need this resolved immediately.
    I understand UCC Article 3 applies. I have investors waiting and a 30-day deadline.
    The amount is $97,000 with interest. I have all documentation ready and I am grateful
    for the speed with which your team moved on this. The result exceeded my expectations.
    """

    result = curate_profile(
        lead_id="lead-001",
        case_outcome="won",
        interview_id="interview-001",
        transcript=SAMPLE_TRANSCRIPT,
        case_value=97000,
        service_type="UCC Article 3 Enforcement",
        jurisdiction="California",
        auto_publish=True
    )

    print(json.dumps(result, indent=2))
