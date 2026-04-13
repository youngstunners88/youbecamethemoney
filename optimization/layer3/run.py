#!/usr/bin/env python3
"""
Layer 3: Learning Engine Entry Point

WEEKLY CYCLE (Runs Sunday 2am)
├─ Collect data (last 7 days)
├─ Run 3 learning modules in parallel
├─ Synthesize insights
├─ Execute improvements
└─ Log results

This is the only file that needs to be scheduled.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from config import *
from db_schema import init_database
from data_layer.collector import DataCollector
from data_layer.cleaner import DataCleaner
from learning_modules.conversion_predictor import ConversionPredictor
from learning_modules.optimal_timing import OptimalTimingModule
from learning_modules.script_optimizer import ScriptOptimizer
from feedback_loop.insight_engine import InsightEngine
from feedback_loop.hermes_api import HermesAPI
from storage.insights_db import InsightsDB

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Run the full Layer 3 learning cycle."""

    logger.info("=" * 80)
    logger.info("LAYER 3 LEARNING ENGINE - WEEKLY CYCLE START")
    logger.info(f"Cycle: {datetime.now().isoformat()}")
    logger.info("=" * 80)

    try:
        # Step 1: Initialize database
        logger.info("\n[1/7] Initializing database...")
        init_database(INSIGHTS_DB_PATH)
        insights_db = InsightsDB(INSIGHTS_DB_PATH)
        logger.info("✅ Database ready")

        # Step 2: Collect data (last 7 days)
        logger.info("\n[2/7] Collecting data...")
        collector = DataCollector()
        call_records = collector.fetch_calls(days=7)
        lead_outcomes = collector.fetch_outcomes(days=7)
        logger.info(f"✅ Collected {len(call_records)} calls, {len(lead_outcomes)} outcomes")

        # Step 3: Clean data
        logger.info("\n[3/7] Cleaning data...")
        cleaner = DataCleaner()
        call_records = cleaner.clean_calls(call_records)
        lead_outcomes = cleaner.clean_outcomes(lead_outcomes)
        logger.info(f"✅ Cleaned data")

        # Step 4: Run learning modules (parallel)
        logger.info("\n[4/7] Running learning modules...")

        # Module 1: Conversion Predictor
        logger.info("  • conversion_predictor...")
        predictor = ConversionPredictor()
        conversion_patterns = predictor.learn_from_data(call_records, lead_outcomes)
        logger.info(f"    - {conversion_patterns['samples']} samples analyzed")

        # Module 2: Optimal Timing
        logger.info("  • optimal_timing...")
        timing = OptimalTimingModule()
        timing_patterns = timing.learn_from_data(call_records)
        logger.info(f"    - Analyzed {timing_patterns['samples']} calls")

        # Module 3: Script Optimizer
        logger.info("  • script_optimizer...")
        # Transform call_records to transcript format
        transcripts = [
            {
                "text": c.get("transcript", ""),
                "outcome": c.get("outcome", "failed"),
                "sentiment": c.get("prospect_sentiment_score", 0.5),
            }
            for c in call_records
        ]
        optimizer = ScriptOptimizer()
        script_patterns = optimizer.learn_from_data(transcripts)
        logger.info(f"    - Analyzed {script_patterns['total_transcripts']} transcripts")

        logger.info("✅ All modules complete")

        # Step 5: Synthesize insights
        logger.info("\n[5/7] Synthesizing insights...")
        engine = InsightEngine(config=None)
        insights = engine.synthesize_insights(
            conversion_patterns,
            timing_patterns,
            script_patterns,
        )
        impact = engine.estimate_weekly_impact(insights)
        logger.info(f"✅ Generated {len(insights)} insights")
        logger.info(f"   Expected improvement: +{impact['total_estimated_improvement']:.1%}")

        # Step 6: Build action plan and execute
        logger.info("\n[6/7] Executing improvements...")
        actions = engine.build_action_plan(insights)

        # Send to Hermes (only if we have insights)
        if insights:
            hermes = HermesAPI()

            # Try to execute (fail gracefully if Hermes unavailable)
            try:
                results = hermes.execute_actions({
                    "script_updates": actions.get("script_updates", []),
                    "routing_rules": actions.get("routing_rules", []),
                    "parameter_changes": actions.get("parameter_changes", []),
                })
                logger.info(f"✅ Executed improvements:")
                logger.info(f"   - Scripts updated: {results['scripts_updated']}")
                logger.info(f"   - Routing updated: {results['routing_updated']}")
                logger.info(f"   - Parameters updated: {results['parameters_updated']}")
                if results['errors']:
                    for err in results['errors']:
                        logger.warning(f"   ⚠️ {err}")
            except Exception as e:
                logger.warning(f"⚠️ Could not reach Hermes API: {e}")
                logger.info("   (This is OK - Hermes not required for learning)")

        # Step 7: Log results
        logger.info("\n[7/7] Logging results...")
        insights_db.store_improvements(insights, impact)

        # Generate report
        report = hermes.create_improvement_report(insights, impact) if insights else "No improvements this week"
        logger.info("\n" + report)

        logger.info("\n" + "=" * 80)
        logger.info("LAYER 3 LEARNING ENGINE - CYCLE COMPLETE")
        logger.info(f"Next cycle: {(datetime.now() + timedelta(days=7)).isoformat()}")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
