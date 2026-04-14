"""
Tests for hall_of_fame_curator.py (Skill 7).
Run: cd optimization/skills && pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from hall_of_fame_curator import HallOfFameCuratorSkill, curate_profile


SAMPLE_TRANSCRIPT = """
I had a promissory note for $85,000 that went into default. I needed this resolved immediately.
I understood UCC Article 3 applied. I had investors waiting and a 30-day deadline.
The amount with interest was $97,000. I had all documentation ready.
I am grateful for the speed with which the team moved. The result exceeded my expectations.
I would recommend this firm without hesitation to anyone in a similar situation.
"""


class TestQuoteExtraction:

    def setup_method(self):
        self.skill = HallOfFameCuratorSkill()

    def test_extracts_quotes_from_transcript(self):
        quotes = self.skill._extract_quotes(SAMPLE_TRANSCRIPT)
        assert isinstance(quotes, list)
        assert len(quotes) >= 1

    def test_quotes_max_3(self):
        quotes = self.skill._extract_quotes(SAMPLE_TRANSCRIPT, n=3)
        assert len(quotes) <= 3

    def test_quotes_are_strings(self):
        quotes = self.skill._extract_quotes(SAMPLE_TRANSCRIPT)
        assert all(isinstance(q, str) for q in quotes)

    def test_quotes_not_interviewer_lines(self):
        quotes = self.skill._extract_quotes(SAMPLE_TRANSCRIPT)
        for q in quotes:
            assert not q.startswith("Interviewer")
            assert not q.startswith("Q")

    def test_empty_transcript_returns_empty_list(self):
        assert self.skill._extract_quotes("") == []


class TestEvidenceScoring:

    def setup_method(self):
        self.skill = HallOfFameCuratorSkill()

    def test_score_with_transcript_higher_than_without(self):
        quotes = self.skill._extract_quotes(SAMPLE_TRANSCRIPT)
        score_with = self.skill._score_evidence(SAMPLE_TRANSCRIPT, quotes, 97_000)
        score_without = self.skill._score_evidence("", [], 0)
        assert score_with > score_without

    def test_score_within_bounds(self):
        quotes = self.skill._extract_quotes(SAMPLE_TRANSCRIPT)
        score = self.skill._score_evidence(SAMPLE_TRANSCRIPT, quotes, 97_000)
        assert 0 <= score <= 100

    def test_high_value_case_boosts_score(self):
        score_low = self.skill._score_evidence(SAMPLE_TRANSCRIPT, [], 5_000)
        score_high = self.skill._score_evidence(SAMPLE_TRANSCRIPT, [], 500_000)
        assert score_high > score_low


class TestTestimonialGeneration:

    def setup_method(self):
        self.skill = HallOfFameCuratorSkill()

    def test_rule_based_returns_tuple(self):
        result = self.skill._rule_based_testimonial({
            "outcome": "won",
            "value": 97_000,
            "service": "UCC Article 3 Enforcement",
            "jurisdiction": "California",
            "quotes": "",
        })
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_rule_based_testimonial_not_empty(self):
        testimonial, headline = self.skill._rule_based_testimonial({
            "outcome": "won", "value": 97_000,
            "service": "UCC Enforcement", "jurisdiction": "CA", "quotes": "",
        })
        assert len(testimonial) > 20
        assert len(headline) > 5

    def test_headline_includes_value_for_won_case(self):
        _, headline = self.skill._rule_based_testimonial({
            "outcome": "won", "value": 97_000,
            "service": "UCC", "jurisdiction": "CA", "quotes": "",
        })
        assert "$97,000" in headline

    def test_settled_case_headline(self):
        _, headline = self.skill._rule_based_testimonial({
            "outcome": "settled", "value": 50_000,
            "service": "Contract", "jurisdiction": "TX", "quotes": "",
        })
        assert "Settled" in headline


class TestFullIntegration:

    def test_curate_profile_returns_dict(self):
        result = curate_profile(
            lead_id="lead-001",
            case_outcome="won",
            transcript=SAMPLE_TRANSCRIPT,
            case_value=97_000,
            service_type="UCC Article 3 Enforcement",
            jurisdiction="California",
        )
        assert isinstance(result, dict)

    def test_curate_profile_success(self):
        result = curate_profile("lead-001", "won", transcript=SAMPLE_TRANSCRIPT)
        assert result["success"] is True

    def test_curate_profile_has_required_keys(self):
        result = curate_profile("lead-001", "won", transcript=SAMPLE_TRANSCRIPT)
        assert {"success", "lead_id", "profile", "published"}.issubset(result.keys())

    def test_profile_contains_testimonial(self):
        result = curate_profile("lead-001", "won", transcript=SAMPLE_TRANSCRIPT, case_value=97_000)
        assert result["success"]
        profile = result["profile"]
        assert isinstance(profile["testimonial"], str)
        assert len(profile["testimonial"]) > 20

    def test_invalid_outcome_returns_error(self):
        result = curate_profile("lead-001", "invalid_outcome")
        assert result["success"] is False
        assert "error" in result

    def test_won_outcome_accepted(self):
        result = curate_profile("lead-001", "won")
        assert result["success"] is True

    def test_settled_outcome_accepted(self):
        result = curate_profile("lead-001", "settled")
        assert result["success"] is True

    def test_referred_outcome_accepted(self):
        result = curate_profile("lead-001", "referred")
        assert result["success"] is True

    def test_published_flag_respected(self):
        result = curate_profile("lead-001", "won", auto_publish=False)
        assert result["profile"]["published"] is False

    def test_confidence_score_within_bounds(self):
        result = curate_profile("lead-001", "won", transcript=SAMPLE_TRANSCRIPT, case_value=97_000)
        score = result["profile"]["confidence_score"]
        assert 0 <= score <= 100
