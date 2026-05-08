"""PYME router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.database import Database, get_db
from app.models.pyme import PymeProporcionResponse
from app.services.pyme_service import PymeService

router = APIRouter(prefix="/api/v1/pyme", tags=["pyme"])


def get_service(db: Database = Depends(get_db)) -> PymeService:
    return PymeService(db)


@router.get(
    "/proporcion",
    response_model=PymeProporcionResponse,
    summary="Proporción de contratos PYME",
    description="Cuenta contratos donde 'Es Pyme' = 'Si' sobre el total.",
)
async def proporcion(svc: PymeService = Depends(get_service)) -> dict:
    return await svc.proporcion()
