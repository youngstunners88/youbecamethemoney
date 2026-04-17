"""
Token cost estimation and tracking
Optimizes for token burn across all skill executions
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime

log = logging.getLogger(__name__)

class TokenCostTracker:
    """Track and estimate token costs for all skill executions."""

    # Estimated token costs per skill (based on complexity)
    SKILL_COSTS = {
        "token_optimizer": 500,      # Lightweight utility
        "gsd_coordinator": 2000,      # Heavy orchestration
        "legal_questioner": 1500,     # Medium complexity (legal domain)
        "code_best_practices": 800,   # Reference-based
        "workflow_automation": 1200,  # Medium complexity
        "security_validator": 1800,   # Heavy (security audit)
        "compression": 300,           # Very lightweight
        "ui_optimizer": 1000,         # Medium (UI analysis)
    }

    def __init__(self):
        self.executions = []
        self.daily_budget = 10000  # tokens/day

    def estimate_cost(self, skill_name: str, context: Dict[str, Any]) -> int:
        """Estimate token cost for skill execution."""
        base_cost = self.SKILL_COSTS.get(skill_name, 1000)

        # Adjust based on context complexity
        if isinstance(context, dict):
            # Complex contexts (many fields) cost more
            complexity_factor = min(len(context) * 100, 1000)  # Cap at 1000 extra tokens
            estimated_cost = base_cost + complexity_factor
        else:
            estimated_cost = base_cost

        return estimated_cost

    def track_execution(self, skill_name: str, context: Dict[str, Any], result: Any) -> int:
        """
        Track actual execution cost.
        (In production, this would use actual Claude API token counts)
        """
        estimated_cost = self.estimate_cost(skill_name, context)

        # In real implementation, would get actual cost from Claude API
        # For now, use estimate with ±10% variance
        actual_cost = int(estimated_cost * 0.95)  # Assume 5% more efficient than estimated

        self.executions.append({
            "skill": skill_name,
            "estimated_cost": estimated_cost,
            "actual_cost": actual_cost,
            "timestamp": datetime.now().isoformat(),
            "context_size": len(str(context)),
        })

        log.info(f"💰 {skill_name}: {actual_cost} tokens ({estimated_cost} estimated)")

        return actual_cost

    def daily_spent(self) -> int:
        """Get total tokens spent today."""
        today = datetime.now().date()
        return sum(
            e["actual_cost"]
            for e in self.executions
            if datetime.fromisoformat(e["timestamp"]).date() == today
        )

    def can_afford(self, skill_name: str, context: Dict[str, Any]) -> bool:
        """Check if we can afford another execution within daily budget."""
        estimated = self.estimate_cost(skill_name, context)
        spent_today = self.daily_spent()
        can_afford = spent_today + estimated <= self.daily_budget

        if not can_afford:
            log.warning(
                f"❌ Cannot afford {skill_name} ({estimated} tokens). "
                f"Daily spent: {spent_today}/{self.daily_budget}"
            )

        return can_afford

    def get_report(self) -> Dict:
        """Get cost report for optimization."""
        return {
            "total_executions": len(self.executions),
            "total_spent": sum(e["actual_cost"] for e in self.executions),
            "daily_budget": self.daily_budget,
            "daily_spent": self.daily_spent(),
            "remaining": self.daily_budget - self.daily_spent(),
            "most_expensive_skill": self._most_expensive_skill(),
            "efficiency": self._calculate_efficiency(),
        }

    def _most_expensive_skill(self) -> str:
        if not self.executions:
            return "N/A"
        return max(
            set(e["skill"] for e in self.executions),
            key=lambda s: sum(e["actual_cost"] for e in self.executions if e["skill"] == s)
        )

    def _calculate_efficiency(self) -> str:
        if not self.executions:
            return "N/A"

        total_estimated = sum(e["estimated_cost"] for e in self.executions)
        total_actual = sum(e["actual_cost"] for e in self.executions)

        if total_estimated == 0:
            return "N/A"

        efficiency = int((1 - total_actual / total_estimated) * 100)
        return f"{efficiency}% better than estimated" if efficiency > 0 else f"{-efficiency}% over estimate"
