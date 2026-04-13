"""
Module 2: Optimal Timing

Learns: "When should we call each lead type?"

Input: Call timestamps + outcomes
Output: Best hours, best days, success rates per time
"""

from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict
from datetime import datetime


@dataclass
class TimingAnalysis:
    """Request to analyze when to call"""
    lead_source: str                # web, sms, telegram, organic
    service_type: str               # UCC Discharge, Securitization, etc
    lead_temperature: str           # hot, warm, luke, cold


@dataclass
class OptimalTiming:
    """Output: Best time to call this lead type"""
    best_hour: int                  # 0-23 (9 = 9am)
    best_day: str                   # Monday, Tuesday, etc
    success_rate_at_best: float     # 0-1
    worst_hour: int                 # Avoid this
    worst_day: str                  # Avoid this too
    success_rate_at_worst: float    # 0-1
    samples: int                    # How many calls informed this
    recommendations: List[str]      # Specific action items


class OptimalTimingModule:
    """
    Learn when calls are most successful.

    Algorithm: Empirical time binning by hour and day.
    """

    def __init__(self, db_cursor=None):
        self.cursor = db_cursor
        self.day_names = [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        ]

    def learn_from_data(self, call_records: List[dict]) -> dict:
        """
        Analyze when calls succeed best.

        Returns: learned patterns (to store in insights_db)
        """

        # Analyze by hour
        by_hour = self._analyze_by_hour(call_records)

        # Analyze by day
        by_day = self._analyze_by_day(call_records)

        # Analyze by service type + time
        by_service_time = self._analyze_by_service_and_time(call_records)

        return {
            "module": "optimal_timing",
            "by_hour": by_hour,
            "by_day": by_day,
            "by_service_time": by_service_time,
            "samples": len(call_records),
        }

    def recommend(self, request: TimingAnalysis) -> OptimalTiming:
        """
        Recommend best time to call this lead type.
        """

        # Mock data (in production, would query insights_db)
        # These would be learned patterns from actual data

        # Default learned patterns (placeholder)
        # In reality: SELECT * FROM learned_patterns WHERE module='optimal_timing'
        hot_leads_timing = {
            "best_hour": 9,  # 9am
            "best_day": "Monday",
            "best_success": 0.87,
            "worst_hour": 18,  # 6pm
            "worst_day": "Sunday",
            "worst_success": 0.43,
        }

        warm_leads_timing = {
            "best_hour": 13,  # 1pm
            "best_day": "Wednesday",
            "best_success": 0.72,
            "worst_hour": 17,  # 5pm
            "worst_day": "Friday",
            "worst_success": 0.38,
        }

        luke_leads_timing = {
            "best_hour": 10,  # 10am
            "best_day": "Tuesday",
            "best_success": 0.55,
            "worst_hour": 19,  # 7pm
            "worst_day": "Sunday",
            "worst_success": 0.22,
        }

        # Select based on lead type
        patterns = {
            "hot": hot_leads_timing,
            "warm": warm_leads_timing,
            "luke": luke_leads_timing,
            "cold": {"best_hour": 0, "best_success": 0},  # Don't call cold
        }

        best_pattern = patterns.get(request.lead_temperature, warm_leads_timing)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            request.lead_temperature,
            best_pattern,
        )

        return OptimalTiming(
            best_hour=best_pattern["best_hour"],
            best_day=best_pattern.get("best_day", "Monday"),
            success_rate_at_best=best_pattern["best_success"],
            worst_hour=best_pattern.get("worst_hour", 20),
            worst_day=best_pattern.get("worst_day", "Sunday"),
            success_rate_at_worst=best_pattern.get("worst_success", 0.2),
            samples=142,  # Mock
            recommendations=recommendations,
        )

    def _analyze_by_hour(self, call_records: List[dict]) -> Dict[int, dict]:
        """Calculate success rate for each hour of day."""
        by_hour = defaultdict(lambda: {"completed": 0, "total": 0})

        for call in call_records:
            # Extract hour from timestamp
            try:
                ts = datetime.fromisoformat(call["timestamp"])
                hour = ts.hour
            except:
                continue

            by_hour[hour]["total"] += 1
            if call["outcome"] == "completed":
                by_hour[hour]["completed"] += 1

        # Convert to success rates
        result = {}
        for hour, stats in by_hour.items():
            if stats["total"] > 0:
                result[hour] = {
                    "success_rate": stats["completed"] / stats["total"],
                    "total_calls": stats["total"],
                }

        return result

    def _analyze_by_day(self, call_records: List[dict]) -> Dict[str, dict]:
        """Calculate success rate for each day of week."""
        by_day = defaultdict(lambda: {"completed": 0, "total": 0})

        for call in call_records:
            # Extract day from timestamp
            try:
                ts = datetime.fromisoformat(call["timestamp"])
                day = self.day_names[ts.weekday()]
            except:
                continue

            by_day[day]["total"] += 1
            if call["outcome"] == "completed":
                by_day[day]["completed"] += 1

        # Convert to success rates
        result = {}
        for day, stats in by_day.items():
            if stats["total"] > 0:
                result[day] = {
                    "success_rate": stats["completed"] / stats["total"],
                    "total_calls": stats["total"],
                }

        return result

    def _analyze_by_service_and_time(self, call_records: List[dict]) -> dict:
        """Analyze timing effectiveness by service type."""
        by_service = defaultdict(lambda: {"hour": {}, "day": {}})

        for call in call_records:
            service = call.get("service_type", "unknown")

            try:
                ts = datetime.fromisoformat(call["timestamp"])
                hour = ts.hour
                day = self.day_names[ts.weekday()]
            except:
                continue

            # Track by hour
            if hour not in by_service[service]["hour"]:
                by_service[service]["hour"][hour] = {"completed": 0, "total": 0}

            by_service[service]["hour"][hour]["total"] += 1
            if call["outcome"] == "completed":
                by_service[service]["hour"][hour]["completed"] += 1

            # Track by day
            if day not in by_service[service]["day"]:
                by_service[service]["day"][day] = {"completed": 0, "total": 0}

            by_service[service]["day"][day]["total"] += 1
            if call["outcome"] == "completed":
                by_service[service]["day"][day]["completed"] += 1

        return dict(by_service)

    def _generate_recommendations(self, temp: str, pattern: dict) -> List[str]:
        """Generate specific recommendations based on pattern."""
        recommendations = []

        best_hour = pattern.get("best_hour", 9)
        worst_hour = pattern.get("worst_hour", 18)
        best_success = pattern.get("best_success", 0)

        # Recommendation 1: Timing window
        recommendations.append(
            f"Schedule {temp} leads between {best_hour}:00-{best_hour + 1}:00 "
            f"({best_success:.0%} success rate)"
        )

        # Recommendation 2: Avoid time
        worst_success = pattern.get("worst_success", 0)
        recommendations.append(
            f"Avoid calling {worst_hour}:00-{worst_hour + 1}:00 "
            f"({worst_success:.0%} success rate)"
        )

        # Recommendation 3: Route optimization
        if temp == "hot":
            recommendations.append("Route HOT leads to premium agent Margarita during best hours")
        elif temp == "warm":
            recommendations.append("Schedule WARM leads for follow-up at optimal times")

        # Recommendation 4: Batch calls
        recommendations.append(
            f"Batch {temp} lead calls into {best_hour}:00 time slots for efficiency"
        )

        return recommendations


# Example usage
if __name__ == "__main__":
    sample_calls = [
        {
            "timestamp": "2026-04-01T09:30:00",
            "outcome": "completed",
            "service_type": "UCC Discharge",
            "lead_temperature": "hot",
        },
        {
            "timestamp": "2026-04-01T18:30:00",
            "outcome": "failed",
            "service_type": "UCC Discharge",
            "lead_temperature": "hot",
        },
    ]

    module = OptimalTimingModule()
    patterns = module.learn_from_data(sample_calls)

    request = TimingAnalysis(
        lead_source="web",
        service_type="UCC Discharge",
        lead_temperature="hot",
    )

    timing = module.recommend(request)
    print(f"Best hour: {timing.best_hour}:00")
    print(f"Best day: {timing.best_day}")
    print(f"Success rate: {timing.success_rate_at_best:.0%}")
    print("\nRecommendations:")
    for rec in timing.recommendations:
        print(f"  • {rec}")
