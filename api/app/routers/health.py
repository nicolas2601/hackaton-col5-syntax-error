"""Health check router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.database import Database, get_db
from app.models.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness + DB",
    description="Verifica que el proceso está vivo y que el pool Postgres responde.",
)
async def health(
    database: Database = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    db_ok = await database.ping()
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        version=settings.app_version,
        db=db_ok,
        snapshot=settings.data_snapshot_date,
    )
