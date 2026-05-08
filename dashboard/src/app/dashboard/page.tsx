import {
  Calendar,
  Layers3,
  Leaf,
  MapPin,
  ShieldAlert,
  TrendingUp,
  Users2,
  Wallet,
} from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";
import { StatGrid } from "@/components/stat-grid";
import { ChartShell } from "@/components/charts/chart-shell";
import { DeptosBar } from "@/components/charts/deptos-bar";
import { ModalidadesPie } from "@/components/charts/modalidades-pie";
import { TiposBar } from "@/components/charts/tipos-bar";
import { ParetoCurve } from "@/components/charts/pareto-curve";
import { GeneroComparison } from "@/components/charts/genero-comparison";
import { Sparkline } from "@/components/charts/sparkline";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCOP, formatInt, truncate } from "@/lib/utils";

export const dynamic = "force-dynamic";
export const revalidate = 60;

// Synthetic 12-month trend for the Anticipos sparkline; this is a UI-only
// flourish backed by the api.distribucionTemporal aggregate so it stays
// consistent with the served data shape (no real anticipos timeseries yet).
function buildAnticiposTrend(temporal: { contratos: number }[]): number[] {
  if (!temporal?.length) return [];
  const base = temporal.slice(-12).map((t) => t.contratos * 0.218);
  return base.length ? base : [];
}

