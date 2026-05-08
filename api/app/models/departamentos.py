"""Schemas para /api/v1/departamentos."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DepartamentoBucket(BaseModel):
    """Stats agregadas de un depto."""

    nombre: str
    contratos: int = Field(description="Cantidad de contratos en el depto")
    valor_total: float = Field(description="Suma del valor de los contratos (COP)")


class DepartamentosTopResponse(BaseModel):
    items: list[DepartamentoBucket]
    count: int


class DepartamentoDetalle(BaseModel):
    """Detalle agregado + muestra de contratos."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "nombre": "Antioquia",
        "contratos": 89432,
        "valor_total": 24135678901234.5,
        "muestras": [
            {
                "id_contrato": "CO1.PCCNTR.5756877",
                "entidad": "Gobernación de Antioquia",
                "objeto": "Prestación de servicios profesionales...",
                "valor": 40825000,
            },
        ],
    }})

    nombre: str
    contratos: int
    valor_total: float
    muestras: list[dict]
