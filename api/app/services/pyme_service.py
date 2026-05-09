"""PYME service."""

from __future__ import annotations

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache


class PymeService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    @ttl_cache(seconds=600)
    async def proporcion(self) -> dict:
        """Proporción contratos PYME (Es Pyme = 'Si')."""
        row = await self.db.fetchrow(
            f"""
            SELECT
                COUNT(*) FILTER (WHERE es_pyme = 'Si')::int AS pyme,
                COUNT(*)::int AS total
            FROM {self.settings.data_table_name}
            """
        )
        if row is None:
            return {"pct": 0.0, "count": 0, "total": 0}
        pyme = int(row["pyme"] or 0)
        total = int(row["total"] or 1)
        pct = round((pyme / total) * 100, 2) if total else 0.0
        return {"pct": pct, "count": pyme, "total": total}
