"""Ambiental + anticipos service."""

from __future__ import annotations

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache


class AmbientalService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    @ttl_cache(seconds=600)
    async def total(self) -> dict:
        row = await self.db.fetchrow(
            f"""
            SELECT
                COUNT(*) FILTER (WHERE obligacion_ambiental = 'Si')::int AS amb_count,
                COUNT(*)::int AS total,
                COALESCE(SUM(valor_contrato_num)
                    FILTER (WHERE obligacion_ambiental = 'Si'), 0)::float AS valor_total
            FROM {self.settings.data_table_name}
            """
        )
        if row is None:
            return {"count": 0, "total": 0, "pct": 0.0, "valor_total": 0.0}
        amb = int(row["amb_count"] or 0)
        total = int(row["total"] or 1)
        return {
            "count": amb,
            "total": total,
            "pct": round((amb / total) * 100, 2) if total else 0.0,
            "valor_total": float(row["valor_total"] or 0),
        }

    @ttl_cache(seconds=600)
    async def anticipos(self) -> dict:
        row = await self.db.fetchrow(
            f"""
            SELECT
                COUNT(*) FILTER (WHERE habilita_pago_adelantado = 'Si')::int AS ant_count,
                COUNT(*)::int AS total,
                COALESCE(SUM(valor_pago_adelantado_num)
                    FILTER (WHERE habilita_pago_adelantado = 'Si'), 0)::float AS total_anticipos
            FROM {self.settings.data_table_name}
            """
        )
        if row is None:
            return {"count": 0, "total": 0, "pct": 0.0, "valor_total_anticipos": 0.0}
        ant = int(row["ant_count"] or 0)
        total = int(row["total"] or 1)
        return {
            "count": ant,
            "total": total,
            "pct": round((ant / total) * 100, 2) if total else 0.0,
            "valor_total_anticipos": float(row["total_anticipos"] or 0),
        }
