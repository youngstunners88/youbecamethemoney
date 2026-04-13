"""Configuration and constants for Layer 3 Learning Engine."""

import os
from datetime import datetime

# API Configuration
RETELL_API_KEY = os.getenv("RETELL_API_KEY", "mock-key-for-testing")
RETELL_API_BASE = "https://api.retellai.com"
HERMES_API_BASE = os.getenv("HERMES_API_BASE", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/youbecamethemoney")

# Learning Thresholds
MIN_CONFIDENCE_TO_ACT = 0.75
MIN_SAMPLES_TO_LEARN = 30
MIN_IMPACT_TO_DEPLOY = 0.02
IMPROVEMENT_AGGRESSIVENESS = "moderate"

# Scoring Multipliers
TEMPERATURE_MULTIPLIERS = {
    "hot": 0.45,
    "warm": 0.20,
    "luke": -0.10,
    "cold": -0.70
}

SENTIMENT_MULTIPLIER_RANGE = (0.8, 1.4)
DURATION_THRESHOLD_GOOD = 8
DURATION_THRESHOLD_BAD = 3

# Timing Windows
OPTIMAL_HOURS = (9, 11)
POOR_HOURS = (18, 23)

# Database
DB_PATH = "optimization/layer3/storage/insights.db"
LOG_PATH = "/var/log/layer3.log"

# Scheduling
LEARNING_SCHEDULE_DAY = 0
LEARNING_SCHEDULE_HOUR = 2

# Data Collection
LOOKBACK_DAYS = 7

# Storage & Caching
INSIGHTS_TTL_DAYS = 30
CACHE_ENABLED = True

# Mock Data
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

def get_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()
