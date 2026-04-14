"""
BaseSkill — shared abstraction for all FastMCP skills.

Every skill (lead_qualifier, interview_analyzer, hall_of_fame_curator, etc.)
extends this class so that:
  - DB connection is centralised
  - Logging is consistent
  - Claude API fallback is shared
  - Config loading is unified
"""

import os
import logging
from datetime import datetime


# ─── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
)


class BaseSkill:
    """Base class for all Garcia Law skills."""

    # Subclasses override this name (used in logs + Hermes routing)
    skill_name: str = "base"

    def __init__(self):
        self.logger = logging.getLogger(self.skill_name)
        self.db_url = os.getenv("DATABASE_URL", "")
        self.claude_key = os.getenv("CLAUDE_API_KEY", "")
        self.hermes_base = os.getenv("HERMES_API_BASE", "http://localhost:3000")
        self.use_mock = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

    # ── Claude API helper ──────────────────────────────────────────────────────
    def _call_claude(self, prompt: str, max_tokens: int = 800) -> str | None:
        """Call Claude API. Returns None on failure — callers must have rule-based fallback."""
        if not self.claude_key:
            self.logger.warning("CLAUDE_API_KEY not set — skipping AI call")
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.claude_key)
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            return None

    # ── DB helper ──────────────────────────────────────────────────────────────
    def _get_db_conn(self):
        """Return a psycopg2 connection or None if not configured."""
        if not self.db_url:
            self.logger.warning("DATABASE_URL not set — running without DB")
            return None
        try:
            import psycopg2
            return psycopg2.connect(self.db_url)
        except Exception as e:
            self.logger.error(f"DB connection error: {e}")
            return None

    # ── Hermes helper ──────────────────────────────────────────────────────────
    def _post_to_hermes(self, path: str, payload: dict) -> bool:
        """POST to Hermes API. Returns True on success."""
        import requests
        url = f"{self.hermes_base}{path}"
        try:
            r = requests.post(url, json=payload, timeout=5)
            r.raise_for_status()
            return True
        except Exception as e:
            self.logger.warning(f"Hermes unreachable at {url}: {e}")
            return False

    # ── Timestamp helper ───────────────────────────────────────────────────────
    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()
