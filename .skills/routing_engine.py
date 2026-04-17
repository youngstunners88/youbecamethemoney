"""
Intelligent skill routing based on token cost + task type
Routes tasks autonomously without user prompting
"""

import json
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass

log = logging.getLogger(__name__)

@dataclass
class Route:
    skill_name: str
    fallback_skill: str
    token_budget: int
    priority: int  # 1=highest, 3=lowest

class SkillRouter:
    """Autonomous router that picks optimal skill for each task."""

    ROUTES = {
        # Layer 3 Learning Engine tasks
        "learn_from_cases": Route(
            skill_name="token_optimizer",
            fallback_skill="gsd_coordinator",
            token_budget=5000,
            priority=1
        ),
        "extract_patterns": Route(
            skill_name="token_optimizer",
            fallback_skill="gsd_coordinator",
            token_budget=3000,
            priority=1
        ),

        # Hermes/Ramsees intake tasks
        "qualify_lead": Route(
            skill_name="legal_questioner",
            fallback_skill="code_best_practices",
            token_budget=2000,
            priority=1
        ),
        "score_urgency": Route(
            skill_name="token_optimizer",
            fallback_skill="legal_questioner",
            token_budget=1000,
            priority=2
        ),

        # Deployment tasks
        "deploy_to_zo": Route(
            skill_name="gsd_coordinator",
            fallback_skill="workflow_automation",
            token_budget=1000,
            priority=1
        ),
        "manage_service": Route(
            skill_name="gsd_coordinator",
            fallback_skill="workflow_automation",
            token_budget=500,
            priority=2
        ),

        # Security/validation
        "validate_security": Route(
            skill_name="security_validator",
            fallback_skill="code_best_practices",
            token_budget=3000,
            priority=1
        ),
        "audit_data_access": Route(
            skill_name="security_validator",
            fallback_skill="token_optimizer",
            token_budget=2000,
            priority=1
        ),

        # Optimization
        "optimize_response": Route(
            skill_name="token_optimizer",
            fallback_skill="compression",
            token_budget=500,
            priority=3
        ),
        "optimize_workflow": Route(
            skill_name="workflow_automation",
            fallback_skill="gsd_coordinator",
            token_budget=1500,
            priority=2
        ),
    }

    def __init__(self, skills: Dict[str, Callable], cost_tracker):
        """
        Initialize router with available skills.

        Args:
            skills: Dict of {skill_name: skill_function}
            cost_tracker: TokenCostTracker instance
        """
        self.skills = skills
        self.cost_tracker = cost_tracker
        self.execution_log = []

    def route(self, task_type: str, context: Dict[str, Any]) -> Any:
        """
        Route task to optimal skill autonomously.

        Args:
            task_type: Type of task (see ROUTES keys)
            context: Task context/data

        Returns:
            Result from executed skill
        """
        if task_type not in self.ROUTES:
            log.warning(f"Unknown task type: {task_type}, using generic fallback")
            return self._execute_generic(context)

        route = self.ROUTES[task_type]

        # Try primary skill
        primary = self.skills.get(route.skill_name)
        if primary and self._can_afford(task_type, primary, context, route.token_budget):
            log.info(f"✅ Routing '{task_type}' → {route.skill_name}")
            return self._execute_skill(task_type, primary, context, route.token_budget)

        # Fall back to fallback skill
        fallback = self.skills.get(route.fallback_skill)
        if fallback:
            log.info(f"⚠️  Primary skill too expensive, routing '{task_type}' → {route.fallback_skill}")
            # Use fallback's budget (usually lower cost)
            fallback_budget = int(route.token_budget * 0.6)
            return self._execute_skill(task_type, fallback, context, fallback_budget)

        # Last resort: generic execution
        log.warning(f"No suitable skill for '{task_type}', using generic fallback")
        return self._execute_generic(context)

    def _can_afford(self, task_type: str, skill: Callable, context: Dict, budget: int) -> bool:
        """Check if skill execution fits token budget."""
        estimated_cost = self.cost_tracker.estimate_cost(skill.__name__, context)
        affordable = estimated_cost <= budget

        if not affordable:
            log.warning(f"Skill '{skill.__name__}' costs {estimated_cost} tokens, budget: {budget}")

        return affordable

    def _execute_skill(self, task_type: str, skill: Callable, context: Dict, budget: int) -> Any:
        """Execute skill and track costs."""
        try:
            result = skill(context)
            actual_cost = self.cost_tracker.track_execution(skill.__name__, context, result)

            log.info(f"✅ Task '{task_type}' completed ({actual_cost}/{budget} tokens used)")

            self.execution_log.append({
                "task_type": task_type,
                "skill": skill.__name__,
                "cost": actual_cost,
                "budget": budget,
                "success": True,
            })

            return result
        except Exception as e:
            log.error(f"❌ Skill execution failed: {e}")
            self.execution_log.append({
                "task_type": task_type,
                "skill": skill.__name__,
                "error": str(e),
                "success": False,
            })
            raise

    def _execute_generic(self, context: Dict) -> Any:
        """Fallback: return context as-is."""
        return context

    def get_cost_summary(self) -> Dict:
        """Get summary of costs across all executions."""
        total_cost = sum(log.get("cost", 0) for log in self.execution_log if log.get("success"))
        total_budget = sum(log.get("budget", 0) for log in self.execution_log if log.get("success"))

        return {
            "total_cost": total_cost,
            "total_budget": total_budget,
            "executions": len([l for l in self.execution_log if l.get("success")]),
            "failures": len([l for l in self.execution_log if not l.get("success")]),
            "efficiency": f"{100 - int((total_cost/total_budget)*100)}%" if total_budget > 0 else "N/A",
        }
