"""Schemas para /api/v1/ambiental."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AmbientalTotalResponse(BaseModel):
    count: int = Field(description="Contratos con Obligación Ambiental = Si")
    total: int = Field(description="Total del snapshot")
    pct: float = Field(description="Porcentaje (0-100)")
    valor_total: float = Field(description="Suma del valor en COP")


class AnticiposResponse(BaseModel):
    count: int = Field(description="Contratos con Habilita Pago Adelantado = Si")
    total: int
    pct: float
    valor_total_anticipos: float
