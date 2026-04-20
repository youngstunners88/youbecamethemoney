"""
Skill: Case Pattern Analyzer (Jarvis-enabled)
Extracts patterns from closed cases + feeds back to hermes_memory.
Returns confidence scores + reasoning.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

log = logging.getLogger(__name__)


class CasePatternAnalyzer:
    """Extract patterns from closed cases with confidence."""

    def analyze_closed_cases(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cases to extract learnings + confidence scores."""
        if not cases:
            return {"patterns": {}, "confidence": 0, "reasoning": "No closed cases to analyze"}

        patterns = {
            "service_type_patterns": self._analyze_service_types(cases),
            "jurisdiction_patterns": self._analyze_jurisdictions(cases),
            "value_patterns": self._analyze_case_values(cases),
            "timeline_patterns": self._analyze_timelines(cases),
            "success_factors": self._extract_success_factors(cases),
        }

        confidence = self._calculate_confidence(cases)
        reasoning = self._generate_reasoning(patterns, cases)

        return {
            "patterns": patterns,
            "confidence": round(confidence, 1),
            "total_cases_analyzed": len(cases),
            "reasoning": reasoning,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def _analyze_service_types(self, cases: List[Dict]) -> Dict[str, Any]:
        """Analyze success rates by service type."""
        type_stats = {}
        for case in cases:
            stype = case.get("service_type", "unknown")
            outcome = case.get("outcome", "").lower()
            if stype not in type_stats:
                type_stats[stype] = {"closed": 0, "won": 0, "settled": 0, "lost": 0}
            type_stats[stype]["closed"] += 1
            if "won" in outcome or "favorable" in outcome:
                type_stats[stype]["won"] += 1
            elif "settled" in outcome:
                type_stats[stype]["settled"] += 1
            elif "lost" in outcome:
                type_stats[stype]["lost"] += 1

        patterns = {}
        for stype, stats in type_stats.items():
            total = stats["closed"]
            favorable = stats["won"] + stats["settled"]
            success_rate = favorable / total if total > 0 else 0
            patterns[stype] = {
                "total_cases": total,
                "success_rate": round(success_rate, 2),
                "favorable_outcomes": favorable,
                "recommendation": self._rate_success(success_rate),
                "confidence": min(0.95, total / 10),  # More cases = higher confidence
            }
        return patterns

    def _analyze_jurisdictions(self, cases: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns by jurisdiction."""
        jurisdiction_stats = {}
        for case in cases:
            jur = case.get("jurisdiction", "unknown")
            if jur not in jurisdiction_stats:
                jurisdiction_stats[jur] = {"cases": 0, "favorable": 0}
            jurisdiction_stats[jur]["cases"] += 1
            if any(w in case.get("outcome", "").lower() for w in ["won", "favorable", "settled"]):
                jurisdiction_stats[jur]["favorable"] += 1

        patterns = {}
        for jur, stats in jurisdiction_stats.items():
            success_rate = stats["favorable"] / stats["cases"] if stats["cases"] > 0 else 0
            patterns[jur] = {
                "cases": stats["cases"],
                "success_rate": round(success_rate, 2),
                "favorable": stats["favorable"],
                "confidence": min(0.95, stats["cases"] / 10),
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
                    "confidence": min(0.95, stats["count"] / 10),
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
                "confidence": min(0.95, len(resolutions) / 10),
            }
        return {}

    def _extract_success_factors(self, cases: List[Dict]) -> List[str]:
        """Extract key success factors from winning cases."""
        factors = []
        winning_cases = [c for c in cases if "won" in c.get("outcome", "").lower()]
        if not winning_cases:
            return []
        for case in winning_cases:
            stype = case.get("service_type", "")
            if stype:
                factors.append(f"Service: {stype}")
            jur = case.get("jurisdiction", "")
            if jur:
                factors.append(f"Jurisdiction: {jur}")
        return list(set(factors))[:5]

    def _calculate_confidence(self, cases: List[Dict]) -> float:
        """Calculate overall confidence based on sample size."""
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

    def _generate_reasoning(self, patterns: Dict, cases: List[Dict]) -> str:
        """Generate human-readable reasoning."""
        total = len(cases)
        service_types = patterns.get("service_type_patterns", {})
        best_stype = max(service_types.items(), key=lambda x: x[1].get("success_rate", 0), default=("N/A", {}))
        return f"Analyzed {total} closed cases. Best service type: {best_stype[0]} ({best_stype[1].get('success_rate', 0)}% success rate)."

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


def execute(context: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point."""
    cases = context.get("closed_cases", [])
    analyzer = CasePatternAnalyzer()
    analysis = analyzer.analyze_closed_cases(cases)
    return {"skill": "case_pattern_analyzer", "analysis": analysis}
