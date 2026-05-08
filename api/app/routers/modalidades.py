"""Modalidades router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.database import Database, get_db
from app.models.modalidades import ModalidadContratosResponse, ModalidadesTopResponse
from app.services.modalidades_service import ModalidadesService

router = APIRouter(prefix="/api/v1/modalidades", tags=["modalidades"])


def get_service(db: Database = Depends(get_db)) -> ModalidadesService:
    return ModalidadesService(db)


@router.get(
    "/top",
    response_model=ModalidadesTopResponse,
    summary="Top 5 modalidades de contratación",
)
async def top(
    limit: int = Query(5, ge=1, le=20),
    svc: ModalidadesService = Depends(get_service),
) -> dict:
    return await svc.top(limit=limit)


@router.get(
    "/{modalidad}/contratos",
    response_model=ModalidadContratosResponse,
    summary="Listar contratos de una modalidad",
)
async def contratos(
    modalidad: str,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    svc: ModalidadesService = Depends(get_service),
) -> dict:
    return await svc.contratos_por_modalidad(
        modalidad=modalidad, limit=limit, offset=offset
    )
