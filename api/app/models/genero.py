"""Schemas para /api/v1/genero."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GeneroStats(BaseModel):
    genero: str = Field(description="M | F | Otro | Sin dato")
    count: int
    total_valor: float
    promedio: float
    mediana: float
    pct_count: float = Field(description="Porcentaje del count total (0-100)")
    pct_valor: float = Field(description="Porcentaje del valor total (0-100)")


class BrechaGeneroResponse(BaseModel):
    items: list[GeneroStats]
    brecha_promedio_pct: float = Field(
        description="Diferencia % entre el promedio del género dominante vs los demás"
    )
    total_contratos: int
    total_valor: float
