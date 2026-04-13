#!/usr/bin/env python3
"""
Tests for Lead Qualifier skill
"""

from lead_qualifier import LeadQualifier, LeadTemperature
import json


def test_hot_lead():
    """Test classification of a HOT lead"""
    qualifier = LeadQualifier()

    result = qualifier.qualify_lead(
        transcript="Ready to hire. When can we start? How much does it cost? I'm ready to move forward.",
        engagement_score=9,
        problem_awareness_score=9,
        decision_readiness_score=9,
        service_type="UCC Discharge",
    )

    assert result["temperature"] == "hot"
    assert result["confidence"] > 0.8
    print("✅ HOT lead test passed")


def test_warm_lead():
    """Test classification of a WARM lead"""
    qualifier = LeadQualifier()

    result = qualifier.qualify_lead(
        transcript="This is interesting. Tell me more about how this works. Makes sense so far.",
        engagement_score=7,
        problem_awareness_score=7,
        decision_readiness_score=5,
        service_type="Securitization Review",
    )

    assert result["temperature"] == "warm"
    assert result["confidence"] > 0.5
    print("✅ WARM lead test passed")


def test_luke_lead():
    """Test classification of a LUKE lead"""
    qualifier = LeadQualifier()

    result = qualifier.qualify_lead(
        transcript="Maybe, I guess. Could be useful. Not sure yet though. I need to think about this.",
        engagement_score=4,
        problem_awareness_score=4,
        decision_readiness_score=2,
        service_type="Creditor Strategy",
    )

    assert result["temperature"] == "luke"
    print("✅ LUKE lead test passed")


def test_cold_lead():
    """Test classification of a COLD lead"""
    qualifier = LeadQualifier()

    result = qualifier.qualify_lead(
        transcript="Not interested. No thanks. Stop calling please.",
        engagement_score=1,
        problem_awareness_score=1,
        decision_readiness_score=0,
        service_type="General Inquiry",
    )

    assert result["temperature"] == "cold"
    print("✅ COLD lead test passed")


def test_batch_qualify():
    """Test batch qualification"""
    qualifier = LeadQualifier()

    leads = [
        {
            "lead_id": "lead_001",
            "transcript": "Ready to hire now. What's next?",
            "engagement_score": 9,
            "problem_awareness_score": 9,
            "decision_readiness_score": 9,
            "service_type": "UCC Discharge",
        },
        {
            "lead_id": "lead_002",
            "transcript": "Maybe. Need to think about it.",
            "engagement_score": 4,
            "problem_awareness_score": 4,
            "decision_readiness_score": 2,
            "service_type": "General",
        },
    ]

    results = qualifier.batch_qualify(leads)

    assert len(results) == 2
    assert results[0]["qualification"]["temperature"] == "hot"
    assert results[1]["qualification"]["temperature"] == "luke"
    print("✅ Batch qualification test passed")


def test_follow_up_templates():
    """Test follow-up email templates for each temperature"""
    qualifier = LeadQualifier()

    for temp in ["hot", "warm", "luke", "cold"]:
        template = qualifier._get_follow_up_template(temp)
        assert "Subject:" in template
        assert len(template) > 50
        print(f"✅ {temp.upper()} template generated: {len(template)} chars")


if __name__ == "__main__":
    print("Running Lead Qualifier tests...\n")

    test_hot_lead()
    test_warm_lead()
    test_luke_lead()
    test_cold_lead()
    test_batch_qualify()
    test_follow_up_templates()

    print("\n✅ All tests passed!")
