"""Entidades router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.database import Database, get_db
from app.models.entidades import EntidadDetalle, EntidadesTopResponse
from app.services.entidades_service import EntidadesService

router = APIRouter(prefix="/api/v1/entidades", tags=["entidades"])


def get_service(db: Database = Depends(get_db)) -> EntidadesService:
    return EntidadesService(db)


@router.get(
    "/top",
    response_model=EntidadesTopResponse,
    summary="Top 10 entidades por dinero ejecutado",
)
async def top(
    limit: int = Query(10, ge=1, le=100),
    svc: EntidadesService = Depends(get_service),
) -> dict:
    return await svc.top(limit=limit)


@router.get(
    "/{nit}",
    response_model=EntidadDetalle,
    summary="Detalle de una entidad por NIT",
)
async def detalle(
    nit: str,
    svc: EntidadesService = Depends(get_service),
) -> dict:
    return await svc.detalle(nit=nit)
