# ARCHITECTURE — Hackathon Colombia 5.0 (ronda 2)

## Vista de alto nivel

```
                ┌─────────────────────────────────────────────┐
                │             USUARIOS (browser)              │
                │      panel.tikno.pro / api-ronda2.tikno.pro │
                └──────────────────┬──────────────────────────┘
                                   │ HTTPS (TLS 1.3)
                                   ▼
                ┌─────────────────────────────────────────────┐
                │            CLOUDFLARE EDGE                  │
                │  · WAF / DDoS / Bot mgmt                    │
                │  · Cache estático (panel)                   │
                │  · DNS: *.tikno.pro → tunnel CNAME          │
                └──────────────────┬──────────────────────────┘
                                   │ Cloudflare Tunnel
                                   │ (QUIC, outbound-only)
                                   ▼
       ╔═══════════════════════════════════════════════════════════╗
       ║   SERVER tikno (control.tikno.pro / LAN 192.168.1.50)     ║
       ║                                                           ║
       ║  ┌─────────────────────────────────────────────────────┐  ║
       ║  │              cloudflared (systemd)                  │  ║
       ║  │  /etc/cloudflared/config.yml                        │  ║
       ║  │  ingress:                                           │  ║
       ║  │   • api.tikno.pro          → https://localhost:443  │  ║
       ║  │   • api-ronda2.tikno.pro   → https://localhost:443  │  ║
       ║  │   • panel.tikno.pro        → https://localhost:443  │  ║
       ║  │   • coolify.tikno.pro      → https://localhost:443  │  ║
       ║  └────────────────────┬────────────────────────────────┘  ║
       ║                       │ HTTP Host header routing          ║
       ║                       ▼                                   ║
       ║  ┌─────────────────────────────────────────────────────┐  ║
       ║  │       Traefik (gestionado por Coolify)              │  ║
       ║  │       container: coolify-proxy                      │  ║
       ║  │       :80, :443 (Let's Encrypt)                     │  ║
       ║  │       Discovery: docker labels                      │  ║
       ║  └────┬─────────────┬──────────────┬───────────────────┘  ║
       ║       │             │              │                      ║
       ║       │             │              │ Host(`coolify...`)   ║
       ║       │             │              ▼                      ║
       ║       │             │     ┌──────────────────┐            ║
       ║       │             │     │ Coolify Panel    │            ║
       ║       │             │     │ (laravel + nuxt) │            ║
       ║       │             │     └──────────────────┘            ║
       ║       │             │                                     ║
       ║       │             │ Host(`panel.tikno.pro`)             ║
       ║       │             ▼                                     ║
       ║       │   ┌──────────────────────────┐                    ║
       ║       │   │   panel (Next.js 15)     │                    ║
       ║       │   │   :3000  standalone      │                    ║
       ║       │   │   image: secop-panel     │                    ║
       ║       │   │   build-time:            │                    ║
       ║       │   │     NEXT_PUBLIC_API_URL  │                    ║
       ║       │   └──────────┬───────────────┘                    ║
       ║       │              │                                    ║
       ║       │              │ fetch (browser-side, no SSR)       ║
       ║       │              │                                    ║
       ║       │ Host(`api-ronda2.tikno.pro`)                      ║
       ║       ▼              │                                    ║
       ║  ┌──────────────────────────┐                             ║
       ║  │   api-ronda2 (FastAPI)   │◄────────────────────────┐   ║
       ║  │   :8000  uvicorn x4 wkrs │                         │   ║
       ║  │   image: secop-api       │                         │   ║
       ║  │   /health, /api/v1/*     │                         │   ║
       ║  └──────────┬───────────────┘                         │   ║
       ║             │ psycopg pool (min=2, max=20)            │   ║
       ║             │                                         │   ║
       ║             ▼                                         │   ║
       ║  ┌────────────────────────────────────────────┐       │   ║
       ║  │  Postgres 16 (UUID: roook084kg4owsgkcc8k…) │       │   ║
       ║  │  DB: secop                                 │       │   ║
       ║  │  Tablas:                                   │       │   ║
       ║  │   • contratos        (5.6M, 2015–2026)     │       │   ║
       ║  │   • contratos_2025   (1M, ronda 2 NEW)     │       │   ║
       ║  │  Volume: /var/lib/coolify/databases/...    │       │   ║
       ║  └────────────────────────────────────────────┘       │   ║
       ║                          ▲                            │   ║
       ║                          │ COPY FROM STDIN            │   ║
       ║                  ┌───────┴────────┐                   │   ║
       ║                  │ etl-load-2025  │                   │   ║
       ║                  │ python:3.12    │                   │   ║
       ║                  │ (one-shot)     │                   │   ║
       ║                  └────────────────┘                   │   ║
       ║                                                       │   ║
       ║  Docker network: `coolify` (bridge)                   │   ║
       ║  Todos los containers en este network se ven por UUID │   ║
       ║                                                       │   ║
       ╚═══════════════════════════════════════════════════════╧═══╝
```

