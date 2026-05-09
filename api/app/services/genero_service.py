"""Brecha de género por representante legal."""

from __future__ import annotations

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache


class GeneroService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    @ttl_cache(seconds=900)
    async def brecha(self) -> dict:
        rows = await self.db.fetch(
            f"""
            SELECT
                COALESCE(NULLIF(TRIM(genero_representante_legal), ''), 'Sin dato') AS genero,
                COUNT(*)::int AS count,
                COALESCE(SUM(valor_contrato_num), 0)::float AS total_valor,
                COALESCE(AVG(valor_contrato_num), 0)::float AS promedio,
                COALESCE(
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY valor_contrato_num),
                    0
                )::float AS mediana
            FROM {self.settings.data_table_name}
            GROUP BY genero
            ORDER BY count DESC
            """
        )
        total_count = sum(int(r["count"]) for r in rows) or 1
        total_valor = sum(float(r["total_valor"]) for r in rows) or 1.0

        items = [
            {
                "genero": r["genero"],
                "count": int(r["count"]),
                "total_valor": float(r["total_valor"]),
                "promedio": round(float(r["promedio"] or 0), 2),
                "mediana": round(float(r["mediana"] or 0), 2),
                "pct_count": round((int(r["count"]) / total_count) * 100, 2),
                "pct_valor": round((float(r["total_valor"]) / total_valor) * 100, 2),
            }
            for r in rows
        ]

        # Brecha: dif entre promedio del género dominante (más count) y los demás
        ranked = [i for i in items if i["genero"] not in ("Sin dato", "")]
        if len(ranked) >= 2:
            top = ranked[0]["promedio"] or 0
            otros = [i["promedio"] for i in ranked[1:] if i["promedio"]]
            avg_otros = sum(otros) / len(otros) if otros else 0
            brecha = (
                round(((top - avg_otros) / top) * 100, 2)
                if top
                else 0.0
            )
        else:
            brecha = 0.0

        return {
            "items": items,
            "brecha_promedio_pct": brecha,
            "total_contratos": total_count,
            "total_valor": round(total_valor, 2),
        }
