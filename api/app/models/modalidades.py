"""Schemas para /api/v1/modalidades."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModalidadBucket(BaseModel):
    modalidad: str
    count: int
    pct: float = Field(description="Porcentaje del total (0-100)")


class ModalidadesTopResponse(BaseModel):
    items: list[ModalidadBucket]
    count: int


class ContratoSummary(BaseModel):
    id_contrato: str
    entidad: str | None
    objeto: str | None
    valor: float | None
    departamento: str | None
    fecha_firma: str | None


class ModalidadContratosResponse(BaseModel):
    modalidad: str
    items: list[ContratoSummary]
    count: int
    limit: int
    offset: int
