"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TipoContratoStat } from "@/types";
import { LightdashTooltip } from "./recharts-tooltip";
import { formatInt, truncate } from "@/lib/utils";

const OPACITIES = [1, 0.85, 0.7, 0.55, 0.45];

export function TiposBar({ data }: { data: TipoContratoStat[] }) {
  // horizontal bar: categories on Y axis (better for long type names).
  const chartData = data.map((d) => ({
    ...d,
    tipoCorto: truncate(d.tipo, 22),
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 4, right: 16, bottom: 4, left: 4 }}
      >
        <CartesianGrid horizontal={false} stroke="#eceff3" />
        <XAxis
          type="number"
          tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          type="category"
          dataKey="tipoCorto"
          width={150}
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#36394a", fontSize: 12 }}
        />
        <Tooltip
          cursor={{ fill: "rgba(94, 76, 255, 0.06)" }}
          content={
            <LightdashTooltip
              formatter={(v) => `${formatInt(v)} contratos`}
            />
          }
          labelFormatter={(_, payload) => {
            const p = payload?.[0]?.payload as
              | { tipo?: string }
              | undefined;
            return p?.tipo ?? "";
          }}
        />
        <Bar dataKey="contratos" name="Contratos" radius={[0, 6, 6, 0]}>
          {chartData.map((_, i) => (
            <Cell
              key={i}
              fill="#5e4cff"
              fillOpacity={OPACITIES[i] ?? 0.4}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
