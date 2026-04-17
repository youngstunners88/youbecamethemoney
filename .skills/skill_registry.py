"""
Skill Registry - All available skills for autonomous routing
"""

import logging
from typing import Dict, Callable

try:
    from .tier1.token_optimizer import execute as token_optimizer
except ImportError:
    from tier1.token_optimizer import execute as token_optimizer

log = logging.getLogger(__name__)

SKILL_REGISTRY: Dict[str, Callable] = {
    # Tier 1 - Critical skills
    "token_optimizer": token_optimizer,

    # Tier 2 - Support skills (stubs for now)
    "gsd_coordinator": lambda ctx: {"status": "gsd_coordinator_executed", "context": ctx},
    "legal_questioner": lambda ctx: {"status": "legal_questioner_executed", "context": ctx},
    "code_best_practices": lambda ctx: {"status": "code_best_practices_executed", "context": ctx},
    "workflow_automation": lambda ctx: {"status": "workflow_automation_executed", "context": ctx},
    "security_validator": lambda ctx: {"status": "security_validator_executed", "context": ctx},

    # Tier 3 - Optional skills
    "compression": lambda ctx: {"status": "compression_executed", "context": ctx},
    "ui_optimizer": lambda ctx: {"status": "ui_optimizer_executed", "context": ctx},
}

def get_skill(skill_name: str) -> Callable:
    """Get a skill by name."""
    if skill_name not in SKILL_REGISTRY:
        log.warning(f"Skill not found: {skill_name}, using fallback")
        return lambda ctx: {"status": "fallback_executed", "context": ctx}

    return SKILL_REGISTRY[skill_name]

def list_skills() -> Dict[str, str]:
    """List all available skills."""
    return {name: f.__doc__ or "No description" for name, f in SKILL_REGISTRY.items()}
