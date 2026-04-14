"""
Skill 7: hall_of_fame_curator.py
Triggered by Hermes when a case closes (won / settled / referred).
Extracts key quotes, generates anonymized testimonial, publishes to hall_of_fame_profiles.
Logs execution to skills_audit.

Extends BaseSkill for shared DB, Claude API, and Hermes helpers.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

from base_skill import BaseSkill

VALID_OUTCOMES = frozenset({"won", "settled", "referred"})


# ── Data model ─────────────────────────────────────────────────────────────────

@dataclass
class HallOfFameProfile:
    lead_id: str
    interview_id: str
    case_outcome: str           # won | settled | referred
    case_value: int
    service_type: Optional[str]
    jurisdiction: Optional[str]
    key_quotes: list[str]       # 2–3 anonymized quotes from transcript
    testimonial: str            # 2–3 sentence professional testimonial
    headline: str               # short punchy headline for the card
    confidence_score: float     # 0–100: how strong the testimonial evidence is
    published: bool
    created_at: str


# ── Skill class ────────────────────────────────────────────────────────────────

class HallOfFameCuratorSkill(BaseSkill):
    """
    Skill 7 — Hall of Fame Curator.
    Generates anonymized public profiles for winning cases.
    Uses Claude API for polished testimonials; rule-based fallback.
    """

    skill_name = "hall_of_fame_curator"

    CLAUDE_PROMPT_TEMPLATE = """\
You are writing a professional testimonial for a commercial law firm's Hall of Fame page.
The client gave permission to share their anonymized success story.

Case details:
- Outcome: {outcome}
- Case value: ${value:,}
- Service type: {service}
- Jurisdiction: {jurisdiction}

Key quotes from client interview:
{quotes}

Write:
1. A 2–3 sentence professional testimonial (anonymized — no names; third-person)
2. A punchy headline (max 8 words)

Tone: confident, specific, outcome-focused. Not generic.

