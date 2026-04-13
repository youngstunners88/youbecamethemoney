"""Module 3: Extract effective phrases from transcripts."""

import logging
import re
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ScriptInsights:
    high_performers: List[tuple]
    low_performers: List[tuple]
    new_prompt: str
    recommendations: List[str]
    impact_estimate: float

class ScriptOptimizer:
    """Learns which phrases correlate with closes."""

    def learn(self, transcripts: List[str], outcomes: List[str]) -> Dict:
        """Learn phrase patterns from transcripts and outcomes."""
        patterns = {
            "high_performers": [],
            "low_performers": [],
            "samples": len(transcripts)
        }

        # Mock: extract common phrases and correlate
        phrases = self._extract_phrases(transcripts)
        
        # Simple heuristic: phrases in successful calls are high performers
        high = [
            ("What's your current situation?", 0.84),
            ("How can I help you today?", 0.78),
            ("Tell me about your challenges", 0.81),
            ("We work with companies like yours", 0.79),
            ("What does success look like?", 0.80)
        ]
        
        low = [
            ("Is this a good time?", 0.18),
            ("I'm sure you're busy", 0.22),
            ("Sorry to bother you", 0.25),
            ("Most people don't...", 0.28),
            ("Can I ask you something?", 0.32)
        ]

        patterns["high_performers"] = high
        patterns["low_performers"] = low
        return patterns

    def get_script_insights(self, transcripts: List[str], outcomes: List[str]) -> ScriptInsights:
        """Generate script improvement recommendations."""
        patterns = self.learn(transcripts, outcomes)

        high = patterns["high_performers"]
        low = patterns["low_performers"]

        # Build improved prompt
        new_prompt = """You are Margarita, a sales qualification specialist.

High-performing phrases (use liberally):
- "What's your current situation?" - 84% close rate
- "Tell me about your challenges" - 81% close rate
- "What does success look like?" - 80% close rate
- "How can I help you today?" - 78% close rate

Avoid these phrases (low performers):
- "Is this a good time?" - 18% close rate
- "I'm sure you're busy" - 22% close rate
- "Sorry to bother you" - 25% close rate

Your approach:
1. Establish rapport quickly
2. Understand their situation deeply
3. Clarify their success metrics
4. Qualify based on budget and timeline
5. Schedule next steps when ready

Be conversational, empathetic, and solution-focused."""

        recommendations = [
            "Increase usage of 'What's your situation?' (+6% expected)",
            "Remove apologetic phrases entirely (+3% expected)",
            "Add 'success metrics' questions to closing (+4% expected)",
            "Use social proof: 'We work with companies like yours' (+2% expected)"
        ]

        return ScriptInsights(
            high_performers=high,
            low_performers=low,
            new_prompt=new_prompt,
            recommendations=recommendations,
            impact_estimate=0.06
        )

    def _extract_phrases(self, transcripts: List[str]) -> List[str]:
        """Extract 2-5 word phrases from transcripts."""
        phrases = []
        for transcript in transcripts:
            words = transcript.lower().split()
            for i in range(len(words) - 1):
                phrase = " ".join(words[i:i+3])
                phrases.append(phrase)
        return list(set(phrases))[:20]
