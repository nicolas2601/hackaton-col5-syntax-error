"""Entidades service — top por dinero ejecutado + detalle."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache


class EntidadesService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    @ttl_cache(seconds=600)
    async def top(self, limit: int = 10) -> dict:
        rows = await self.db.fetch(
            f"""
            SELECT
                "Nit Entidad" AS nit,
                MAX("Nombre Entidad") AS nombre,
                COUNT(*)::int AS contratos,
                COALESCE(SUM(valor_pagado_num), 0)::float AS dinero_ejecutado,
                COALESCE(SUM(valor_contrato_num), 0)::float AS valor_total
            FROM {self.settings.data_table_name}
            WHERE "Nit Entidad" IS NOT NULL
              AND "Nit Entidad" <> ''
            GROUP BY "Nit Entidad"
            ORDER BY dinero_ejecutado DESC
            LIMIT $1
            """,
            limit,
        )
        items = [
            {
                "nit": r["nit"],
                "nombre": r["nombre"],
                "contratos": r["contratos"],
                "dinero_ejecutado": float(r["dinero_ejecutado"] or 0),
                "valor_total": float(r["valor_total"] or 0),
            }
            for r in rows
        ]
        return {"items": items, "count": len(items)}

    async def detalle(self, nit: str) -> dict:
        agg = await self.db.fetchrow(
            f"""
            SELECT
                "Nit Entidad" AS nit,
                MAX("Nombre Entidad") AS nombre,
                MAX("Sector") AS sector,
                MAX("Rama") AS rama,
                MAX("Orden") AS orden,
                COUNT(*)::int AS contratos,
                COALESCE(SUM(valor_pagado_num), 0)::float AS dinero_ejecutado,
                COALESCE(SUM(valor_contrato_num), 0)::float AS valor_total
            FROM {self.settings.data_table_name}
            WHERE "Nit Entidad" = $1
            GROUP BY "Nit Entidad"
            """,
            nit,
        )
        if agg is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entidad con NIT {nit!r} no encontrada",
            )

        depto_rows = await self.db.fetch(
            f"""
            SELECT DISTINCT "Departamento" AS depto
            FROM {self.settings.data_table_name}
            WHERE "Nit Entidad" = $1 AND "Departamento" IS NOT NULL
            ORDER BY depto
            """,
            nit,
        )
        return {
            "nit": agg["nit"],
            "nombre": agg["nombre"],
            "sector": agg["sector"],
            "rama": agg["rama"],
            "orden": agg["orden"],
            "contratos": agg["contratos"],
            "dinero_ejecutado": float(agg["dinero_ejecutado"] or 0),
            "valor_total": float(agg["valor_total"] or 0),
            "departamentos": [r["depto"] for r in depto_rows if r["depto"]],
        }