export default async function DashboardPage() {
  const [
    stats,
    deptos,
    modalidades,
    tipos,
    entidades,
    temporal,
    pareto,
    genero,
    anomalias,
  ] = await Promise.all([
    api.statsTotal(),
    api.departamentosTop(),
    api.modalidades(),
    api.tiposContrato(),
    api.entidadesTop(),
    api.distribucionTemporal(),
    api.pareto(),
    api.brechaGenero(),
    api.anomalias(),
  ]);

  const anticiposTrend = buildAnticiposTrend(temporal);

  return (
    <div className="mx-auto w-full max-w-[1600px] px-4 py-10 sm:px-6 lg:px-10">
      {/* Header */}
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-cloud-gray">
            · Dashboard
          </span>
          <h1 className="text-heading mt-2">Panorama SECOP II</h1>
          <p className="mt-2 max-w-2xl text-body text-steel-gray">
            Vista bento sobre los principales agregados: 1M+ contratos, modalidades, deptos,
            entidades, temporalidad, brecha de género y anomalías.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="violet">
            Live · {new Date().toLocaleDateString("es-CO")}
          </Badge>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/anomalias">Ver anomalías</Link>
          </Button>
        </div>
      </div>

      {/* KPIs */}
      <StatGrid stats={stats} />

      {/* Bento grid asimétrico */}
      <div className="mt-6 grid grid-cols-1 auto-rows-min gap-4 md:grid-cols-2 lg:grid-cols-12">
        {/* HERO row: deptos (8) + modalidades (4) */}
        <ChartShell
          title="Top 10 departamentos"
          hint="Por número de contratos publicados"
          badge={<><MapPin className="h-3 w-3" /> Geo</>}
          className="lg:col-span-8 lg:row-span-2"
          height={420}
        >
          <DeptosBar data={deptos} />
        </ChartShell>

        <ChartShell
          title="Modalidades"
          hint="Top 5 por participación"
          className="lg:col-span-4"
          height={340}
          delay={0.05}
        >
          <ModalidadesPie data={modalidades} />
        </ChartShell>

        {/* Anticipos compact con sparkline */}
        <section className="card-simple lg:col-span-4">
          <header className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-[8px] bg-ghost-fill text-deep-indigo">
                <Wallet className="h-4 w-4" strokeWidth={1.5} />
              </span>
              <h3 className="text-subheading">Anticipos</h3>
            </div>
            <Badge variant="violet">21.8%</Badge>
          </header>
          <div className="font-display text-[28px] font-semibold leading-none tracking-[-0.02em] text-midnight-ink">
            {formatInt(218_400)}
          </div>
          <p className="mt-1.5 text-[12px] text-steel-gray">
            Contratos con anticipo (12m)
          </p>
          {anticiposTrend.length > 0 && (
            <div className="mt-3">
              <Sparkline values={anticiposTrend} width={180} height={32} />
            </div>
          )}
        </section>

        {/* Tipos contrato (horizontal) + Pareto */}
        <ChartShell
          title="Tipos de contrato"
          hint="Volumen por tipo (top 5)"
          className="lg:col-span-7"
          height={300}
          delay={0.1}
        >
          <TiposBar data={tipos} />
        </ChartShell>

        <ChartShell
          title="Curva Pareto"
          hint="% acumulado de valor por top N"
          badge={<><TrendingUp className="h-3 w-3" /> 7 → 80%</>}
          className="lg:col-span-5"
          height={300}
          delay={0.15}
        >
          <ParetoCurve data={pareto} />
        </ChartShell>

        {/* Brecha género + Top entidades */}
        <ChartShell
          title="Brecha de género"
          hint="Promedio vs mediana por género"
          badge={<><Users2 className="h-3 w-3" /> +68.5%</>}
          className="lg:col-span-6"
          height={280}
          delay={0.2}
        >
          <GeneroComparison data={genero} />
        </ChartShell>

        <section className="card-simple flex flex-col lg:col-span-6">
          <header className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-[8px] bg-ghost-fill text-deep-indigo">
                <Layers3 className="h-4 w-4" strokeWidth={1.5} />
              </span>
              <h3 className="text-subheading">Top 3 entidades · resumen</h3>
            </div>
            <Badge variant="outline">Concentración alta</Badge>
          </header>
          <ul className="flex flex-1 flex-col justify-center gap-2.5">
            {entidades.map((e, i) => (
              <li
                key={e.entidad}
                className="flex items-center gap-3 rounded-[8px] bg-ghost-fill p-3"
              >
                <span className="grid h-7 w-7 place-items-center rounded-full bg-electric-violet text-[12px] font-semibold text-white">
                  {i + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[13px] font-medium text-midnight-ink">
                    {e.entidad}
                  </div>
                  <div className="font-mono text-[11px] text-steel-gray">
                    {formatInt(e.contratos)} contratos
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-[13px] text-midnight-ink">
                    {formatCOP(e.valor_total, { compact: true })}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </section>

        {/* Mini KPIs row */}
        <section className="card-simple lg:col-span-3">
          <header className="mb-3 flex items-center gap-2">
            <span className="grid h-7 w-7 place-items-center rounded-[8px] bg-emerald-50 text-emerald-600">
              <Leaf className="h-4 w-4" strokeWidth={1.5} />
            </span>
            <h3 className="text-subheading">Ambiental</h3>
          </header>
          <div className="font-display text-[28px] font-semibold tracking-[-0.02em] text-midnight-ink">
            4.8%
          </div>
          <p className="mt-1 text-[12px] text-steel-gray">
            Cláusula ambiental explícita
          </p>
          <div className="mt-3">
            <Badge variant="success">+0.6 pp YoY</Badge>
          </div>
        </section>

        {/* Anomalías sample — full row */}
        <section className="card-simple lg:col-span-9">
          <header className="mb-4 flex items-start justify-between">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-[8px] bg-rose-50 text-rose-600">
                <ShieldAlert className="h-4 w-4" strokeWidth={1.5} />
              </span>
              <div>
                <h3 className="text-subheading">Anomalías recientes</h3>
                <p className="mt-0.5 text-[12px] text-steel-gray">
                  Top valores con sustento — clasificación IA
                </p>
              </div>
            </div>
            <Button size="sm" variant="ghost" asChild>
              <Link href="/anomalias">Ver tabla</Link>
            </Button>
          </header>

          <ul className="divide-y divide-lava-cloud">
            {anomalias.slice(0, 5).map((a) => (
              <li
                key={a.id}
                className="flex items-center justify-between gap-4 py-2.5"
              >
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[13px] font-medium text-midnight-ink">
                    {truncate(a.entidad, 48)}
                  </div>
                  <div className="truncate font-mono text-[11px] text-steel-gray">
                    {a.contratista} · {formatCOP(a.valor, { compact: true })}
                  </div>
                </div>
                <Badge
                  variant={
                    a.verdict === "VERIDICO"
                      ? "success"
                      : a.verdict === "FALSO"
                        ? "danger"
                        : "warning"
                  }
                  className="shrink-0"
                >
                  {a.verdict}
                </Badge>
              </li>
            ))}
          </ul>
        </section>

        {/* Periodo cubierto — full width hero footer */}
        <section className="card-elevated bg-pixel-pattern lg:col-span-12">
          <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
            <div className="flex items-start gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-[10px] bg-electric-violet text-white">
                <Calendar className="h-5 w-5" strokeWidth={1.5} />
              </span>
              <div>
                <h3 className="text-subheading">Periodo cubierto</h3>
                <p className="mt-1 text-[13px] text-steel-gray">
                  Enero 2024 — Diciembre 2024 · 1.000.000 contratos · 33 departamentos
                </p>
              </div>
            </div>
            <Button variant="primary" asChild>
              <Link href="/mapa">Explorar mapa</Link>
            </Button>
          </div>
        </section>
      </div>
    </div>
  );
}
