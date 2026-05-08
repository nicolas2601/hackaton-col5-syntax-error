"""Pareto router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.database import Database, get_db
from app.models.pareto import ParetoEntidadesResponse
from app.services.pareto_service import ParetoService

router = APIRouter(prefix="/api/v1/pareto", tags=["pareto"])


def get_service(db: Database = Depends(get_db)) -> ParetoService:
    return ParetoService(db)


@router.get(
    "/entidades",
    response_model=ParetoEntidadesResponse,
    summary="Curva de Pareto: top X% de entidades concentra Y% del dinero",
    description="Divide entidades en 5 quintiles ordenados por dinero ejecutado descendente.",
)
async def entidades(svc: ParetoService = Depends(get_service)) -> dict:
    return await svc.entidades()
