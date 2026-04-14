"""
BaseRepository — shared DB access pattern.

Each feature gets its own repository class that extends this.
No raw SQL scattered across skills — all DB work lives here.

Usage:
    from base_repository import BaseRepository

    class LeadRepository(BaseRepository):
        def get_hot_leads(self):
            return self.query("SELECT * FROM leads WHERE temperature = 'hot'")
"""

import logging
from typing import Any


class BaseRepository:
    """Thin wrapper around psycopg2 for structured DB access."""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.logger = logging.getLogger(self.__class__.__name__)

    def _connect(self):
        if not self.db_url:
            raise RuntimeError("DATABASE_URL not configured")
        import psycopg2
        return psycopg2.connect(self.db_url)

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        """Run SELECT, return list of dicts."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
        finally:
            conn.close()

    def execute(self, sql: str, params: tuple = ()) -> int:
        """Run INSERT/UPDATE/DELETE, return rowcount."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
                return cur.rowcount
        finally:
            conn.close()

    def execute_returning(self, sql: str, params: tuple = ()) -> Any:
        """Run INSERT ... RETURNING id, return the value."""
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                conn.commit()
                return cur.fetchone()[0]
        finally:
            conn.close()
