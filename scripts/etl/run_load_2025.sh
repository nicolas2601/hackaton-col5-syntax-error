#!/usr/bin/env bash
# run_load_2025.sh — Wrapper para correr load_2025.py dentro del container python:3.12-slim
# conectado al network `coolify` para alcanzar el Postgres por su UUID interno.
#
# Uso (en el SERVER tikno):
#   sudo ./scripts/etl/run_load_2025.sh
#   sudo ./scripts/etl/run_load_2025.sh --force      # recargar de cero
#
# Pre-requisitos:
#   - CSV en /tmp/ronda2/SECOP_II_-_Contratos_Electrónicos_20260506.csv
#   - $POSTGRES_PASSWORD seteado o /root/.config/coolify/secop-creds existente
#   - Network docker `coolify` activo (creado por Coolify v4)

set -euo pipefail

# ─── Resolución de paths ───────────────────────────────────────
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
CSV_HOST="${CSV_HOST:-/tmp/ronda2/SECOP_II_-_Contratos_Electrónicos_20260506.csv}"

# ─── Credenciales ──────────────────────────────────────────────
if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
    if [[ -f /root/.config/coolify/secop-creds ]]; then
        # shellcheck disable=SC1091
        source /root/.config/coolify/secop-creds
    elif [[ -f "$HOME/.config/coolify/secop-creds" ]]; then
        # shellcheck disable=SC1091
        source "$HOME/.config/coolify/secop-creds"
    else
        echo "ERROR: POSTGRES_PASSWORD no seteado y no existe ~/.config/coolify/secop-creds" >&2
        exit 2
    fi
fi

PG_UUID="${PG_UUID:-roook084kg4owsgkcc8k08s8}"
DSN="postgres://postgres:${POSTGRES_PASSWORD}@${PG_UUID}:5432/secop"

# ─── Sanity checks ─────────────────────────────────────────────
if [[ ! -f "$CSV_HOST" ]]; then
    echo "ERROR: CSV no encontrado: $CSV_HOST" >&2
    exit 2
fi

if ! docker network ls --format '{{.Name}}' | grep -qx coolify; then
    echo "ERROR: docker network 'coolify' no existe. ¿Coolify levantado?" >&2
    exit 2
fi

echo "==> CSV:   $CSV_HOST ($(du -h "$CSV_HOST" | cut -f1))"
echo "==> DB:    secop @ $PG_UUID (network coolify)"
echo "==> Args:  $*"

# ─── Run dentro del container ──────────────────────────────────
docker run --rm \
    --network coolify \
    --name etl-load-2025 \
    -v "$REPO_ROOT/scripts/etl:/etl:ro" \
    -v "$CSV_HOST:/data/contratos_2025.csv:ro" \
    -e DATABASE_URL="$DSN" \
    -e CSV_PATH="/data/contratos_2025.csv" \
    -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
    -e BATCH_SIZE="${BATCH_SIZE:-10000}" \
    python:3.12-slim \
    bash -c "
        set -e
        pip install --quiet --no-cache-dir 'psycopg[binary]>=3.2'
        exec python /etl/load_2025.py $*
    "

echo "==> ETL completo."
