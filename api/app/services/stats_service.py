"""Stats service — totales y distribuciones del dataset."""

from __future__ import annotations

from app.config import get_settings
from app.database import Database
from app.utils.cache import ttl_cache

# Lista canónica de las 84 columnas del snapshot SECOP II 2025
COLUMNAS_SECOP_II: list[str] = [
    nombre_entidad, nit_entidad, "Departamento", "Ciudad", "Localización",
    "Orden", "Sector", "Rama", entidad_centralizada, proceso_de_compra,
    id_contrato, referencia_del_contrato, estado_contrato,
    codigo_de_categoria_principal, descripcion_del_proceso,
    tipo_de_contrato, modalidad_de_contratacion,
    justificacion_modalidad, fecha_de_firma,
    fecha_de_inicio_del_contrato, fecha_de_fin_del_contrato,
    condiciones_de_entrega, "TipoDocProveedor", documento_proveedor,
    proveedor_adjudicado, es_grupo, es_pyme, habilita_pago_adelantado,
    "Liquidación", obligacion_ambiental, obligaciones_postconsumo,
    "Reversion", origen_de_los_recursos, destino_gasto, valor_del_contrato,
    valor_de_pago_adelantado, valor_facturado, valor_pendiente_de_pago,
    valor_pagado, valor_amortizado, valor_pendiente_de_amortizacion,
    valor_pendiente_de_ejecucion, saldo_cdp, saldo_vigencia,
    "EsPostConflicto", dias_adicionados, puntos_del_acuerdo,
    pilares_del_acuerdo, "URLProceso", nombre_representante_legal,
    nacionalidad_representante_legal, domicilio_representante_legal,
    tipo_id_representante_legal,
    identificacion_representante_legal, genero_representante_legal,
    "Presupuesto General de la Nacion – PGN", sistema_general_participaciones,
    sistema_general_regalias,
    "Recursos Propios (Alcaldías, Gobernaciones y Resguardos Indígenas)",
    recursos_de_credito, recursos_propios, ultima_actualizacion,
    codigo_entidad, codigo_proveedor, fecha_inicio_liquidacion,
    fecha_fin_liquidacion, objeto_del_contrato, duracion_del_contrato,
    nombre_del_banco, tipo_de_cuenta, numero_de_cuenta,
    puede_ser_prorrogado, fecha_notif_prorrogacion,
    nombre_ordenador_del_gasto, tipo_doc_ordenador_gasto,
    num_doc_ordenador_gasto, nombre_supervisor,
    tipo_doc_supervisor, num_doc_supervisor,
    nombre_ordenador_de_pago, tipo_doc_ordenador_pago,
    num_doc_ordenador_pago, documentos_tipo,
    descripcion_documentos_tipo,
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
                EXTRACT(YEAR FROM fecha_de_firma::date)::int AS anio,
                COUNT(*)::int AS contratos
            FROM {self.settings.data_table_name}
            WHERE fecha_de_firma IS NOT NULL
              AND fecha_de_firma <> ''
            GROUP BY anio
            ORDER BY anio
            """
        )
        items = [{"anio": r["anio"], "contratos": r["contratos"]} for r in rows]
        return {"items": items, "count": len(items)}
