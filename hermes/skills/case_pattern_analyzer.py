"""
Skill: Case Pattern Analyzer
Extracts learnings from closed cases
Feeds patterns back to lead scorer for continuous improvement
"""

import json
import logging
from typing import Dict, Any, List

log = logging.getLogger(__name__)

class CasePatternAnalyzer:
    """Extract patterns and learnings from closed cases."""

    def __init__(self):
        self.pattern_types = [
            "service_type_success_rate",
            "jurisdiction_patterns",
            "value_to_outcome_ratio",
            "time_to_resolution",
            "client_profile_success",
        ]

    def analyze_closed_cases(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze closed cases to extract learnings.

        Args:
            cases: List of closed case dictionaries from PostgreSQL

        Returns:
            Dict of patterns with confidence scores
        """
        if not cases:
            log.warning("No closed cases to analyze")
            return {"patterns": {}, "confidence": 0}

        patterns = {
            "service_type_patterns": self._analyze_service_types(cases),
            "jurisdiction_patterns": self._analyze_jurisdictions(cases),
            "value_patterns": self._analyze_case_values(cases),
            "timeline_patterns": self._analyze_timelines(cases),
            "success_factors": self._extract_success_factors(cases),
        }

        # Calculate overall confidence
        confidence = self._calculate_confidence(cases)

        return {
            "patterns": patterns,
            "confidence": confidence,
            "total_cases_analyzed": len(cases),
            "analysis_timestamp": self._get_timestamp(),
        }

    def _analyze_service_types(self, cases: List[Dict]) -> Dict[str, Any]:
        """Analyze success rates by service type."""
        type_stats = {}

        for case in cases:
            stype = case.get("service_type", "unknown")
            outcome = case.get("outcome", "")

            if stype not in type_stats:
                type_stats[stype] = {"closed": 0, "won": 0, "settled": 0, "lost": 0}

            type_stats[stype]["closed"] += 1

            if "won" in outcome.lower() or "favorable" in outcome.lower():
                type_stats[stype]["won"] += 1
            elif "settled" in outcome.lower():
                type_stats[stype]["settled"] += 1
            elif "lost" in outcome.lower():
                type_stats[stype]["lost"] += 1

        # Calculate success rates
        patterns = {}
        for stype, stats in type_stats.items():
            total = stats["closed"]
            won_or_settled = stats["won"] + stats["settled"]
            success_rate = won_or_settled / total if total > 0 else 0

            patterns[stype] = {
                "total_cases": total,
                "success_rate": round(success_rate, 2),
                "favorable_outcomes": won_or_settled,
                "unfavorable_outcomes": stats["lost"],
                "recommendation": self._rate_success(success_rate),
            }

        log.info(f"Analyzed {len(patterns)} service types")
        return patterns

    def _analyze_jurisdictions(self, cases: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns by jurisdiction."""
        jurisdiction_stats = {}

        for case in cases:
            jur = case.get("jurisdiction", "unknown")
            if jur not in jurisdiction_stats:
                jurisdiction_stats[jur] = {"cases": 0, "favorable": 0}

            jurisdiction_stats[jur]["cases"] += 1

            if any(word in case.get("outcome", "").lower() for word in ["won", "favorable", "settled"]):
                jurisdiction_stats[jur]["favorable"] += 1

        patterns = {}
        for jur, stats in jurisdiction_stats.items():
            success_rate = stats["favorable"] / stats["cases"] if stats["cases"] > 0 else 0
            patterns[jur] = {
                "cases": stats["cases"],
                "success_rate": round(success_rate, 2),
                "favorable": stats["favorable"],
            }

        return patterns

    def _analyze_case_values(self, cases: List[Dict]) -> Dict[str, Any]:
        """Analyze case value vs outcome patterns."""
        value_buckets = {
            "under_10k": {"count": 0, "favorable": 0},
            "10k_50k": {"count": 0, "favorable": 0},
            "50k_100k": {"count": 0, "favorable": 0},
            "over_100k": {"count": 0, "favorable": 0},
        }

        for case in cases:
            value = case.get("case_value", 0)
            favorable = "won" in case.get("outcome", "").lower() or "favorable" in case.get("outcome", "").lower()

            if value < 10000:
                bucket = "under_10k"
            elif value < 50000:
                bucket = "10k_50k"
            elif value < 100000:
                bucket = "50k_100k"
            else:
                bucket = "over_100k"

            value_buckets[bucket]["count"] += 1
            if favorable:
                value_buckets[bucket]["favorable"] += 1

        patterns = {}
        for bucket, stats in value_buckets.items():
            if stats["count"] > 0:
                success_rate = stats["favorable"] / stats["count"]
                patterns[bucket] = {
                    "cases": stats["count"],
                    "success_rate": round(success_rate, 2),
                    "recommendation": self._rate_success(success_rate),
                }

        return patterns

    def _analyze_timelines(self, cases: List[Dict]) -> Dict[str, Any]:
        """Analyze time to resolution patterns."""
        resolutions = []

        for case in cases:
            intake = case.get("intake_date")
            close = case.get("close_date")

            if intake and close:
                try:
                    # Calculate days to resolution
                    from datetime import datetime
                    intake_date = datetime.fromisoformat(intake) if isinstance(intake, str) else intake
                    close_date = datetime.fromisoformat(close) if isinstance(close, str) else close
                    days = (close_date - intake_date).days
                    resolutions.append(days)
                except:
                    pass

        if resolutions:
            avg_days = sum(resolutions) / len(resolutions)
            return {
                "avg_days_to_resolution": round(avg_days),
                "fastest_resolution_days": min(resolutions),
                "slowest_resolution_days": max(resolutions),
            }

        return {}

    def _extract_success_factors(self, cases: List[Dict]) -> List[str]:
        """Extract key success factors from winning cases."""
        factors = []

        winning_cases = [c for c in cases if "won" in c.get("outcome", "").lower()]

        if not winning_cases:
            return []

        # Analyze common characteristics of winning cases
        for case in winning_cases:
            stype = case.get("service_type", "")
            if stype:
                factors.append(f"Service type: {stype}")

            jur = case.get("jurisdiction", "")
            if jur:
                factors.append(f"Jurisdiction: {jur}")

        return list(set(factors))  # Remove duplicates

    def _calculate_confidence(self, cases: List[Dict]) -> float:
        """Calculate confidence in analysis based on sample size."""
        # More cases = higher confidence
        if len(cases) >= 50:
            return 0.95
        elif len(cases) >= 20:
            return 0.85
        elif len(cases) >= 10:
            return 0.70
        elif len(cases) >= 5:
            return 0.50
        else:
            return 0.30

    def _rate_success(self, rate: float) -> str:
        """Rate success rate."""
        if rate >= 0.8:
            return "STRONG"
        elif rate >= 0.6:
            return "MODERATE"
        elif rate >= 0.4:
            return "WEAK"
        else:
            return "POOR"

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for Hermes skill."""
    cases = context.get("closed_cases", [])

    analyzer = CasePatternAnalyzer()
    analysis = analyzer.analyze_closed_cases(cases)

    return {
        "skill": "case_pattern_analyzer",
        "analysis": analysis,
    }
