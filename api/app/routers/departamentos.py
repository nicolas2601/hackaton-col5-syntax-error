"""Departamentos router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.database import Database, get_db
from app.models.departamentos import DepartamentoDetalle, DepartamentosTopResponse
from app.services.departamentos_service import DepartamentosService

router = APIRouter(prefix="/api/v1/departamentos", tags=["departamentos"])


def get_service(db: Database = Depends(get_db)) -> DepartamentosService:
    return DepartamentosService(db)


@router.get(
    "/top",
    response_model=DepartamentosTopResponse,
    summary="Top 10 departamentos por cantidad de contratos",
)
async def top(
    limit: int = Query(10, ge=1, le=33, description="Cantidad de deptos (default 10, max 33)"),
    svc: DepartamentosService = Depends(get_service),
) -> dict:
    return await svc.top(limit=limit)


@router.get(
    "/{nombre}",
    response_model=DepartamentoDetalle,
    summary="Detalle de un departamento (con muestras de contratos top)",
)
async def detalle(
    nombre: str,
    muestras: int = Query(10, ge=1, le=100),
    svc: DepartamentosService = Depends(get_service),
) -> dict:
    return await svc.detalle(nombre=nombre, muestras=muestras)
