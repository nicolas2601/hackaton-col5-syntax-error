import { MapPin } from "lucide-react";
import { api } from "@/lib/api";
import { ColombiaMap } from "@/components/colombia-map";
import { Badge } from "@/components/ui/badge";
import { formatCOP, formatInt } from "@/lib/utils";

export const dynamic = "force-dynamic";
export const revalidate = 60;

export default async function MapaPage() {
  const data = await api.mapaDeptos();
  const sorted = [...data].sort((a, b) => b.contratos - a.contratos);
  const total = data.reduce((acc, d) => acc + d.contratos, 0);
  const totalValor = data.reduce((acc, d) => acc + d.valor_total, 0);

  return (
    <div className="mx-auto w-full max-w-[1600px] px-4 py-10 sm:px-6 lg:px-10">
      <header className="mb-8">
        <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-cloud-gray">
          · Geografía
        </span>
        <h1 className="text-heading mt-2">Mapa de Colombia</h1>
        <p className="mt-2 max-w-2xl text-body text-steel-gray">
          Choropleth de contratos por departamento. Pasá el mouse sobre cada zona
          para ver el detalle.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        {/* Map: portrait aspect ratio */}
        <section className="card-simple lg:col-span-8">
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="grid h-7 w-7 place-items-center rounded-[8px] bg-ghost-fill text-deep-indigo">
                <MapPin className="h-4 w-4" strokeWidth={1.5} />
              </span>
              <h3 className="text-subheading">Distribución geográfica</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="violet">{formatInt(total)} contratos</Badge>
              <Badge variant="outline">
                {formatCOP(totalValor, { compact: true })}
              </Badge>
            </div>
          </div>
          {/* Aspect-ratio portrait para que el mapa de Colombia no se aplaste */}
          <div className="relative aspect-[3/4] w-full max-h-[640px] mx-auto">
            <ColombiaMap data={data} />
          </div>
        </section>

        {/* Side ranking */}
        <aside className="card-simple lg:col-span-4">
          <h3 className="text-subheading mb-4">Top departamentos</h3>
          <ul className="space-y-2">
            {sorted.slice(0, 12).map((d, i) => {
              const pct = (d.contratos / total) * 100;
              return (
                <li
                  key={d.codigo}
                  className="rounded-[8px] p-2 transition-colors hover:bg-ghost-fill"
                >
                  <div className="flex items-baseline justify-between gap-2">
                    <div className="flex min-w-0 items-center gap-2">
                      <span className="font-mono text-[11px] text-cloud-gray">
                        {(i + 1).toString().padStart(2, "0")}
                      </span>
                      <span className="truncate text-[13px] font-medium text-midnight-ink">
                        {d.nombre}
                      </span>
                    </div>
                    <span className="shrink-0 font-mono text-[12px] text-deep-indigo">
                      {formatInt(d.contratos)}
                    </span>
                  </div>
                  <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-lava-cloud">
                    <div
                      className="h-full rounded-full bg-electric-violet transition-[width] duration-500"
                      style={{ width: `${Math.min(100, pct * 4)}%` }}
                    />
                  </div>
                  <div className="mt-1 flex items-center justify-between font-mono text-[11px] text-steel-gray">
                    <span>{pct.toFixed(2)}%</span>
                    <span>
                      {formatCOP(d.valor_total, { compact: true })}
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>
        </aside>
      </div>
    </div>
  );
}
