"""Stats service — totales y distribuciones del dataset."""

from __future__ import annotations

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache

# Lista canónica de las 84 columnas del snapshot SECOP II 2025
COLUMNAS_SECOP_II: list[str] = [
    "Nombre Entidad", "Nit Entidad", "Departamento", "Ciudad", "Localización",
    "Orden", "Sector", "Rama", "Entidad Centralizada", "Proceso de Compra",
    "ID Contrato", "Referencia del Contrato", "Estado Contrato",
    "Codigo de Categoria Principal", "Descripcion del Proceso",
    "Tipo de Contrato", "Modalidad de Contratacion",
    "Justificacion Modalidad de Contratacion", "Fecha de Firma",
    "Fecha de Inicio del Contrato", "Fecha de Fin del Contrato",
    "Condiciones de Entrega", "TipoDocProveedor", "Documento Proveedor",
    "Proveedor Adjudicado", "Es Grupo", "Es Pyme", "Habilita Pago Adelantado",
    "Liquidación", "Obligación Ambiental", "Obligaciones Postconsumo",
    "Reversion", "Origen de los Recursos", "Destino Gasto", "Valor del Contrato",
    "Valor de pago adelantado", "Valor Facturado", "Valor Pendiente de Pago",
    "Valor Pagado", "Valor Amortizado", "Valor Pendiente de Amortizacion",
    "Valor Pendiente de Ejecucion", "Saldo CDP", "Saldo Vigencia",
    "EsPostConflicto", "Dias adicionados", "Puntos del Acuerdo",
    "Pilares del Acuerdo", "URLProceso", "Nombre Representante Legal",
    "Nacionalidad Representante Legal", "Domicilio Representante Legal",
    "Tipo de Identificación Representante Legal",
    "Identificación Representante Legal", "Género Representante Legal",
    "Presupuesto General de la Nacion – PGN", "Sistema General de Participaciones",
    "Sistema General de Regalías",
    "Recursos Propios (Alcaldías, Gobernaciones y Resguardos Indígenas)",
    "Recursos de Credito", "Recursos Propios", "Ultima Actualizacion",
    "Codigo Entidad", "Codigo Proveedor", "Fecha Inicio Liquidacion",
    "Fecha Fin Liquidacion", "Objeto del Contrato", "Duración del contrato",
    "Nombre del banco", "Tipo de cuenta", "Número de cuenta",
    "El contrato puede ser prorrogado", "Fecha de notificación de prorrogación",
    "Nombre ordenador del gasto", "Tipo de documento Ordenador del gasto",
    "Número de documento Ordenador del gasto", "Nombre supervisor",
    "Tipo de documento supervisor", "Número de documento supervisor",
    "Nombre Ordenador de Pago", "Tipo de documento Ordenador de Pago",
    "Número de documento Ordenador de Pago", "Documentos Tipo",
    "Descripcion Documentos Tipo",
]


class StatsService:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.settings = get_settings()

    async def total(self) -> dict:
        """Total real consultado a Postgres + snapshot date."""
        total = await self.db.fetchval(
            f"SELECT COUNT(*) FROM {self.settings.data_table_name}"
        )
        return {
            "total": int(total or self.settings.data_total_rows),
            "snapshot": self.settings.data_snapshot_date,
        }

    def columnas(self) -> dict:
        """Lista estática de columnas (no consulta DB — es metadata)."""
        return {"count": len(COLUMNAS_SECOP_II), "columnas": COLUMNAS_SECOP_II}

    @ttl_cache(seconds=600)
    async def anios(self) -> dict:
        """Distribución de contratos por año de firma."""
        rows = await self.db.fetch(
            f"""
            SELECT
                EXTRACT(YEAR FROM "Fecha de Firma"::date)::int AS anio,
                COUNT(*)::int AS contratos
            FROM {self.settings.data_table_name}
            WHERE "Fecha de Firma" IS NOT NULL
              AND "Fecha de Firma" <> ''
            GROUP BY anio
            ORDER BY anio
            """
        )
        items = [{"anio": r["anio"], "contratos": r["contratos"]} for r in rows]
        return {"items": items, "count": len(items)}
