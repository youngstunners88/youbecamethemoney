"""
Tests for interview_analyzer.py (Skill 6).
Run: cd optimization/skills && pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from interview_analyzer import InterviewAnalyzerSkill, analyze_interview


STRONG_TRANSCRIPT = """
Q1: Describe your situation.
A: I have a promissory note for $85,000 issued in California. The maker defaulted.
   I need this resolved immediately. I understand UCC Article 3 applies.

Q2: Matter type? A: UCC Discharge
Q3: Amount? A: $50,000–$250,000
Q4: Urgency? A: Immediate — action needed this week
Q5: Jurisdiction? A: California
Q6: Prior action? A: Yes, I have
Q7: Documentation? A: Yes — fully organized
Q8: Desired outcome?
A: I need to enforce the note and recover $97,000 with interest.
"""

WEAK_TRANSCRIPT = """
Q1: Describe your situation.
A: I'm not sure... maybe I have some kind of debt issue. I think it might be around $5,000?
   I guess I'm wondering if this is something you can help with perhaps.

Q2: Matter type? A: Other
Q3: Amount? A: Under $10,000
Q4: Urgency? A: Exploratory — just researching
Q5: Jurisdiction? A: Not certain
Q6: Prior action? A: No, this would be my first step
Q7: Documentation? A: No documentation exists
Q8: Desired outcome? A: I'm not really sure what I want to happen.
"""


class TestRuleBasedAnalysis:

    def setup_method(self):
        self.skill = InterviewAnalyzerSkill()

    def test_strong_transcript_high_confidence(self):
        profile = self.skill._analyze_rule_based(STRONG_TRANSCRIPT)
        assert profile.tone_confidence >= 50, "Strong transcript should score high confidence"

    def test_strong_transcript_positive_warmth_delta(self):
        profile = self.skill._analyze_rule_based(STRONG_TRANSCRIPT)
        assert profile.warmth_delta > 0, "Strong case should produce positive warmth delta"

    def test_strong_transcript_detects_jurisdiction(self):
        profile = self.skill._analyze_rule_based(STRONG_TRANSCRIPT)
        assert profile.stated_jurisdiction == "California"

    def test_strong_transcript_detects_urgency(self):
        profile = self.skill._analyze_rule_based(STRONG_TRANSCRIPT)
        assert profile.stated_urgency == "immediate"

    def test_strong_transcript_detects_amount(self):
        profile = self.skill._analyze_rule_based(STRONG_TRANSCRIPT)
        assert profile.stated_amount is not None
        assert profile.stated_amount > 10_000

    def test_weak_transcript_lower_warmth_delta(self):
        strong_profile = self.skill._analyze_rule_based(STRONG_TRANSCRIPT)
        weak_profile = self.skill._analyze_rule_based(WEAK_TRANSCRIPT)
        assert strong_profile.warmth_delta > weak_profile.warmth_delta

    def test_warmth_delta_within_bounds(self):
        for transcript in [STRONG_TRANSCRIPT, WEAK_TRANSCRIPT]:
            profile = self.skill._analyze_rule_based(transcript)
            assert -20 <= profile.warmth_delta <= 30, f"Delta {profile.warmth_delta} out of bounds"

    def test_key_signals_list_not_empty(self):
        profile = self.skill._analyze_rule_based(STRONG_TRANSCRIPT)
        assert isinstance(profile.key_signals, list)
        assert len(profile.key_signals) >= 1

    def test_key_signals_max_3(self):
        profile = self.skill._analyze_rule_based(STRONG_TRANSCRIPT)
        assert len(profile.key_signals) <= 3

    def test_scores_in_valid_range(self):
        for transcript in [STRONG_TRANSCRIPT, WEAK_TRANSCRIPT]:
            p = self.skill._analyze_rule_based(transcript)
            assert 0 <= p.tone_confidence <= 100
            assert 0 <= p.tone_urgency <= 100
            assert 0 <= p.hesitation_score <= 100
            assert 1 <= p.knowledge_level <= 10


class TestServiceExtraction:

    def setup_method(self):
        self.skill = InterviewAnalyzerSkill()

    def test_extracts_ucc_service(self):
        service = self.skill._extract_service("I have a UCC Article 3 promissory note issue")
        assert "UCC" in service

    def test_extracts_securitization(self):
        service = self.skill._extract_service("I need a securitization review of my mortgage")
        assert "Securitization" in service

    def test_defaults_to_commercial_law(self):
        service = self.skill._extract_service("I just need legal help")
        assert service == "Commercial Law"


class TestFullIntegration:

    def test_analyze_interview_returns_dict(self):
        result = analyze_interview(
            interview_id="test-001",
            transcript=STRONG_TRANSCRIPT,
            lead_id="lead-001",
            current_warmth=50.0,
        )
        assert isinstance(result, dict)

    def test_analyze_interview_success_true(self):
        result = analyze_interview("test-001", STRONG_TRANSCRIPT, "lead-001")
        assert result["success"] is True

    def test_analyze_interview_has_required_keys(self):
        result = analyze_interview("test-001", STRONG_TRANSCRIPT, "lead-001")
        required = {"success", "interview_id", "behavior_profile", "warmth_score_before",
                    "warmth_score_after", "warmth_delta", "extracted_service", "extracted_jurisdiction"}
        assert required.issubset(result.keys())

    def test_short_transcript_returns_error(self):
        result = analyze_interview("test-001", "hi", "lead-001")
        assert result["success"] is False
        assert result["error"] is not None

    def test_warmth_score_after_within_bounds(self):
        result = analyze_interview("test-001", STRONG_TRANSCRIPT, current_warmth=90.0)
        assert 0 <= result["warmth_score_after"] <= 100

    def test_warmth_increases_for_strong_transcript(self):
        result = analyze_interview("test-001", STRONG_TRANSCRIPT, current_warmth=50.0)
        assert result["warmth_score_after"] >= result["warmth_score_before"]

    def test_interview_id_preserved(self):
        result = analyze_interview("my-interview-uuid", STRONG_TRANSCRIPT)
        assert result["interview_id"] == "my-interview-uuid"
