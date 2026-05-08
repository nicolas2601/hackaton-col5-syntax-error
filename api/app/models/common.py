"""Schemas compartidos."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """Error body uniforme."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "error": "not_found",
        "detail": "Departamento 'Atlantida' no existe en el dataset",
        "status_code": 404,
    }})

    error: str = Field(description="Código corto de error")
    detail: str = Field(description="Descripción human-readable")
    status_code: int = Field(description="HTTP status")


class HealthResponse(BaseModel):
    """Liveness + DB check."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "status": "ok",
        "version": "0.1.0",
        "db": True,
        "snapshot": "2026-05-06",
    }})

    status: str = Field(description="ok | degraded")
    version: str
    db: bool = Field(description="True si Postgres responde")
    snapshot: str = Field(description="Fecha del snapshot SECOP II")
