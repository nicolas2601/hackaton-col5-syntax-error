#!/usr/bin/env bash
# deploy_dashboard.sh — Build & deploy Next.js 15 standalone a Coolify (panel.tikno.pro).
#
# Uso:
#   ./scripts/deploy/deploy_dashboard.sh
#   ./scripts/deploy/deploy_dashboard.sh --redeploy

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
DASHBOARD_DIR="$REPO_ROOT/dashboard"

# ─── Config ────────────────────────────────────────────────────
COOLIFY_URL="${COOLIFY_URL:-https://coolify.tikno.pro}"
PROJECT_UUID="${PROJECT_UUID:-tsc8k8c4088cgw0ws4w8osgc}"
APP_NAME="panel"
APP_DOMAIN="panel.tikno.pro"
APP_PORT=3000
IMAGE_NAME="secop-panel"
IMAGE_TAG="${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}"
CONFIG_JSON="$REPO_ROOT/deploy/coolify/panel.json"

# ─── Token ─────────────────────────────────────────────────────
if [[ -z "${COOLIFY_TOKEN:-}" ]]; then
    if [[ -f "$HOME/.config/coolify/token" ]]; then
        COOLIFY_TOKEN="$(<"$HOME/.config/coolify/token")"
    else
        echo "ERROR: COOLIFY_TOKEN no seteado." >&2
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

# ─── Generate Dockerfile if missing ────────────────────────────
ensure_dockerfile() {
    if [[ ! -f "$DASHBOARD_DIR/Dockerfile" ]]; then
        echo "==> Generando Dockerfile (Next.js standalone)..."
        cat > "$DASHBOARD_DIR/Dockerfile" <<'DOCKERFILE'
# syntax=docker/dockerfile:1.7
# Multi-stage Next.js 15 standalone (output: "standalone" en next.config.ts).

FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat && corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile --prefer-offline || pnpm install

FROM node:20-alpine AS builder
RUN corepack enable
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL=https://api-ronda2.tikno.pro
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1
RUN pnpm run build

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup -S -g 1001 nodejs && adduser -S -u 1001 -G nodejs nextjs
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public 2>/dev/null || true
USER nextjs
EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget -qO- http://localhost:3000/ > /dev/null || exit 1
CMD ["node", "server.js"]
DOCKERFILE
        echo "    ✓ Dockerfile creado"
    fi
}

build_image() {
    ensure_dockerfile
    echo "==> [1/4] Build Docker image: $IMAGE_NAME:$IMAGE_TAG"
    docker build \
        -t "$IMAGE_NAME:$IMAGE_TAG" \
        -t "$IMAGE_NAME:latest" \
        --build-arg NEXT_PUBLIC_API_URL=https://api-ronda2.tikno.pro \
        "$DASHBOARD_DIR"
    echo "    ✓ Image built"
}

create_or_update_app() {
    echo "==> [2/4] Verificando app '$APP_NAME' en Coolify..."
    local existing
    existing=$(api GET "/applications" \
        | jq -r --arg name "$APP_NAME" \
            '.[] | select(.name == $name) | .uuid' || true)

    if [[ -z "$existing" ]]; then
        echo "    Creando app..."
        local payload
        payload=$(jq \
            --arg image "$IMAGE_NAME:$IMAGE_TAG" \
            --arg project "$PROJECT_UUID" \
            '.docker_registry_image_name = $image | .project_uuid = $project' \
            < "$CONFIG_JSON")
        local resp
        resp=$(api POST "/applications/dockerimage" -d "$payload")
        APP_UUID=$(echo "$resp" | jq -r '.uuid')
        echo "    ✓ App creada: $APP_UUID"
    else
        APP_UUID="$existing"
        api PATCH "/applications/$APP_UUID" -d "$(jq \
            --arg image "$IMAGE_NAME:$IMAGE_TAG" \
            '{docker_registry_image_name: $image}' < /dev/null)" > /dev/null
        echo "    ✓ Imagen actualizada en app $APP_UUID"
    fi
}

trigger_deploy() {
    echo "==> [3/4] Trigger deploy..."
    api POST "/applications/$APP_UUID/start" > /dev/null
    echo "    ✓ Deploy iniciado"
}

wait_healthy() {
    echo "==> [4/4] Esperando https://$APP_DOMAIN ..."
    local max_attempts=60 attempt=0
    while (( attempt < max_attempts )); do
        if curl -fsS --max-time 5 -I "https://$APP_DOMAIN" 2>/dev/null | head -1 | grep -qE "200|301|302"; then
            echo "    ✓ Dashboard up: https://$APP_DOMAIN"
            return 0
        fi
        sleep 5
        ((attempt++))
        echo "    ... intento $attempt/$max_attempts"
    done
    echo "    ⚠ Dashboard no respondió en 5 min." >&2
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
    echo "==> Dashboard deploy completo: https://$APP_DOMAIN"
}

main "$@"
