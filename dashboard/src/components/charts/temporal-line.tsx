"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DistribucionTemporal } from "@/types";
import { LightdashTooltip } from "./recharts-tooltip";
import { formatInt } from "@/lib/utils";

export function TemporalLine({ data }: { data: DistribucionTemporal[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data} margin={{ top: 4, right: 12, bottom: 4, left: 0 }}>
        <defs>
          <linearGradient id="g-temporal" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#5e4cff" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#5e4cff" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke="#eceff3" />
        <XAxis dataKey="mes" tickLine={false} axisLine={false} />
        <YAxis tickFormatter={(v) => `${(v / 1000).toFixed(0)}K`} tickLine={false} axisLine={false} />
        <Tooltip
          cursor={{ stroke: "#5e4cff", strokeWidth: 1, strokeOpacity: 0.5 }}
          content={
            <LightdashTooltip formatter={(v) => `${formatInt(v)} contratos`} />
          }
        />
        <Area
          type="monotone"
          dataKey="contratos"
          name="Contratos"
          stroke="#5e4cff"
          strokeWidth={2}
          fill="url(#g-temporal)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
