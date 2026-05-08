"""FastAPI app entrypoint — middlewares, lifespan, routers."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.gzip import GZipMiddleware

from app import __version__
from app.config import get_settings
from app.database import db
from app.routers import (
    ambiental,
    anomalias,
    departamentos,
    entidades,
    genero,
    health,
    modalidades,
    pareto,
    pyme,
    stats,
    tipos,
)
from app.utils.logging import configure_logging

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Boot DB pool al inicio, cerrar al apagar."""
    configure_logging()
    settings = get_settings()
    log.info(
        "app.starting",
        version=__version__,
        env=settings.app_env,
        snapshot=settings.data_snapshot_date,
    )
    await db.connect()
    yield
    log.info("app.stopping")
    await db.disconnect()


def create_app() -> FastAPI:
    settings = get_settings()
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    )

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API FastAPI para análisis del snapshot SECOP II 2025 "
            "(1.003.902 contratos · 84 columnas).\n\n"
            "Hackathon COL 5.0 — Equipo **Syntax Error**.\n\n"
            "**Endpoints**: stats, pyme, departamentos, modalidades, entidades, "
            "tipos, anomalías, pareto, género, ambiental.\n\n"
            "**Cache**: queries pesadas (Pareto, Top X) cacheadas en memoria con "
            f"TTL de {settings.cache_ttl_seconds}s.\n\n"
            f"**Rate limit**: {settings.rate_limit_per_minute} req/min/IP."
        ),
        default_response_class=ORJSONResponse,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        contact={"name": "Syntax Error", "url": "https://api.tikno.pro"},
        license_info={"name": "MIT", "url": "https://opensource.org/license/mit"},
        openapi_tags=[
            {"name": "health", "description": "Liveness + DB"},
            {"name": "stats", "description": "Totales y distribuciones globales"},
            {"name": "pyme", "description": "Métricas PYME"},
            {"name": "departamentos", "description": "Por departamento"},
            {"name": "modalidades", "description": "Modalidades de contratación"},
            {"name": "entidades", "description": "Por entidad contratante"},
            {"name": "tipos", "description": "Tipos de contrato"},
            {"name": "anomalias", "description": "Detección de valores anómalos"},
            {"name": "pareto", "description": "Concentración 80/20 del gasto"},
            {"name": "genero", "description": "Brecha de género por rep. legal"},
            {"name": "ambiental", "description": "Obligaciones ambientales y anticipos"},
        ],
        lifespan=lifespan,
    )

    # ── Middlewares ────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Rate limit ─────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Logging middleware ─────────────────────────────────
    @app.middleware("http")
    async def log_requests(request: Request, call_next):  # type: ignore[no-untyped-def]
        log.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )
        response = await call_next(request)
        log.info(
            "http.response",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
        )
        return response

    # ── Routers ────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(stats.router)
    app.include_router(pyme.router)
    app.include_router(departamentos.router)
    app.include_router(modalidades.router)
    app.include_router(entidades.router)
    app.include_router(tipos.router)
    app.include_router(anomalias.router)
    app.include_router(pareto.router)
    app.include_router(genero.router)
    app.include_router(ambiental.router)

    # ── Root ───────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "snapshot": settings.data_snapshot_date,
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health",
        }

    return app


app = create_app()
