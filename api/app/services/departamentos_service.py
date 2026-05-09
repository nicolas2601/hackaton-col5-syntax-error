"""Departamentos service."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache


class DepartamentosService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    @ttl_cache(seconds=600)
    async def top(self, limit: int = 10) -> dict:
        rows = await self.db.fetch(
            f"""
            SELECT
                "Departamento" AS nombre,
                COUNT(*)::int AS contratos,
                COALESCE(SUM(valor_contrato_num), 0)::float AS valor_total
            FROM {self.settings.data_table_name}
            WHERE "Departamento" IS NOT NULL
              AND "Departamento" <> ''
            GROUP BY "Departamento"
            ORDER BY contratos DESC
            LIMIT $1
            """,
            limit,
        )
        items = [
            {
                "nombre": r["nombre"],
                "contratos": r["contratos"],
                "valor_total": float(r["valor_total"] or 0),
            }
            for r in rows
        ]
        return {"items": items, "count": len(items)}

    async def detalle(self, nombre: str, muestras: int = 10) -> dict:
        agg = await self.db.fetchrow(
            f"""
            SELECT
                COUNT(*)::int AS contratos,
                COALESCE(SUM(valor_contrato_num), 0)::float AS valor_total
            FROM {self.settings.data_table_name}
            WHERE LOWER("Departamento") = LOWER($1)
            """,
            nombre,
        )
        if agg is None or int(agg["contratos"] or 0) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento '{nombre}' no encontrado en el dataset",
            )

        sample_rows = await self.db.fetch(
            f"""
            SELECT
                id_contrato AS id_contrato,
                nombre_entidad AS entidad,
                objeto_del_contrato AS objeto,
                COALESCE(valor_contrato_num, 0)::float AS valor
            FROM {self.settings.data_table_name}
            WHERE LOWER("Departamento") = LOWER($1)
            ORDER BY valor_contrato_num DESC NULLS LAST
            LIMIT $2
            """,
            nombre,
            muestras,
        )
        muestras_list = [
            {
                "id_contrato": r["id_contrato"],
                "entidad": r["entidad"],
                "objeto": (r["objeto"] or "")[:200],
                "valor": float(r["valor"] or 0),
            }
            for r in sample_rows
        ]
        return {
            "nombre": nombre,
            "contratos": int(agg["contratos"]),
            "valor_total": float(agg["valor_total"] or 0),
            "muestras": muestras_list,
        }
