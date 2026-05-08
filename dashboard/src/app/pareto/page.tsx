import { api } from "@/lib/api";
import { ChartShell } from "@/components/charts/chart-shell";
import { ParetoCurve } from "@/components/charts/pareto-curve";
import { Badge } from "@/components/ui/badge";
import { formatCOP } from "@/lib/utils";

export const dynamic = "force-dynamic";
export const revalidate = 60;

export default async function ParetoPage() {
  const [pareto, entidades, stats] = await Promise.all([
    api.pareto(),
    api.entidadesTop(),
    api.statsTotal(),
  ]);

  const totalValorAprox = stats.total_valor || 1;

  return (
    <div className="mx-auto w-full max-w-[1600px] px-4 py-10 sm:px-6 lg:px-10">
      <header className="mb-8">
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-cloud-gray">
          · Concentración
        </span>
        <h1 className="text-heading mt-2">Curva de Pareto</h1>
        <p className="mt-2 max-w-2xl text-body text-steel-gray">
          Solo {stats.pareto_entidades} entidades concentran el {stats.pareto_pct_valor}% del valor total
          contratado. La curva muestra el principio 80/20 aplicado a la contratación pública colombiana.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="violet">
            {stats.pareto_entidades} / {stats.pareto_pct_valor}% · Pareto fuerte
          </Badge>
          <Badge variant="outline">Top 80 entidades cubren 100%</Badge>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ChartShell
          title="Curva acumulada"
          hint="% acumulado de valor contractual por top N entidades"
          className="lg:col-span-2"
          height={460}
        >
          <ParetoCurve data={pareto} />
        </ChartShell>

        <section className="card-simple lg:col-span-1">
          <header className="mb-4 flex items-center justify-between">
            <h3 className="text-subheading">Top 10 entidades</h3>
            <Badge variant="outline">{entidades.length} totales</Badge>
          </header>
          <ul className="flex flex-col gap-2.5">
            {entidades.slice(0, 10).map((e, i) => {
              const pct = (e.valor_total / totalValorAprox) * 100;
              return (
                <li
                  key={e.entidad}
                  className="rounded-[10px] bg-ghost-fill p-3"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="inline-flex h-5 shrink-0 items-center justify-center rounded-full bg-canvas-white px-2 font-mono text-[10px] font-semibold text-midnight-ink shadow-[rgba(39,40,53,0.08)_0_0_0_1px]">
                      #{i + 1}
                    </span>
                    <Badge variant="violet" className="shrink-0">
                      {pct.toFixed(1)}%
                    </Badge>
                  </div>
                  <div className="mt-1.5 line-clamp-2 text-[12px] font-medium leading-tight text-midnight-ink">
                    {e.entidad}
                  </div>
                  <div className="mt-1 font-mono text-[11px] text-steel-gray">
                    {formatCOP(e.valor_total, { compact: true })}
                  </div>
                </li>
              );
            })}
          </ul>
          {entidades.length > 10 && (
            <p className="mt-3 text-center font-mono text-[11px] text-cloud-gray">
              +{entidades.length - 10} entidades adicionales
            </p>
          )}
        </section>

        {/* Insights row */}
        <div className="grid grid-cols-1 gap-4 lg:col-span-3 lg:grid-cols-3">
          <Insight
            title="Concentración alta"
            value={`${stats.pareto_entidades}`}
            hint={`entidades cubren ${stats.pareto_pct_valor}% del valor`}
          />
          <Insight
            title="Cola larga"
            value="73"
            hint="entidades pequeñas suman el restante 20%"
          />
          <Insight
            title="Riesgo sistémico"
            value="ALTO"
            hint="Concentración crítica en pocos actores estatales"
            danger
          />
        </div>
      </div>
    </div>
  );
}

function Insight({
  title,
  value,
  hint,
  danger = false,
}: {
  title: string;
  value: string;
  hint: string;
  danger?: boolean;
}) {
  return (
    <div className="card-simple">
      <div className="font-mono text-[11px] uppercase tracking-[0.14em] text-cloud-gray">
        {title}
      </div>
      <div
        className={`mt-2 font-display text-[36px] font-semibold leading-none tracking-[-0.02em] ${
          danger ? "text-rose-600" : "text-electric-violet"
        }`}
      >
        {value}
      </div>
      <div className="mt-2 text-[12px] text-steel-gray">{hint}</div>
    </div>
  );
}
