#!/usr/bin/env python3
"""
ETL Loader — SECOP II Contratos Electrónicos 2025 (ronda 2 hackathon).

Carga el CSV /tmp/ronda2/SECOP_II_-_Contratos_Electrónicos_20260506.csv
(1.7 GB / 1,003,902 filas / 84 cols) a la tabla `contratos_2025` en el Postgres
del server tikno (DB `secop`).

Estrategia:
  1. Crear tabla con schema tipado (84 cols + id BIGSERIAL + ingested_at).
  2. Resume-safe: si COUNT(*) ya == filas esperadas, skipea.
  3. Stream del CSV línea por línea, normalizando tipos:
       - "$40,825,000" → 40825000.0       (regex [$,] → float)
       - "01/17/2024"  → DATE              (MM/DD/YYYY)
       - "2026 Mar 25 12:00:00 AM" → DATE  (formato Ultima Actualizacion)
       - "Si"/"No"     → bool
       - "" / null     → NULL
  4. Bulk load via COPY FROM STDIN (psycopg3) — ~80-150k rows/sec.
  5. Crear índices al final (más rápido que durante INSERT).

Uso:
    python load_2025.py [--csv /path/file.csv] [--force]

Variables de entorno:
    DATABASE_URL        DSN del Postgres (obligatorio)
    CSV_PATH            override del path del CSV (default: /tmp/ronda2/...)
    BATCH_SIZE          filas por flush a stdout COPY (default: 10000)
"""

from __future__ import annotations

import argparse
import csv
import io
import logging
import os
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

try:
    import psycopg
    from psycopg import sql
except ImportError:  # pragma: no cover
    print("ERROR: pip install psycopg[binary]>=3.2", file=sys.stderr)
    sys.exit(1)


# ─── Config ───────────────────────────────────────────────────

DEFAULT_CSV = "/tmp/ronda2/SECOP_II_-_Contratos_Electrónicos_20260506.csv"
EXPECTED_ROWS = 1_003_902
TABLE = "contratos_2025"
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10000"))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("etl-2025")


# ─── Schema ───────────────────────────────────────────────────
# (csv_header, db_column, pg_type, parser_key)
# parser_key: "text" | "money" | "date" | "date_alt" | "bool" | "int" | "bigint"

