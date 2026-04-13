"""API client for sending improvements to Hermes."""

import requests
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class HermesAPI:
    """Communicates improvements to Hermes AI platform."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def update_agent_prompt(self, agent_name: str, new_prompt: str) -> Dict:
        """Update Margarita's system prompt."""
        try:
            url = f"{self.base_url}/agents/{agent_name}/system-prompt"
            data = {"system_prompt": new_prompt}
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Updated {agent_name} prompt")
            return {"success": True, "agent": agent_name}
        except Exception as e:
            logger.error(f"Error updating prompt: {e}")
            return {"success": False, "error": str(e)}

    def update_routing_rules(self, rules: List[Dict]) -> Dict:
        """Update lead routing rules."""
        try:
            url = f"{self.base_url}/routing-rules"
            data = {"rules": rules}
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Updated {len(rules)} routing rules")
            return {"success": True, "rules_updated": len(rules)}
        except Exception as e:
            logger.error(f"Error updating routing: {e}")
            return {"success": False, "error": str(e)}

    def update_scoring_parameters(self, model_name: str, weights: Dict) -> Dict:
        """Update conversion scoring model."""
        try:
            url = f"{self.base_url}/scoring-parameters"
            data = {"model": model_name, "weights": weights}
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Updated scoring model {model_name}")
            return {"success": True, "model": model_name}
        except Exception as e:
            logger.error(f"Error updating scoring: {e}")
            return {"success": False, "error": str(e)}

    def execute_actions(self, actions: List[Dict]) -> Dict:
        """Execute all improvements via Hermes."""
        results = {
            "total": len(actions),
            "succeeded": 0,
            "failed": 0,
            "details": []
        }

        for action in actions:
            if action.get("type") == "script_update":
                result = self.update_agent_prompt(
                    action.get("agent", "margarita"),
                    action.get("prompt")
                )
            elif action.get("type") == "routing_update":
                result = self.update_routing_rules(action.get("rules", []))
            elif action.get("type") == "scoring_update":
                result = self.update_scoring_parameters(
                    action.get("model"),
                    action.get("weights", {})
                )
            else:
                result = {"success": False, "error": "Unknown action type"}

            if result.get("success"):
                results["succeeded"] += 1
            else:
                results["failed"] += 1
            results["details"].append(result)

        return results

    def create_improvement_report(self, insights: List[Dict], total_impact: float) -> str:
        """Generate human-readable improvement report."""
        report = []
        report.append("=" * 80)
        report.append("LAYER 3 WEEKLY IMPROVEMENT REPORT")
        report.append("=" * 80)
        report.append(f"\nIMPROVEMENTS DEPLOYED: {len(insights)}")
        report.append(f"EXPECTED TOTAL IMPROVEMENT: +{total_impact:.1%}\n")

        for i, insight in enumerate(insights, 1):
            report.append(f"{i}. {insight['title'].upper()}")
            report.append(f"   Action: {insight['recommendation']}")
            report.append(f"   Confidence: {insight['confidence']:.0%}")
            report.append(f"   Expected Impact: +{insight['impact']:.1%}\n")

        report.append("=" * 80)
        return "\n".join(report)
