"""Schemas para /api/v1/stats."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TotalResponse(BaseModel):
    """Total agregado del snapshot."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "total": 1003902,
        "snapshot": "2026-05-06",
    }})

    total: int = Field(description="Total de filas/contratos en el snapshot")
    snapshot: str = Field(description="Fecha del snapshot (YYYY-MM-DD)")


class ColumnasResponse(BaseModel):
    """Lista de columnas del dataset."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "count": 84,
        "columnas": ["Nombre Entidad", "Nit Entidad", "Departamento"],
    }})

    count: int
    columnas: list[str]


class AnioBucket(BaseModel):
    """Bucket por año."""

    anio: int = Field(description="Año de firma")
    contratos: int = Field(description="Cantidad de contratos firmados ese año")


class AniosResponse(BaseModel):
    """Distribución por año de firma."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "items": [{"anio": 2024, "contratos": 412350}, {"anio": 2025, "contratos": 591552}],
        "count": 2,
    }})

    items: list[AnioBucket]
    count: int
