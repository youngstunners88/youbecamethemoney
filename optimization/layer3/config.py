"""
Layer 3 Configuration

Constants, thresholds, and settings for the learning engine.
"""

import os
from pathlib import Path

# Database paths
BASE_DIR = Path(__file__).parent
INSIGHTS_DB_PATH = BASE_DIR / "storage" / "insights.db"
CACHE_DIR = BASE_DIR / "storage" / "cache"

# API Configuration
RETELL_API_BASE = "https://api.retellai.com/v2"
HERMES_API_BASE = os.getenv("HERMES_API_BASE", "http://localhost:3000/api")

# Learning thresholds
MIN_CONFIDENCE_TO_ACT = 0.75  # Don't act unless 75%+ confident
MIN_SAMPLES_TO_LEARN = 30     # Need at least 30 data points
MIN_IMPACT_TO_DEPLOY = 0.02   # Only act if 2%+ improvement expected

# Scheduling
LEARNING_CYCLE_DAY = "Sunday"
LEARNING_CYCLE_HOUR = 2  # 2am Sunday
DATA_COLLECTION_WINDOW = 7  # Last 7 days

# Sentiment analysis thresholds
POSITIVE_SENTIMENT_THRESHOLD = 0.6
NEGATIVE_SENTIMENT_THRESHOLD = 0.35

# Caching
CACHE_TTL_SECONDS = 3600  # 1 hour

# Modules to run
ENABLED_MODULES = [
    "conversion_predictor",
    "optimal_timing",
    "script_optimizer"
]

# How aggressive should improvements be?
# conservative: only the safest improvements
# moderate: balance safety and speed
# aggressive: try everything with >75% confidence
IMPROVEMENT_AGGRESSIVENESS = "moderate"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "layer3.log"
