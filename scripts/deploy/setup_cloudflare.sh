#!/usr/bin/env bash
# setup_cloudflare.sh — Actualiza /etc/cloudflared/config.yml con los nuevos
# subdominios (api-ronda2 + panel) y reload del túnel.
#
# Estrategia: idempotente (no duplica entries existentes), backup automático,
# validación previa con `cloudflared tunnel ingress validate`.
#
# Uso (en el server tikno, como root o con sudo):
#   sudo ./scripts/deploy/setup_cloudflare.sh
#   sudo ./scripts/deploy/setup_cloudflare.sh --dry-run   # solo muestra diff

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

CONFIG_PATH="${CLOUDFLARED_CONFIG:-/etc/cloudflared/config.yml}"
DESIRED_PATH="$REPO_ROOT/deploy/cloudflare/config.yml"
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
fi

# ─── Sanity ────────────────────────────────────────────────────
if [[ ! -f "$DESIRED_PATH" ]]; then
    echo "ERROR: archivo deseado no encontrado: $DESIRED_PATH" >&2
    exit 2
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
    echo "ERROR: $CONFIG_PATH no existe. ¿cloudflared instalado?" >&2
    exit 2
fi

if ! command -v cloudflared >/dev/null 2>&1; then
    echo "ERROR: 'cloudflared' no está en PATH." >&2
    exit 2
fi

# ─── Backup ────────────────────────────────────────────────────
TS=$(date +%Y%m%d-%H%M%S)
BACKUP="$CONFIG_PATH.bak.$TS"

echo "==> [1/4] Backup: $CONFIG_PATH → $BACKUP"
if ! $DRY_RUN; then
    cp -p "$CONFIG_PATH" "$BACKUP"
fi

# ─── Diff ──────────────────────────────────────────────────────
echo "==> [2/4] Diff (deseado vs actual):"
diff -u "$CONFIG_PATH" "$DESIRED_PATH" || true
echo

if $DRY_RUN; then
    echo "==> --dry-run: no se modifica nada. Backup hipotético: $BACKUP"
    exit 0
fi

# ─── Apply ─────────────────────────────────────────────────────
echo "==> [3/4] Validando nuevo config..."
TMPFILE=$(mktemp)
cp "$DESIRED_PATH" "$TMPFILE"

if ! cloudflared tunnel --config "$TMPFILE" ingress validate; then
    echo "ERROR: ingress validate FALLÓ. NO se aplica." >&2
    rm -f "$TMPFILE"
    exit 3
fi

echo "    ✓ Config válido. Aplicando..."
install -m 0644 "$TMPFILE" "$CONFIG_PATH"
rm -f "$TMPFILE"

# ─── Reload ────────────────────────────────────────────────────
echo "==> [4/4] Reload cloudflared..."
if systemctl list-units --type=service --all | grep -q cloudflared; then
    systemctl restart cloudflared
    sleep 2
    if systemctl is-active --quiet cloudflared; then
        echo "    ✓ cloudflared activo (reload OK)"
    else
        echo "    ⚠ cloudflared NO activo. Restaurando backup..." >&2
        cp "$BACKUP" "$CONFIG_PATH"
        systemctl restart cloudflared || true
        exit 4
    fi
else
    echo "    ⚠ cloudflared no es systemd unit. Reload manual requerido." >&2
fi

echo
echo "==> ✓ Cloudflare Tunnel actualizado."
echo "    Backup: $BACKUP"
echo "    Test:"
echo "      curl -I https://api-ronda2.tikno.pro/health"
echo "      curl -I https://panel.tikno.pro"
