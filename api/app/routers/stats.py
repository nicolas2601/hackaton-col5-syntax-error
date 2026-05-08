"""Stats router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.database import Database, get_db
from app.models.stats import AniosResponse, ColumnasResponse, TotalResponse
from app.services.stats_service import StatsService

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


def get_service(db: Database = Depends(get_db)) -> StatsService:
    return StatsService(db)


@router.get(
    "/total",
    response_model=TotalResponse,
    summary="Total de contratos en el snapshot",
)
async def total(svc: StatsService = Depends(get_service)) -> dict:
    return await svc.total()


@router.get(
    "/columnas",
    response_model=ColumnasResponse,
    summary="Lista de las 84 columnas",
)
async def columnas(svc: StatsService = Depends(get_service)) -> dict:
    return svc.columnas()


@router.get(
    "/anios",
    response_model=AniosResponse,
    summary="Distribución de contratos por año de firma",
)
async def anios(svc: StatsService = Depends(get_service)) -> dict:
    return await svc.anios()
