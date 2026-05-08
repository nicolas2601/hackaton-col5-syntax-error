"""Schemas para /api/v1/entidades."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EntidadBucket(BaseModel):
    nit: str
    nombre: str
    contratos: int
    dinero_ejecutado: float = Field(description="Suma Valor Pagado (COP)")
    valor_total: float = Field(description="Suma Valor del Contrato (COP)")


class EntidadesTopResponse(BaseModel):
    items: list[EntidadBucket]
    count: int


class EntidadDetalle(BaseModel):
    nit: str
    nombre: str
    sector: str | None
    rama: str | None
    orden: str | None
    contratos: int
    dinero_ejecutado: float
    valor_total: float
    departamentos: list[str]
