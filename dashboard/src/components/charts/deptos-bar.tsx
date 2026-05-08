"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";
import type { DepartamentoTop } from "@/types";
import { LightdashTooltip } from "./recharts-tooltip";
import { formatInt } from "@/lib/utils";

interface Props {
  data: DepartamentoTop[];
}

const COLORS = ["#5e4cff", "#7669ff", "#9089ff", "#a4abb8", "#c8ccf3"];

export function DeptosBar({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 0, left: 4 }}>
        <CartesianGrid horizontal={false} stroke="#eceff3" />
        <XAxis
          type="number"
          tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          type="category"
          dataKey="departamento"
          width={120}
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
        />
        <Bar dataKey="contratos" name="Contratos" radius={[0, 6, 6, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length] ?? "#5e4cff"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