---

## Componentes y responsabilidades

### 1. Cloudflare Edge

- **Función**: terminación TLS pública, DNS, WAF, cache.
- **DNS**: `api-ronda2.tikno.pro` y `panel.tikno.pro` → CNAME al tunnel.
- **No requiere abrir puertos en el server** (tunnel outbound-only sobre QUIC).

### 2. cloudflared (systemd)

- **Container/proceso**: systemd unit `cloudflared.service` en el host.
- **Config**: `/etc/cloudflared/config.yml`.
- **Routing**: por `hostname` HTTP host header → todos van a `https://localhost:443` (Traefik) con `httpHostHeader` preservado, `noTLSVerify: true` porque el cert de localhost es self-signed pero la validación real ocurrió en Cloudflare Edge.

### 3. Traefik (Coolify-managed)

- **Container**: `coolify-proxy`.
- **Discovery**: labels Docker en cada container (declarados en `deploy/coolify/*.json` → `custom_labels`).
- **TLS**: Let's Encrypt resolver `letsencrypt`. Cert per-domain, auto-renew.
- **Routing rules** (vía labels):
  - `Host(\`api-ronda2.tikno.pro\`)` → service port `8000`
  - `Host(\`panel.tikno.pro\`)` → service port `3000`

### 4. FastAPI (`api-ronda2`)

- **Stack**: Python 3.12 + FastAPI + uvicorn + psycopg3 (binary).
- **Imagen**: `secop-api:latest` (multi-stage uv-based, ~120MB).
- **Workers**: 4 uvicorn workers (1 GB RAM limit → ~250 MB/worker).
- **Pool DB**: psycopg async pool, min=2 max=20 (no satura los 100 conn default de PG).
- **Endpoints**:
  - `GET /health` → status + DB ping + counts
  - `GET /api/v1/contratos/...` → query sobre `contratos` + `contratos_2025`
  - `GET /api/v1/stats/...` → agregaciones precomputadas / cached
- **Cache**: TTL 300s en endpoints de stats (in-process LRU).

### 5. Next.js Dashboard (`panel`)

- **Stack**: Next.js 15.0.3 + React 19 RC + Tailwind v4 + recharts + framer-motion + react-simple-maps.
- **Output**: `standalone` → solo Node.js + `.next/standalone` + `static` + `public` (~150 MB image).
- **Render**: SSG donde se pueda, RSC + cliente para charts interactivos.
- **API URL**: `NEXT_PUBLIC_API_URL` baked-in en build → `https://api-ronda2.tikno.pro`.
- **Rewrite proxy**: `/api/proxy/*` → API (evita CORS para fetches server-side si hicieran falta).

### 6. Postgres (compartido)

- **Versión**: 16 (default Coolify).
- **DB**: `secop`.
- **Tablas existentes**: `contratos` (5.6M filas, 2015–2026) — fuente para queries históricas.
- **Tabla nueva**: `contratos_2025` (1,003,902 filas, snapshot 2026-05-06) — ronda 2 hackathon.
- **Schema**: 84 columnas tipadas + `id BIGSERIAL` + `ingested_at TIMESTAMPTZ`.
- **Índices**: 7 B-tree (nit, doc_proveedor, fechas, valor, modalidad, estado, departamento) + 1 GIN tsvector spanish (`objeto_del_contrato`).
- **Tamaño esperado**: ~2.5 GB tabla + ~500 MB índices.

### 7. ETL (`etl-load-2025`)

- **Tipo**: container one-shot (no resident).
- **Imagen**: `python:3.12-slim` + `psycopg[binary]` instalado en runtime.
- **Estrategia**: stream del CSV línea por línea → transform → `COPY FROM STDIN` (text format con `\N` para NULL).
- **Resume-safe**: verifica `COUNT(*) >= 1003902` antes de cargar.
- **Throughput esperado**: 80–150k rows/sec → 7-13 min para 1M filas.
- **Network**: conectado a `coolify` para alcanzar el Postgres por UUID interno.

---

## Flujo de datos: query típica

