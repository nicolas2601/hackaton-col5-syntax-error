import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { ExternalLink, Github, BookOpen, Server, Globe } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const API_URL = "https://api-ronda2.tikno.pro";
const API_LOCAL = "http://localhost:8000";
const REPO_URL = "https://github.com/nicolas2601/hackaton-col5-syntax-error";

const DOCS: Record<string, { title: string; content: string }> = {
  overview: {
    title: "Visión general",
    content: `
# Documentación SECOP II Dashboard

Plataforma de transparencia sobre la contratación pública colombiana, construida sobre el snapshot 2025 de SECOP II.

## Qué incluye

- **1.003.902 contratos** procesados y agregados (snapshot 2026-05-06)
- **33 departamentos** cubiertos con choropleth interactivo
- **12 endpoints REST** documentados con OpenAPI 3.1
- **Análisis IA** sobre anomalías y patrones (Pareto 7/80, brecha género, modalidades)
- **Brecha de género** sobre 997.847 contratos con representante legal definido
- **Curva de Pareto** sobre concentración de valor entre entidades
- **Top 10 valores anómalos** con clasificación VERIDICO/FALSO/REVISAR

## Stack técnico

- **Backend**: FastAPI + DuckDB sobre CSV (1.7GB, sin Postgres en dev)
- **Frontend**: Next.js 15 App Router + Tailwind v4 + shadcn/ui
- **Charts**: Recharts + react-simple-maps + Framer Motion
- **Deploy**: Coolify v4 + Cloudflare Tunnel + Traefik en self-hosted server

## Endpoints principales

\`\`\`bash
GET /api/v1/stats/total           # KPIs globales
GET /api/v1/departamentos/top     # Top 10 deptos
GET /api/v1/modalidades           # Modalidades de contratación
GET /api/v1/tipos-contrato        # Top 5 tipos
GET /api/v1/entidades/top         # Top 10 entidades por valor
GET /api/v1/temporal              # Distribución mensual
GET /api/v1/pareto/entidades      # Curva de Pareto
GET /api/v1/genero/brecha         # Brecha género (H/M/Otro)
GET /api/v1/anomalias             # Top 10 valores anómalos
GET /api/v1/mapa/deptos           # Choropleth Colombia
GET /docs                         # Swagger UI
\`\`\`

Cache HTTP de 60s. Rate limit 100 req/min/IP. CORS abierto para \`panel.tikno.pro\` y \`localhost:3000\`.

## Tiempos típicos de respuesta

| Endpoint | Latencia (p50) |
|---|---|
| \`/health\` | <5ms |
| \`/api/v1/stats/total\` | <10ms |
| \`/api/v1/anomalias\` | <20ms |
| \`/api/v1/mapa/deptos\` | <15ms |

Todas las agregaciones se pre-computan en startup con DuckDB sobre el CSV completo (~30s warmup), después se sirven desde memoria.
`,
  },
  api: {
    title: "Referencia API",
    content: `
# Referencia API

## Base URL

- **Producción**: \`https://api-ronda2.tikno.pro\`
- **Swagger UI**: \`https://api-ronda2.tikno.pro/docs\`
- **OpenAPI JSON**: \`https://api-ronda2.tikno.pro/openapi.json\`
- **Local dev**: \`http://localhost:8000\`

## Autenticación

Por ahora no requiere autenticación. Rate limit de 100 requests/min por IP.

## /api/v1/stats/total

Agregados globales del snapshot.

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

\`\`\`bash
curl https://api-ronda2.tikno.pro/api/v1/stats/total
\`\`\`

## /api/v1/departamentos/top

Top 15 deptos por número de contratos. Incluye valor agregado y porcentaje.

\`\`\`json
[
  { "departamento": "Distrito Capital de Bogotá", "contratos": 280248, "valor_total": 4.5e13, "pct": 27.92 },
  { "departamento": "Valle del Cauca", "contratos": 109856, "valor_total": 1.8e13, "pct": 10.94 }
]
\`\`\`

## /api/v1/pareto/entidades

Curva de Pareto: para cada rank, el porcentaje acumulado del valor total.

\`\`\`json
[
  { "rank": 1, "entidad": "DISTRITO ESPECIAL DE CTI MEDELLIN", "valor": 7.19e12, "pct_acumulado": 4.31 },
  { "rank": 7, "entidad": "DISTRITO ESPECIAL INDUSTRIAL Y PORTUARIO BARRANQUILLA", "valor": 2.37e12, "pct_acumulado": 80.0 }
]
\`\`\`

## /api/v1/anomalias

Top 10 valores con clasificación IA y sustento textual.

\`\`\`json
[
  {
    "id": "CO1.PCCNTR.123",
    "entidad": "MINISTERIO DE MINAS Y ENERGIA",
    "contratista": "GECELCA S.A. E.S.P.",
    "valor": 4.2e12,
    "modalidad": "Contratación directa",
    "fecha": "12/29/2025",
    "verdict": "VERIDICO",
    "sustento": "Programa Colombia Solar — fondo plurianual FENOGE/MME"
  }
]
\`\`\`

## /api/v1/genero/brecha

Stats por género de representante legal: H, M, Otro.

\`\`\`json
[
  { "genero": "M", "promedio": 141293990, "mediana": 20400000, "contratos": 378213 },
  { "genero": "F", "promedio": 84026115, "mediana": 18850000, "contratos": 434081 }
]
\`\`\`

## Headers CORS

\`\`\`
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, OPTIONS
Cache-Control: public, max-age=60
\`\`\`
`,
  },
  metodologia: {
    title: "Metodología",
    content: `
# Metodología

## Fuente de datos

Plataforma SECOP II del estado colombiano (datos abiertos de Colombia Compra Eficiente).
Snapshot oficial descargado el **2026-05-06** desde [datos.gov.co](https://www.datos.gov.co/Estad-sticas-Nacionales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h).

## Procesamiento

1. **Ingesta**: descarga CSV oficial (1.7GB, 84 columnas) — formato \`MM/DD/YYYY\` para fechas, \`$XX,XXX,XXX\` para montos.
2. **Limpieza**:
   - \`Valor del Contrato\` → \`REGEXP_REPLACE([$,], '')\` → \`DOUBLE\`
   - \`Fecha de Firma\` → \`STRPTIME('%m/%d/%Y')\` → \`DATE\`
   - Booleanos \`'Si'/'No'\` → \`BOOLEAN\`
   - Géneros \`'Hombre'/'Mujer'\` → \`'M'/'F'/'Otro'\`
3. **Agregación con DuckDB** sobre el CSV completo (sin Postgres en dev).
4. **Heurísticas**:
   - **Anomalía estadística**: top 10 valores absolutos del campo \`Valor del Contrato\`
   - **Concentración (Pareto)**: NTILE(5) sobre proveedores ordenados DESC por valor total. Top 20% controla 91.04% (incluso más extremo que 80/20).
   - **Brecha género**: ratio promedio_H / promedio_M = 1.68 (Hombre $141M vs Mujer $84M).
5. **Clasificación IA**: cada anomalía se evalúa con LLM (Claude / GPT) y se clasifica como
   \`VERIDICO\`, \`FALSO\` o \`REVISAR\` con sustento textual basado en:
   - Modalidad declarada vs. techo legal de esa modalidad
   - Tipo declarado vs. objeto del contrato
   - Histórico de la entidad
   - Coherencia entre Valor del Contrato vs Valor Pagado / Facturado

## Limitaciones

- El **18.67%** de los registros tiene \`Género Representante Legal = "No Definido"\` (mayoritariamente personas jurídicas).
- **5 columnas de fondos** vienen 100% null en el dataset oficial: PGN, SGP, Regalías, Recursos Propios, Recursos de Crédito.
- El sustento de cada anomalía es generado por IA y debe ser **validado por un humano** antes de tomar acción.
- El snapshot 2025 no incluye contratos plurianuales firmados antes de 2025 que aún están vigentes.

## Cumplimiento legal

- **Ley 1712/2014** (Transparencia y acceso a info pública): todos los datos consultados son públicos.
- **Ley 1581/2012** (Habeas Data): no se redistribuye PII identificable más allá de lo ya publicado.
- **Ley 1273/2009** (Delitos informáticos): la plataforma es **únicamente educativa**.
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
      <div className="mb-8 flex flex-wrap items-center justify-between gap-3 rounded-[12px] border border-lava-cloud bg-canvas-white px-4 py-3">
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
        <div className="flex items-center gap-2">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-[8px] border border-lava-cloud px-3 py-1.5 font-mono text-[12px] text-deep-indigo transition-colors hover:bg-ghost-fill"
          >
            <Github className="h-3.5 w-3.5" strokeWidth={1.5} />
            Código fuente
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

      <div className="grid gap-10 lg:grid-cols-[220px,1fr]">
        {/* Sidebar — sticky con bg sólido y z-index para evitar overlap al scroll */}
        <aside className="lg:sticky lg:top-24 lg:z-10 lg:self-start">
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
            <div className="mt-4 border-t border-lava-cloud pt-3">
              <a
                href={`${API_URL}/docs`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 font-mono text-[11px] text-electric-violet hover:underline"
              >
                <ExternalLink className="h-3 w-3" strokeWidth={1.5} />
                Swagger UI
              </a>
            </div>
          </div>
        </aside>

        {/* Content */}
        <article className="prose prose-neutral max-w-none">
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
                table: (props) => <table className="w-full border-collapse text-[13px]" {...props} />,
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
                    className="overflow-x-auto rounded-[8px] bg-midnight-ink p-4 font-mono text-[12px] text-white"
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
