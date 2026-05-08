"use client";

import {
  Area,
  CartesianGrid,
  ComposedChart,
  Label,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ParetoPunto } from "@/types";
import { LightdashTooltip } from "./recharts-tooltip";

export function ParetoCurve({ data }: { data: ParetoPunto[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart
        data={data}
        margin={{ top: 12, right: 24, bottom: 12, left: 8 }}
      >
        <defs>
          <linearGradient id="g-pareto" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#5e4cff" stopOpacity={0.28} />
            <stop offset="100%" stopColor="#5e4cff" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke="#eceff3" />
        <XAxis
          dataKey="rank"
          tickLine={false}
          axisLine={false}
          label={{
            value: "Top N entidades",
            position: "insideBottom",
            offset: -2,
            fill: "#666d80",
            fontSize: 11,
          }}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          domain={[0, 100]}
          tickFormatter={(v) => `${v}%`}
        />

        {/* Reference grid in soft gray; annotation labels en violet */}
        <ReferenceLine
          y={80}
          stroke="#a4abb8"
          strokeDasharray="4 4"
          ifOverflow="extendDomain"
        >
          <Label
            value="80% del valor"
            position="insideTopRight"
            fill="#5e4cff"
            fontSize={11}
            fontWeight={600}
          />
        </ReferenceLine>
        <ReferenceLine
          x={7}
          stroke="#a4abb8"
          strokeDasharray="4 4"
          ifOverflow="extendDomain"
        >
          <Label
            value="7 entidades"
            position="insideTop"
            fill="#5e4cff"
            fontSize={11}
            fontWeight={600}
            offset={8}
          />
        </ReferenceLine>

        <Tooltip
          content={
            <LightdashTooltip
              formatter={(v) => `${(v as number).toFixed(1)}%`}
            />
          }
        />
        <Area
          type="monotone"
          dataKey="pct_acumulado"
          name="% acumulado"
          stroke="#5e4cff"
          strokeWidth={2.5}
          fill="url(#g-pareto)"
        />
        <Line
          type="monotone"
          dataKey="pct_acumulado"
          stroke="#5e4cff"
          strokeWidth={0}
          dot={{ r: 2.5, fill: "#5e4cff" }}
          activeDot={{ r: 5 }}
          legendType="none"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
