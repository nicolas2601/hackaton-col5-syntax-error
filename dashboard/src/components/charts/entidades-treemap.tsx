"use client";

import { ResponsiveContainer, Tooltip, Treemap } from "recharts";
import type { EntidadTop } from "@/types";
import { LightdashTooltip } from "./recharts-tooltip";
import { formatCOP } from "@/lib/utils";

const COLORS = ["#5e4cff", "#9089ff", "#c8ccf3"];

interface ContentProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  name?: string;
  value?: number;
  index?: number;
}

const ContentRenderer = ({ x = 0, y = 0, width = 0, height = 0, name = "", index = 0, value = 0 }: ContentProps) => (
  <g>
    <rect
      x={x}
      y={y}
      width={width}
      height={height}
      style={{
        fill: COLORS[index % COLORS.length],
        stroke: "#fff",
        strokeWidth: 2,
      }}
    />
    {width > 90 && height > 36 && (
      <>
        <text x={x + 12} y={y + 22} fill="#fff" fontSize={12} fontWeight={600}>
          {name}
        </text>
        <text x={x + 12} y={y + 38} fill="#fff" fontSize={11} opacity={0.85}>
          {formatCOP(value, { compact: true })}
        </text>
      </>
    )}
  </g>
);

export function EntidadesTreemap({ data }: { data: EntidadTop[] }) {
  const treeData = data.map((d) => ({ name: d.entidad, size: d.valor_total, valor: d.valor_total }));
  return (
    <ResponsiveContainer width="100%" height="100%">
      <Treemap
        data={treeData}
        dataKey="size"
        stroke="#fff"
        content={<ContentRenderer />}
      >
        <Tooltip
          content={
            <LightdashTooltip
              formatter={(v) => formatCOP(v, { compact: true })}
            />
          }
        />
      </Treemap>
    </ResponsiveContainer>
  );
}
