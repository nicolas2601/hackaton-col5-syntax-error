# SECOP II Dashboard

Dashboard de transparencia sobre la contratación pública colombiana — Hackathon Colombia 5.0.

## Stack

- Next.js 15 App Router + TypeScript strict
- Tailwind CSS v4 (CSS-first config con `@theme`)
- shadcn/ui sobre Radix Primitives
- Recharts · react-simple-maps
- Framer Motion · TanStack Query
- pnpm

## Quickstart

```bash
pnpm install
cp .env.example .env.local   # apunta al API
pnpm dev                     # http://localhost:3000
```

## Build production

```bash
pnpm build && pnpm start
```

## Docker

```bash
docker build -t secop-dashboard .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://api-ronda2.tikno.pro secop-dashboard
```

## Estructura

```
src/
  app/            # rutas (landing, dashboard, mapa, anomalias, pareto, genero, docs)
  components/     # ui shadcn + KPI cards + charts + ColombiaMap
  lib/            # api client, mock-data, utils, query-client
  types/          # tipos compartidos
public/
  colombia-deptos.geojson  # placeholder, reemplazar con GeoJSON real
```

## Páginas

| Ruta              | Descripción                                |
|-------------------|--------------------------------------------|
| `/`               | Landing con hero + stats + features        |
| `/dashboard`      | Bento grid con 12+ visualizaciones         |
| `/mapa`           | Choropleth Colombia por depto              |
| `/anomalias`      | Tabla top 20 con sustento expandible       |
| `/pareto`         | Curva acumulada 7/80                       |
| `/genero`         | Brecha de género (M/F/Otro)                |
| `/docs/[slug]`    | Documentación (overview, api, metodología) |

## API

API base configurable vía `NEXT_PUBLIC_API_URL`. Si el endpoint falla, todas
las páginas hacen fallback automático a `lib/mock-data.ts`.

## Notas

- El GeoJSON de departamentos en `/public/colombia-deptos.geojson` es un
  placeholder con bounding boxes simplificados. Reemplazar con uno real
  (e.g. `marcovega/colombia-json`) para producción.
- `next-themes` está forzado a `light` (no hay dark mode por design).
