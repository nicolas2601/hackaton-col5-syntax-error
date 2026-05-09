"""Anomalías financieras — detección por z-score."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache

# Umbral de z-score para considerar un contrato anómalo
Z_SCORE_ANOMALIA = 3.0
Z_SCORE_SOSPECHOSO = 2.0


class AnomaliasService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    async def _stats_globales(self) -> tuple[float, float]:
        row = await self.db.fetchrow(
            f"""
            SELECT
                AVG(valor_contrato_num)::float AS media,
                STDDEV_POP(valor_contrato_num)::float AS desv
            FROM {self.settings.data_table_name}
            WHERE valor_contrato_num IS NOT NULL
              AND valor_contrato_num > 0
            """
        )
        if row is None:
            return 0.0, 0.0
        return float(row["media"] or 0.0), float(row["desv"] or 0.0)

    @ttl_cache(seconds=300)
    async def top_anomalias(self, limit: int = 10) -> dict:
        media, desv = await self._stats_globales()
        if desv <= 0:
            return {
                "items": [],
                "count": 0,
                "media_dataset": media,
                "desv_std_dataset": desv,
            }

        rows = await self.db.fetch(
            f"""
            SELECT
                id_contrato AS id_contrato,
                nombre_entidad AS entidad,
                proveedor_adjudicado AS proveedor,
                objeto_del_contrato AS objeto,
                "Departamento" AS departamento,
                COALESCE(valor_contrato_num, 0)::float AS valor_contrato,
                COALESCE(valor_pagado_num, 0)::float AS valor_pagado,
                ((valor_contrato_num - $1) / NULLIF($2, 0))::float AS z_score
            FROM {self.settings.data_table_name}
            WHERE valor_contrato_num IS NOT NULL
              AND valor_contrato_num > 0
            ORDER BY valor_contrato_num DESC
            LIMIT $3
            """,
            media,
            desv,
            limit,
        )
        items = [
            {
                "id_contrato": r["id_contrato"],
                "entidad": r["entidad"],
                "proveedor": r["proveedor"],
                "objeto": (r["objeto"] or "")[:200] if r["objeto"] else None,
                "valor_contrato": float(r["valor_contrato"]),
                "valor_pagado": float(r["valor_pagado"]),
                "departamento": r["departamento"],
                "z_score": round(float(r["z_score"] or 0), 2),
            }
            for r in rows
        ]
        return {
            "items": items,
            "count": len(items),
            "media_dataset": round(media, 2),
            "desv_std_dataset": round(desv, 2),
        }

    async def validar(self, id_contrato: str) -> dict:
        row = await self.db.fetchrow(
            f"""
            SELECT
                id_contrato AS id_contrato,
                tipo_de_contrato AS tipo,
                modalidad_de_contratacion AS modalidad,
                COALESCE(valor_contrato_num, 0)::float AS valor_contrato,
                COALESCE(valor_pagado_num, 0)::float AS valor_pagado
            FROM {self.settings.data_table_name}
            WHERE id_contrato = $1
            LIMIT 1
            """,
            id_contrato,
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contrato {id_contrato!r} no encontrado",
            )

        # Stats por categoría (mismo Tipo de Contrato)
        cat_stats = await self.db.fetchrow(
            f"""
            SELECT
                COUNT(*)::int AS n,
                AVG(valor_contrato_num)::float AS media,
                STDDEV_POP(valor_contrato_num)::float AS desv
            FROM {self.settings.data_table_name}
            WHERE tipo_de_contrato = $1
              AND valor_contrato_num IS NOT NULL
              AND valor_contrato_num > 0
            """,
            row["tipo"],
        )
        media_cat = float((cat_stats and cat_stats["media"]) or 0.0)
        desv_cat = float((cat_stats and cat_stats["desv"]) or 0.0)
        n_cat = int((cat_stats and cat_stats["n"]) or 0)
        z = (
            (float(row["valor_contrato"]) - media_cat) / desv_cat
            if desv_cat > 0
            else 0.0
        )

        razones: list[str] = []
        if abs(z) >= Z_SCORE_ANOMALIA:
            razones.append(
                f"Z-score {z:.2f} excede umbral de anomalía ({Z_SCORE_ANOMALIA})"
            )
        elif abs(z) >= Z_SCORE_SOSPECHOSO:
            razones.append(
                f"Z-score {z:.2f} en zona sospechosa ({Z_SCORE_SOSPECHOSO}-{Z_SCORE_ANOMALIA})"
            )
        if float(row["valor_pagado"]) > float(row["valor_contrato"]) * 1.05:
            razones.append("Valor pagado supera valor del contrato en >5%")
        if float(row["valor_contrato"]) <= 0:
            razones.append("Valor del contrato es cero o negativo")

        if abs(z) >= Z_SCORE_ANOMALIA:
            veredicto = "anomalia"
        elif abs(z) >= Z_SCORE_SOSPECHOSO or razones:
            veredicto = "sospechoso"
        else:
            veredicto = "normal"
            razones = razones or ["Valor dentro de 2σ de la categoría — normal"]

        return {
            "id_contrato": row["id_contrato"],
            "veredicto": veredicto,
            "razones": razones,
            "valor_contrato": float(row["valor_contrato"]),
            "valor_pagado": float(row["valor_pagado"]),
            "z_score": round(z, 2),
            "media_categoria": round(media_cat, 2),
            "desv_std_categoria": round(desv_cat, 2),
            "contratos_referencia": n_cat,
        }