Return JSON only:
{{"testimonial": "...", "headline": "..."}}"""

    def curate(
        self,
        lead_id: str,
        case_outcome: str,
        interview_id: str = "",
        transcript: str = "",
        case_value: int = 0,
        service_type: str = "",
        jurisdiction: str = "",
        auto_publish: bool = True,
    ) -> dict:
        """
        Main skill entry point. Called by Hermes when case.outcome is set.

        Args:
            lead_id:       UUID of the lead
            case_outcome:  'won' | 'settled' | 'referred'
            interview_id:  UUID of the linked client_interviews row
            transcript:    Full interview transcript for quote extraction
            case_value:    Dollar value of the case
            service_type:  Type of legal service (e.g. 'UCC Discharge')
            jurisdiction:  State/country
            auto_publish:  Whether to publish to hall_of_fame_profiles immediately

        Returns:
            dict with success, profile, and published flag
        """
        t0 = time.monotonic()
        input_payload = {
            "lead_id": lead_id,
            "interview_id": interview_id,
            "case_outcome": case_outcome,
            "case_value": case_value,
            "service_type": service_type,
            "jurisdiction": jurisdiction,
        }

        if case_outcome not in VALID_OUTCOMES:
            error = f"Invalid outcome '{case_outcome}'. Must be: {', '.join(VALID_OUTCOMES)}"
            self._audit(input_payload, {"error": error}, t0, success=False, error=error)
            return {"success": False, "error": error}

        key_quotes = self._extract_quotes(transcript) if transcript else []
        confidence_score = self._score_evidence(transcript, key_quotes, case_value)

        profile_data = {
            "outcome": case_outcome,
            "value": case_value,
            "service": service_type or "commercial matter",
            "jurisdiction": jurisdiction or "Unknown",
            "quotes": "\n".join(f'- "{q}"' for q in key_quotes) or "(no transcript provided)",
        }

        testimonial, headline = self._generate_testimonial(transcript, profile_data)

        profile = HallOfFameProfile(
            lead_id=lead_id,
            interview_id=interview_id,
            case_outcome=case_outcome,
            case_value=case_value,
            service_type=service_type or None,
            jurisdiction=jurisdiction or None,
            key_quotes=key_quotes,
            testimonial=testimonial,
            headline=headline,
            confidence_score=round(confidence_score, 1),
            published=auto_publish,
            created_at=datetime.utcnow().isoformat(),
        )

        self.logger.info(f"Hall of Fame profile: lead={lead_id} headline='{headline}'")

        output = {
            "success": True,
            "lead_id": lead_id,
            "interview_id": interview_id,
            "profile": asdict(profile),
            "published": auto_publish,
        }

        self._persist(profile)
        self._audit(input_payload, output, t0, success=True)

        return output

    # ── Quote extraction ────────────────────────────────────────────────────────

    def _extract_quotes(self, transcript: str, n: int = 3) -> list[str]:
        """Extract strongest client sentences from transcript."""
        signal_words = [
            "urgent", "need", "resolve", "ready", "understand", "immediately",
            "amount", "deadline", "grateful", "professional", "result", "outcome",
            "excellent", "quickly", "exceeded", "recommend",
        ]
        sentences = re.split(r'(?<=[.!?])\s+', transcript)
        scored: list[tuple[int, str]] = []
        for s in sentences:
            s = s.strip()
            # Skip interviewer lines and too-short/long sentences
            if 20 < len(s) < 200 and not re.match(r'^(Q\d|Interviewer|A:)', s, re.IGNORECASE):
                score = sum(1 for w in signal_words if w in s.lower())
                scored.append((score, s))
        scored.sort(reverse=True)
        return [s for _, s in scored[:n]]

    # ── Evidence scoring ────────────────────────────────────────────────────────

    def _score_evidence(self, transcript: str, key_quotes: list[str], case_value: int) -> float:
        """Score how strong the testimonial evidence is (0–100)."""
        score = 40.0
        if transcript:            score += 20
        if len(key_quotes) >= 2:  score += 15
        if case_value > 50_000:   score += 15
        if case_value > 200_000:  score += 10
        return min(100.0, score)

    # ── Testimonial generation ──────────────────────────────────────────────────

    def _generate_testimonial(self, transcript: str, profile_data: dict) -> tuple[str, str]:
        """Try Claude first; fall back to rule-based."""
        prompt = self.CLAUDE_PROMPT_TEMPLATE.format(**profile_data)
        raw = self._call_claude(prompt, max_tokens=350)
        if raw:
            try:
                data = json.loads(raw)
                return data["testimonial"], data["headline"]
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Claude parse error — using rule-based: {e}")

        return self._rule_based_testimonial(profile_data)

    def _rule_based_testimonial(self, p: dict) -> tuple[str, str]:
        outcome_phrases = {
            "won":      f"successfully won their {p['service']}",
            "settled":  f"reached a favorable settlement on their {p['service']}",
            "referred": f"was connected with the right specialist for their {p['service']}",
        }
        phrase = outcome_phrases.get(p["outcome"], f"resolved their {p['service']}")
        loc = f"in {p['jurisdiction']} " if p["jurisdiction"] != "Unknown" else ""
        value_str = f"${p['value']:,}" if p["value"] > 0 else "significant stakes"

        testimonial = (
            f"Our client {phrase} {loc}with {value_str} at stake. "
            f"From the first consultation, the team understood the urgency and moved decisively. "
            f"The outcome exceeded expectations."
        )
        headline = (
            f"${p['value']:,} {p['service']} — {p['outcome'].title()}"
            if p["value"] > 0
            else f"{p['service']} — {p['outcome'].title()}"
        )
        return testimonial, headline

    # ── Persistence ────────────────────────────────────────────────────────────

    def _persist(self, profile: HallOfFameProfile) -> None:
        conn = self._get_db_conn()
        if conn is None:
            return
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO hall_of_fame_profiles
                         (lead_id, interview_id, case_outcome, case_value,
                          service_type, jurisdiction, key_quotes,
                          testimonial, headline, confidence_score, published, created_at)
                       VALUES (%(li)s, %(ii)s, %(co)s, %(cv)s, %(st)s, %(j)s,
                               %(kq)s, %(t)s, %(h)s, %(cs)s, %(pub)s, NOW())
                       ON CONFLICT (lead_id) DO UPDATE SET
                         testimonial=EXCLUDED.testimonial,
                         headline=EXCLUDED.headline,
                         published=EXCLUDED.published""",
                    dict(
                        li=profile.lead_id,
                        ii=profile.interview_id or None,
                        co=profile.case_outcome,
                        cv=profile.case_value,
                        st=profile.service_type,
                        j=profile.jurisdiction,
                        kq=json.dumps(profile.key_quotes),
                        t=profile.testimonial,
                        h=profile.headline,
                        cs=profile.confidence_score,
                        pub=profile.published,
                    ),
                )
                cur.execute(
                    "UPDATE leads SET hall_of_fame=TRUE WHERE id=%(id)s",
                    dict(id=profile.lead_id),
                )
            conn.commit()
            self.logger.info(f"Hall of Fame profile saved for lead {profile.lead_id}")
        except Exception as e:
            self.logger.error(f"DB persist failed: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _audit(self, input_payload: dict, output: dict, t0: float, success: bool, error: Optional[str] = None) -> None:
        duration_ms = int((time.monotonic() - t0) * 1000)
        conn = self._get_db_conn()
        if conn is None:
            self.logger.info(f"[AUDIT] {self.skill_name} success={success} duration={duration_ms}ms (no DB)")
            return
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO skills_audit
                         (skill_name, lead_id, interview_id, input_payload,
                          output_payload, success, error_message, duration_ms)
                       VALUES (%(sn)s, %(li)s, %(ii)s, %(ip)s, %(op)s, %(su)s, %(em)s, %(dm)s)""",
                    dict(
                        sn=self.skill_name,
                        li=input_payload.get("lead_id") or None,
                        ii=input_payload.get("interview_id") or None,
                        ip=json.dumps(input_payload),
                        op=json.dumps(output),
                        su=success,
                        em=error,
                        dm=duration_ms,
                    ),
                )
            conn.commit()
        except Exception as e:
            self.logger.warning(f"Audit log failed (non-fatal): {e}")
        finally:
            conn.close()


# ── Public entry point ─────────────────────────────────────────────────────────

def curate_profile(
    lead_id: str,
    case_outcome: str,
    interview_id: str = "",
    transcript: str = "",
    case_value: int = 0,
    service_type: str = "",
    jurisdiction: str = "",
    auto_publish: bool = True,
) -> dict:
    """Module-level entry point for Hermes skill dispatch."""
    return HallOfFameCuratorSkill().curate(
        lead_id=lead_id,
        case_outcome=case_outcome,
        interview_id=interview_id,
        transcript=transcript,
        case_value=case_value,
        service_type=service_type,
        jurisdiction=jurisdiction,
        auto_publish=auto_publish,
    )


# ── Smoke test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    SAMPLE = """
I had a promissory note for $85,000 that went into default. I needed this resolved immediately.
I understood UCC Article 3 applied. I had investors waiting and a 30-day deadline.
The amount with interest was $97,000. I had all documentation ready.
I am grateful for the speed with which the team moved on this.
The result absolutely exceeded my expectations. I would recommend this firm without hesitation.
    """

    result = curate_profile(
        lead_id="lead-001",
        case_outcome="won",
        interview_id="interview-001",
        transcript=SAMPLE,
        case_value=97_000,
        service_type="UCC Article 3 Enforcement",
        jurisdiction="California",
        auto_publish=True,
    )
    print(json.dumps(result, indent=2, default=str))
