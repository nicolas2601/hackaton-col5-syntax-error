"use client";

import type { ModalidadStat } from "@/types";
import { formatPct, formatInt, truncate } from "@/lib/utils";
import { motion } from "framer-motion";

interface Props {
  data: ModalidadStat[];
}

const PALETTE = ["#5e4cff", "#7669ff", "#9089ff", "#c8ccf3", "#dfdbff"];

/**
 * Top 5 modalidades como horizontal bar list — más legible que un pie
 * para nombres largos. Cada fila: dot + nombre truncado + barra + pct.
 */
export function ModalidadesPie({ data }: Props) {
  const top = data.slice(0, 5);
  const max = Math.max(...top.map((d) => d.pct), 1);

  return (
    <div className="flex h-full w-full flex-col justify-center gap-3 px-1 py-2">
      {top.map((d, i) => {
        const color = PALETTE[i % PALETTE.length];
        const widthPct = (d.pct / max) * 100;
        return (
          <div key={d.modalidad} className="group">
            <div className="flex items-center justify-between gap-2 text-[12px]">
              <div className="flex min-w-0 items-center gap-2">
                <span
                  className="h-2 w-2 shrink-0 rounded-full"
                  style={{ background: color }}
                />
                <span
                  className="truncate font-medium text-midnight-ink"
                  title={d.modalidad}
                >
                  {truncate(d.modalidad, 28)}
                </span>
              </div>
              <span className="shrink-0 font-mono text-[11px] text-deep-indigo">
                {formatPct(d.pct)}
              </span>
            </div>
            <div className="relative mt-1.5 h-1.5 overflow-hidden rounded-full bg-lava-cloud">
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width: `${widthPct}%` }}
                viewport={{ once: true, margin: "-30px" }}
                transition={{
                  duration: 0.5,
                  delay: i * 0.05,
                  ease: [0.22, 1, 0.36, 1],
                }}
                className="h-full rounded-full"
                style={{ background: color }}
              />
            </div>
            <div className="mt-1 font-mono text-[10px] text-cloud-gray">
              {formatInt(d.contratos)} contratos
            </div>
          </div>
        );
      })}
    </div>
  );
}
