"""
Skill 6: interview_analyzer.py
Analyzes Lemonslice video interviews for behavioral signals.
Updates warmth_score in leads table based on interview quality.
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
class BehaviorProfile:
    tone_confidence: float      # 0–100
    tone_urgency: float         # 0–100
    knowledge_level: int        # 1–10
    hesitation_score: float     # 0–100 (lower = more confident)
    stated_urgency: str         # immediate | week | month | unknown
    stated_amount: Optional[int]
    stated_jurisdiction: Optional[str]
    key_signals: list           # top 3 behavioral signals
    warmth_delta: float         # -20 to +30, applied to warmth_score
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


# ── Core analyzer ─────────────────────────────────────────────

class InterviewAnalyzer:
    """
    Analyzes transcripts + video metadata from Lemonslice interviews.
    Uses Claude API to extract behavioral signals.
    Falls back to rule-based scoring if API unavailable.
    """

    SYSTEM_PROMPT = """You are a behavioral analyst specializing in commercial law client intake.
Analyze the interview transcript and extract behavioral signals.

Return JSON only — no markdown, no explanation.

Schema:
{
  "tone_confidence": <0-100>,
  "tone_urgency": <0-100>,
  "knowledge_level": <1-10>,
  "hesitation_score": <0-100>,
  "stated_urgency": "<immediate|week|month|unknown>",
  "stated_amount": <integer or null>,
  "stated_jurisdiction": "<state/country or null>",
  "key_signals": ["signal1", "signal2", "signal3"],
  "warmth_delta": <-20 to 30>,
  "summary": "<2-sentence behavioral summary>"
}

