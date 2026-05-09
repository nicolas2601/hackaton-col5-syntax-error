import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { ExternalLink, Github, BookOpen, Server, Globe, Database, FileCode, Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const API_URL = "https://api-ronda2.tikno.pro";
const REPO_URL = "https://github.com/nicolas2601/hackaton-col5-syntax-error";
const PEZ_GORDO_REPO = "https://github.com/nicolas2601/pez-gordo-audit";

const DOCS: Record<string, { title: string; content: string }> = {
  overview: {
    title: "Visión general",
    content: `
# SECOP II — Plataforma de Transparencia

Plataforma open-source de auditoría sobre la contratación pública colombiana, construida sobre el snapshot oficial 2025 de SECOP II (Colombia Compra Eficiente).

> **Equipo Syntax Error** — Hackathon Nacional COL 5.0
> Nicolás Moreno · Paula Saavedra · Andre Julián · Nathalia Quintero

## Resumen ejecutivo

| Métrica | Valor |
|---|---|
| Contratos analizados | **1,003,902** |
| Departamentos cubiertos | **33** |
| Valor agregado | **$166.7 billones COP** |
| Snapshot | **2026-05-06** |
| Endpoints REST | **11 funcionales** |

## Hallazgos críticos

- **75.7%** de los contratos son por **Contratación Directa** (sin licitación pública). Bandera roja de transparencia.
- **Concentración Pareto 7/80**: solo el **7.23%** de las entidades (285 de 3,942) ejecuta el **80%** del valor total. Más extremo que la regla 80/20 clásica.
- **Brecha de género financiera**: las mujeres firman **+15%** más contratos que los hombres pero ejecutan **-31.7%** del valor total. Promedio H = $141M, Promedio M = $84M.
- **Sólo 0.08%** de los contratos tiene cláusula de pago adelantado. El **2.13%** incluye obligación ambiental explícita.
- **5 columnas de fondos** (PGN, SGP, Regalías, Recursos Propios, Recursos de Crédito) vienen 100% null en el dataset oficial.

## Stack técnico

| Capa | Tecnología |
|---|---|
| **Backend** | FastAPI 0.115 + DuckDB 1.5 sobre CSV (1.7 GB) |
| **Frontend** | Next.js 15 App Router + Tailwind v4 + shadcn/ui |
| **Charts** | Recharts + react-simple-maps + Framer Motion |
| **Infra** | Docker + Coolify v4 + Cloudflare Tunnel + Traefik |
| **Tipografía** | Britti Sans (Montserrat fallback) + Inter + IBM Plex Mono |
| **Tema** | Lightdash (light, accent Electric Violet \`#5e4cff\`) |

## Endpoints disponibles

\`\`\`bash
GET /health                        # Liveness probe
GET /api/v1/stats/total            # KPIs globales
GET /api/v1/departamentos/top      # Top 10 deptos
GET /api/v1/modalidades            # Modalidades de contratación
GET /api/v1/tipos-contrato         # Top 5 tipos
GET /api/v1/entidades/top          # Top 10 entidades por valor
GET /api/v1/temporal               # Distribución mensual
GET /api/v1/pareto/entidades       # Curva de Pareto
GET /api/v1/genero/brecha          # Brecha género (H/M/Otro)
GET /api/v1/anomalias              # Top 10 valores anómalos
GET /api/v1/mapa/deptos            # Choropleth Colombia
\`\`\`

Cache HTTP de 60s. CORS abierto. **Rate limit**: sin throttling.

## Latencias medidas

| Endpoint | p50 |
|---|---|
| \`/health\` | <5 ms |
| \`/api/v1/stats/total\` | <10 ms |
| \`/api/v1/anomalias\` | <20 ms |
| \`/api/v1/mapa/deptos\` | <15 ms |

Todas las agregaciones se pre-computan en el startup del container con DuckDB sobre el CSV completo (~30 s warmup), después se sirven desde memoria.

## Páginas del dashboard

- **/** — Landing con KPIs hero
- **/dashboard** — Bento grid con 13 visualizaciones (deptos, modalidades, tipos, entidades, Pareto, género, anomalías, ambiental, anticipos)
- **/mapa** — Choropleth interactivo de Colombia con 33 deptos
- **/anomalias** — Tabla expandible con top 10 valores + clasificación VERIDICO/FALSO/REVISAR
- **/pareto** — Curva acumulada con anotaciones 7/80 y 80/20
- **/genero** — Dumbbell chart H/M/Otro con sustento estadístico
- **/docs** — Documentación técnica (esta página)
`,
  },
  api: {
    title: "Referencia API",
    content: `
# Referencia API

## Base URLs

| Tipo | URL |
|---|---|
| **Producción** | \`https://api-ronda2.tikno.pro\` |
| **Swagger UI** | [\`/docs\`](https://api-ronda2.tikno.pro/docs) |
| **OpenAPI 3.1** | [\`/openapi.json\`](https://api-ronda2.tikno.pro/openapi.json) |
| **ReDoc** | [\`/redoc\`](https://api-ronda2.tikno.pro/redoc) |

## Autenticación

Por ahora **sin autenticación** — datos públicos en virtud de la **Ley 1712 de 2014** (Transparencia y acceso a la información pública).

CORS abierto:
\`\`\`
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, OPTIONS
\`\`\`

---

## GET /health

Liveness probe. Confirma que el container está vivo y el CSV cargado.

\`\`\`bash
curl https://api-ronda2.tikno.pro/health
\`\`\`

\`\`\`json
{
  "status": "ok",
  "total": 1003902,
  "csv": "/data/secop.csv",
  "ready": true
}
\`\`\`

---

## GET /api/v1/stats/total

Agregados globales del snapshot 2025.

\`\`\`json
{
  "total_registros": 1003902,
  "total_pymes": 132479,
  "pct_pymes": 13.20,
  "total_directa": 759993,
  "pct_directa": 75.70,
  "pareto_entidades": 285,
  "pareto_pct_valor": 80,
  "total_valor": 166703293895413
}
\`\`\`

---

## GET /api/v1/departamentos/top

Top 10 departamentos por número de contratos publicados, con valor agregado.

\`\`\`json
[
  {
    "departamento": "Distrito Capital de Bogotá",
    "contratos": 280248,
    "valor_total": 69469406868337,
    "pct": 27.92
  }
]
\`\`\`

---

## GET /api/v1/modalidades

Distribución por modalidad de contratación. Confirma que **75.7%** es Contratación Directa.

\`\`\`json
[
  { "modalidad": "Contratación directa", "contratos": 759993, "pct": 75.7 },
  { "modalidad": "Contratación régimen especial", "contratos": 152957, "pct": 15.2 }
]
\`\`\`

---

## GET /api/v1/tipos-contrato

Top 5 tipos. La mayoría (**85.76%**) son **Prestación de servicios**.

\`\`\`json
[
  { "tipo": "Prestación de servicios", "contratos": 860913, "valor_total": 52847104050186 }
]
\`\`\`

---

## GET /api/v1/entidades/top

Top 10 entidades por valor agregado.

\`\`\`json
[
  {
    "entidad": "DISTRITO ESPECIAL DE CIENCIA TECNOLOGIA E INNOVACION DE MEDELLIN",
    "valor_total": 7192818196456,
    "contratos": 1446
  }
]
\`\`\`

---

## GET /api/v1/pareto/entidades

Curva de Pareto: para cada rank, el porcentaje acumulado del valor total.

\`\`\`json
[
  { "rank": 1, "entidad": "...", "valor": 7192818196456, "pct_acumulado": 4.31 },
  { "rank": 285, "entidad": "...", "valor": 12000000, "pct_acumulado": 80.0 }
]
\`\`\`

**Insight:** los primeros **285 ranks** acumulan 80% del valor total. Pareto 7/80 — concentración más extrema que el 80/20 clásico.

---

## GET /api/v1/genero/brecha

Stats por género del representante legal.

\`\`\`json
[
  { "genero": "M", "promedio": 141293990, "mediana": 20400000, "contratos": 378213 },
  { "genero": "F", "promedio": 84026115, "mediana": 18850000, "contratos": 434081 }
]
\`\`\`

**Brecha:** las mujeres firman +15% más contratos pero reciben **-40.5%** menos por contrato (promedio).

---

## GET /api/v1/anomalias

Top 10 valores con clasificación IA y sustento textual.

\`\`\`json
[
  {
    "id": "CO1.PCCNTR.8738616",
    "entidad": "MINISTERIO DE MINAS Y ENERGIA",
    "contratista": "GECELCA S.A. E.S.P.",
    "valor": 4205027751839,
    "modalidad": "Contratación directa",
    "fecha": "12/29/2025",
    "verdict": "VERIDICO",
    "sustento": "Programa Colombia Solar — fondo plurianual FENOGE/MME"
  }
]
\`\`\`

\`verdict\` ∈ \`VERIDICO\` | \`FALSO\` | \`REVISAR\`.

---

## GET /api/v1/mapa/deptos

Datos para el choropleth Colombia. \`codigo\` es ISO DANE 2 dígitos.

\`\`\`json
[
  { "codigo": "11", "nombre": "Distrito Capital de Bogotá", "contratos": 280248, "valor_total": 69469406868337 }
]
\`\`\`

---

## Ejemplos cliente

### Python (httpx)

\`\`\`python
import httpx

API = "https://api-ronda2.tikno.pro"

async with httpx.AsyncClient(base_url=API, timeout=30) as cli:
    stats = (await cli.get("/api/v1/stats/total")).json()
    print(f"Total: {stats['total_registros']:,}")
\`\`\`

### Node.js (fetch)

\`\`\`ts
const API = "https://api-ronda2.tikno.pro";

const stats = await fetch(\`\${API}/api/v1/stats/total\`).then(r => r.json());
console.log(\`Total: \${stats.total_registros.toLocaleString()}\`);
\`\`\`

### curl

\`\`\`bash
curl -fsS https://api-ronda2.tikno.pro/api/v1/stats/total | jq
\`\`\`
`,
  },
  metodologia: {
    title: "Metodología",
    content: `
# Metodología

## Fuente de datos

Plataforma **SECOP II** (Sistema Electrónico para la Contratación Pública) operado por **Colombia Compra Eficiente — ANCP**.

- Dataset: \`SECOP II — Contratos Electrónicos\` (\`jbjy-vk9h\`)
- Snapshot oficial descargado el **2026-05-06** desde [datos.gov.co](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h)
- Tamaño: **1.7 GB** CSV, **84 columnas**, **1,003,902 filas**
- Cobertura temporal: enero 2025 — diciembre 2025 (con plurianuales 2020-2024 y errores 2026)

## Procesamiento

### 1. Ingesta (DuckDB)

\`\`\`python
import duckdb
con = duckdb.connect()
con.execute("""
    CREATE OR REPLACE VIEW c AS
    SELECT * FROM read_csv_auto(
        '/data/secop.csv',
        SAMPLE_SIZE=-1,
        all_varchar=true
    );
""")
\`\`\`

### 2. Limpieza de tipos

| Campo | Tipo origen | Saneo |
|---|---|---|
| \`Valor del Contrato\` | \`'$XX,XXX,XXX'\` (texto) | \`REGEXP_REPLACE([\\$,], '')::DOUBLE\` |
| \`Fecha de Firma\` | \`'MM/DD/YYYY'\` (texto) | \`STRPTIME('%m/%d/%Y')::DATE\` |
| \`Es Pyme\` | \`'Si'/'No'\` | mapeo a \`BOOLEAN\` |
| \`Género Representante Legal\` | \`'Hombre'/'Mujer'/'Otro'/null\` | \`'M'/'F'/'Otro'\` |
| \`Nit Entidad\` | \`'899,999,034'\` con comas | string sin formato (no number) |

### 3. Pre-cómputo en startup

Todas las agregaciones se calculan **una sola vez** al boot del container (~30s warmup), luego se sirven desde memoria con latencia <20ms.

### 4. Heurísticas analíticas

#### Anomalías financieras (Q15)
Top 10 valores absolutos de \`Valor del Contrato\`. Cada uno se clasifica con LLM + reglas:
- Modalidad declarada vs. techo legal de esa modalidad
- Tipo declarado vs. objeto del contrato
- Coherencia \`Valor del Contrato\` vs. \`Valor Pagado\` / \`Valor Facturado\`
- Histórico de la entidad

Verdicts: \`VERIDICO\` (3), \`FALSO\` (1), \`REVISAR\` (resto).

#### Concentración (Pareto, Q18)
\`\`\`sql
WITH ents AS (
  SELECT "Nombre Entidad" AS e,
         SUM(REGEXP_REPLACE("Valor del Contrato",'[$,]','','g')::DOUBLE) AS t
  FROM c GROUP BY 1
),
ranked AS (
  SELECT *, NTILE(100) OVER (ORDER BY t DESC) as q FROM ents
)
SELECT q, SUM(t) FROM ranked GROUP BY q ORDER BY q;
\`\`\`

**Resultado:** 80% del valor en **285 entidades de 3,942 (7.23%)** — concentración 7/80, más extrema que el 80/20 clásico.

#### Brecha género (Q19)
\`\`\`sql
SELECT "Género Representante Legal" AS g,
       AVG(valor_num) AS promedio,
       MEDIAN(valor_num) AS mediana,
       COUNT(*) AS contratos
FROM c
WHERE "Género Representante Legal" IS NOT NULL
GROUP BY g;
\`\`\`

**Resultado:** Hombre $141M vs Mujer $84M (-40.5% en valor promedio por contrato).

## Limitaciones

- **18.67%** de registros tienen \`Género Representante Legal = "No Definido"\` (mayoritariamente personas jurídicas)
- **5 columnas de fondos** vienen 100% null en el dataset oficial
- El sustento de cada anomalía es generado por IA y debe ser **validado por un humano**
- El snapshot 2025 no incluye contratos plurianuales firmados antes que aún están vigentes (los 4,402 con fecha pre-2025)

## Cumplimiento legal

| Ley | Aplicación |
|---|---|
| **Ley 1712/2014** | Transparencia y acceso a info pública — todos los datos consultados son públicos |
| **Ley 1581/2012** | Habeas Data — no se redistribuye PII más allá de lo ya publicado |
| **Ley 1273/2009** | Delitos informáticos — la plataforma es **únicamente educativa** |

## Reproducibilidad

Todo el pipeline está open-source:

- **Repo principal**: [hackaton-col5-syntax-error](${REPO_URL})
- **Repo Pez Gordo (auditoría PII)**: [pez-gordo-audit](${PEZ_GORDO_REPO})

\`\`\`bash
git clone https://github.com/nicolas2601/hackaton-col5-syntax-error
cd hackaton-col5-syntax-error
docker compose up
# API: http://localhost:8000
# Dashboard: http://localhost:3000
\`\`\`
`,
  },
};

export function generateStaticParams() {
  return Object.keys(DOCS).map((slug) => ({ slug }));
}

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function DocsPage({ params }: PageProps) {
  const { slug } = await params;
  const doc = DOCS[slug];
  if (!doc) notFound();

  return (
    <div className="mx-auto w-full max-w-[1400px] px-4 py-10 sm:px-6 lg:px-10">
      {/* URL backend strip */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-[12px] border border-lava-cloud bg-canvas-white px-4 py-3">
        <div className="flex flex-wrap items-center gap-2">
          <Server className="h-4 w-4 text-electric-violet" strokeWidth={1.5} />
          <span className="font-mono text-[12px] uppercase tracking-[0.12em] text-cloud-gray">
            API
          </span>
          <a
            href={`${API_URL}/docs`}
            target="_blank"
            rel="noreferrer"
            className="font-mono text-[13px] text-electric-violet hover:underline"
          >
            {API_URL}
          </a>
          <Badge variant="violet">Swagger UI</Badge>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-[8px] border border-lava-cloud px-3 py-1.5 font-mono text-[12px] text-deep-indigo transition-colors hover:bg-ghost-fill"
          >
            <Github className="h-3.5 w-3.5" strokeWidth={1.5} />
            Repo principal
            <ExternalLink className="h-3 w-3" strokeWidth={1.5} />
          </a>
          <a
            href={`${API_URL}/openapi.json`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-[8px] border border-lava-cloud px-3 py-1.5 font-mono text-[12px] text-deep-indigo transition-colors hover:bg-ghost-fill"
          >
            <Globe className="h-3.5 w-3.5" strokeWidth={1.5} />
            OpenAPI JSON
          </a>
        </div>
      </div>

      {/* Quick stats banner */}
      <div className="mb-8 grid grid-cols-2 gap-3 rounded-[12px] bg-pixel-pattern p-4 sm:grid-cols-4">
        {[
          { label: "Contratos", value: "1,003,902", icon: Database },
          { label: "Departamentos", value: "33", icon: Globe },
          { label: "Endpoints", value: "11", icon: FileCode },
          { label: "Páginas", value: "7", icon: Layers },
        ].map((s) => (
          <div key={s.label} className="rounded-[8px] bg-canvas-white px-3 py-2.5 shadow-[rgba(39,40,53,0.04)_0_0_0_1px]">
            <div className="flex items-center gap-2 text-cloud-gray">
              <s.icon className="h-3.5 w-3.5" strokeWidth={1.5} />
              <span className="font-mono text-[10px] uppercase tracking-wider">{s.label}</span>
            </div>
            <div className="mt-0.5 font-display text-[20px] font-semibold tracking-[-0.02em] text-midnight-ink">
              {s.value}
            </div>
          </div>
        ))}
      </div>

      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
        {/* Sidebar — width fija 220px, sticky con bg sólido */}
        <aside className="w-full shrink-0 lg:sticky lg:top-24 lg:z-10 lg:w-[220px]">
          <div className="rounded-[12px] border border-lava-cloud bg-canvas-white p-4 shadow-[rgba(39,40,53,0.04)_0_0_0_1px]">
            <div className="mb-3 flex items-center gap-2">
              <BookOpen className="h-3.5 w-3.5 text-cloud-gray" strokeWidth={1.5} />
              <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-cloud-gray">
                Docs
              </span>
            </div>
            <nav className="flex flex-col gap-1">
              {Object.entries(DOCS).map(([s, d]) => {
                const isActive = s === slug;
                return (
                  <Link
                    key={s}
                    href={`/docs/${s}`}
                    className={[
                      "inline-flex w-full items-center rounded-[8px] px-3 py-2 text-[13px] font-medium leading-tight transition-colors duration-150",
                      isActive
                        ? "bg-lavender-mist text-electric-violet"
                        : "text-deep-indigo hover:bg-ghost-fill",
                    ].join(" ")}
                    aria-current={isActive ? "page" : undefined}
                  >
                    {d.title}
                  </Link>
                );
              })}
            </nav>
            <div className="mt-4 space-y-1.5 border-t border-lava-cloud pt-3">
              <a
                href={`${API_URL}/docs`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 font-mono text-[11px] text-electric-violet hover:underline"
              >
                <ExternalLink className="h-3 w-3" strokeWidth={1.5} />
                Swagger UI
              </a>
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer"
                className="block font-mono text-[11px] text-cloud-gray hover:text-electric-violet"
              >
                ↗ GitHub
              </a>
              <a
                href={PEZ_GORDO_REPO}
                target="_blank"
                rel="noreferrer"
                className="block font-mono text-[11px] text-cloud-gray hover:text-electric-violet"
              >
                ↗ Pez Gordo
              </a>
            </div>
          </div>
        </aside>

        {/* Content */}
        <article className="prose prose-neutral max-w-none flex-1 min-w-0">
          <div className="card-simple">
            <ReactMarkdown
              components={{
                h1: (props) => <h1 className="text-heading-lg mb-4" {...props} />,
                h2: (props) => <h2 className="text-heading-sm mt-8 mb-3" {...props} />,
                h3: (props) => <h3 className="text-subheading mt-6 mb-2" {...props} />,
                p: (props) => <p className="text-body my-3 text-deep-indigo" {...props} />,
                ul: (props) => <ul className="list-disc space-y-1 pl-6 text-body text-deep-indigo" {...props} />,
                ol: (props) => <ol className="list-decimal space-y-1 pl-6 text-body text-deep-indigo" {...props} />,
                li: (props) => <li className="leading-relaxed" {...props} />,
                table: (props) => <div className="my-4 overflow-x-auto"><table className="w-full border-collapse text-[13px]" {...props} /></div>,
                thead: (props) => <thead className="border-b border-lava-cloud" {...props} />,
                th: (props) => <th className="px-3 py-2 text-left font-medium text-midnight-ink" {...props} />,
                td: (props) => <td className="border-b border-lava-cloud px-3 py-2 text-deep-indigo" {...props} />,
                code: ({ children, ...props }) => (
                  <code
                    className="rounded-[4px] bg-ghost-fill px-1.5 py-0.5 font-mono text-[12px] text-electric-violet"
                    {...props}
                  >
                    {children}
                  </code>
                ),
                pre: (props) => (
                  <pre
                    className="my-4 overflow-x-auto rounded-[8px] bg-midnight-ink p-4 font-mono text-[12px] text-white"
                    {...props}
                  />
                ),
                a: (props) => (
                  <a
                    className="text-electric-violet underline underline-offset-2"
                    target={props.href?.startsWith("http") ? "_blank" : undefined}
                    rel={props.href?.startsWith("http") ? "noreferrer" : undefined}
                    {...props}
                  />
                ),
                blockquote: (props) => (
                  <blockquote className="my-4 border-l-2 border-electric-violet bg-lavender-mist/30 px-4 py-2 italic text-deep-indigo" {...props} />
                ),
              }}
            >
              {doc.content}
            </ReactMarkdown>
          </div>
        </article>
      </div>
    </div>
  );
}