COLUMNS: list[tuple[str, str, str, str]] = [
    ("Nombre Entidad",                                  "nombre_entidad",                       "TEXT",        "text"),
    ("Nit Entidad",                                     "nit_entidad",                          "TEXT",        "text"),
    ("Departamento",                                    "departamento",                         "TEXT",        "text"),
    ("Ciudad",                                          "ciudad",                               "TEXT",        "text"),
    ("Localización",                                    "localizacion",                         "TEXT",        "text"),
    ("Orden",                                           "orden",                                "TEXT",        "text"),
    ("Sector",                                          "sector",                               "TEXT",        "text"),
    ("Rama",                                            "rama",                                 "TEXT",        "text"),
    ("Entidad Centralizada",                            "entidad_centralizada",                 "TEXT",        "text"),
    ("Proceso de Compra",                               "proceso_de_compra",                    "TEXT",        "text"),
    ("ID Contrato",                                     "id_contrato",                          "TEXT",        "text"),
    ("Referencia del Contrato",                         "referencia_del_contrato",              "TEXT",        "text"),
    ("Estado Contrato",                                 "estado_contrato",                      "TEXT",        "text"),
    ("Codigo de Categoria Principal",                   "codigo_de_categoria_principal",        "TEXT",        "text"),
    ("Descripcion del Proceso",                         "descripcion_del_proceso",              "TEXT",        "text"),
    ("Tipo de Contrato",                                "tipo_de_contrato",                     "TEXT",        "text"),
    ("Modalidad de Contratacion",                       "modalidad_de_contratacion",            "TEXT",        "text"),
    ("Justificacion Modalidad de Contratacion",         "justificacion_modalidad",              "TEXT",        "text"),
    ("Fecha de Firma",                                  "fecha_de_firma",                       "DATE",        "date"),
    ("Fecha de Inicio del Contrato",                    "fecha_de_inicio_del_contrato",         "DATE",        "date"),
    ("Fecha de Fin del Contrato",                       "fecha_de_fin_del_contrato",            "DATE",        "date"),
    ("Condiciones de Entrega",                          "condiciones_de_entrega",               "TEXT",        "text"),
    ("TipoDocProveedor",                                "tipodocproveedor",                     "TEXT",        "text"),
    ("Documento Proveedor",                             "documento_proveedor",                  "TEXT",        "text"),
    ("Proveedor Adjudicado",                            "proveedor_adjudicado",                 "TEXT",        "text"),
    ("Es Grupo",                                        "es_grupo",                             "BOOLEAN",     "bool"),
    ("Es Pyme",                                         "es_pyme",                              "BOOLEAN",     "bool"),
    ("Habilita Pago Adelantado",                        "habilita_pago_adelantado",             "BOOLEAN",     "bool"),
    ("Liquidación",                                     "liquidacion",                          "BOOLEAN",     "bool"),
    ("Obligación Ambiental",                            "obligacion_ambiental",                 "BOOLEAN",     "bool"),
    ("Obligaciones Postconsumo",                        "obligaciones_postconsumo",             "BOOLEAN",     "bool"),
    ("Reversion",                                       "reversion",                            "BOOLEAN",     "bool"),
    ("Origen de los Recursos",                          "origen_de_los_recursos",               "TEXT",        "text"),
    ("Destino Gasto",                                   "destino_gasto",                        "TEXT",        "text"),
    ("Valor del Contrato",                              "valor_del_contrato",                   "NUMERIC(20,2)", "money"),
    ("Valor de pago adelantado",                        "valor_de_pago_adelantado",             "NUMERIC(20,2)", "money"),
    ("Valor Facturado",                                 "valor_facturado",                      "NUMERIC(20,2)", "money"),
    ("Valor Pendiente de Pago",                         "valor_pendiente_de_pago",              "NUMERIC(20,2)", "money"),
    ("Valor Pagado",                                    "valor_pagado",                         "NUMERIC(20,2)", "money"),
    ("Valor Amortizado",                                "valor_amortizado",                     "NUMERIC(20,2)", "money"),
    ("Valor Pendiente de Amortizacion",                 "valor_pendiente_de_amortizacion",      "NUMERIC(20,2)", "money"),
    ("Valor Pendiente de Ejecucion",                    "valor_pendiente_de_ejecucion",         "NUMERIC(20,2)", "money"),
    ("Saldo CDP",                                       "saldo_cdp",                            "NUMERIC(20,2)", "money"),
    ("Saldo Vigencia",                                  "saldo_vigencia",                       "NUMERIC(20,2)", "money"),
    ("EsPostConflicto",                                 "es_post_conflicto",                    "BOOLEAN",     "bool"),
    ("Dias adicionados",                                "dias_adicionados",                     "INTEGER",     "int"),
    ("Puntos del Acuerdo",                              "puntos_del_acuerdo",                   "TEXT",        "text"),
    ("Pilares del Acuerdo",                             "pilares_del_acuerdo",                  "TEXT",        "text"),
    ("URLProceso",                                      "url_proceso",                          "TEXT",        "text"),
    ("Nombre Representante Legal",                      "nombre_representante_legal",           "TEXT",        "text"),
    ("Nacionalidad Representante Legal",                "nacionalidad_representante_legal",     "TEXT",        "text"),
    ("Domicilio Representante Legal",                   "domicilio_representante_legal",        "TEXT",        "text"),
    ("Tipo de Identificación Representante Legal",      "tipo_id_representante_legal",          "TEXT",        "text"),
    ("Identificación Representante Legal",              "identificacion_representante_legal",   "TEXT",        "text"),
    ("Género Representante Legal",                      "genero_representante_legal",           "TEXT",        "text"),
    ("Presupuesto General de la Nacion – PGN",          "presupuesto_pgn",                      "NUMERIC(20,2)", "money"),
    ("Sistema General de Participaciones",              "sistema_general_participaciones",      "NUMERIC(20,2)", "money"),
    ("Sistema General de Regalías",                     "sistema_general_regalias",             "NUMERIC(20,2)", "money"),
    ("Recursos Propios (Alcaldías, Gobernaciones y Resguardos Indígenas)", "recursos_propios_alcaldias", "NUMERIC(20,2)", "money"),
    ("Recursos de Credito",                             "recursos_de_credito",                  "NUMERIC(20,2)", "money"),
    ("Recursos Propios",                                "recursos_propios",                     "NUMERIC(20,2)", "money"),
    ("Ultima Actualizacion",                            "ultima_actualizacion",                 "DATE",        "date_alt"),
    ("Codigo Entidad",                                  "codigo_entidad",                       "TEXT",        "text"),
    ("Codigo Proveedor",                                "codigo_proveedor",                     "TEXT",        "text"),
    ("Fecha Inicio Liquidacion",                        "fecha_inicio_liquidacion",             "DATE",        "date_alt"),
    ("Fecha Fin Liquidacion",                           "fecha_fin_liquidacion",                "DATE",        "date_alt"),
    ("Objeto del Contrato",                             "objeto_del_contrato",                  "TEXT",        "text"),
    ("Duración del contrato",                           "duracion_del_contrato",                "TEXT",        "text"),
    ("Nombre del banco",                                "nombre_del_banco",                     "TEXT",        "text"),
    ("Tipo de cuenta",                                  "tipo_de_cuenta",                       "TEXT",        "text"),
    ("Número de cuenta",                                "numero_de_cuenta",                     "TEXT",        "text"),
    ("El contrato puede ser prorrogado",                "puede_ser_prorrogado",                 "BOOLEAN",     "bool"),
    ("Fecha de notificación de prorrogación",           "fecha_notif_prorrogacion",             "DATE",        "date"),
    ("Nombre ordenador del gasto",                      "nombre_ordenador_del_gasto",           "TEXT",        "text"),
    ("Tipo de documento Ordenador del gasto",           "tipo_doc_ordenador_gasto",             "TEXT",        "text"),
    ("Número de documento Ordenador del gasto",         "num_doc_ordenador_gasto",              "TEXT",        "text"),
    ("Nombre supervisor",                               "nombre_supervisor",                    "TEXT",        "text"),
    ("Tipo de documento supervisor",                    "tipo_doc_supervisor",                  "TEXT",        "text"),
    ("Número de documento supervisor",                  "num_doc_supervisor",                   "TEXT",        "text"),
    ("Nombre Ordenador de Pago",                        "nombre_ordenador_de_pago",             "TEXT",        "text"),
    ("Tipo de documento Ordenador de Pago",             "tipo_doc_ordenador_pago",              "TEXT",        "text"),
    ("Número de documento Ordenador de Pago",           "num_doc_ordenador_pago",               "TEXT",        "text"),
    ("Documentos Tipo",                                 "documentos_tipo",                      "TEXT",        "text"),
    ("Descripcion Documentos Tipo",                     "descripcion_documentos_tipo",          "TEXT",        "text"),
]