Scoring guidance:
- tone_confidence: How clearly and directly they describe their situation
- tone_urgency: How time-sensitive their language suggests the matter is
- knowledge_level: Their understanding of the legal/financial issue (1=none, 10=expert)
- hesitation_score: Pauses, contradictions, vagueness (higher = more hesitant)
- warmth_delta: Overall interview quality vs baseline. +20 for strong case, -10 for weak signals."""

    def analyze(self, interview_id: str, video_url: str, transcript: str,
                 lead_id: str = "", current_warmth: float = 50.0) -> InterviewAnalysisResult:
        """
        Main entry point. Analyzes interview and returns behavior profile.
        """
        if not transcript or len(transcript.strip()) < 50:
            return self._error_result(interview_id, lead_id, current_warmth, "Transcript too short")

        # Try Claude API first
        profile = self._analyze_with_claude(transcript)

        # Fall back to rule-based if API fails
        if profile is None:
            logger.warning("Claude API unavailable — using rule-based analyzer")
            profile = self._analyze_rule_based(transcript)

        new_warmth = max(0.0, min(100.0, current_warmth + profile.warmth_delta))

        return InterviewAnalysisResult(
            interview_id=interview_id,
            lead_id=lead_id,
            profile=profile,
            warmth_score_before=current_warmth,
            warmth_score_after=new_warmth,
            success=True
        )

    def _analyze_with_claude(self, transcript: str) -> Optional[BehaviorProfile]:
        """Send transcript to Claude API and parse response."""
        if not ANTHROPIC_API_KEY:
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=800,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": f"Transcript:\n\n{transcript[:4000]}"}]
            )
            raw = msg.content[0].text.strip()
            data = json.loads(raw)
            return self._dict_to_profile(data)
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return None

    def _analyze_rule_based(self, transcript: str) -> BehaviorProfile:
        """
        Rule-based fallback when Claude API unavailable.
        Uses keyword patterns and text statistics.
        """
        text = transcript.lower()
        words = text.split()
        total = len(words)

        # Confidence signals
        confident_phrases = ["i need", "i want", "my situation is", "specifically", "the amount is",
                             "my deadline", "i understand", "we are ready"]
        hesitant_phrases = ["i think", "maybe", "i'm not sure", "perhaps", "kind of", "sort of",
                            "possibly", "i guess", "um", "uh", "you know"]

        conf_hits = sum(1 for p in confident_phrases if p in text)
        hesit_hits = sum(1 for p in hesitant_phrases if p in text)

        tone_confidence = min(100.0, 40.0 + (conf_hits * 8) - (hesit_hits * 4))
        hesitation_score = min(100.0, max(0.0, 30 + hesit_hits * 6))

        # Urgency signals
        urgent_words = ["urgent", "immediately", "asap", "today", "tomorrow", "emergency",
                        "deadline", "critical", "must", "need now"]
        urgency_hits = sum(1 for w in urgent_words if w in text)
        tone_urgency = min(100.0, 20.0 + urgency_hits * 15)

        stated_urgency = "unknown"
        if any(w in text for w in ["immediately", "today", "asap", "right now"]):
            stated_urgency = "immediate"
        elif any(w in text for w in ["this week", "few days", "next week"]):
            stated_urgency = "week"
        elif any(w in text for w in ["next month", "30 days", "month"]):
            stated_urgency = "month"

        # Knowledge level
        legal_terms = ["ucc", "article 3", "promissory note", "breach", "jurisdiction",
                       "plaintiff", "defendant", "statute", "liability", "fiduciary"]
        knowledge_hits = sum(1 for t in legal_terms if t in text)
        knowledge_level = min(10, max(1, 3 + knowledge_hits * 1))

        # Amount extraction
        amount_match = re.search(r'\$[\d,]+|\d[\d,]+\s*(?:dollars|k\b)', text)
        stated_amount = None
        if amount_match:
            raw = re.sub(r'[^\d]', '', amount_match.group())
            stated_amount = int(raw) if raw else None

        # Jurisdiction
        us_states = ["california", "texas", "new york", "florida", "illinois"]
        stated_jurisdiction = None
        for state in us_states:
            if state in text:
                stated_jurisdiction = state.title()
                break
        if "south africa" in text:
            stated_jurisdiction = "South Africa"

        # Warmth delta
        warmth_delta = 0.0
        if tone_confidence > 60: warmth_delta += 10
        if tone_urgency > 60: warmth_delta += 8
        if knowledge_level >= 6: warmth_delta += 7
        if hesitation_score > 70: warmth_delta -= 10
        if stated_urgency == "immediate": warmth_delta += 10
        if stated_amount and stated_amount > 10000: warmth_delta += 5

        key_signals = []
        if conf_hits > 2: key_signals.append("Clear, direct communication style")
        if urgency_hits > 1: key_signals.append("Time-sensitive situation")
        if knowledge_hits > 1: key_signals.append("Prior legal/financial knowledge")
        if hesit_hits > 3: key_signals.append("Some uncertainty about details")
        if len(key_signals) == 0: key_signals = ["Standard intake communication"]

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
            summary=f"Confidence: {tone_confidence:.0f}/100. Urgency: {tone_urgency:.0f}/100. Knowledge: {knowledge_level}/10.",
            analyzed_at=datetime.utcnow().isoformat()
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
            analyzed_at=datetime.utcnow().isoformat()
        )

    def _error_result(self, interview_id, lead_id, warmth, msg) -> InterviewAnalysisResult:
        return InterviewAnalysisResult(
            interview_id=interview_id, lead_id=lead_id,
            profile=BehaviorProfile(50,50,5,50,"unknown",None,None,[],0,"Error",datetime.utcnow().isoformat()),
            warmth_score_before=warmth, warmth_score_after=warmth,
            success=False, error=msg
        )


# ── Database persistence ───────────────────────────────────────

def save_analysis_to_db(result: InterviewAnalysisResult, db_conn) -> bool:
    """Persist analysis result to PostgreSQL."""
    try:
        cursor = db_conn.cursor()
        p = result.profile

        cursor.execute("""
            UPDATE client_interviews SET
              tone_confidence    = %s,
              tone_urgency       = %s,
              knowledge_level    = %s,
              hesitation_score   = %s,
              stated_urgency     = %s,
              stated_amount      = %s,
              stated_jurisdiction= %s,
              behavior_profile   = %s,
              warmth_delta       = %s,
              analyzed_at        = NOW()
            WHERE id = %s
        """, (
            p.tone_confidence, p.tone_urgency, p.knowledge_level,
            p.hesitation_score, p.stated_urgency, p.stated_amount,
            p.stated_jurisdiction, json.dumps(asdict(p)),
            p.warmth_delta, result.interview_id
        ))

        cursor.execute("""
            UPDATE leads SET
              warmth_score     = %s,
              behavior_profile = %s
            WHERE id = %s
        """, (result.warmth_score_after, json.dumps(asdict(p)), result.lead_id))

        db_conn.commit()
        cursor.close()
        logger.info(f"Interview {result.interview_id} saved. Warmth: {result.warmth_score_before} → {result.warmth_score_after}")
        return True
    except Exception as e:
        logger.error(f"DB save failed: {e}")
        db_conn.rollback()
        return False


# ── Public API ─────────────────────────────────────────────────

def analyze_interview(interview_id: str, video_url: str, transcript: str,
                      lead_id: str = "", current_warmth: float = 50.0) -> dict:
    """
    Main skill entry point called by Hermes.

    Args:
        interview_id: UUID of the client_interviews row
        video_url:    Lemonslice recording URL
        transcript:   Full interview transcript text
        lead_id:      UUID of the associated lead
        current_warmth: Lead's current warmth_score (0–100)

    Returns:
        dict with behavior_profile and updated warmth_score
    """
    analyzer = InterviewAnalyzer()
    result = analyzer.analyze(interview_id, video_url, transcript, lead_id, current_warmth)
    return {
        "success": result.success,
        "interview_id": result.interview_id,
        "lead_id": result.lead_id,
        "behavior_profile": asdict(result.profile),
        "warmth_score_before": result.warmth_score_before,
        "warmth_score_after": result.warmth_score_after,
        "error": result.error
    }


# ── Example / test ─────────────────────────────────────────────

if __name__ == "__main__":
    SAMPLE_TRANSCRIPT = """
    Interviewer: Can you tell me about your situation?
    Client: Yes. I have a promissory note for $85,000 that was issued in California.
            The maker defaulted three months ago. I need this resolved immediately —
            I have investors waiting on this. I understand the UCC Article 3 applies here.

    Interviewer: What's your timeline?
    Client: I need to file within 30 days or I lose the opportunity to claim full interest.
            This is urgent. I've already consulted one attorney who confirmed the jurisdiction.

    Interviewer: What's the amount in dispute?
    Client: The principal is $85,000 plus 18% interest, which brings it to about $97,000
            at this point. I have all the documentation ready.
    """

    result = analyze_interview(
        interview_id="test-interview-001",
        video_url="https://lemonslice.com/v/test",
        transcript=SAMPLE_TRANSCRIPT,
        lead_id="test-lead-001",
        current_warmth=60.0
    )

    print(json.dumps(result, indent=2))
