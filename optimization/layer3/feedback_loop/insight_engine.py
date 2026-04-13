"""
Insight Engine: Combines all 3 learning modules into actionable insights.

Data → Module1 → Data
Data → Module2 → Data
Data → Module3 → Data
     ↓
 Combine insights (ranked by confidence × impact)
     ↓
 Filter contradictions
     ↓
 Generate 3-5 actionable changes
     ↓
 Send to Hermes
"""

from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass
class Insight:
    """A single actionable insight"""
    module: str                  # conversion_predictor, optimal_timing, script_optimizer
    finding: str                 # Human-readable finding
    action: str                  # What Hermes should do
    confidence: float            # 0-1
    impact_estimate: float       # Expected improvement %
    samples: int                 # Data points supporting this


class InsightEngine:
    """
    Combine insights from 3 modules into a coherent improvement strategy.
    """

    def __init__(self, config=None):
        self.config = config
        self.min_confidence = 0.75  # Only act if 75%+ confident

    def synthesize_insights(
        self,
        conversion_output: dict,
        timing_output: dict,
        script_output: dict,
    ) -> List[Insight]:
        """
        Combine outputs from all 3 modules into ranked insights.

        Returns: Top 5 insights ranked by (confidence × impact)
        """

        insights = []

        # Extract insights from conversion_predictor
        if conversion_output.get("patterns", {}).get("by_temperature"):
            insights.extend(self._extract_conversion_insights(conversion_output))

        # Extract insights from optimal_timing
        if timing_output.get("by_hour"):
            insights.extend(self._extract_timing_insights(timing_output))

        # Extract insights from script_optimizer
        if script_output.get("high_performers"):
            insights.extend(self._extract_script_insights(script_output))

        # Filter low-confidence insights
        insights = [i for i in insights if i.confidence >= self.min_confidence]

        # Rank by (confidence × impact)
        insights.sort(
            key=lambda x: x.confidence * x.impact_estimate,
            reverse=True
        )

        # Return top 5
        return insights[:5]

    def _extract_conversion_insights(self, output: dict) -> List[Insight]:
        """Extract insights from conversion predictor."""
        insights = []

        patterns = output.get("patterns", {})
        by_temp = patterns.get("by_temperature", {})

        # Insight 1: Hot leads are highly predictable
        if "hot" in by_temp and by_temp["hot"]["close_rate"] > 0.70:
            insights.append(Insight(
                module="conversion_predictor",
                finding="Hot leads close at 70%+ rate",
                action="Prioritize hot leads for immediate action",
                confidence=0.85,
                impact_estimate=0.05,  # 5% improvement expected
                samples=by_temp["hot"]["samples"],
            ))

        # Insight 2: Luke leads are weak
        if "luke" in by_temp and by_temp["luke"]["close_rate"] < 0.40:
            insights.append(Insight(
                module="conversion_predictor",
                finding="Luke leads have low conversion (40%-)",
                action="Route luke leads to drip campaigns, not immediate calls",
                confidence=0.80,
                impact_estimate=0.03,
                samples=by_temp["luke"]["samples"],
            ))

        return insights

    def _extract_timing_insights(self, output: dict) -> List[Insight]:
        """Extract insights from optimal_timing module."""
        insights = []

        by_hour = output.get("by_hour", {})

        # Find best and worst hours
        if by_hour:
            best_hour = max(by_hour.items(), key=lambda x: x[1].get("success_rate", 0))
            worst_hour = min(by_hour.items(), key=lambda x: x[1].get("success_rate", 1))

            # Insight: Time matters significantly
            if best_hour[1]["success_rate"] - worst_hour[1]["success_rate"] > 0.25:
                insights.append(Insight(
                    module="optimal_timing",
                    finding=f"Best hour ({best_hour[0]}:00) is {(best_hour[1]['success_rate'] - worst_hour[1]['success_rate']):.0%} better than worst ({worst_hour[0]}:00)",
                    action=f"Batch calls into {best_hour[0]}:00 time windows",
                    confidence=0.82,
                    impact_estimate=0.04,
                    samples=best_hour[1].get("total_calls", 0),
                ))

        return insights

    def _extract_script_insights(self, output: dict) -> List[Insight]:
        """Extract insights from script_optimizer."""
        insights = []

        high_perf = output.get("high_performers", [])
        low_perf = output.get("low_performers", [])

        # Insight 1: Use high-performing phrases
        if high_perf:
            avg_rate = sum(p[1] for p in high_perf) / len(high_perf)
            top_phrases = [p[0] for p in high_perf[:3]]
            insights.append(Insight(
                module="script_optimizer",
                finding=f"Top phrases average {avg_rate:.0%} close rate: {', '.join(top_phrases)}",
                action="Increase frequency of high-performing phrases in Margarita's script",
                confidence=0.88,
                impact_estimate=0.06,
                samples=len(high_perf),
            ))

        # Insight 2: Remove low-performing phrases
        if low_perf:
            worst_phrases = [p[0] for p in low_perf[:3]]
            insights.append(Insight(
                module="script_optimizer",
                finding=f"Bottom phrases average <30% rate: {', '.join(worst_phrases)}",
                action="Remove or rephrase low-performing phrases",
                confidence=0.85,
                impact_estimate=0.03,
                samples=len(low_perf),
            ))

        return insights

    def build_action_plan(self, insights: List[Insight]) -> dict:
        """
        Convert insights into specific Hermes actions.

        Returns: {
            "script_updates": [...],
            "routing_rules": [...],
            "parameter_changes": [...],
        }
        """

        actions = {
            "script_updates": [],
            "routing_rules": [],
            "parameter_changes": [],
        }

        for insight in insights:
            if insight.module == "script_optimizer":
                actions["script_updates"].append({
                    "finding": insight.finding,
                    "action": insight.action,
                    "confidence": insight.confidence,
                })

            elif insight.module == "optimal_timing":
                actions["routing_rules"].append({
                    "finding": insight.finding,
                    "action": insight.action,
                    "confidence": insight.confidence,
                })

            elif insight.module == "conversion_predictor":
                actions["parameter_changes"].append({
                    "finding": insight.finding,
                    "action": insight.action,
                    "confidence": insight.confidence,
                })

        return actions

    def estimate_weekly_impact(self, insights: List[Insight]) -> dict:
        """
        Estimate total impact of all insights combined.

        Returns: expected improvement metrics
        """

        total_impact = sum(i.impact_estimate for i in insights)

        return {
            "total_estimated_improvement": total_impact,
            "estimated_new_close_rate": 0.185 + total_impact,  # baseline + improvement
            "num_insights": len(insights),
            "avg_confidence": sum(i.confidence for i in insights) / len(insights) if insights else 0,
        }


