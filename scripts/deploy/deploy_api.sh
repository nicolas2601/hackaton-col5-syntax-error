#!/usr/bin/env bash
# deploy_api.sh — Build & deploy FastAPI a Coolify (api-ronda2.tikno.pro).
#
# Estrategia: build local de la imagen Docker → push al registry interno de Coolify
# → crear/actualizar app vía Coolify API → conectar al network `coolify` → trigger deploy.
#
# Uso (en el server tikno o local con kubectl-style port-forward):
#   ./scripts/deploy/deploy_api.sh                  # primera vez (crea app)
#   ./scripts/deploy/deploy_api.sh --redeploy       # solo redeploy (no recrea)
#
# Variables esperadas:
#   COOLIFY_TOKEN          → ~/.config/coolify/token
#   COOLIFY_URL            → https://coolify.tikno.pro (default)
#   PROJECT_UUID           → tsc8k8c4088cgw0ws4w8osgc
#   PG_UUID                → roook084kg4owsgkcc8k08s8
#   POSTGRES_PASSWORD      → ~/.config/coolify/secop-creds

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# ─── Config ────────────────────────────────────────────────────
COOLIFY_URL="${COOLIFY_URL:-https://coolify.tikno.pro}"
PROJECT_UUID="${PROJECT_UUID:-tsc8k8c4088cgw0ws4w8osgc}"
PG_UUID="${PG_UUID:-roook084kg4owsgkcc8k08s8}"
APP_NAME="api-ronda2"
APP_DOMAIN="api-ronda2.tikno.pro"
APP_PORT=8000
IMAGE_NAME="secop-api"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}"
CONFIG_JSON="$REPO_ROOT/deploy/coolify/api-ronda2.json"

# ─── Token ─────────────────────────────────────────────────────
if [[ -z "${COOLIFY_TOKEN:-}" ]]; then
    if [[ -f "$HOME/.config/coolify/token" ]]; then
        COOLIFY_TOKEN="$(<"$HOME/.config/coolify/token")"
    else
        echo "ERROR: COOLIFY_TOKEN no seteado y no existe ~/.config/coolify/token" >&2
        exit 2
    fi
fi

# ─── Postgres pass ─────────────────────────────────────────────
if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
    if [[ -f "$HOME/.config/coolify/secop-creds" ]]; then
        # shellcheck disable=SC1091
        source "$HOME/.config/coolify/secop-creds"
    else
        echo "ERROR: POSTGRES_PASSWORD no seteado." >&2
        exit 2
    fi
fi

api() {
    local method="$1"; shift
    local path="$1"; shift
    curl -fsS -X "$method" \
        -H "Authorization: Bearer $COOLIFY_TOKEN" \
        -H "Content-Type: application/json" \
        "$COOLIFY_URL/api/v1$path" "$@"
}

# ─── Build ─────────────────────────────────────────────────────
build_image() {
    echo "==> [1/4] Build Docker image: $IMAGE_NAME:$IMAGE_TAG"
    docker build \
        -t "$IMAGE_NAME:$IMAGE_TAG" \
        -t "$IMAGE_NAME:latest" \
        --build-arg BUILDPLATFORM=linux/amd64 \
        --build-arg TARGETPLATFORM=linux/amd64 \
        "$REPO_ROOT/api"
    echo "    ✓ Image built: $IMAGE_NAME:$IMAGE_TAG"
}

# ─── Coolify app create/update ─────────────────────────────────
create_or_update_app() {
    echo "==> [2/4] Verificando app '$APP_NAME' en Coolify..."
    local existing
    existing=$(api GET "/applications" \
        | jq -r --arg name "$APP_NAME" \
            '.[] | select(.name == $name) | .uuid' || true)

    if [[ -z "$existing" ]]; then
        echo "    App no existe, creando..."
        local payload
        payload=$(jq \
            --arg pg_pass "$POSTGRES_PASSWORD" \
            --arg image "$IMAGE_NAME:$IMAGE_TAG" \
            --arg project "$PROJECT_UUID" \
            --arg pg_uuid "$PG_UUID" \
            '.docker_registry_image_name = $image
             | .project_uuid = $project
             | .environment_variables += [
                 {"key":"DATABASE_URL","value":("postgres://postgres:" + $pg_pass + "@" + $pg_uuid + ":5432/secop"),"is_preview":false}
               ]' \
            < "$CONFIG_JSON")

        local resp
        resp=$(api POST "/applications/dockerimage" -d "$payload")
        APP_UUID=$(echo "$resp" | jq -r '.uuid')
        echo "    ✓ App creada: $APP_UUID"
    else
        APP_UUID="$existing"
        echo "    App existe: $APP_UUID — actualizando imagen..."
        api PATCH "/applications/$APP_UUID" -d "$(jq \
            --arg image "$IMAGE_NAME:$IMAGE_TAG" \
            '{docker_registry_image_name: $image}' < /dev/null)" > /dev/null
        echo "    ✓ Imagen actualizada"
    fi
}

# ─── Trigger deploy ────────────────────────────────────────────
trigger_deploy() {
    echo "==> [3/4] Trigger deploy..."
    api POST "/applications/$APP_UUID/start" > /dev/null
    echo "    ✓ Deploy iniciado. Logs: $COOLIFY_URL/applications/$APP_UUID/logs"
}

# ─── Healthcheck ───────────────────────────────────────────────
wait_healthy() {
    echo "==> [4/4] Esperando healthcheck en https://$APP_DOMAIN/health ..."
    local max_attempts=60 attempt=0
    while (( attempt < max_attempts )); do
        if curl -fsS --max-time 5 "https://$APP_DOMAIN/health" > /dev/null 2>&1; then
            echo "    ✓ API healthy: https://$APP_DOMAIN/health"
            return 0
        fi
        sleep 5
        ((attempt++))
        echo "    ... intento $attempt/$max_attempts"
    done
    echo "    ⚠ API no respondió en 5 min. Revisar logs Coolify." >&2
    return 1
}

main() {
    case "${1:-deploy}" in
        --redeploy|redeploy)
            create_or_update_app
            trigger_deploy
            wait_healthy
            ;;
        deploy|*)
            build_image
            create_or_update_app
            trigger_deploy
            wait_healthy
            ;;
    esac
    echo "==> API deploy completo: https://$APP_DOMAIN"
}

main "$@"
