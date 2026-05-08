import { Layers3, Building2, Zap, TrendingUp } from "lucide-react";
import { KpiCard } from "@/components/kpi-card";
import { formatInt, formatPct } from "@/lib/utils";
import type { StatsTotal } from "@/types";

interface StatGridProps {
  stats: StatsTotal;
}

/** 4-up KPI grid used on landing + dashboard. */
export function StatGrid({ stats }: StatGridProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <KpiCard
        label="Total registros"
        value={`${(stats.total_registros / 1_000_000).toFixed(1)}M`}
        hint="Contratos SECOP II analizados"
        icon={<Layers3 className="h-4 w-4" strokeWidth={1.5} />}
        accent
        delay={0}
      />
      <KpiCard
        label="Pymes"
        value={formatPct(stats.pct_pymes)}
        hint={`${formatInt(stats.total_pymes)} contratos a Pymes`}
        icon={<Building2 className="h-4 w-4" strokeWidth={1.5} />}
        delay={0.05}
      />
      <KpiCard
        label="Contratación directa"
        value={formatPct(stats.pct_directa)}
        hint={`${formatInt(stats.total_directa)} contratos sin licitación`}
        icon={<Zap className="h-4 w-4" strokeWidth={1.5} />}
        delay={0.1}
      />
      <KpiCard
        label="Pareto entidades"
        value={`${stats.pareto_entidades}/${stats.pareto_pct_valor}`}
        hint={`${stats.pareto_entidades} entidades concentran ${stats.pareto_pct_valor}% del valor`}
        icon={<TrendingUp className="h-4 w-4" strokeWidth={1.5} />}
        delay={0.15}
      />
    </div>
  );
}
