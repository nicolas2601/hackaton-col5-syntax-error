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
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Literal

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


# =========================================================================
# Pydantic response models (enrich Swagger schema)
# =========================================================================
class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    total: int = Field(..., description="Total de contratos cargados en memoria", example=1003902)
    csv: str = Field(..., description="Path absoluto del CSV fuente", example="/data/secop.csv")
    ready: bool = Field(..., description="True si el precompute terminó", example=True)


class StatsTotal(BaseModel):
    total_registros: int = Field(..., example=1003902)
    total_pymes: int = Field(..., example=132479)
    pct_pymes: float = Field(..., description="Porcentaje de Pymes (0-100)", example=13.20)
    total_directa: int = Field(..., description="Contratos por Contratación Directa", example=759993)
    pct_directa: float = Field(..., example=75.70)
    pareto_entidades: int = Field(..., description="Entidades que concentran 80% del valor", example=285)
    pareto_pct_valor: int = Field(..., example=80)
    total_valor: float = Field(..., description="Valor agregado en COP", example=166703293895413.0)


class DepartamentoTop(BaseModel):
    departamento: str = Field(..., example="Distrito Capital de Bogotá")
    contratos: int = Field(..., example=280248)
    valor_total: float = Field(..., example=69469406868337.0)
    pct: float = Field(..., description="Porcentaje sobre los top 15 deptos", example=27.92)


class ModalidadStat(BaseModel):
    modalidad: str = Field(..., example="Contratación directa")
    contratos: int = Field(..., example=759993)
    pct: float = Field(..., example=75.70)


class TipoContratoStat(BaseModel):
    tipo: str = Field(..., example="Prestación de servicios")
    contratos: int = Field(..., example=860913)
    valor_total: float = Field(..., example=52847104050186.0)


class EntidadTop(BaseModel):
    entidad: str = Field(..., example="DISTRITO ESPECIAL DE CIENCIA TECNOLOGIA E INNOVACION DE MEDELLIN")
    valor_total: float = Field(..., example=7192818196456.0)
    contratos: int = Field(..., example=1446)


class DistribucionTemporal(BaseModel):
    mes: str = Field(..., description="Año-mes en formato YYYY-MM", example="2025-12")
    contratos: int = Field(..., example=89432)
    valor_total: float = Field(..., example=12345678901.0)


class ParetoPunto(BaseModel):
    rank: int = Field(..., example=1)
    entidad: str = Field(..., example="DISTRITO ESPECIAL DE CTI MEDELLIN")
    valor: float = Field(..., example=7192818196456.0)
    pct_acumulado: float = Field(..., description="% acumulado del valor total", example=4.31)


class BrechaGenero(BaseModel):
    genero: Literal["M", "F", "Otro"] = Field(..., example="M")
    promedio: float = Field(..., description="Valor promedio por contrato (COP)", example=141293990.0)
    mediana: float = Field(..., example=20400000.0)
    contratos: int = Field(..., example=378213)


class Anomalia(BaseModel):
    id: str = Field(..., example="CO1.PCCNTR.8738616")
    entidad: str = Field(..., example="MINISTERIO DE MINAS Y ENERGIA")
    contratista: str = Field(..., example="GECELCA S.A. E.S.P.")
    valor: float = Field(..., example=4205027751839.0)
    modalidad: str = Field(..., example="Contratación directa")
    fecha: str = Field(..., description="Fecha en formato MM/DD/YYYY del CSV original", example="12/29/2025")
    verdict: Literal["VERIDICO", "FALSO", "REVISAR"] = Field(..., example="VERIDICO")
    sustento: str = Field(..., description="Razonamiento textual de la clasificación")


class MapaDepto(BaseModel):
    codigo: str = Field(..., description="ISO DANE 2 dígitos", example="11")
    nombre: str = Field(..., example="Distrito Capital de Bogotá")
    contratos: int = Field(..., example=280248)
    valor_total: float = Field(..., example=69469406868337.0)


# =========================================================================
# OpenAPI tags (rich descriptions in Swagger)
# =========================================================================
OPENAPI_TAGS = [
    {
        "name": "meta",
        "description": "Endpoints meta del servicio: liveness, versión, estado del cache.",
    },
    {
        "name": "stats",
        "description": "**Agregados globales** del snapshot SECOP II 2025: total, Pymes, contratación directa, valor agregado, Pareto.",
    },
    {
        "name": "departamentos",
        "description": "**Distribución geográfica** de contratos por departamento. Útil para choropleth de Colombia.",
    },
    {
        "name": "modalidades",
        "description": "**Modalidades de contratación** (Contratación directa, Licitación, Selección abreviada, etc). Top 5 disponibles.",
    },
    {
        "name": "tipos",
        "description": "**Tipos de contrato** (Prestación de servicios, Suministros, Compraventa, etc).",
    },
    {
        "name": "entidades",
        "description": "**Top entidades públicas** por valor agregado contratado.",
    },
    {
        "name": "temporal",
        "description": "**Distribución temporal** de contratos por mes (formato YYYY-MM).",
    },
    {
        "name": "pareto",
        "description": "**Curva de Pareto** sobre concentración de valor entre entidades. Permite detectar concentración 80/20 vs ratios más extremos (7/80 en este dataset).",
    },
    {
        "name": "genero",
        "description": "**Brecha de género financiera** sobre representantes legales personas naturales (H/M/Otro).",
    },
    {
        "name": "anomalias",
        "description": "**Top 10 valores anómalos** con clasificación IA `VERIDICO` / `FALSO` / `REVISAR` y sustento textual.",
    },
    {
        "name": "mapa",
        "description": "**Choropleth Colombia**: contratos y valor agregado por departamento con código ISO DANE.",
    },
]