assert len(COLUMNS) == 84, f"Esperaba 84 columnas, hay {len(COLUMNS)}"


# ─── Parsers ──────────────────────────────────────────────────

_MONEY_RE = re.compile(r"[$,\s]")


def parse_money(s: str | None) -> str:
    """'$40,825,000' → '40825000'  (string para COPY, NULL si vacío)."""
    if not s or s.strip() in ("", "-", "null", "NULL"):
        return r"\N"
    cleaned = _MONEY_RE.sub("", s).strip()
    if not cleaned or cleaned == "-":
        return r"\N"
    try:
        # validar que sea numérico
        float(cleaned)
        return cleaned
    except ValueError:
        return r"\N"


def parse_date(s: str | None) -> str:
    """'01/17/2024' → '2024-01-17' (MM/DD/YYYY)."""
    if not s or not s.strip():
        return r"\N"
    s = s.strip()
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return r"\N"


def parse_date_alt(s: str | None) -> str:
    """'2026 Mar 25 12:00:00 AM' → '2026-03-25' (Ultima Actualizacion fmt)."""
    if not s or not s.strip():
        return r"\N"
    s = s.strip()
    # Intentar formato alt primero, luego los regulares.
    for fmt in (
        "%Y %b %d %I:%M:%S %p",
        "%Y %b %d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
    ):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return r"\N"


def parse_bool(s: str | None) -> str:
    if not s:
        return r"\N"
    v = s.strip().lower()
    if v in ("si", "sí", "yes", "true", "1", "y"):
        return "t"
    if v in ("no", "false", "0", "n"):
        return "f"
    if v in ("", "no aplica", "no definido", "n/a", "na"):
        return r"\N"
    return r"\N"


def parse_int(s: str | None) -> str:
    if not s or not s.strip():
        return r"\N"
    try:
        return str(int(float(s.replace(",", "").strip())))
    except ValueError:
        return r"\N"


def parse_text(s: str | None) -> str:
    if s is None:
        return r"\N"
    if s == "":
        return r"\N"
    # COPY usa \t como separador → escape de tab/newline/backslash.
    return (
        s.replace("\\", "\\\\")
        .replace("\t", " ")
        .replace("\n", " ")
        .replace("\r", " ")
    )


PARSERS = {
    "text":     parse_text,
    "money":    parse_money,
    "date":     parse_date,
    "date_alt": parse_date_alt,
    "bool":     parse_bool,
    "int":      parse_int,
    "bigint":   parse_int,
}


# ─── DDL ──────────────────────────────────────────────────────

def ddl_create_table() -> str:
    cols_sql = ",\n  ".join(
        f'"{db_col}" {pg_type}'
        for _, db_col, pg_type, _ in COLUMNS
    )
    return f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
  id BIGSERIAL PRIMARY KEY,
  {cols_sql},
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


INDEXES = [
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_nit            ON {TABLE} (nit_entidad);",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_doc_prov       ON {TABLE} (documento_proveedor);",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_fecha_firma    ON {TABLE} (fecha_de_firma);",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_valor          ON {TABLE} (valor_del_contrato);",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_modalidad      ON {TABLE} (modalidad_de_contratacion);",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_estado         ON {TABLE} (estado_contrato);",
    f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_departamento   ON {TABLE} (departamento);",
    (
        f"CREATE INDEX IF NOT EXISTS idx_{TABLE}_objeto_fts ON {TABLE} "
        f"USING GIN (to_tsvector('spanish', coalesce(objeto_del_contrato,'')));"
    ),
]


