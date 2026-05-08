"""Schemas para /api/v1/pyme."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PymeProporcionResponse(BaseModel):
    """Proporción de contratos PYME."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "pct": 13.20,
        "count": 132479,
        "total": 1003902,
    }})

    pct: float = Field(description="Porcentaje (0-100) con 2 decimales")
    count: int = Field(description="Contratos con Es Pyme = Si")
    total: int = Field(description="Total de contratos en el snapshot")
