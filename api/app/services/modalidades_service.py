"""Modalidades service."""

from __future__ import annotations

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache


class ModalidadesService:
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
            SELECT
                "Modalidad de Contratacion" AS modalidad,
                COUNT(*)::int AS count
            FROM {self.settings.data_table_name}
            WHERE "Modalidad de Contratacion" IS NOT NULL
              AND "Modalidad de Contratacion" <> ''
            GROUP BY "Modalidad de Contratacion"
            ORDER BY count DESC
            LIMIT $1
            """,
            limit,
        )
        items = [
            {
                "modalidad": r["modalidad"],
                "count": r["count"],
                "pct": round((r["count"] / total_int) * 100, 2),
            }
            for r in rows
        ]
        return {"items": items, "count": len(items)}

    async def contratos_por_modalidad(
        self, modalidad: str, limit: int = 50, offset: int = 0
    ) -> dict:
        rows = await self.db.fetch(
            f"""
            SELECT
                "ID Contrato" AS id_contrato,
                "Nombre Entidad" AS entidad,
                "Objeto del Contrato" AS objeto,
                "Departamento" AS departamento,
                "Fecha de Firma" AS fecha_firma,
                COALESCE(valor_contrato_num, 0)::float AS valor
            FROM {self.settings.data_table_name}
            WHERE LOWER("Modalidad de Contratacion") = LOWER($1)
            ORDER BY valor_contrato_num DESC NULLS LAST
            LIMIT $2 OFFSET $3
            """,
            modalidad,
            limit,
            offset,
        )
        items = [
            {
                "id_contrato": r["id_contrato"],
                "entidad": r["entidad"],
                "objeto": (r["objeto"] or "")[:300] if r["objeto"] else None,
                "valor": float(r["valor"] or 0),
                "departamento": r["departamento"],
                "fecha_firma": r["fecha_firma"],
            }
            for r in rows
        ]
        return {
            "modalidad": modalidad,
            "items": items,
            "count": len(items),
            "limit": limit,
            "offset": offset,
        }
