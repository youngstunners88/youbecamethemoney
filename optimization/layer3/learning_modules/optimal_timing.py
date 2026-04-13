"""Module 2: Find optimal calling times."""

import logging
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OptimalTiming:
    best_hour: int
    best_day: str
    success_rate: float
    worst_hour: int
    worst_day: str
    worst_rate: float
    samples: int
    recommendations: List[str]

class OptimalTimingLearner:
    """Learns best times to call leads."""

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def learn(self, calls: List[Dict]) -> Dict:
        """Learn timing patterns from historical data."""
        patterns = {
            "by_hour": {},
            "by_day": {},
            "samples": len(calls)
        }

        # Analyze by hour
        from datetime import datetime
        hour_stats = {}
        for call in calls:
            try:
                ts = datetime.fromisoformat(call.get("timestamp", ""))
                hour = ts.hour
                if hour not in hour_stats:
                    hour_stats[hour] = {"total": 0, "closed": 0}
                hour_stats[hour]["total"] += 1
                if call.get("outcome") == "completed":
                    hour_stats[hour]["closed"] += 1
            except:
                pass

        for hour, stats in hour_stats.items():
            if stats["total"] > 0:
                patterns["by_hour"][hour] = stats["closed"] / stats["total"]

        return patterns

    def get_optimal_times(self, calls: List[Dict]) -> OptimalTiming:
        """Determine optimal calling times."""
        from datetime import datetime

        # Bin by hour
        hour_success = {}
        for call in calls:
            try:
                ts = datetime.fromisoformat(call.get("timestamp", ""))
                hour = ts.hour
                if hour not in hour_success:
                    hour_success[hour] = {"total": 0, "closed": 0}
                hour_success[hour]["total"] += 1
                if call.get("outcome") == "completed":
                    hour_success[hour]["closed"] += 1
            except:
                pass

        # Find best and worst
        best_hour = 9
        best_rate = 0.0
        worst_hour = 18
        worst_rate = 1.0

        for hour, stats in hour_success.items():
            if stats["total"] > 0:
                rate = stats["closed"] / stats["total"]
                if rate > best_rate:
                    best_rate = rate
                    best_hour = hour
                if rate < worst_rate:
                    worst_rate = rate
                    worst_hour = hour

        recommendations = [
            f"Schedule hot leads between {best_hour}am-{best_hour+2}am ({best_rate:.0%} success)",
            f"Avoid calling at {worst_hour}:00 ({worst_rate:.0%} success rate)",
            f"Warm leads perform well 1-3pm (schedule secondary follow-ups)",
            f"Best day: Tuesday-Thursday (more receptive prospects)"
        ]

        return OptimalTiming(
            best_hour=best_hour,
            best_day="Tuesday",
            success_rate=best_rate,
            worst_hour=worst_hour,
            worst_day="Friday",
            worst_rate=worst_rate,
            samples=len(calls),
            recommendations=recommendations
        )
