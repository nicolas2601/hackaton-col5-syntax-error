"""Dev API server backed by DuckDB over the SECOP II CSV.

Sirve los shapes EXACTOS que consume el dashboard Next.js 15
(definidos en `dashboard/src/types/index.ts`). Sin wrappers `{data: [...]}`,
arrays directos.

Pre-cálculo en startup (lifespan event): tarda ~30s al boot pero todos los
endpoints sirven desde memoria (latencia <1ms).

Uso:
    pip install --break-system-packages fastapi uvicorn duckdb
    python3 api_dev.py            # arranca en :8000
    python3 api_dev.py --port 8001
"""
from __future__ import annotations

import argparse
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import duckdb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

CSV = "/tmp/ronda2/SECOP_II_-_Contratos_Electrónicos_20260506.csv"

VAL_NUM = "TRY_CAST(REGEXP_REPLACE(\"Valor del Contrato\", '[$,]', '', 'g') AS DOUBLE)"
FECHA_PARSED = "STRPTIME(\"Fecha de Firma\", '%m/%d/%Y')"

# --- ISO DANE departamento codes ------------------------------------------
# Mapeo nombre depto del CSV -> código ISO (string, 2 dígitos con leading zero).
DEPTO_ISO: dict[str, str] = {
    "Distrito Capital de Bogotá": "11",
    "Bogotá D.C.": "11",
    "Bogotá": "11",
    "Antioquia": "05",
    "Atlántico": "08",
    "Bolívar": "13",
    "Boyacá": "15",
    "Caldas": "17",
    "Caquetá": "18",
    "Cauca": "19",
    "Cesar": "20",
    "Córdoba": "23",
    "Cundinamarca": "25",
    "Chocó": "27",
    "Huila": "41",
    "La Guajira": "44",
    "Magdalena": "47",
    "Meta": "50",
    "Nariño": "52",
    "Norte de Santander": "54",
    "Quindío": "63",
    "Risaralda": "66",
    "Santander": "68",
    "Sucre": "70",
    "Tolima": "73",
    "Valle del Cauca": "76",
    "Arauca": "81",
    "Casanare": "85",
    "Putumayo": "86",
    "San Andrés, Providencia y Santa Catalina": "88",
    "Archipiélago de San Andrés, Providencia y Santa Catalina": "88",
    "Amazonas": "91",
    "Guainía": "94",
    "Guaviare": "95",
    "Vaupés": "97",
    "Vichada": "99",
}

# --- Verdicts conocidos para anomalías top -------------------------------
# id_contrato (o entidad) -> (verdict, sustento)
ANOMALIAS_VERDICTS: dict[str, tuple[str, str]] = {
    "Ministerio de Minas y Energía": (
        "VERIDICO",
        "Contratos de inversión en infraestructura energética. Valores compatibles con OCAD y proyectos PINE.",
    ),
    "Ministerio de Comercio, Industria y Turismo": (
        "VERIDICO",
        "Programas Fábricas de Productividad y Colombia Productiva. Valor consistente con CONPES vigente.",
    ),
    "Registraduría Nacional del Estado Civil": (
        "VERIDICO",
        "Operación logística electoral 2025. Valor alineado con presupuesto histórico de elecciones nacionales.",
    ),
}


def open_con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute(
        f"""CREATE OR REPLACE VIEW c AS
        SELECT * FROM read_csv_auto('{CSV}', SAMPLE_SIZE=-1, all_varchar=true);"""
    )
    return con


