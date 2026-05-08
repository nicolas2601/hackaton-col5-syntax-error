"use client";

import type { TooltipProps } from "recharts";

/** Lightdash-style tooltip for Recharts. */
export function LightdashTooltip({
  active,
  payload,
  label,
  formatter,
}: TooltipProps<number, string> & {
  formatter?: (v: number, name: string) => string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-[8px] border border-lava-cloud bg-canvas-white p-3 shadow-[rgba(0,0,0,0.06)_0_8px_20px]">
      {label && (
        <div className="mb-1 text-[11px] font-medium uppercase tracking-wide text-cloud-gray">
          {label}
        </div>
      )}
      <div className="flex flex-col gap-1">
        {payload.map((p, i) => (
          <div key={i} className="flex items-center gap-2 text-[12px]">
            <span
              className="h-2 w-2 rounded-full"
              style={{ background: (p.color as string) ?? "#5e4cff" }}
            />
            <span className="text-steel-gray">{p.name}:</span>
            <span className="font-mono font-medium text-midnight-ink">
              {formatter
                ? formatter(p.value as number, p.name as string)
                : (p.value as number).toLocaleString("es-CO")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
