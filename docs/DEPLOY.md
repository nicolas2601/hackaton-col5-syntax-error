# DEPLOY — Hackathon Colombia 5.0 ronda 2

Guía paso a paso para desplegar API + Dashboard al server tikno (Coolify v4 + Cloudflare Tunnel).

> **Tiempo estimado**: 25-40 min (incluye carga ETL del CSV de 1.7 GB).

---

## 0. Pre-requisitos

### Local (workstation Nicolas)

- `docker` 24+ con buildx
- `jq`, `curl`, `bash 5+`
- Token Coolify en `~/.config/coolify/token` (chmod 600)
- Pass Postgres en `~/.config/coolify/secop-creds`:
  ```bash
  export POSTGRES_PASSWORD='...'
  ```

### Server tikno (control.tikno.pro)

- Coolify v4.0.0-beta.442 corriendo
- Postgres `secop` (UUID `roook084kg4owsgkcc8k08s8`) con tabla `contratos` (5.6M filas)
- Network docker `coolify` activo
- `cloudflared` v2024+ instalado como systemd service
- DNS de `*.tikno.pro` apuntando al tunnel ID

### DNS Cloudflare

Antes de empezar, en el dashboard de Cloudflare crear los CNAMEs:

```
api-ronda2.tikno.pro  CNAME  <TUNNEL_ID>.cfargotunnel.com  (proxied)
panel.tikno.pro       CNAME  <TUNNEL_ID>.cfargotunnel.com  (proxied)
```

---

## 1. Cargar CSV a Postgres (ETL)

### 1.1 Copiar CSV al server

```bash
# Desde local (1.7 GB → puede tardar 3-10 min según red)
scp /tmp/ronda2/SECOP_II_-_Contratos_Electrónicos_20260506.csv \
    tikno@control.tikno.pro:/tmp/ronda2/
```

### 1.2 Copiar scripts ETL al server

```bash
ssh tikno@control.tikno.pro 'mkdir -p ~/hackaton_colombia5.0/scripts/etl'
scp scripts/etl/load_2025.py scripts/etl/run_load_2025.sh \
    tikno@control.tikno.pro:~/hackaton_colombia5.0/scripts/etl/
```

### 1.3 Ejecutar ETL

```bash
ssh tikno@control.tikno.pro
cd ~/hackaton_colombia5.0
chmod +x scripts/etl/run_load_2025.sh
sudo -E ./scripts/etl/run_load_2025.sh
```

Output esperado:
```
==> CSV: /tmp/ronda2/...csv (1.7G)
==> DB:  secop @ roook084kg4owsgkcc8k08s8
[INFO] Creando tabla contratos_2025 ...
[INFO] Iniciando COPY (~1.7 GB)...
[INFO]   COPY: 100,000 / ~1,003,902 (10.0%) — 95,432 rows/s
...
[INFO]   COPY: 1,003,902 / ~1,003,902 (100.0%) — 110,200 rows/s
[INFO] Creando 8 índices...
[INFO] ✓ Carga 2025 completa.
```

### 1.4 Verificación

```bash
docker exec -i $(docker ps -qf name=postgres-roook) \
    psql -U postgres -d secop -c \
    "SELECT count(*) FROM contratos_2025;"
# → 1003902
```

---

## 2. Build & deploy API

```bash
# Desde local (workstation Nicolas)
cd /home/nicolas/hackaton_colombia5.0
chmod +x scripts/deploy/deploy_api.sh
./scripts/deploy/deploy_api.sh
```

Pasos internos:
1. `docker build -t secop-api:TIMESTAMP api/`
2. POST a Coolify API → crea app `api-ronda2` en project SECOP
3. Inyecta `DATABASE_URL` con la pass real
4. Trigger deploy → Coolify pull image + start container
5. Wait healthcheck `https://api-ronda2.tikno.pro/health`

**Nota**: si la imagen está local, podés pushearla al registry interno de Coolify, o hacer `docker save | ssh ... docker load` antes del deploy.

### Alternativa: build en el server

```bash
ssh tikno@control.tikno.pro
cd ~/hackaton_colombia5.0
docker build -t secop-api:latest api/
# luego en Coolify panel: usar imagen local secop-api:latest
```

---

## 3. Build & deploy Dashboard

```bash
cd /home/nicolas/hackaton_colombia5.0
chmod +x scripts/deploy/deploy_dashboard.sh
./scripts/deploy/deploy_dashboard.sh
```

El script:
1. Genera `dashboard/Dockerfile` (Next.js 15 standalone) si no existe
2. Build con `NEXT_PUBLIC_API_URL=https://api-ronda2.tikno.pro` baked-in
3. Push a Coolify, crea app `panel`
4. Wait `https://panel.tikno.pro` (HTTP 200/301/302)

---

## 4. Configurar Cloudflare Tunnel

