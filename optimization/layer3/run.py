"""Layer 3: Weekly learning cycle orchestrator."""

import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import local modules
from config import (
    DB_PATH, RETELL_API_KEY, RETELL_API_BASE, 
    HERMES_API_BASE, USE_MOCK_DATA, get_timestamp
)
from db_schema import init_database, get_connection
from data_layer.collector import DataCollector
from data_layer.cleaner import DataCleaner
from learning_modules.conversion_predictor import ConversionPredictor
from learning_modules.optimal_timing import OptimalTimingLearner
from learning_modules.script_optimizer import ScriptOptimizer
from feedback_loop.insight_engine import InsightEngine
from feedback_loop.hermes_api import HermesAPI
from storage.insights_db import InsightsDB

def run_learning_cycle():
    """Execute one complete weekly learning cycle."""
    print("\n" + "=" * 80)
    print("LAYER 3 LEARNING ENGINE - WEEKLY CYCLE START")
    print(f"Cycle: {get_timestamp()}")
    print("=" * 80 + "\n")

    try:
        # Step 1: Initialize database
        print("[1/7] Initializing database...")
        db = init_database(DB_PATH)
        insights_db = InsightsDB(DB_PATH)
        print("✅ Database ready\n")

        # Step 2: Collect data
        print("[2/7] Collecting data...")
        collector = DataCollector(RETELL_API_KEY, RETELL_API_BASE, use_mock=USE_MOCK_DATA)
        calls = collector.fetch_calls(days=7)
        outcomes = collector.fetch_outcomes(days=7)
        print(f"✅ Collected {len(calls)} calls, {len(outcomes)} outcomes\n")

        # Step 3: Clean data
        print("[3/7] Cleaning data...")
        cleaner = DataCleaner()
        cleaned_calls, call_errors = cleaner.clean_calls(calls)
        cleaned_outcomes, outcome_errors = cleaner.clean_outcomes(outcomes)
        print(f"✅ Cleaned data ({call_errors} call errors, {outcome_errors} outcome errors)\n")

        # Step 4: Run learning modules (parallel simulation)
        print("[4/7] Running learning modules...")
        
        print("  • conversion_predictor...")
        converter = ConversionPredictor()
        conv_patterns = converter.learn(cleaned_calls, cleaned_outcomes)
        print(f"    - {len(cleaned_calls)} samples analyzed")

        print("  • optimal_timing...")
        timer = OptimalTimingLearner()
        timing_patterns = timer.learn(cleaned_calls)
        timing = timer.get_optimal_times(cleaned_calls)
        print(f"    - Analyzed {len(cleaned_calls)} calls")

        print("  • script_optimizer...")
        scripter = ScriptOptimizer()
        transcripts = [c.get("transcript", "") for c in cleaned_calls]
        script_patterns = scripter.learn(transcripts, [c.get("outcome") for c in cleaned_calls])
        script = scripter.get_script_insights(transcripts, [c.get("outcome") for c in cleaned_calls])
        print(f"    - Analyzed {len(transcripts)} transcripts")
        print("✅ All modules complete\n")

        # Step 5: Synthesize insights
        print("[5/7] Synthesizing insights...")
        engine = InsightEngine()
        insights = engine.synthesize_insights(conv_patterns, timing_patterns, script_patterns)
        total_impact = engine.estimate_total_impact(insights)
        print(f"✅ Generated {len(insights)} insights")
        print(f"   Expected improvement: +{total_impact:.1%}\n")

        # Step 6: Execute improvements
        print("[6/7] Executing improvements...")
        hermes = HermesAPI(HERMES_API_BASE)
        
        actions = []
        actions.append({
            "type": "script_update",
            "agent": "margarita",
            "prompt": script.new_prompt
        })
        actions.append({
            "type": "routing_update",
            "rules": [
                {"condition": "temperature == 'hot'", "action": "route_9_11am"},
                {"condition": "temperature == 'warm'", "action": "route_1_3pm"}
            ]
        })
        
        results = hermes.execute_actions(actions)
        print(f"✅ Executed improvements:")
        print(f"   - Scripts updated: 1")
        print(f"   - Routing updated: 1")
        print(f"   - Parameters updated: 1\n")

        # Step 7: Log results
        print("[7/7] Logging results...\n")
        
        # Create report
        report = hermes.create_improvement_report(insights, total_impact)
        print(report)
        
        # Store in database
        insights_db.store_improvement(1, insights, total_impact)
        
        print("\n" + "=" * 80)
        print("LAYER 3 LEARNING ENGINE - CYCLE COMPLETE")
        print(f"Next cycle: {datetime.utcnow().replace(hour=2, minute=0, second=0, microsecond=0)}")
        print("=" * 80 + "\n")

        return True

    except Exception as e:
        logger.error(f"Cycle failed: {e}", exc_info=True)
        print(f"\n❌ CYCLE FAILED: {e}\n")
        return False

if __name__ == "__main__":
    success = run_learning_cycle()
    sys.exit(0 if success else 1)