# ─── ETL ──────────────────────────────────────────────────────

def transform_row(row: dict[str, str]) -> str:
    """Convierte una row DictReader → línea TSV para COPY."""
    parts = []
    for csv_h, _, _, parser_key in COLUMNS:
        raw = row.get(csv_h, "")
        parts.append(PARSERS[parser_key](raw))
    return "\t".join(parts) + "\n"


def stream_tsv(csv_path: Path) -> Iterator[bytes]:
    """Generator: cada chunk = N filas TSV listas para COPY."""
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        # Validar headers
        missing = [c for c, _, _, _ in COLUMNS if c not in reader.fieldnames]
        if missing:
            log.warning(f"CSV missing cols: {missing[:5]}...")

        buf = io.StringIO()
        n_buf = 0
        for i, row in enumerate(reader, 1):
            buf.write(transform_row(row))
            n_buf += 1
            if n_buf >= BATCH_SIZE:
                yield buf.getvalue().encode("utf-8")
                buf = io.StringIO()
                n_buf = 0
                if i % 100_000 == 0:
                    log.info(f"  ... transformadas {i:,} filas")
        if n_buf:
            yield buf.getvalue().encode("utf-8")


def load(csv_path: Path, dsn: str, force: bool = False) -> None:
    log.info(f"Conectando a Postgres...")
    with psycopg.connect(dsn, autocommit=False) as conn:
        with conn.cursor() as cur:
            log.info(f"Creando tabla {TABLE} (IF NOT EXISTS)...")
            cur.execute(ddl_create_table())

            cur.execute(f"SELECT COUNT(*) FROM {TABLE};")
            current = cur.fetchone()[0]

            if current >= EXPECTED_ROWS and not force:
                log.info(
                    f"✓ Tabla ya tiene {current:,} filas (>= {EXPECTED_ROWS:,}). "
                    "Skipeando carga. Usá --force para recargar."
                )
                # Igual asegurar índices.
                _create_indexes(cur)
                conn.commit()
                return

            if force and current > 0:
                log.warning(f"--force: TRUNCATE {TABLE} ({current:,} filas eliminadas)")
                cur.execute(f"TRUNCATE TABLE {TABLE} RESTART IDENTITY;")

            log.info(f"Iniciando COPY desde {csv_path} ({csv_path.stat().st_size/1e9:.2f} GB)...")

            db_cols = [db for _, db, _, _ in COLUMNS]
            copy_sql = sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT text, NULL '\\N')").format(
                sql.Identifier(TABLE),
                sql.SQL(", ").join(map(sql.Identifier, db_cols)),
            )

            t0 = time.time()
            total = 0
            with cur.copy(copy_sql) as copy:
                for chunk in stream_tsv(csv_path):
                    copy.write(chunk)
                    total_lines = chunk.count(b"\n")
                    total += total_lines
                    elapsed = time.time() - t0
                    rate = total / max(elapsed, 0.001)
                    log.info(
                        f"  COPY: {total:,} / ~{EXPECTED_ROWS:,} "
                        f"({100*total/EXPECTED_ROWS:.1f}%) — {rate:,.0f} rows/s"
                    )

            elapsed = time.time() - t0
            log.info(f"✓ COPY completo: {total:,} filas en {elapsed:.1f}s ({total/elapsed:,.0f} rows/s)")

            _create_indexes(cur)
            log.info("Commit final...")
        conn.commit()
    log.info("✓ Carga 2025 completa.")


def _create_indexes(cur) -> None:
    log.info(f"Creando {len(INDEXES)} índices (IF NOT EXISTS)...")
    for idx in INDEXES:
        t0 = time.time()
        cur.execute(idx)
        log.info(f"  ✓ {idx[:80]}... ({time.time()-t0:.1f}s)")


# ─── Entrypoint ───────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default=os.getenv("CSV_PATH", DEFAULT_CSV))
    p.add_argument("--force", action="store_true",
                   help="TRUNCATE + recargar incluso si ya hay data")
    p.add_argument("--dsn", default=os.getenv("DATABASE_URL"),
                   help="Postgres DSN (default: $DATABASE_URL)")
    args = p.parse_args()

    if not args.dsn:
        log.error("DATABASE_URL no seteado y --dsn no provisto.")
        return 2

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        log.error(f"CSV no encontrado: {csv_path}")
        return 2

    try:
        load(csv_path, args.dsn, force=args.force)
        return 0
    except KeyboardInterrupt:
        log.warning("Interrumpido por usuario.")
        return 130
    except Exception as e:
        log.exception(f"FALLO ETL: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