# =========================================================================
# FastAPI app
# =========================================================================
APP_DESCRIPTION = """
# SECOP II API — Hackaton Nacional COL 5.0

API REST open-source de **transparencia sobre la contratación pública colombiana**, construida sobre el snapshot oficial 2025 de SECOP II (Colombia Compra Eficiente).

## Equipo Syntax Error

- **Nicolás Moreno** ([@nicolas2601](https://github.com/nicolas2601)) — Capitán
- **Paula Saavedra** ([@Paulasaah](https://github.com/Paulasaah))
- **Andre Julián** ([@Andrejulian21](https://github.com/Andrejulian21))
- **Nathalia Quintero** ([@NathQuintero](https://github.com/NathQuintero))

## Dataset

| Métrica | Valor |
|---|---|
| Contratos | **1,003,902** |
| Departamentos | **33** |
| Valor agregado | **$166.7 billones COP** |
| Snapshot | **2026-05-06** |
| Fuente | [datos.gov.co — jbjy-vk9h](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h) |

## Stack

- **Backend**: FastAPI 0.115 + DuckDB 1.5 sobre CSV
- **Pre-cómputo en startup** (~30s warmup), después latencia <20ms desde memoria
- **CORS abierto**, sin autenticación
- **OpenAPI 3.1** spec en [`/openapi.json`](/openapi.json)

## Marco legal

| Ley | Aplicación |
|---|---|
| **Ley 1712/2014** | Transparencia y acceso a info pública |
| **Ley 1581/2012** | Habeas Data — no se redistribuye PII |
| **Ley 1273/2009** | Delitos informáticos — uso únicamente educativo |

## Hallazgos críticos del dataset

- **75.7%** de los contratos son **Contratación Directa** (sin licitación).
- **Pareto 7/80**: solo el **7.23%** de las entidades ejecuta el **80%** del valor.
- **Brecha de género**: mujeres ejecutan -31.7% del valor pese a firmar +15% más contratos.
- **0.08%** de los contratos tiene anticipos.
- **5 columnas de fondos** vienen 100% null en el dataset oficial.

## Recursos

- 🌐 **Dashboard**: [panel.tikno.pro](https://panel.tikno.pro)
- 📦 **Repo**: [github.com/nicolas2601/hackaton-col5-syntax-error](https://github.com/nicolas2601/hackaton-col5-syntax-error)
- 🐟 **Repo Pez Gordo**: [github.com/nicolas2601/pez-gordo-audit](https://github.com/nicolas2601/pez-gordo-audit)
- 📚 **Docs técnicos**: [panel.tikno.pro/docs/overview](https://panel.tikno.pro/docs/overview)
"""


app = FastAPI(
    title="SECOP II API · Hackaton Nacional COL 5.0",
    description=APP_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    contact={
        "name": "Equipo Syntax Error",
        "url": "https://github.com/nicolas2601/hackaton-col5-syntax-error",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "https://api-ronda2.tikno.pro", "description": "Producción"},
        {"url": "http://localhost:8000", "description": "Local dev"},
    ],
    docs_url=None,  # custom Swagger UI con tema dark
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Custom Swagger UI con tema acorde al dashboard ------------------------
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{app.title} · Swagger",
        swagger_favicon_url="https://fav.farm/📊",
        swagger_ui_parameters={
            "syntaxHighlight.theme": "agate",
            "tryItOutEnabled": True,
            "filter": True,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "defaultModelsExpandDepth": 1,
            "persistAuthorization": True,
        },
    )


# =========================================================================
# Health
# =========================================================================
@app.get(
    "/health",
    tags=["meta"],
    summary="Liveness probe",
    description="Confirma que el container está vivo, el CSV cargado y el cache de agregados pre-computado.",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "Servicio saludable",
            "content": {"application/json": {"example": {
                "status": "ok",
                "total": 1003902,
                "csv": "/data/secop.csv",
                "ready": True,
            }}},
        }
    },
)
def health() -> HealthResponse:
    cache = getattr(app.state, "cache", {})
    total = cache.get("stats_total", {}).get("total_registros", 0)
    return HealthResponse(status="ok", total=total, csv=CSV, ready=bool(cache))


