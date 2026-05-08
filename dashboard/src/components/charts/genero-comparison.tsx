"use client";

import { motion } from "framer-motion";
import type { BrechaGenero } from "@/types";
import { formatCOP } from "@/lib/utils";

const LABEL: Record<BrechaGenero["genero"], string> = {
  M: "Masculino",
  F: "Femenino",
  Otro: "Otro",
};

/**
 * Dumbbell chart: por cada género, marca Promedio + Mediana sobre un
 * track horizontal con el rango global. Mejor que un bar pair para
 * visualizar la brecha relativa entre M / F / Otro.
 */
export function GeneroComparison({ data }: { data: BrechaGenero[] }) {
  if (!data?.length) return null;

  const allValues = data.flatMap((d) => [d.promedio, d.mediana]);
  const min = Math.min(...allValues);
  const max = Math.max(...allValues);
  const range = max - min || 1;

  const m = data.find((d) => d.genero === "M");
  const f = data.find((d) => d.genero === "F");
  const brecha =
    m && f && m.promedio > 0
      ? ((m.promedio - f.promedio) / m.promedio) * 100
      : null;

  return (
    <div className="flex h-full w-full flex-col justify-center gap-5 px-2 py-3">
      {data.map((d, i) => {
        const promPos = ((d.promedio - min) / range) * 100;
        const medPos = ((d.mediana - min) / range) * 100;
        const left = Math.min(promPos, medPos);
        const right = Math.max(promPos, medPos);
        return (
          <div key={d.genero}>
            <div className="mb-2 flex items-center justify-between text-[12px]">
              <span className="font-medium text-midnight-ink">
                {LABEL[d.genero]}
              </span>
              <span className="font-mono text-[11px] text-cloud-gray">
                {d.contratos.toLocaleString("es-CO")} contratos
              </span>
            </div>
            <div className="relative h-6">
              {/* track */}
              <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-lava-cloud" />
              {/* connector */}
              <motion.div
                initial={{ width: 0, left: `${left}%` }}
                whileInView={{ width: `${right - left}%`, left: `${left}%` }}
                viewport={{ once: true, margin: "-30px" }}
                transition={{ duration: 0.5, delay: i * 0.06 }}
                className="absolute top-1/2 h-[3px] -translate-y-1/2 rounded-full bg-electric-violet/30"
              />
              {/* mediana dot — light */}
              <motion.div
                initial={{ scale: 0, left: `${medPos}%` }}
                whileInView={{ scale: 1, left: `${medPos}%` }}
                viewport={{ once: true, margin: "-30px" }}
                transition={{ duration: 0.4, delay: i * 0.06 + 0.1 }}
                className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-[2px] border-pixel-purple bg-canvas-white"
                title={`Mediana: ${formatCOP(d.mediana, { compact: true })}`}
              />
              {/* promedio dot — solid violet */}
              <motion.div
                initial={{ scale: 0, left: `${promPos}%` }}
                whileInView={{ scale: 1, left: `${promPos}%` }}
                viewport={{ once: true, margin: "-30px" }}
                transition={{ duration: 0.4, delay: i * 0.06 + 0.15 }}
                className="absolute top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-electric-violet shadow-[0_0_0_3px_rgba(94,76,255,0.18)]"
                title={`Promedio: ${formatCOP(d.promedio, { compact: true })}`}
              />
            </div>
            <div className="mt-1.5 flex items-center justify-between font-mono text-[11px]">
              <span className="text-cloud-gray">
                <span className="mr-1.5 inline-block h-2 w-2 rounded-full border-2 border-pixel-purple bg-canvas-white align-middle" />
                Med: {formatCOP(d.mediana, { compact: true })}
              </span>
              <span className="text-deep-indigo">
                <span className="mr-1.5 inline-block h-2 w-2 rounded-full bg-electric-violet align-middle" />
                Prom: {formatCOP(d.promedio, { compact: true })}
              </span>
            </div>
          </div>
        );
      })}

      {brecha !== null && (
        <div className="mt-1 inline-flex w-fit items-center gap-1.5 self-start rounded-full bg-lavender-mist px-3 py-1 font-mono text-[11px] text-electric-violet">
          <span>brecha M → F</span>
          <span className="font-semibold">+{brecha.toFixed(1)}%</span>
        </div>
      )}
    </div>
  );
}
