# Hackaton Nacional COL 5.0 — Equipo Syntax Error

> **Análisis de transparencia y contratación pública sobre SECOP II**
> Plataforma con API REST + Dashboard interactivo deployada self-hosted

[![API](https://img.shields.io/badge/API-api--ronda2.tikno.pro-5e4cff)](https://api-ronda2.tikno.pro/docs)
[![Dashboard](https://img.shields.io/badge/Dashboard-panel.tikno.pro-1a1b25)](https://panel.tikno.pro)
[![License](https://img.shields.io/badge/license-MIT-eceff3)](LICENSE)

## Equipo

- **Nicolás Moreno** ([@nicolas2601](https://github.com/nicolas2601)) — Capitán, Backend & Infra
- **Paula Saavedra** ([@Paulasaah](https://github.com/Paulasaah)) — Análisis & QA
- **Andre Julián** ([@Andrejulian21](https://github.com/Andrejulian21)) — Frontend
- **Nathalia Quintero** ([@NathQuintero](https://github.com/NathQuintero)) — UX & Docs

## Stack

| Capa | Tech | Subdominio |
|---|---|---|
| **API REST** | FastAPI + PostgREST + Postgres 16 | `api-ronda2.tikno.pro` |
| **Dashboard** | Next.js 15 + Tailwind v4 + shadcn/ui | `panel.tikno.pro` |
| **Storage** | Postgres 16 (Coolify) | self-hosted |
| **Infra** | Coolify v4 + Cloudflare Tunnel + Traefik | server tikno (LAN) |

## Datasets analizados

| Ronda | Dataset | ID | Filas |
|---|---|---|---|
| Ronda 1 BD1 | SECOP II Contratos Electrónicos | `jbjy-vk9h` | 5,614,448 |
| Ronda 1 BD2 | SECOP II Archivos Descarga 2025 | `dmgg-8hin` | 17,353,029 |
| Ronda 2 | SECOP II snapshot 2025 (1.7GB CSV) | snapshot 2026-05-06 | 1,003,902 |

## Arquitectura

```
┌──────────────────────────┐         ┌─────────────────────────┐
│  Cloudflare Edge         │         │  Server tikno (LAN)     │
│  - api-ronda2.tikno.pro  │ tunnel  │  ├─ Coolify v4          │
│  - panel.tikno.pro       │ ──────► │  ├─ FastAPI (uvicorn)   │
│  - api.tikno.pro (R1)    │         │  ├─ Postgres 16         │
└──────────────────────────┘         │  ├─ PostgREST           │
                                     │  └─ Next.js (build SSR) │
                                     └─────────────────────────┘
```

## Estructura del repo

```
hackaton_colombia5.0/
├── api/              # FastAPI backend (Python)
│   ├── app/          # Routers, models, services
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── dashboard/        # Next.js 15 + Tailwind v4 + shadcn/ui
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── public/
│   └── package.json
├── docs/             # Documentación técnica
│   ├── ARCHITECTURE.md
│   ├── STYLE_GUIDE.md (Lightdash tokens)
│   ├── ROUNDS.md
│   └── DEPLOY.md
├── scripts/
│   ├── etl/          # Cargar CSV → Postgres
│   ├── ronda1/       # bd1_respuestas.py
│   ├── ronda2/       # analisis_ronda2.py
│   └── deploy/       # bash scripts Coolify/Cloudflare
└── deploy/
    ├── coolify/      # Coolify configs
    └── cloudflare/   # Tunnel ingress
```

## Quick Start

### Backend (API)
```bash
cd api && uv sync && uv run uvicorn app.main:app --reload
# OpenAPI Swagger en http://localhost:8000/docs
```

### Frontend (Dashboard)
```bash
cd dashboard && pnpm install && pnpm dev
# http://localhost:3000
```

## Diseño

**Style guide**: [Lightdash](docs/STYLE_GUIDE.md) — light theme, Electric Violet (`#5e4cff`) accent, Britti Sans + Inter typography, soft 8/12px border radius.

## Documentación

- [📐 Arquitectura](docs/ARCHITECTURE.md)
- [🎨 Style Guide](docs/STYLE_GUIDE.md)
- [📊 Análisis Rondas 1 y 2](docs/ROUNDS.md)
- [🚀 Deploy Guide](docs/DEPLOY.md)
- [🔌 API Reference](https://api-ronda2.tikno.pro/docs) (OpenAPI Swagger auto-generado)

## Licencia

MIT © 2026 Equipo Syntax Error
