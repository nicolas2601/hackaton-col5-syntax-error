"""Pareto service — concentración de dinero por entidad."""

from __future__ import annotations

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache


class ParetoService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    @ttl_cache(seconds=900)
    async def entidades(self) -> dict:
        """Curva de Pareto en 5 quintiles ordenados por dinero ejecutado."""
        rows = await self.db.fetch(
            f"""
            WITH agg AS (
                SELECT
                    "Nit Entidad" AS nit,
                    COALESCE(SUM(valor_pagado_num), 0)::float AS dinero
                FROM {self.settings.data_table_name}
                WHERE "Nit Entidad" IS NOT NULL AND "Nit Entidad" <> ''
                GROUP BY "Nit Entidad"
                HAVING COALESCE(SUM(valor_pagado_num), 0) > 0
            ),
            ranked AS (
                SELECT
                    nit,
                    dinero,
                    NTILE(5) OVER (ORDER BY dinero DESC) AS quintil
                FROM agg
            )
            SELECT
                quintil::int AS quintil,
                COUNT(*)::int AS entidades,
                SUM(dinero)::float AS dinero_total
            FROM ranked
            GROUP BY quintil
            ORDER BY quintil
            """
        )

        total_entidades = sum(int(r["entidades"]) for r in rows)
        total_dinero = sum(float(r["dinero_total"]) for r in rows) or 1.0

        quintiles = [
            {
                "quintil": int(r["quintil"]),
                "pct_entidades": round((int(r["entidades"]) / max(total_entidades, 1)) * 100, 2),
                "pct_dinero": round((float(r["dinero_total"]) / total_dinero) * 100, 2),
                "entidades": int(r["entidades"]),
                "dinero_total": float(r["dinero_total"]),
            }
            for r in rows
        ]
        return {
            "quintiles": quintiles,
            "total_entidades": total_entidades,
            "dinero_total": round(total_dinero, 2),
        }
