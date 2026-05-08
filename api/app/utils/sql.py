"""Helpers SQL — sanitización de identificadores y limpieza monetaria.

NOTA importante: la columna `Valor del Contrato` viene como texto con `$` y comas
en el CSV (`"$40,825,000"`). En la tabla destino la suposición es que existe
una columna numérica saneada (`valor_contrato_num`). Los queries usan esa
versión numérica para agregaciones.
"""

from __future__ import annotations

import re

# Whitelist de columnas para protección contra SQL-injection en filtros dinámicos
_SAFE_IDENT_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def safe_ident(name: str) -> str:
    """Validar identificador Postgres seguro o lanzar ValueError."""
    if not _SAFE_IDENT_RE.match(name):
        raise ValueError(f"Identificador inseguro: {name!r}")
    return name
