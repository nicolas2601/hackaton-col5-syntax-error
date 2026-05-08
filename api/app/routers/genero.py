"""Género router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.database import Database, get_db
from app.models.genero import BrechaGeneroResponse
from app.services.genero_service import GeneroService

router = APIRouter(prefix="/api/v1/genero", tags=["genero"])


def get_service(db: Database = Depends(get_db)) -> GeneroService:
    return GeneroService(db)


@router.get(
    "/brecha",
    response_model=BrechaGeneroResponse,
    summary="Brecha de género por representante legal",
    description="Stats por género: count, total, promedio, mediana del valor del contrato.",
)
async def brecha(svc: GeneroService = Depends(get_service)) -> dict:
    return await svc.brecha()
