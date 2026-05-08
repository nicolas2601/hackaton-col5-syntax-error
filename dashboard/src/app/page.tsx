import Link from "next/link";
import { ArrowRight, Code2, Database, Sparkles, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ElevatedCard } from "@/components/elevated-card";
import { StatGrid } from "@/components/stat-grid";
import { api } from "@/lib/api";
import { HeroAnim, SectionFade } from "./_landing-anim";

// Render on-demand: si la API está caída, el error sube al boundary
// (no queremos prerender estático con datos potencialmente vacíos).
export const dynamic = "force-dynamic";
export const revalidate = 60;

export default async function LandingPage() {
  const stats = await api.statsTotal();

  return (
    <>
      {/* HERO */}
      <section className="relative isolate overflow-hidden bg-canvas-white">
        <div className="absolute inset-0 bg-pixel-fade opacity-60" aria-hidden />
        <div className="absolute inset-x-0 top-0 -z-10 h-[420px] bg-gradient-to-b from-transparent via-lavender-mist/15 to-transparent" />

        <div className="mx-auto max-w-[1400px] px-4 pb-24 pt-20 sm:px-6 sm:pt-28 lg:px-8">
          <HeroAnim>
            <div className="mx-auto max-w-3xl text-center">
              <span className="pill pill-violet mx-auto inline-flex">
                <Sparkles className="h-3 w-3" /> Hackathon Colombia 5.0
              </span>
              <h1 className="text-display mt-6 text-center">
                Transparencia
                <br />
                <span className="text-electric-violet">SECOP II</span>
              </h1>
              <p className="mt-6 text-[18px] leading-[1.5] text-steel-gray">
                Un millón de contratos públicos analizados con IA. Detecta concentración
                de mercado, brechas de género, anomalías estadísticas y patrones de
                contratación directa, todo en una vista unificada.
              </p>

              <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Button variant="primary" size="lg" asChild>
                  <Link href="/dashboard">
                    Ver Dashboard
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
                <Button variant="ghost" size="lg" asChild>
                  <a
                    href="https://api-ronda2.tikno.pro/docs"
                    target="_blank"
                    rel="noreferrer"
                  >
                    API Docs
                  </a>
                </Button>
              </div>

              <p className="mt-6 text-mono text-cloud-gray">
                Datos públicos · ColombiaCompra · 1.000.000 registros · 33 deptos
              </p>
            </div>
          </HeroAnim>

          <div className="mt-16">
            <StatGrid stats={stats} />
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <SectionFade>
        <section className="bg-off-white py-20 sm:py-24">
          <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <span className="text-mono uppercase tracking-wider text-electric-violet">
                · Plataforma
              </span>
              <h2 className="text-heading-lg mt-4">
                Todo lo que necesitás para auditar la contratación pública
              </h2>
              <p className="mt-4 text-body text-steel-gray">
                API REST con 12 endpoints, dashboard interactivo y un asistente
                IA que explica cada anomalía en lenguaje natural.
              </p>
            </div>

            <div className="mt-12 grid gap-6 md:grid-cols-3">
              <ElevatedCard
                icon={<Code2 className="h-5 w-5" strokeWidth={1.6} />}
                title="API REST"
                description="12 endpoints documentados, OpenAPI 3.1, rate limit y cache. Listo para integrar a cualquier dashboard o BI tool."
                delay={0}
              />
              <ElevatedCard
                icon={<BarChart3 className="h-5 w-5" strokeWidth={1.6} />}
                title="Dashboard interactivo"
                description="13 visualizaciones bento-grid: choropleth, treemap, Pareto, brecha de género y anomalías top-20 con sustento."
                delay={0.1}
              />
              <ElevatedCard
                icon={<Database className="h-5 w-5" strokeWidth={1.6} />}
                title="Análisis IA"
                description="Heurísticas estadísticas + LLM para clasificar cada anomalía como verídica, falsa o por revisar — con sustento en lenguaje natural."
                delay={0.2}
              />
            </div>
          </div>
        </section>
      </SectionFade>

      {/* CTA strip */}
      <section className="border-y border-lava-cloud bg-canvas-white py-16">
        <div className="mx-auto flex max-w-[1400px] flex-col items-start justify-between gap-6 px-4 sm:flex-row sm:items-center sm:px-6 lg:px-8">
          <div>
            <h3 className="text-heading-sm">¿Listo para explorar los datos?</h3>
            <p className="mt-2 text-[14px] text-steel-gray">
              Abrí el dashboard y empezá a auditar 1M de contratos en menos de un segundo.
            </p>
          </div>
          <Button variant="primary" size="lg" asChild>
            <Link href="/dashboard">
              Abrir dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>
    </>
  );
}
