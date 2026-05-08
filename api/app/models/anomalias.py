"""Schemas para /api/v1/anomalias."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnomaliaItem(BaseModel):
    id_contrato: str
    entidad: str | None
    proveedor: str | None
    objeto: str | None
    valor_contrato: float
    valor_pagado: float | None
    departamento: str | None
    z_score: float = Field(description="Z-score del valor vs media del dataset")


class AnomaliasResponse(BaseModel):
    items: list[AnomaliaItem]
    count: int
    media_dataset: float
    desv_std_dataset: float


class ValidacionAnomalia(BaseModel):
    id_contrato: str
    veredicto: str = Field(description="anomalia | normal | sospechoso")
    razones: list[str]
    valor_contrato: float
    valor_pagado: float | None
    z_score: float
    media_categoria: float
    desv_std_categoria: float
    contratos_referencia: int
