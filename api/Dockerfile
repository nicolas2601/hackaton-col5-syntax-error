# syntax=docker/dockerfile:1.7
# Multi-stage build for SECOP API. Multi-arch (amd64 + arm64).

# ─── Stage 1: builder ────────────────────────────────────────
FROM python:3.12-slim AS builder

ARG TARGETPLATFORM
ARG BUILDPLATFORM

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy

# Instalar uv (works for amd64+arm64 via the official install script)
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && cp /root/.local/bin/uv /usr/local/bin/uv

WORKDIR /build

# Copiar SOLO pyproject primero para cachear deps
COPY pyproject.toml ./

# Resolver e instalar deps en /opt/venv (aislado)
RUN uv venv /opt/venv \
    && . /opt/venv/bin/activate \
    && uv pip install --no-cache -r pyproject.toml

# Copiar código y instalar el paquete
COPY app ./app
RUN . /opt/venv/bin/activate && uv pip install --no-cache .

# ─── Stage 2: runtime ────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

# usuario no-root
RUN groupadd -r api && useradd -r -g api -u 1000 api \
    && apt-get update && apt-get install -y --no-install-recommends \
        curl libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar venv desde builder
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=api:api app ./app

USER api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--log-config", "app/utils/logging_config.json"]
