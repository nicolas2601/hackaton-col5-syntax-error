"""Tipos de contrato router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.database import Database, get_db
from app.models.tipos import TiposTopResponse
from app.services.tipos_service import TiposService

router = APIRouter(prefix="/api/v1/tipos", tags=["tipos"])


def get_service(db: Database = Depends(get_db)) -> TiposService:
    return TiposService(db)


@router.get(
    "/top",
    response_model=TiposTopResponse,
    summary="Top 5 tipos de contrato + porcentaje",
)
async def top(
    limit: int = Query(5, ge=1, le=20),
    svc: TiposService = Depends(get_service),
) -> dict:
    return await svc.top(limit=limit)
