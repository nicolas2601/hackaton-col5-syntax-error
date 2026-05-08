"""Schemas para /api/v1/pareto."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ParetoQuintil(BaseModel):
    quintil: int = Field(description="1 = top 20% (mayor concentración) ... 5 = bottom 20%", ge=1, le=5)
    pct_entidades: float = Field(description="Porcentaje de entidades en este quintil")
    pct_dinero: float = Field(description="Porcentaje del dinero total que concentran")
    entidades: int
    dinero_total: float


class ParetoEntidadesResponse(BaseModel):
    """Curva de Pareto: top X% de entidades concentra Y% del dinero."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "quintiles": [
            {"quintil": 1, "pct_entidades": 20.0, "pct_dinero": 78.4, "entidades": 1234, "dinero_total": 1.5e13},
        ],
        "total_entidades": 6170,
        "dinero_total": 2.0e13,
    }})

    quintiles: list[ParetoQuintil]
    total_entidades: int
    dinero_total: float