```
1. Browser  → GET https://panel.tikno.pro/contratos
2. CF Edge  → tunnel  → cloudflared  → Traefik (Host=panel.tikno.pro)
              → panel:3000  (Next.js render server-side)
3. Browser  → GET https://api-ronda2.tikno.pro/api/v1/contratos?dept=Bogotá
4. CF Edge  → tunnel  → cloudflared  → Traefik (Host=api-ronda2.tikno.pro)
              → api-ronda2:8000  (FastAPI route)
5. FastAPI  → psycopg pool  → postgres-roook:5432
              → SELECT * FROM contratos_2025 WHERE departamento='Bogotá' LIMIT 50
6. Postgres → resultset (índice idx_contratos_2025_departamento, ~10ms)
7. FastAPI  → JSON response (gzip vía Traefik middleware)
8. Browser  → render charts (recharts) + table (TanStack)
```

---

## Decisiones arquitectónicas (ADRs cortos)

### ADR-1: Reusar Postgres existente en lugar de DB separada

- **Por qué**: misma fuente SECOP → joins entre `contratos` (histórico) y `contratos_2025` (snapshot ronda 2) son clave para análisis de tendencias.
- **Trade-off**: una sola DB es SPOF. Mitigación: backups diarios de Coolify ya existentes.

### ADR-2: Tabla `contratos_2025` separada en lugar de UNION en `contratos`

- **Por qué**: schema del CSV de ronda 2 trae 84 cols (vs 73 en `contratos`); algunas con tipos diferentes. Migrar `contratos` rompe queries existentes.
- **Trade-off**: queries cross-año requieren UNION ALL explícito o vista materializada.

### ADR-3: Cloudflare Tunnel sin abrir puertos públicos

- **Por qué**: server detrás de NAT residencial, IP dinámica. Tunnel resuelve eso + da DDoS protection gratis.
- **Trade-off**: latencia +20-40ms vs A record directo. Para hackathon, irrelevante.

### ADR-4: Imágenes Docker pre-built local en lugar de buildpack en Coolify

- **Por qué**: build de Next.js 15 con React 19 RC en el server (4 GB RAM total) puede OOM. Build local con más recursos es más rápido y reproducible.
- **Trade-off**: requiere `docker push` al registry interno de Coolify O `docker save | ssh` si no hay registry.

### ADR-5: COPY FROM STDIN en lugar de pandas+to_sql o INSERTs

- **Por qué**: COPY text format es 10-50× más rápido que INSERTs y no requiere cargar el CSV completo en RAM.
- **Trade-off**: parsing manual de tipos en Python. Mitigación: parsers tipados con regex + datetime.strptime, tests de smoke en `tests/`.

### ADR-6: Índices al final del COPY

- **Por qué**: crear índices durante INSERT/COPY es 5-10× más lento que crearlos después.
- **Trade-off**: la tabla es read-only durante la creación de índices (~30s c/u).

---

## Operacional

### Healthchecks

| Servicio   | Endpoint                              | Interval | Timeout |
|------------|---------------------------------------|----------|---------|
| api-ronda2 | `GET :8000/health`                    | 30s      | 10s     |
| panel      | `GET :3000/`                          | 30s      | 10s     |
| Postgres   | `pg_isready` (built-in Coolify)       | 60s      | 5s      |
| Tunnel     | `cloudflared tunnel info` + systemd   | -        | -       |

### Logs

- **API/Panel**: `docker logs -f <container>` o Coolify panel → Logs.
- **Cloudflared**: `journalctl -u cloudflared -f`.
- **Postgres**: Coolify panel → DB → Logs.

### Backup

- Postgres: backup automático diario de Coolify (ver UUID en `Databases → secop → Backups`).
- Para snapshot manual antes de cargar:
  ```bash
  docker exec <pg> pg_dump -U postgres -Fc secop > secop-pre-2025.dump
  ```

### Métricas (futuro)

- Plug-and-play: Grafana + Prometheus stack en Coolify (otro project).
- Por ahora: Coolify panel muestra CPU/RAM/network por container.

---

## Diagrama de componentes (C4 nivel 2)

```
[USUARIOS] ──▶ [Cloudflare Edge] ──▶ [Tunnel] ──▶ [Traefik]
                                                      │
                                  ┌───────────────────┼───────────────────┐
                                  ▼                   ▼                   ▼
                              [api-ronda2]         [panel]            [coolify]
                                  │
                                  ▼
                              [Postgres secop]
                                  ▲
                                  │
                              [etl-load-2025]
```
