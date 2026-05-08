"""Schemas para /api/v1/tipos."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TipoBucket(BaseModel):
    tipo: str
    count: int
    pct: float = Field(description="Porcentaje del total")


class TiposTopResponse(BaseModel):
    items: list[TipoBucket]
    total: int