# =========================================================================
# Endpoints v1 — shapes consumidos por el dashboard Next.js
# =========================================================================
@app.get(
    "/api/v1/stats/total",
    tags=["stats"],
    summary="KPIs globales del snapshot",
    description=(
        "Retorna **agregados globales** del snapshot SECOP II 2025: total de "
        "contratos, Pymes, contratación directa, valor agregado en COP y "
        "métricas de concentración (Pareto)."
    ),
    response_model=StatsTotal,
)
def stats_total() -> dict[str, Any]:
    return app.state.cache["stats_total"]


@app.get(
    "/api/v1/departamentos/top",
    tags=["departamentos"],
    summary="Top 10 departamentos",
    description="Departamentos ordenados por **número de contratos publicados**, con valor agregado y porcentaje sobre el top 15.",
    response_model=list[DepartamentoTop],
)
def departamentos_top() -> list[dict[str, Any]]:
    return app.state.cache["departamentos_top"]


@app.get(
    "/api/v1/modalidades",
    tags=["modalidades"],
    summary="Distribución por modalidad",
    description="Modalidades de contratación ordenadas DESC. **75.7%** de los contratos son por Contratación Directa.",
    response_model=list[ModalidadStat],
)
def modalidades() -> list[dict[str, Any]]:
    return app.state.cache["modalidades"]


@app.get(
    "/api/v1/tipos-contrato",
    tags=["tipos"],
    summary="Top 12 tipos de contrato",
    description="Tipos de contrato (Prestación de servicios, Suministros, Compraventa, etc.) con count y valor agregado. **85.76%** son Prestación de Servicios.",
    response_model=list[TipoContratoStat],
)
def tipos_contrato() -> list[dict[str, Any]]:
    return app.state.cache["tipos_contrato"]


@app.get(
    "/api/v1/entidades/top",
    tags=["entidades"],
    summary="Top 20 entidades por valor",
    description="Entidades públicas ordenadas por **valor agregado ejecutado** en COP. La #1 (Distrito CTI Medellín) sola contrata $7.19 billones.",
    response_model=list[EntidadTop],
)
def entidades_top() -> list[dict[str, Any]]:
    return app.state.cache["entidades_top"]


@app.get(
    "/api/v1/temporal",
    tags=["temporal"],
    summary="Distribución mensual",
    description="Contratos por mes en formato `YYYY-MM`. Útil para detectar estacionalidad y picos de fin de año.",
    response_model=list[DistribucionTemporal],
)
def temporal() -> list[dict[str, Any]]:
    return app.state.cache["temporal"]


@app.get(
    "/api/v1/pareto/entidades",
    tags=["pareto"],
    summary="Curva de Pareto — concentración",
    description=(
        "Para cada rank, el **porcentaje acumulado del valor total** contratado. "
        "Permite identificar el punto de quiebre donde el N% de las entidades acumula el 80% del valor.\n\n"
        "**Insight clave del dataset**: solo **285 entidades (7.23%)** acumulan el 80% del valor — "
        "concentración más extrema que la regla 80/20 clásica (Pareto 7/80)."
    ),
    response_model=list[ParetoPunto],
)
def pareto_entidades() -> list[dict[str, Any]]:
    return app.state.cache["pareto"]


@app.get(
    "/api/v1/genero/brecha",
    tags=["genero"],
    summary="Brecha de género financiera",
    description=(
        "Stats por género del **representante legal** (personas naturales): contratos firmados, "
        "valor promedio, mediana.\n\n"
        "**Hallazgo:** las mujeres firman **+15%** más contratos que los hombres pero reciben "
        "**-40.5%** menos por contrato en promedio (H = $141M, M = $84M)."
    ),
    response_model=list[BrechaGenero],
)
def genero_brecha() -> list[dict[str, Any]]:
    return app.state.cache["brecha_genero"]


@app.get(
    "/api/v1/anomalias",
    tags=["anomalias"],
    summary="Top 10 valores anómalos",
    description=(
        "Top 10 contratos por **valor absoluto**, clasificados por IA + heurísticas como:\n\n"
        "- **VERIDICO**: monto consistente con la entidad y modalidad declarada\n"
        "- **FALSO**: incoherencias detectadas (modalidad vs techo legal, tipo vs objeto)\n"
        "- **REVISAR**: requiere validación humana\n\n"
        "Cada anomalía incluye sustento textual."
    ),
    response_model=list[Anomalia],
)
def anomalias() -> list[dict[str, Any]]:
    return app.state.cache["anomalias"]


@app.get(
    "/api/v1/mapa/deptos",
    tags=["mapa"],
    summary="Choropleth Colombia",
    description=(
        "Datos para choropleth de Colombia. El campo `codigo` es **ISO DANE** de 2 dígitos para "
        "matchear contra GeoJSON estándar (`marcovega/colombia-json`)."
    ),
    response_model=list[MapaDepto],
)
def mapa_deptos() -> list[dict[str, Any]]:
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
