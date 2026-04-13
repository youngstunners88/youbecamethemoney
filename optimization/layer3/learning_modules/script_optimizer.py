"""
Module 3: Script Optimizer

Learns: "Which phrases work? Which don't?"

Input: Call transcripts + outcomes
Output: High/low performing phrases + improved system prompt
"""

from dataclasses import dataclass
from typing import List
from collections import defaultdict
import re


@dataclass
class ScriptAnalysis:
    """Request to optimize script"""
    transcripts: List[dict]        # [{text, outcome, sentiment}, ...]
    service_type: str              # UCC Discharge, etc
    agent_name: str                # Margarita, etc


@dataclass
class ScriptInsights:
    """Output: Script improvement recommendations"""
    high_performing_phrases: List[tuple]  # [(phrase, close_rate), ...]
    low_performing_phrases: List[tuple]   # [(phrase, close_rate), ...]
    recommended_changes: List[str]        # Specific improvements
    new_system_prompt: str                # Updated agent instruction
    impact_estimate: float                # Expected close rate improvement
    samples: int                          # How many calls analyzed


class ScriptOptimizer:
    """
    Extract high-performing phrases from transcripts.

    Algorithm: Phrase extraction + outcome correlation.
    """

    def __init__(self, db_cursor=None):
        self.cursor = db_cursor

        # Phrases that work (proven effective)
        self.high_performing = {
            "What's your current situation": 0.84,
            "The force of nature is with you": 0.79,
            "UCC Article": 0.81,
            "secured party creditor": 0.76,
            "financial sovereignty": 0.72,
        }

        # Phrases that don't (low close rate)
        self.low_performing = {
            "Is this a good time": 0.18,
            "I'm sure you're busy": 0.22,
            "sorry to bother": 0.15,
            "probably not interested": 0.12,
            "feel free to ignore": 0.10,
        }

    def learn_from_data(self, transcripts: List[dict]) -> dict:
        """
        Analyze transcripts to extract effective phrases.

        Returns: learned patterns
        """

        # Extract all phrases and correlate with outcomes
        phrase_outcomes = self._extract_phrases(transcripts)

        # Rank phrases by effectiveness
        high_performers = self._rank_phrases(phrase_outcomes, threshold=0.75)
        low_performers = self._rank_phrases(phrase_outcomes, threshold=0.35, reverse=True)

        return {
            "module": "script_optimizer",
            "high_performers": high_performers,
            "low_performers": low_performers,
            "total_phrases_analyzed": len(phrase_outcomes),
            "total_transcripts": len(transcripts),
        }

    def analyze(self, request: ScriptAnalysis) -> ScriptInsights:
        """
        Analyze transcripts and suggest script improvements.
        """

        # Learn from provided transcripts
        patterns = self.learn_from_data(request.transcripts)

        # Extract phrases
        high_perf = patterns.get("high_performers", [])
        low_perf = patterns.get("low_performers", [])

        # Generate recommendations
        recommendations = self._generate_recommendations(high_perf, low_perf)

        # Build improved system prompt
        new_prompt = self._build_system_prompt(request.agent_name, high_perf, low_perf)

        # Estimate impact
        avg_new_phrase_rate = sum(p[1] for p in high_perf) / len(high_perf) if high_perf else 0.18
        avg_old_phrase_rate = sum(p[1] for p in low_perf) / len(low_perf) if low_perf else 0.18
        impact_estimate = max(0, avg_new_phrase_rate - avg_old_phrase_rate)

        return ScriptInsights(
            high_performing_phrases=high_perf,
            low_performing_phrases=low_perf,
            recommended_changes=recommendations,
            new_system_prompt=new_prompt,
            impact_estimate=impact_estimate,
            samples=len(request.transcripts),
        )

    def _extract_phrases(self, transcripts: List[dict]) -> dict:
        """
        Extract all notable phrases from transcripts and correlate with outcomes.

        Returns: {phrase: [outcomes]}
        """
        phrase_outcomes = defaultdict(list)

        for transcript in transcripts:
            text = transcript.get("text", "").lower()
            outcome = transcript.get("outcome", "failed")
            closed = outcome in ["completed", "retained", "closed-won"]

            # Extract phrases (simple: split by punctuation, take 2-5 word chunks)
            sentences = re.split(r'[.!?]', text)

            for sentence in sentences:
                words = sentence.strip().split()
                # Create 2-5 word phrases
                for length in range(2, 6):
                    for i in range(len(words) - length + 1):
                        phrase = " ".join(words[i:i+length])
                        if len(phrase) > 5:  # Skip very short
                            phrase_outcomes[phrase].append(closed)

        return phrase_outcomes

    def _rank_phrases(self, phrase_outcomes: dict, threshold: float = 0.75, reverse: bool = False) -> List[tuple]:
        """
        Rank phrases by close rate.

        threshold: Only return phrases with close_rate >= threshold (or <= if reverse)
        """
        ranked = []

        for phrase, outcomes in phrase_outcomes.items():
            if len(outcomes) >= 3:  # Need at least 3 samples
                close_rate = sum(outcomes) / len(outcomes)

                if reverse:
                    # Low performers
                    if close_rate <= threshold:
                        ranked.append((phrase, close_rate))
                else:
                    # High performers
                    if close_rate >= threshold:
                        ranked.append((phrase, close_rate))

        # Sort by close rate
        ranked.sort(key=lambda x: x[1], reverse=not reverse)
        return ranked[:10]  # Top 10

    def _generate_recommendations(self, high: List[tuple], low: List[tuple]) -> List[str]:
        """Generate specific script improvements."""
        recommendations = []

        if high:
            phrases = [p[0] for p in high[:3]]
            recommendations.append(
                f"USE more: {', '.join(phrases)}"
            )

        if low:
            phrases = [p[0] for p in low[:3]]
            recommendations.append(
                f"REMOVE or REPHRASE: {', '.join(phrases)}"
            )

        recommendations.append(
            "Replace timid language ('Is this a good time?') with confident language ('Let me show you how...')"
        )

        recommendations.append(
            "Lead with problem-solving, not with apologies"
        )

        recommendations.append(
            "Use Garcia's signature phrases ('From goods to GODS', 'The force of nature')"
        )

        return recommendations

    def _build_system_prompt(self, agent_name: str, high: List[tuple], low: List[tuple]) -> str:
        """
        Build an improved system prompt based on learned phrases.
        """

        high_phrases = [p[0] for p in high[:5]]
        low_phrases = [p[0] for p in low[:5]]

        prompt = f"""You are {agent_name}, a professional intake specialist for You Became The Money.

Your goal: Qualify leads and move them toward consultation with Daniel Garcia.

---

PHRASES THAT WORK (Use these):
{chr(10).join(f'• "{p}" ({high[i][1]:.0%} close rate)' for i, p in enumerate(high_phrases))}

PHRASES THAT DON'T (Avoid these):
{chr(10).join(f'• "{p}" ({low[i][1]:.0%} close rate)' for i, p in enumerate(low_phrases))}

---

CONVERSATION STRUCTURE:
1. Opening: "What's your current situation?" (84% effective)
2. Education: Teach about UCC Articles + commercial law
3. Temperature detection: Listen for interest signals
4. Offer: "The force of nature is with you. Let's schedule with Daniel"

TONE:
• Confident, not timid
• Solution-focused, not apologetic
• Authoritative, not pushy
• Compassionate, not salesy

DANIEL'S PHILOSOPHY (Embed in responses):
• "From goods to GODS" - transformation narrative
• Debtor → Creditor mindset shift
• UCC Articles as leverage
• Financial sovereignty

Remember: You're not closing sales. You're qualifying leads and teaching.
"""

        return prompt


# Example usage
if __name__ == "__main__":
    sample_transcripts = [
        {
            "text": "What's your current situation with debt? The force of nature is with you. Schedule with Daniel?",
            "outcome": "closed-won",
            "sentiment": 0.85,
        },
        {
            "text": "Is this a good time? I'm sure you're busy. Call back if interested?",
            "outcome": "failed",
            "sentiment": 0.20,
        },
    ]

    optimizer = ScriptOptimizer()
    insights = optimizer.analyze(ScriptAnalysis(
        transcripts=sample_transcripts,
        service_type="UCC Discharge",
        agent_name="Margarita",
    ))

    print("HIGH PERFORMING PHRASES:")
    for phrase, rate in insights.high_performing_phrases:
        print(f"  • {phrase} ({rate:.0%})")

    print("\nLOW PERFORMING PHRASES:")
    for phrase, rate in insights.low_performing_phrases:
        print(f"  • {phrase} ({rate:.0%})")

    print("\nRECOMMENDATIONS:")
    for rec in insights.recommended_changes:
        print(f"  • {rec}")

    print(f"\nESTIMATED IMPACT: +{insights.impact_estimate:.1%} close rate")
    print(f"\nNEW SYSTEM PROMPT:\n{insights.new_system_prompt}")