```bash
# Copiar config al server
scp deploy/cloudflare/config.yml \
    tikno@control.tikno.pro:/tmp/cloudflared-config.yml

ssh tikno@control.tikno.pro
sudo mv /tmp/cloudflared-config.yml ~/hackaton_colombia5.0/deploy/cloudflare/config.yml

# IMPORTANTE: editar tunnel ID para que matchee con el actual del server
sudo grep -E "^tunnel:" /etc/cloudflared/config.yml
# copiar ese ID al config nuevo:
sudo sed -i "s/TIKNO_TUNNEL_ID/<ID_REAL>/" ~/hackaton_colombia5.0/deploy/cloudflare/config.yml

# Aplicar
chmod +x ~/hackaton_colombia5.0/scripts/deploy/setup_cloudflare.sh
sudo ~/hackaton_colombia5.0/scripts/deploy/setup_cloudflare.sh --dry-run    # preview
sudo ~/hackaton_colombia5.0/scripts/deploy/setup_cloudflare.sh              # aplicar
```

Output esperado:
```
==> [1/4] Backup: /etc/cloudflared/config.yml → ...bak.20260508-153022
==> [2/4] Diff: ... (3 hostnames nuevos)
==> [3/4] Validando: OK
==> [4/4] Reload cloudflared: ✓ activo
```

---

## 5. Verificación end-to-end

```bash
# API health
curl -fsS https://api-ronda2.tikno.pro/health | jq
# → {"status":"ok","db":"connected","rows_2025":1003902}

# API endpoint real
curl -fsS 'https://api-ronda2.tikno.pro/api/v1/contratos/stats' | jq

# Dashboard
curl -I https://panel.tikno.pro
# → HTTP/2 200

# Dashboard renderiza
curl -fsS https://panel.tikno.pro | grep -o '<title>[^<]*' | head -1
```

---

## 6. Rollback

### Rollback API

```bash
# En Coolify panel → applications → api-ronda2 → Deployments
# Click "Rollback" en el deploy anterior, O:

curl -X POST -H "Authorization: Bearer $COOLIFY_TOKEN" \
    https://coolify.tikno.pro/api/v1/applications/<APP_UUID>/rollback
```

### Rollback Cloudflare

```bash
ssh tikno@control.tikno.pro
ls -lt /etc/cloudflared/config.yml.bak.* | head -1
sudo cp /etc/cloudflared/config.yml.bak.YYYYMMDD-HHMMSS /etc/cloudflared/config.yml
sudo systemctl restart cloudflared
```

### Rollback ETL

```bash
docker exec -i $(docker ps -qf name=postgres-roook) \
    psql -U postgres -d secop -c "DROP TABLE contratos_2025 CASCADE;"
# luego re-correr scripts/etl/run_load_2025.sh
```

---

## 7. Troubleshooting

### 502 Bad Gateway en api-ronda2

```bash
# 1. ¿Container corriendo?
ssh tikno docker ps | grep api-ronda2

# 2. ¿Healthcheck pasa?
ssh tikno 'docker exec <ID> curl -s http://localhost:8000/health'

# 3. ¿Traefik routea?
ssh tikno 'docker logs $(docker ps -qf name=coolify-proxy) 2>&1 | tail -50 | grep api-ronda2'

# 4. ¿DB alcanzable desde el container?
ssh tikno 'docker exec <ID> python -c "import psycopg; psycopg.connect(\"$DATABASE_URL\")"'
```

### Redirect loop en panel.tikno.pro

- Verificar que Cloudflare SSL esté en **Full (strict)**, NO Flexible.
- Verificar que el tunnel use `https://localhost:443` con `noTLSVerify: true` (no http).

### CSV ETL falla con "FATAL: password authentication failed"

```bash
# Re-leer pass del secret de Coolify:
docker inspect <postgres-container> --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | grep POSTGRES_PASSWORD
```

### `pg_dump` o `COPY` muy lento

Aumentar `BATCH_SIZE`:
```bash
sudo BATCH_SIZE=50000 ./scripts/etl/run_load_2025.sh
```

### Container OOM-killed

Aumentar memory limit en `deploy/coolify/api-ronda2.json` (default 1024m → 2048m) y `--redeploy`.

---

## 8. Comandos rápidos

```bash
# Logs en vivo
ssh tikno 'docker logs -f $(docker ps -qf name=api-ronda2)'
ssh tikno 'docker logs -f $(docker ps -qf name=panel)'

# Restart sin redeploy
curl -X POST -H "Authorization: Bearer $COOLIFY_TOKEN" \
    https://coolify.tikno.pro/api/v1/applications/<UUID>/restart

# Stats DB
docker exec -i <pg> psql -U postgres -d secop -c \
    "SELECT count(*), pg_size_pretty(pg_total_relation_size('contratos_2025')) FROM contratos_2025;"
```
