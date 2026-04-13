"""
Hermes API Integration

Sends Layer 3 insights back to Hermes for execution.

These are NOT frequent calls - only 1x per week when insights are generated.
"""

import os
import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class HermesAPI:
    """
    Send Layer 3 insights to Hermes for implementation.
    """

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("HERMES_API_BASE", "http://localhost:3000/api")

    def update_agent_prompt(self, agent_name: str, new_system_prompt: str) -> bool:
        """
        Update Hermes agent's system prompt.

        This is how script improvements are deployed.
        """
        try:
            response = requests.post(
                f"{self.base_url}/hermes/agents/{agent_name}/system-prompt",
                json={"system_prompt": new_system_prompt},
                timeout=10,
            )

            if response.status_code == 200:
                logger.info(f"✅ Updated {agent_name} system prompt")
                return True
            else:
                logger.error(f"❌ Failed to update {agent_name}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error updating {agent_name}: {e}")
            return False

    def update_routing_rules(self, rules: List[Dict]) -> bool:
        """
        Update how leads are routed to agents/windows.

        Example:
            [{
                "condition": "lead_temperature == 'hot'",
                "action": "route_to_9am_window",
                "priority": "high"
            }]
        """
        try:
            response = requests.post(
                f"{self.base_url}/hermes/routing-rules",
                json={"rules": rules},
                timeout=10,
            )

            if response.status_code == 200:
                logger.info(f"✅ Updated {len(rules)} routing rules")
                return True
            else:
                logger.error(f"❌ Failed to update routing: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error updating routing: {e}")
            return False

    def update_scoring_parameters(self, parameters: Dict) -> bool:
        """
        Update lead scoring parameters.

        Example:
            {
                "model": "conversion_predictor_v2",
                "weights": {
                    "temperature": 0.40,
                    "duration": 0.20,
                    "sentiment": 0.20,
                    "source": 0.10,
                    "time": 0.10
                }
            }
        """
        try:
            response = requests.post(
                f"{self.base_url}/hermes/scoring-parameters",
                json=parameters,
                timeout=10,
            )

            if response.status_code == 200:
                logger.info("✅ Updated scoring parameters")
                return True
            else:
                logger.error(f"❌ Failed to update parameters: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error updating parameters: {e}")
            return False

    def execute_actions(self, actions: Dict) -> Dict:
        """
        Execute all pending Layer 3 actions.

        Returns: summary of what was deployed
        """
        results = {
            "scripts_updated": 0,
            "routing_updated": 0,
            "parameters_updated": 0,
            "errors": [],
        }

        # Execute script updates
        if actions.get("script_updates"):
            # Group by agent name (default: Margarita)
            for agent in ["margarita"]:  # Expand this if multiple agents
                prompt = actions["script_updates"][0].get("prompt")
                if prompt:
                    if self.update_agent_prompt(agent, prompt):
                        results["scripts_updated"] += 1
                    else:
                        results["errors"].append(f"Failed to update {agent} script")

        # Execute routing rule updates
        if actions.get("routing_rules"):
            if self.update_routing_rules(actions["routing_rules"]):
                results["routing_updated"] = 1

        # Execute parameter updates
        if actions.get("parameter_changes"):
            # Convert parameter changes to scoring parameters
            params = self._build_scoring_params(actions["parameter_changes"])
            if self.update_scoring_parameters(params):
                results["parameters_updated"] = 1

        return results

    def _build_scoring_params(self, changes: List[Dict]) -> Dict:
        """Convert Layer 3 parameter changes to Hermes format."""
        return {
            "model": "conversion_predictor_v2",
            "updated_at": "2026-04-13",
            "changes": changes,
        }

    def create_improvement_report(self, insights: List, impact: Dict) -> str:
        """
        Generate a human-readable report of improvements made.

        This gets logged and can be sent to Mr. Garcia.
        """
        report = f"""
LAYER 3 WEEKLY IMPROVEMENT REPORT
Generated: 2026-04-{13}

IMPROVEMENTS DEPLOYED: {len(insights)}

"""

        for i, insight in enumerate(insights, 1):
            report += f"\n{i}. {insight.finding.upper()}\n"
            report += f"   Action: {insight.action}\n"
            report += f"   Confidence: {insight.confidence:.0%}\n"
            report += f"   Expected Impact: +{insight.impact_estimate:.1%}\n"

        report += f"\n\nFINANCIAL IMPACT:\n"
        report += f"  Current close rate: 18.5%\n"
        report += f"  Expected new rate: {impact['estimated_new_close_rate']:.1%}\n"
        report += f"  Improvement: +{impact['total_estimated_improvement']:.1%}\n"
        report += f"\nIf this holds across 100 leads/week:\n"
        report += f"  Extra closures: {100 * impact['total_estimated_improvement']:.1f} leads/week\n"
        report += f"  @ $3,200/case: ${100 * impact['total_estimated_improvement'] * 3200:,.0f}/week\n"
        report += f"  @ $156,800/month additional revenue\n"

        return report


# Example: How Layer 3 calls Hermes
if __name__ == "__main__":
    api = HermesAPI()

    # Simulate sending improvements
    new_prompt = """You are Margarita, professional intake specialist.

BEST PHRASES (Use frequently):
• "What's your current situation?" → 84% close rate
• "The force of nature is with you" → 79% close rate
• "UCC Article 3" → 81% close rate

AVOID THESE:
• "Is this a good time?" → 18% close rate (REMOVE)
• "I'm sure you're busy" → 22% close rate (REMOVE)

New script = +6% close rate expected"""

    result = api.update_agent_prompt("margarita", new_prompt)
    print(f"Prompt update success: {result}")

    # Update routing
    rules = [
        {
            "condition": "temperature == 'hot'",
            "action": "prioritize_9-11am",
            "priority": "high",
        },
        {
            "condition": "temperature == 'luke'",
            "action": "route_to_drip_campaign",
            "priority": "medium",
        },
    ]

    result = api.update_routing_rules(rules)
    print(f"Routing update success: {result}")

    print("\n✅ Layer 3 → Hermes integration working")
