"""
Skill 6: interview_analyzer.py
Analyzes Lemonslice interview transcripts for behavioral signals.
Updates warmth_score in leads table. Logs execution to skills_audit.

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


# ── Data models ────────────────────────────────────────────────────────────────

@dataclass
class BehaviorProfile:
    tone_confidence: float      # 0–100: clarity + directness
    tone_urgency: float         # 0–100: time-pressure signals
    knowledge_level: int        # 1–10: legal/financial term usage
    hesitation_score: float     # 0–100: vagueness + contradiction (higher = worse)
    stated_urgency: str         # immediate | week | month | unknown
    stated_amount: Optional[int]
    stated_jurisdiction: Optional[str]
    key_signals: list[str]      # top 3 behavioral signals for Margarita
    warmth_delta: float         # -20 to +30 applied to warmth_score
    summary: str
    analyzed_at: str


@dataclass
class InterviewAnalysisResult:
    interview_id: str
    lead_id: str
    profile: BehaviorProfile
    warmth_score_before: float
    warmth_score_after: float
    success: bool
    error: Optional[str] = None


# ── Skill class ────────────────────────────────────────────────────────────────

class InterviewAnalyzerSkill(BaseSkill):
    """
    Skill 6 — Interview Analyzer.
    Analyzes Lemonslice interview transcripts using Claude API (rule-based fallback).
    Updates lead warmth_score and behavior_profile in PostgreSQL.
    Logs every execution to skills_audit.
    """

    skill_name = "interview_analyzer"

    SYSTEM_PROMPT = (
        "You are a behavioral analyst specializing in commercial law client intake.\n"
        "Analyze the interview transcript and extract behavioral signals.\n\n"
        "Return JSON only — no markdown, no explanation.\n\n"
        "Schema:\n"
        '{\n'
        '  "tone_confidence": <0-100>,\n'
        '  "tone_urgency": <0-100>,\n'
        '  "knowledge_level": <1-10>,\n'
        '  "hesitation_score": <0-100>,\n'
        '  "stated_urgency": "<immediate|week|month|unknown>",\n'
        '  "stated_amount": <integer or null>,\n'
        '  "stated_jurisdiction": "<state/country or null>",\n'
        '  "key_signals": ["signal1", "signal2", "signal3"],\n'
        '  "warmth_delta": <-20 to 30>,\n'
        '  "summary": "<2-sentence behavioral summary>"\n'
        "}\n\n"
        "Scoring guidance:\n"
        "- tone_confidence: How clearly and directly they describe their situation\n"
        "- tone_urgency: How time-sensitive their language suggests the matter is\n"
        "- knowledge_level: Their understanding of the legal/financial issue (1=none, 10=expert)\n"
        "- hesitation_score: Pauses, contradictions, vagueness (higher = more hesitant)\n"
        "- warmth_delta: +20 for strong case signals, -10 for weak/vague signals"
    )

    def analyze(
        self,
        interview_id: str,
        transcript: str,
        lead_id: str = "",
        video_url: str = "",
        current_warmth: float = 50.0,
    ) -> dict:
        """
        Main skill entry point. Called by Hermes or interview_api.py.

        Args:
            interview_id:    UUID of the client_interviews row
            transcript:      Full Q&A text from Lemonslice portal
            lead_id:         UUID of the associated lead
            video_url:       Lemonslice video URL (stored, not analyzed)
            current_warmth:  Lead's current warmth_score (0–100)

        Returns:
            dict matching InterviewAnalysisResult shape + extracted fields
        """
        t0 = time.monotonic()
        input_payload = {
            "interview_id": interview_id,
            "lead_id": lead_id,
            "transcript_length": len(transcript),
            "current_warmth": current_warmth,
        }

        if not transcript or len(transcript.strip()) < 30:
            result = self._error_result(interview_id, lead_id, current_warmth, "Transcript too short")
            self._audit(input_payload, result, t0, success=False, error=result["error"])
            return result

        # Claude first, rule-based fallback
        profile = self._analyze_with_claude(transcript)
        if profile is None:
            self.logger.warning("Claude unavailable — using rule-based analyzer")
            profile = self._analyze_rule_based(transcript)

        new_warmth = max(0.0, min(100.0, current_warmth + profile.warmth_delta))

        output = {
            "success": True,
            "interview_id": interview_id,
            "lead_id": lead_id,
            "behavior_profile": asdict(profile),
            "warmth_score_before": current_warmth,
            "warmth_score_after": new_warmth,
            "warmth_delta": profile.warmth_delta,
            "extracted_service": self._extract_service(transcript),
            "extracted_jurisdiction": profile.stated_jurisdiction or "Unknown",
            "error": None,
        }

        # Persist to DB (non-fatal if fails)
        self._persist(interview_id, lead_id, profile, new_warmth, output)
        self._audit(input_payload, output, t0, success=True)

        return output

    # ── Claude analysis ────────────────────────────────────────────────────────

    def _analyze_with_claude(self, transcript: str) -> Optional[BehaviorProfile]:
        raw = self._call_claude(
            f"{self.SYSTEM_PROMPT}\n\nTranscript:\n\n{transcript[:4000]}",
            max_tokens=800,
        )
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            return self._dict_to_profile(data)
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Claude response parse error: {e}")
            return None

    # ── Rule-based analysis ────────────────────────────────────────────────────

    def _analyze_rule_based(self, transcript: str) -> BehaviorProfile:
        text = transcript.lower()

        confident_phrases = [
            "i need", "i want", "my situation is", "specifically",
            "the amount is", "my deadline", "i understand", "we are ready",
            "definitely", "absolutely", "immediately",
        ]
        hesitant_phrases = [
            "i think", "maybe", "i'm not sure", "perhaps", "kind of",
            "sort of", "possibly", "i guess", "um", "uh", "you know",
        ]
        urgent_words = [
            "urgent", "immediately", "asap", "today", "emergency",
            "deadline", "critical", "must", "need now", "right away",
        ]
        legal_terms = [
            "ucc", "article 3", "promissory note", "breach", "jurisdiction",
            "plaintiff", "defendant", "statute", "liability", "fiduciary",
            "securitization", "discharge", "trust", "lien", "secured party",
        ]

        conf_hits = sum(1 for p in confident_phrases if p in text)
        hesit_hits = sum(1 for p in hesitant_phrases if p in text)
        urgency_hits = sum(1 for w in urgent_words if w in text)
        knowledge_hits = sum(1 for t in legal_terms if t in text)

        tone_confidence = min(100.0, max(0.0, 40.0 + conf_hits * 8 - hesit_hits * 4))
        hesitation_score = min(100.0, max(0.0, 30.0 + hesit_hits * 6))
        tone_urgency = min(100.0, max(0.0, 20.0 + urgency_hits * 15))
        knowledge_level = min(10, max(1, 3 + knowledge_hits))

        # Stated urgency
        stated_urgency = "unknown"
        if any(w in text for w in ["immediately", "today", "asap", "right now"]):
            stated_urgency = "immediate"
        elif any(w in text for w in ["this week", "few days", "next week"]):
            stated_urgency = "week"
        elif any(w in text for w in ["next month", "30 days", "within the month"]):
            stated_urgency = "month"

        # Amount
        amount_match = re.search(r'\$[\d,]+|\d[\d,]+\s*(?:dollars|k\b)', text)
        stated_amount: Optional[int] = None
        if amount_match:
            raw_digits = re.sub(r'[^\d]', '', amount_match.group())
            stated_amount = int(raw_digits) if raw_digits else None

        # Jurisdiction
        jurisdictions = [
            "california", "texas", "new york", "florida", "illinois",
            "georgia", "north carolina", "ohio", "virginia", "south africa",
        ]
        stated_jurisdiction: Optional[str] = None
        for j in jurisdictions:
            if j in text:
                stated_jurisdiction = j.title()
                break

        # Warmth delta
        warmth_delta = 0.0
        if tone_confidence > 60:   warmth_delta += 10
        if tone_urgency > 60:      warmth_delta += 8
        if knowledge_level >= 6:   warmth_delta += 7
        if hesitation_score > 70:  warmth_delta -= 10
        if stated_urgency == "immediate": warmth_delta += 10
        if stated_amount and stated_amount > 10_000: warmth_delta += 5
        warmth_delta = max(-20.0, min(30.0, warmth_delta))

        key_signals: list[str] = []
        if conf_hits > 2:          key_signals.append("Clear, direct communication style")
        if urgency_hits > 1:       key_signals.append("Time-sensitive situation")
        if knowledge_hits > 1:     key_signals.append("Prior legal/financial knowledge")
        if hesit_hits > 3:         key_signals.append("Some uncertainty — needs guidance")
        if not key_signals:        key_signals = ["Standard intake communication"]

        return BehaviorProfile(
            tone_confidence=round(tone_confidence, 1),
            tone_urgency=round(tone_urgency, 1),
            knowledge_level=knowledge_level,
            hesitation_score=round(hesitation_score, 1),
            stated_urgency=stated_urgency,
            stated_amount=stated_amount,
            stated_jurisdiction=stated_jurisdiction,
            key_signals=key_signals[:3],
            warmth_delta=round(warmth_delta, 1),
            summary=f"Confidence {tone_confidence:.0f}/100 · Urgency {tone_urgency:.0f}/100 · Knowledge {knowledge_level}/10.",
            analyzed_at=datetime.utcnow().isoformat(),
        )

    def _dict_to_profile(self, data: dict) -> BehaviorProfile:
        return BehaviorProfile(
            tone_confidence=float(data.get("tone_confidence", 50)),
            tone_urgency=float(data.get("tone_urgency", 50)),
            knowledge_level=int(data.get("knowledge_level", 5)),
            hesitation_score=float(data.get("hesitation_score", 50)),
            stated_urgency=data.get("stated_urgency", "unknown"),
            stated_amount=data.get("stated_amount"),
            stated_jurisdiction=data.get("stated_jurisdiction"),
            key_signals=data.get("key_signals", []),
            warmth_delta=float(data.get("warmth_delta", 0)),
            summary=data.get("summary", ""),
            analyzed_at=datetime.utcnow().isoformat(),
        )

    def _extract_service(self, transcript: str) -> str:
        """Heuristic: pull the most mentioned service type."""
        text = transcript.lower()
        services = {
            "UCC Discharge": ["ucc", "article 3", "discharge"],
            "Securitization Review": ["securitization", "securitized"],
            "Trust Verification": ["trust", "trustee", "beneficiary"],
            "Secured Party Creditor": ["secured party", "creditor"],
            "Contract Dispute": ["contract", "breach", "agreement"],
            "Debt Enforcement": ["debt", "collection", "enforcement"],
        }
        scores = {svc: sum(1 for kw in kws if kw in text) for svc, kws in services.items()}
        best = max(scores, key=lambda k: scores[k])
        return best if scores[best] > 0 else "Commercial Law"

    # ── Persistence ────────────────────────────────────────────────────────────

    def _persist(
        self,
        interview_id: str,
        lead_id: str,
        profile: BehaviorProfile,
        new_warmth: float,
        output: dict,
    ) -> None:
        conn = self._get_db_conn()
        if conn is None:
            return
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """UPDATE client_interviews SET
                         tone_confidence=%(tc)s, tone_urgency=%(tu)s,
                         knowledge_level=%(kl)s, hesitation_score=%(hs)s,
                         stated_urgency=%(su)s, stated_amount=%(sa)s,
                         stated_jurisdiction=%(sj)s, behavior_profile=%(bp)s,
                         warmth_delta=%(wd)s, analyzed_at=NOW()
                       WHERE id=%(id)s""",
                    dict(
                        tc=profile.tone_confidence, tu=profile.tone_urgency,
                        kl=profile.knowledge_level, hs=profile.hesitation_score,
                        su=profile.stated_urgency, sa=profile.stated_amount,
                        sj=profile.stated_jurisdiction,
                        bp=json.dumps(asdict(profile)),
                        wd=profile.warmth_delta, id=interview_id,
                    ),
                )
                if lead_id:
                    cur.execute(
                        """UPDATE leads SET warmth_score=%(ws)s, behavior_profile=%(bp)s
                           WHERE id=%(id)s""",
                        dict(ws=new_warmth, bp=json.dumps(asdict(profile)), id=lead_id),
                    )
            conn.commit()
            self.logger.info(f"Interview {interview_id}: warmth updated to {new_warmth}")
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
                         (skill_name, lead_id, interview_id, input_payload, output_payload,
                          success, error_message, duration_ms)
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

    def _error_result(self, interview_id: str, lead_id: str, warmth: float, msg: str) -> dict:
        return {
            "success": False,
            "interview_id": interview_id,
            "lead_id": lead_id,
            "behavior_profile": None,
            "warmth_score_before": warmth,
            "warmth_score_after": warmth,
            "warmth_delta": 0,
            "extracted_service": "Unknown",
            "extracted_jurisdiction": "Unknown",
            "error": msg,
        }


# ── Public entry point (called by Hermes + interview_api.py) ──────────────────

def analyze_interview(
    interview_id: str,
    transcript: str,
    lead_id: str = "",
    video_url: str = "",
    current_warmth: float = 50.0,
) -> dict:
    """Module-level entry point for Hermes skill dispatch."""
    return InterviewAnalyzerSkill().analyze(
        interview_id=interview_id,
        transcript=transcript,
        lead_id=lead_id,
        video_url=video_url,
        current_warmth=current_warmth,
    )


# ── Smoke test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    SAMPLE = """
Q1: Describe your situation.
A: I have a promissory note for $85,000 issued in California. The maker defaulted three months ago.
   I need this resolved immediately — I have investors waiting. I understand UCC Article 3 applies.

Q2: What type of legal matter?
A: UCC Discharge

Q3: Amount at stake?
A: $50,000–$250,000

Q4: How urgent?
A: Immediate — action needed this week

Q5: Jurisdiction?
A: California

Q6: Prior legal action?
A: Yes, I have

Q7: Documentation ready?
A: Yes — fully organized

Q8: Desired outcome?
A: I need to enforce the note and recover $97,000 including accrued interest.
    """

    result = analyze_interview(
        interview_id="test-interview-001",
        transcript=SAMPLE,
        lead_id="test-lead-001",
        current_warmth=60.0,
    )
    print(json.dumps(result, indent=2, default=str))
