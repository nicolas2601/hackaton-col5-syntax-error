"""Ambiental + anticipos router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.database import Database, get_db
from app.models.ambiental import AmbientalTotalResponse, AnticiposResponse
from app.services.ambiental_service import AmbientalService

router = APIRouter(prefix="/api/v1/ambiental", tags=["ambiental"])


def get_service(db: Database = Depends(get_db)) -> AmbientalService:
    return AmbientalService(db)


@router.get(
    "/total",
    response_model=AmbientalTotalResponse,
    summary="Contratos con Obligación Ambiental = Si",
)
async def total(svc: AmbientalService = Depends(get_service)) -> dict:
    return await svc.total()


@router.get(
    "/anticipos",
    response_model=AnticiposResponse,
    summary="Contratos con Habilita Pago Adelantado = Si",
)
async def anticipos(svc: AmbientalService = Depends(get_service)) -> dict:
    return await svc.anticipos()
