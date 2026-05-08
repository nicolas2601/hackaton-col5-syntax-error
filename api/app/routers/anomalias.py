"""Anomalías router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.database import Database, get_db
from app.models.anomalias import AnomaliasResponse, ValidacionAnomalia
from app.services.anomalias_service import AnomaliasService

router = APIRouter(prefix="/api/v1/anomalias", tags=["anomalias"])


def get_service(db: Database = Depends(get_db)) -> AnomaliasService:
    return AnomaliasService(db)


@router.get(
    "/financieras",
    response_model=AnomaliasResponse,
    summary="Top 10 valores anómalos (z-score sobre Valor del Contrato)",
)
async def financieras(
    limit: int = Query(10, ge=1, le=100),
    svc: AnomaliasService = Depends(get_service),
) -> dict:
    return await svc.top_anomalias(limit=limit)


@router.get(
    "/financieras/validar/{id_contrato}",
    response_model=ValidacionAnomalia,
    summary="Análisis verídico/falso de un contrato individual",
    description="Calcula z-score contra contratos del mismo tipo y emite veredicto: anomalia | sospechoso | normal.",
)
async def validar(
    id_contrato: str,
    svc: AnomaliasService = Depends(get_service),
) -> dict:
    return await svc.validar(id_contrato=id_contrato)