# Example
if __name__ == "__main__":
    sample_conversion = {
        "patterns": {
            "by_temperature": {
                "hot": {"close_rate": 0.78, "samples": 32},
                "luke": {"close_rate": 0.35, "samples": 25},
            }
        }
    }

    sample_timing = {
        "by_hour": {
            9: {"success_rate": 0.87, "total_calls": 24},
            18: {"success_rate": 0.43, "total_calls": 22},
        }
    }

    sample_script = {
        "high_performers": [
            ("What's your current situation", 0.84),
            ("The force of nature is with you", 0.79),
        ],
        "low_performers": [
            ("Is this a good time", 0.18),
            ("I'm sure you're busy", 0.22),
        ],
    }

    engine = InsightEngine()
    insights = engine.synthesize_insights(sample_conversion, sample_timing, sample_script)

    print("TOP INSIGHTS:")
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. [{insight.module}] {insight.finding}")
        print(f"   Action: {insight.action}")
        print(f"   Confidence: {insight.confidence:.0%} | Impact: +{insight.impact_estimate:.1%}")

    actions = engine.build_action_plan(insights)
    impact = engine.estimate_weekly_impact(insights)

    print(f"\n\nESTIMATED WEEKLY IMPACT:")
    print(f"  Current close rate: 18.5%")
    print(f"  Expected new rate: {impact['estimated_new_close_rate']:.1%}")
    print(f"  Total improvement: +{impact['total_estimated_improvement']:.1%}")
