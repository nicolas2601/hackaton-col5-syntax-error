import { api } from "@/lib/api";
import { ChartShell } from "@/components/charts/chart-shell";
import { GeneroComparison } from "@/components/charts/genero-comparison";
import { KpiCard } from "@/components/kpi-card";
import { Badge } from "@/components/ui/badge";
import { Users2 } from "lucide-react";
import { formatCOP, formatInt, formatPct } from "@/lib/utils";

export const dynamic = "force-dynamic";
export const revalidate = 60;

export default async function GeneroPage() {
  const data = await api.brechaGenero();
  const m = data.find((d) => d.genero === "M");
  const f = data.find((d) => d.genero === "F");

  const brechaProm =
    m && f && m.promedio > 0 ? ((m.promedio - f.promedio) / m.promedio) * 100 : 0;
  const brechaMed =
    m && f && m.mediana > 0 ? ((m.mediana - f.mediana) / m.mediana) * 100 : 0;
  const totalContratos = data.reduce((s, d) => s + d.contratos, 0);
  const pctF = f ? (f.contratos / totalContratos) * 100 : 0;

  return (
    <div className="mx-auto w-full max-w-[1600px] px-4 py-10 sm:px-6 lg:px-10">
      <header className="mb-8">
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-cloud-gray">
          · Equidad
        </span>
        <h1 className="text-heading mt-2">Brecha de género</h1>
        <p className="mt-2 max-w-2xl text-body text-steel-gray">
          Comparación de valor promedio y mediana por género del contratista. Análisis sobre
          contratos donde se identificó el género de la persona natural beneficiaria.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Brecha promedio"
          value={formatPct(brechaProm)}
          hint="M vs F · valor promedio"
          icon={<Users2 className="h-4 w-4" strokeWidth={1.5} />}
          accent
        />
        <KpiCard
          label="Brecha mediana"
          value={formatPct(brechaMed)}
          hint="M vs F · valor mediano"
          delay={0.05}
        />
        <KpiCard
          label="Contratos a mujeres"
          value={formatPct(pctF)}
          hint={`${formatInt(f?.contratos ?? 0)} contratos`}
          delay={0.1}
        />
        <KpiCard
          label="Promedio M"
          value={formatCOP(m?.promedio ?? 0, { compact: true })}
          hint={`${formatInt(m?.contratos ?? 0)} contratos`}
          delay={0.15}
        />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <ChartShell
          title="Promedio vs Mediana"
          hint="Dumbbell por género del contratista"
          className="lg:col-span-2"
          height={360}
        >
          <GeneroComparison data={data} />
        </ChartShell>

        <section className="card-simple lg:col-span-1">
          <h3 className="text-subheading mb-4">Detalle por género</h3>
          <ul className="space-y-3">
            {data.map((d) => (
              <li
                key={d.genero}
                className="rounded-[8px] bg-ghost-fill p-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[13px] font-medium text-midnight-ink">
                    {d.genero === "M"
                      ? "Masculino"
                      : d.genero === "F"
                        ? "Femenino"
                        : "Otro"}
                  </span>
                  <Badge
                    variant={
                      d.genero === "M"
                        ? "violet"
                        : d.genero === "F"
                          ? "outline"
                          : "default"
                    }
                  >
                    {formatInt(d.contratos)}
                  </Badge>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-[12px]">
                  <div>
                    <div className="text-cloud-gray">Promedio</div>
                    <div className="font-mono text-midnight-ink">
                      {formatCOP(d.promedio, { compact: true })}
                    </div>
                  </div>
                  <div>
                    <div className="text-cloud-gray">Mediana</div>
                    <div className="font-mono text-midnight-ink">
                      {formatCOP(d.mediana, { compact: true })}
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
