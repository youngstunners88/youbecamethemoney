#!/usr/bin/env python3
"""
Master Execution Script — Track 1 + Track 2 Parallel Launch
Initializes skill system and executes Learning Engine + Hermes Deployment
"""

import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# Add .skills to path
sys.path.insert(0, str(Path(__file__).parent / '.skills'))

from routing_engine import SkillRouter
from token_cost_tracker import TokenCostTracker
from autonomous_executor import AutonomousExecutor
from skill_registry import get_skill, list_skills

def main():
    """Execute Track 1 and Track 2 in parallel."""

    print("\n" + "="*80)
    print("🚀 GARCIA COMMAND CENTER - PARALLEL TRACK EXECUTION")
    print("="*80 + "\n")

    # Step 1: Initialize system
    print("[1/4] Initializing skill system...")
    cost_tracker = TokenCostTracker()

    # Load all skills
    skills = {}
    for skill_name in [
        "token_optimizer",
        "gsd_coordinator",
        "legal_questioner",
        "code_best_practices",
        "workflow_automation",
        "security_validator",
        "compression",
        "ui_optimizer",
    ]:
        skills[skill_name] = get_skill(skill_name)

    router = SkillRouter(skills=skills, cost_tracker=cost_tracker)
    executor = AutonomousExecutor(router, max_workers=2)

    print(f"✅ Skill system initialized ({len(skills)} skills available)\n")

    # Step 2: Launch Track 1 (Learning Engine)
    print("[2/4] Queuing Track 1 tasks (Learning Engine → PostgreSQL)...")
    track1_results = executor.execute_track_1_tasks()
    print(f"✅ Track 1: {len(track1_results)} tasks executed\n")

    # Step 3: Launch Track 2 (Hermes Deployment)
    print("[3/4] Queuing Track 2 tasks (Hermes/Ramsees deployment to Zo)...")
    track2_results = executor.execute_track_2_tasks()
    print(f"✅ Track 2: {len(track2_results)} tasks executed\n")

    # Step 4: Generate summary
    print("[4/4] Generating execution summary...\n")

    summary = {
        "timestamp": datetime.now().isoformat(),
        "track_1": {
            "tasks": len(track1_results),
            "successful": len([r for r in track1_results.values() if r.get("status") == "success"]),
            "failed": len([r for r in track1_results.values() if r.get("status") == "failed"]),
        },
        "track_2": {
            "tasks": len(track2_results),
            "successful": len([r for r in track2_results.values() if r.get("status") == "success"]),
            "failed": len([r for r in track2_results.values() if r.get("status") == "failed"]),
        },
        "cost_report": cost_tracker.get_report(),
        "router_summary": executor.router.get_cost_summary(),
    }

    # Print summary
    print("="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    print(f"\n📊 Track 1 (Learning Engine):")
    print(f"   Tasks: {summary['track_1']['tasks']}")
    print(f"   ✅ Successful: {summary['track_1']['successful']}")
    print(f"   ❌ Failed: {summary['track_1']['failed']}")

    print(f"\n📊 Track 2 (Hermes Deployment):")
    print(f"   Tasks: {summary['track_2']['tasks']}")
    print(f"   ✅ Successful: {summary['track_2']['successful']}")
    print(f"   ❌ Failed: {summary['track_2']['failed']}")

    print(f"\n💰 Token Cost Report:")
    print(f"   Total executions: {summary['cost_report']['total_executions']}")
    print(f"   Total spent: {summary['cost_report']['total_spent']} tokens")
    print(f"   Daily budget: {summary['cost_report']['daily_budget']} tokens")
    print(f"   Remaining today: {summary['cost_report']['remaining']} tokens")
    print(f"   Efficiency: {summary['cost_report']['efficiency']}")

    # Save summary to file
    summary_path = Path(__file__).parent / ".ctrl" / "execution_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Summary saved to: {summary_path}")

    print("\n" + "="*80)
    print("🎯 NEXT STEPS:")
    print("="*80)
    print("""
1. ✅ Track 1: Verify PostgreSQL bridge connected to real Garcia database
   - Check: optimization/layer3/integration/postgres_bridge.py
   - Test: fetch_recent_leads(), fetch_closed_cases()

2. ✅ Track 2: Verify Hermes installed on Zo and running
   - Check: hermes/install_hermes.sh executed
   - Verify: sudo systemctl status ramsees on Zo
   - Check: ~/.env has DATABASE_PASSWORD set

3. ✅ Integration: Wire 5 FastMCP skills to Hermes
   - intake_commercial_law
   - lead_urgency_scorer
   - case_pattern_analyzer
   - discharge_protocol
   - email_drafter

4. ✅ Testing: Run full learning cycle
   - Create test lead in embark.html
   - Watch Ramsees process it
   - Check PostgreSQL for learned patterns
   - Verify NTFY notification sent

5. ✅ Monitor: Token costs stay under 10K/day
   - Check: .ctrl/execution_summary.json
   - Adjust: fallback skills if budget exceeded
    """)

    print("="*80)
    print("✅ PARALLEL EXECUTION COMPLETE")
    print("="*80 + "\n")

    return summary

if __name__ == "__main__":
    try:
        summary = main()
        sys.exit(0)
    except Exception as e:
        log.error(f"❌ Execution failed: {e}", exc_info=True)
        sys.exit(1)