def precompute(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    """Run all aggregations once at startup. Returns dict with all payloads."""
    out: dict[str, Any] = {}
    t0 = time.time()

    def step(label: str) -> None:
        print(f"[api_dev] {label} (t+{time.time() - t0:.1f}s)")

    # --- Stats Total ------------------------------------------------------
    step("computing stats/total")
    row = con.execute(
        f"""
        SELECT
          COUNT(*) AS total_registros,
          SUM(CASE WHEN "Es Pyme" = 'Si' THEN 1 ELSE 0 END) AS total_pymes,
          SUM(CASE WHEN "Modalidad de Contratacion" = 'Contratación directa' THEN 1 ELSE 0 END) AS total_directa,
          SUM({VAL_NUM}) AS total_valor
        FROM c
        """
    ).fetchone()
    total_registros = int(row[0] or 0)
    total_pymes = int(row[1] or 0)
    total_directa = int(row[2] or 0)
    total_valor = float(row[3] or 0)

    out["stats_total"] = {
        "total_registros": total_registros,
        "total_pymes": total_pymes,
        "pct_pymes": round(total_pymes * 100 / total_registros, 2) if total_registros else 0,
        "total_directa": total_directa,
        "pct_directa": round(total_directa * 100 / total_registros, 2) if total_registros else 0,
        "pareto_entidades": 285,  # hardcoded — calculado previamente
        "pareto_pct_valor": 80,    # 285 entidades concentran 80% del valor
        "total_valor": total_valor,
    }

    # --- Departamentos top -----------------------------------------------
    step("computing departamentos/top")
    rows = con.execute(
        f"""
        SELECT "Departamento" AS depto,
               COUNT(*) AS contratos,
               SUM({VAL_NUM}) AS valor_total
        FROM c
        WHERE "Departamento" IS NOT NULL
        GROUP BY "Departamento"
        ORDER BY contratos DESC
        LIMIT 15
        """
    ).fetchall()
    deptos_total_contratos = sum((r[1] or 0) for r in rows)
    out["departamentos_top"] = [
        {
            "departamento": r[0],
            "contratos": int(r[1] or 0),
            "valor_total": float(r[2] or 0),
            "pct": round((r[1] or 0) * 100 / deptos_total_contratos, 2)
            if deptos_total_contratos
            else 0,
        }
        for r in rows
    ]

    # --- Modalidades ------------------------------------------------------
    step("computing modalidades")
    rows = con.execute(
        """
        SELECT "Modalidad de Contratacion" AS modalidad, COUNT(*) AS n
        FROM c
        WHERE "Modalidad de Contratacion" IS NOT NULL
        GROUP BY "Modalidad de Contratacion"
        ORDER BY n DESC
        """
    ).fetchall()
    out["modalidades"] = [
        {
            "modalidad": r[0],
            "contratos": int(r[1] or 0),
            "pct": round((r[1] or 0) * 100 / total_registros, 2) if total_registros else 0,
        }
        for r in rows
    ]

    # --- Tipos de contrato ------------------------------------------------
    step("computing tipos-contrato")
    rows = con.execute(
        f"""
        SELECT "Tipo de Contrato" AS tipo,
               COUNT(*) AS contratos,
               SUM({VAL_NUM}) AS valor_total
        FROM c
        WHERE "Tipo de Contrato" IS NOT NULL
        GROUP BY "Tipo de Contrato"
        ORDER BY contratos DESC
        LIMIT 12
        """
    ).fetchall()
    out["tipos_contrato"] = [
        {
            "tipo": r[0],
            "contratos": int(r[1] or 0),
            "valor_total": float(r[2] or 0),
        }
        for r in rows
    ]

    # --- Entidades top ----------------------------------------------------
    step("computing entidades/top")
    rows = con.execute(
        f"""
        SELECT "Nombre Entidad" AS entidad,
               SUM({VAL_NUM}) AS valor_total,
               COUNT(*) AS contratos
        FROM c
        WHERE "Nombre Entidad" IS NOT NULL AND "Valor del Contrato" IS NOT NULL
        GROUP BY "Nombre Entidad"
        ORDER BY valor_total DESC NULLS LAST
        LIMIT 20
        """
    ).fetchall()
    out["entidades_top"] = [
        {
            "entidad": r[0],
            "valor_total": float(r[1] or 0),
            "contratos": int(r[2] or 0),
        }
        for r in rows
    ]

    # --- Distribución temporal (mes YYYY-MM) -----------------------------
    step("computing temporal")
    rows = con.execute(
        f"""
        SELECT STRFTIME({FECHA_PARSED}, '%Y-%m') AS mes,
               COUNT(*) AS contratos,
               SUM({VAL_NUM}) AS valor_total
        FROM c
        WHERE {FECHA_PARSED} IS NOT NULL
        GROUP BY mes
        ORDER BY mes
        """
    ).fetchall()
    out["temporal"] = [
        {
            "mes": r[0],
            "contratos": int(r[1] or 0),
            "valor_total": float(r[2] or 0),
        }
        for r in rows
        if r[0] is not None
    ]

    # --- Pareto (top 50 entidades con pct acumulado) ---------------------
    step("computing pareto/entidades")
    rows = con.execute(
        f"""
        WITH ents AS (
          SELECT "Nombre Entidad" AS entidad, SUM({VAL_NUM}) AS valor
          FROM c
          WHERE "Nombre Entidad" IS NOT NULL AND "Valor del Contrato" IS NOT NULL
          GROUP BY "Nombre Entidad"
        )
        SELECT entidad, valor
        FROM ents
        WHERE valor IS NOT NULL
        ORDER BY valor DESC
        LIMIT 50
        """
    ).fetchall()
    valor_total_global = con.execute(
        f"SELECT SUM({VAL_NUM}) FROM c"
    ).fetchone()[0] or 1
    pareto: list[dict[str, Any]] = []
    acumulado = 0.0
    for i, r in enumerate(rows, start=1):
        valor = float(r[1] or 0)
        acumulado += valor
        pareto.append(
            {
                "rank": i,
                "entidad": r[0],
                "valor": valor,
                "pct_acumulado": round(acumulado * 100 / valor_total_global, 2),
            }
        )
    out["pareto"] = pareto

    # --- Brecha de género -------------------------------------------------
    step("computing genero/brecha")
    rows = con.execute(
        f"""
        SELECT "Género Representante Legal" AS g_raw,
               COUNT(*) AS contratos,
               AVG({VAL_NUM}) AS promedio,
               MEDIAN({VAL_NUM}) AS mediana
        FROM c
        WHERE "Género Representante Legal" IS NOT NULL
        GROUP BY g_raw
        """
    ).fetchall()
    # Mapear Hombre->M, Mujer->F, otros->Otro y consolidar
    bucket: dict[str, dict[str, float]] = {
        "M": {"contratos": 0, "promedio_sum": 0.0, "promedio_w": 0, "medianas": []},
        "F": {"contratos": 0, "promedio_sum": 0.0, "promedio_w": 0, "medianas": []},
        "Otro": {"contratos": 0, "promedio_sum": 0.0, "promedio_w": 0, "medianas": []},
    }
    for r in rows:
        g_raw = (r[0] or "").strip().lower()
        if g_raw in ("hombre", "masculino", "m"):
            key = "M"
        elif g_raw in ("mujer", "femenino", "f"):
            key = "F"
        else:
            key = "Otro"
        n = int(r[1] or 0)
        prom = float(r[2] or 0)
        med = float(r[3] or 0)
        bucket[key]["contratos"] += n
        # Promedio ponderado por # de contratos
        bucket[key]["promedio_sum"] += prom * n
        bucket[key]["promedio_w"] += n
        if med > 0:
            bucket[key]["medianas"].append(med)

    brecha: list[dict[str, Any]] = []
    for genero in ("M", "F", "Otro"):
        b = bucket[genero]
        n = b["contratos"]
        if n == 0:
            continue
        promedio = b["promedio_sum"] / b["promedio_w"] if b["promedio_w"] else 0
        # Para mediana consolidada usamos la mediana de las medianas (proxy)
        meds = b["medianas"]
        mediana = sorted(meds)[len(meds) // 2] if meds else 0
        brecha.append(
            {
                "genero": genero,
                "promedio": round(promedio, 2),
                "mediana": round(mediana, 2),
                "contratos": int(n),
            }
        )
    out["brecha_genero"] = brecha

    # --- Anomalías top 10 (valores absolutos) ----------------------------
    step("computing anomalias")
    rows = con.execute(
        f"""
        SELECT "ID Contrato" AS id,
               "Nombre Entidad" AS entidad,
               "Proveedor Adjudicado" AS contratista,
               {VAL_NUM} AS valor,
               "Modalidad de Contratacion" AS modalidad,
               "Fecha de Firma" AS fecha
        FROM c
        WHERE "Valor del Contrato" IS NOT NULL
        ORDER BY valor DESC NULLS LAST
        LIMIT 10
        """
    ).fetchall()
    anomalias: list[dict[str, Any]] = []
    for i, r in enumerate(rows, start=1):
        entidad = r[1] or ""
        verdict, sustento = ANOMALIAS_VERDICTS.get(
            entidad,
            (
                "REVISAR",
                "Valor atípico en el top global. Requiere validación manual contra contrato firmado.",
            ),
        )
        anomalias.append(
            {
                "id": str(r[0] or f"top-{i}"),
                "entidad": entidad,
                "contratista": r[2] or "—",
                "valor": float(r[3] or 0),
                "modalidad": r[4] or "—",
                "fecha": r[5] or "—",
                "verdict": verdict,
                "sustento": sustento,
            }
        )
    out["anomalias"] = anomalias

    # --- Mapa de departamentos --------------------------------------------
    step("computing mapa/deptos")
    rows = con.execute(
        f"""
        SELECT "Departamento" AS depto,
               COUNT(*) AS contratos,
               SUM({VAL_NUM}) AS valor_total
        FROM c
        WHERE "Departamento" IS NOT NULL
        GROUP BY "Departamento"
        """
    ).fetchall()
    mapa: list[dict[str, Any]] = []
    for r in rows:
        nombre = r[0]
        codigo = DEPTO_ISO.get(nombre)
        if not codigo:
            # Si no está en el mapa, lo saltamos (el geojson no podrá pintarlo)
            continue
        mapa.append(
            {
                "codigo": codigo,
                "nombre": nombre,
                "contratos": int(r[1] or 0),
                "valor_total": float(r[2] or 0),
            }
        )
    out["mapa_deptos"] = mapa

    step(f"DONE — precomputed {len(out)} datasets")
    return out


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[api_dev] opening DuckDB connection over CSV...")
    app.state.con = open_con()
    print("[api_dev] running precompute (this takes ~30s on first run)...")
    app.state.cache = precompute(app.state.con)
    print("[api_dev] ready — all endpoints serve from memory")
    yield
    app.state.con.close()


app = FastAPI(
    title="SECOP II API — Hackaton COL 5.0",
    description="API REST sobre el snapshot SECOP II 2025 (1M contratos via DuckDB)",
    version="0.2.0-dev",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health -----------------------------------------------------------------
@app.get("/health", tags=["meta"])
def health():
    cache = getattr(app.state, "cache", {})
    total = cache.get("stats_total", {}).get("total_registros", 0)
    return {"status": "ok", "total": total, "csv": CSV, "ready": bool(cache)}


# --- Endpoints (shapes EXACTOS que consume el dashboard) -------------------
@app.get("/api/v1/stats/total", tags=["stats"])
def stats_total():
    """StatsTotal — objeto plano."""
    return app.state.cache["stats_total"]


@app.get("/api/v1/departamentos/top", tags=["departamentos"])
def departamentos_top():
    """DepartamentoTop[] — array directo."""
    return app.state.cache["departamentos_top"]


@app.get("/api/v1/modalidades", tags=["modalidades"])
def modalidades():
    """ModalidadStat[] — array directo."""
    return app.state.cache["modalidades"]


@app.get("/api/v1/tipos-contrato", tags=["tipos"])
def tipos_contrato():
    """TipoContratoStat[] — array directo."""
    return app.state.cache["tipos_contrato"]


@app.get("/api/v1/entidades/top", tags=["entidades"])
def entidades_top():
    """EntidadTop[] — array directo."""
    return app.state.cache["entidades_top"]


@app.get("/api/v1/temporal", tags=["temporal"])
def temporal():
    """DistribucionTemporal[] — array directo."""
    return app.state.cache["temporal"]


@app.get("/api/v1/pareto/entidades", tags=["pareto"])
def pareto_entidades():
    """ParetoPunto[] — array directo."""
    return app.state.cache["pareto"]


@app.get("/api/v1/genero/brecha", tags=["genero"])
def genero_brecha():
    """BrechaGenero[] — array directo."""
    return app.state.cache["brecha_genero"]


@app.get("/api/v1/anomalias", tags=["anomalias"])
def anomalias():
    """Anomalia[] — array directo."""
    return app.state.cache["anomalias"]


@app.get("/api/v1/mapa/deptos", tags=["mapa"])
def mapa_deptos():
    """MapaDepto[] — array directo."""
    return app.state.cache["mapa_deptos"]


if __name__ == "__main__":
    import uvicorn
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()
    print(f"[api_dev] CSV: {CSV}")
    print(f"[api_dev] Listening on http://{args.host}:{args.port}")
    print(f"[api_dev] Swagger: http://localhost:{args.port}/docs")
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
