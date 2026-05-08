"""Tipos de contrato service."""

from __future__ import annotations

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache


class TiposService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    @ttl_cache(seconds=600)
    async def top(self, limit: int = 5) -> dict:
        total = await self.db.fetchval(
            f"SELECT COUNT(*) FROM {self.settings.data_table_name}"
        )
        total_int = int(total or 0) or 1

        rows = await self.db.fetch(
            f"""
            SELECT "Tipo de Contrato" AS tipo, COUNT(*)::int AS count
            FROM {self.settings.data_table_name}
            WHERE "Tipo de Contrato" IS NOT NULL AND "Tipo de Contrato" <> ''
            GROUP BY "Tipo de Contrato"
            ORDER BY count DESC
            LIMIT $1
            """,
            limit,
        )
        items = [
            {
                "tipo": r["tipo"],
                "count": r["count"],
                "pct": round((r["count"] / total_int) * 100, 2),
            }
            for r in rows
        ]
        return {"items": items, "total": total_int}
