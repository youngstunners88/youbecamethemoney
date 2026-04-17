"""
Autonomous Task Executor
Executes routed tasks without user prompting
Coordinates Track 1 (Learning Engine) and Track 2 (Hermes Deployment)
"""

import logging
import json
from typing import Dict, Any, List, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

log = logging.getLogger(__name__)

class AutonomousExecutor:
    """Execute tasks autonomously using intelligent routing."""

    def __init__(self, skill_router, max_workers: int = 2):
        """
        Initialize executor.

        Args:
            skill_router: SkillRouter instance
            max_workers: Max concurrent tasks (for parallel execution)
        """
        self.router = skill_router
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.execution_queue: List[Dict] = []
        self.results: Dict[str, Any] = {}

    def queue_task(self, task_id: str, task_type: str, context: Dict[str, Any], track: str = "general"):
        """
        Queue task for execution.

        Args:
            task_id: Unique task ID
            task_type: Type of task (e.g., "learn_from_cases")
            context: Task data/context
            track: Which track this belongs to ("learning_engine", "hermes_deployment", "general")
        """
        self.execution_queue.append({
            "task_id": task_id,
            "task_type": task_type,
            "context": context,
            "track": track,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
        })

        log.info(f"📋 Queued task: {task_id} ({task_type}) on {track}")

    def execute_all(self) -> Dict[str, Any]:
        """
        Execute all queued tasks (possibly in parallel).
        Returns results indexed by task_id.
        """
        if not self.execution_queue:
            log.info("No tasks queued")
            return {}

        log.info(f"🚀 Executing {len(self.execution_queue)} tasks autonomously...")

        futures = {}
        for task in self.execution_queue:
            task_id = task["task_id"]
            task_type = task["task_type"]
            context = task["context"]

            # Submit task for execution (may run in parallel)
            future = self.executor.submit(
                self._execute_single_task,
                task_id,
                task_type,
                context
            )
            futures[task_id] = future

        # Wait for all tasks and collect results
        for task_id, future in futures.items():
            try:
                result = future.result(timeout=300)  # 5 min timeout per task
                self.results[task_id] = {
                    "status": "success",
                    "result": result,
                }
                log.info(f"✅ Task completed: {task_id}")
            except Exception as e:
                log.error(f"❌ Task failed: {task_id} - {e}")
                self.results[task_id] = {
                    "status": "failed",
                    "error": str(e),
                }

        return self.results

    def execute_track_1_tasks(self) -> Dict[str, Any]:
        """
        Execute all Track 1 (Learning Engine) tasks.
        This runs autonomously without prompting.
        """
        track_1_tasks = [
            {
                "task_id": "layer3-postgres-migration",
                "task_type": "deploy_to_zo",
                "context": {
                    "component": "layer3",
                    "action": "migrate_sqlite_to_postgresql",
                    "target": "garcia_ramsees_db"
                },
                "track": "learning_engine"
            },
            {
                "task_id": "layer3-retell-connector",
                "task_type": "optimize_workflow",
                "context": {
                    "component": "layer3",
                    "action": "connect_retell_api",
                    "target": "retell_data_ingestion"
                },
                "track": "learning_engine"
            },
            {
                "task_id": "layer3-garcia-inputs",
                "task_type": "learn_from_cases",
                "context": {
                    "component": "layer3",
                    "action": "enable_manual_case_inputs",
                    "target": "garcia_manual_data"
                },
                "track": "learning_engine"
            },
            {
                "task_id": "layer3-deploy-zo",
                "task_type": "deploy_to_zo",
                "context": {
                    "component": "layer3",
                    "action": "systemd_service",
                    "target": "zo_computer"
                },
                "track": "learning_engine"
            },
        ]

        for task in track_1_tasks:
            self.queue_task(task["task_id"], task["task_type"], task["context"], task["track"])

        return self.execute_all()

    def execute_track_2_tasks(self) -> Dict[str, Any]:
        """
        Execute all Track 2 (Hermes/Ramsees Deployment) tasks.
        This runs autonomously without prompting.
        """
        track_2_tasks = [
            {
                "task_id": "hermes-install-zo",
                "task_type": "deploy_to_zo",
                "context": {
                    "component": "hermes_agent",
                    "action": "install_from_nous_research",
                    "target": "zo_computer"
                },
                "track": "hermes_deployment"
            },
            {
                "task_id": "hermes-postgres-config",
                "task_type": "optimize_workflow",
                "context": {
                    "component": "hermes_agent",
                    "action": "configure_postgresql",
                    "target": "garcia_ramsees_db"
                },
                "track": "hermes_deployment"
            },
            {
                "task_id": "hermes-skills-integration",
                "task_type": "optimize_workflow",
                "context": {
                    "component": "hermes_agent",
                    "action": "wire_fastmcp_skills",
                    "skills": [
                        "intake_commercial_law",
                        "lead_urgency_scorer",
                        "case_pattern_analyzer",
                        "discharge_protocol",
                        "email_drafter"
                    ]
                },
                "track": "hermes_deployment"
            },
            {
                "task_id": "hermes-validate-security",
                "task_type": "validate_security",
                "context": {
                    "component": "hermes_agent",
                    "action": "security_audit",
                    "target": "data_access_patterns"
                },
                "track": "hermes_deployment"
            },
            {
                "task_id": "hermes-systemd-deploy",
                "task_type": "deploy_to_zo",
                "context": {
                    "component": "hermes_agent",
                    "action": "systemd_service",
                    "target": "zo_computer"
                },
                "track": "hermes_deployment"
            },
        ]

        for task in track_2_tasks:
            self.queue_task(task["task_id"], task["task_type"], task["context"], task["track"])

        return self.execute_all()

    def _execute_single_task(self, task_id: str, task_type: str, context: Dict[str, Any]) -> Any:
        """Execute a single task via router (no user prompting)."""
        log.info(f"⚙️  Executing task: {task_id}")

        try:
            # Route to optimal skill and execute autonomously
            result = self.router.route(task_type, context)

            log.info(f"✅ Task result: {task_id}")
            return result

        except Exception as e:
            log.error(f"❌ Task execution failed: {task_id} - {e}")
            raise

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all executed tasks."""
        successful = len([r for r in self.results.values() if r["status"] == "success"])
        failed = len([r for r in self.results.values() if r["status"] == "failed"])

        return {
            "total_tasks": len(self.results),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{int(successful/(successful+failed)*100)}%" if (successful+failed) > 0 else "N/A",
            "cost_summary": self.router.get_cost_summary(),
        }
