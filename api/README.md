# SECOP API — Hackathon COL 5.0 (Syntax Error)

Backend FastAPI para análisis del snapshot SECOP II 2025 (1.003.902 contratos · 84 columnas).

## Stack

- Python 3.12 · FastAPI 0.115 · Pydantic v2
- asyncpg pool · structlog · slowapi · orjson
- uv como package manager · Docker multi-stage multi-arch

## Quickstart local

```bash
# 1. Clonar y posicionarse
cd api/

# 2. Copiar env
cp .env.example .env
# editar DATABASE_URL con la pass real (cat ~/.config/coolify/secop-creds)

# 3. Instalar deps con uv
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# 4. Correr en local
uvicorn app.main:app --reload --port 8000
```

Abrir:
- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc
- OpenAPI → http://localhost:8000/openapi.json

## Endpoints

| Router | Path | Descripción |
|---|---|---|
| stats | `GET /api/v1/stats/total` | Total de contratos + snapshot |
| stats | `GET /api/v1/stats/columnas` | Lista de columnas |
| stats | `GET /api/v1/stats/anios` | Distribución por año |
| pyme | `GET /api/v1/pyme/proporcion` | % de contratos PYME |
| departamentos | `GET /api/v1/departamentos/top` | Top 10 deptos |
| departamentos | `GET /api/v1/departamentos/{nombre}` | Detalle depto |
| modalidades | `GET /api/v1/modalidades/top` | Top 5 modalidades |
| modalidades | `GET /api/v1/modalidades/{modalidad}/contratos` | Contratos por modalidad |
| entidades | `GET /api/v1/entidades/top` | Top 10 entidades |
| entidades | `GET /api/v1/entidades/{nit}` | Detalle entidad |
| tipos | `GET /api/v1/tipos/top` | Top 5 tipos |
| anomalias | `GET /api/v1/anomalias/financieras` | Top 10 valores anómalos |
| anomalias | `GET /api/v1/anomalias/financieras/validar/{id}` | Validar contrato |
| pareto | `GET /api/v1/pareto/entidades` | Curva Pareto (5 quintiles) |
| genero | `GET /api/v1/genero/brecha` | Brecha de género |
| ambiental | `GET /api/v1/ambiental/total` | Contratos con obligación ambiental |
| ambiental | `GET /api/v1/ambiental/anticipos` | Contratos con pago adelantado |
| health | `GET /health` | Liveness + DB |

## Tests

```bash
pytest -v
pytest --cov=app --cov-report=term-missing
```

## Deploy Coolify

```bash
# 1. Push al repo
git push origin main

# 2. En Coolify:
# - New Resource → Application → Public Repo
# - Build Pack: Dockerfile
# - Branch: main
# - Base Directory: /api
# - Network: conectar a la misma network del Postgres `secop`
# - Env vars: copiar de .env.example y poner DATABASE_URL real
# - Domains: api.tikno.pro/v2 (o subdomain)
# - Health Check: GET /health
```

## Convenciones

- Controller-Service-Repository
- DTO con Pydantic v2 (`model_config`)
- Errores con `HTTPException` + body uniforme
- Logs JSON estructurados via structlog
- Cache LRU para queries pesadas (Pareto, Top X)
