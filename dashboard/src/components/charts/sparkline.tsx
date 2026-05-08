"use client";

import { motion } from "framer-motion";

interface Props {
  values: number[];
  width?: number;
  height?: number;
  className?: string;
}

/**
 * Lightweight inline sparkline (no recharts overhead). Rendered as a
 * smooth SVG polyline + gradient area. Used in compact KPI cards.
 */
export function Sparkline({
  values,
  width = 120,
  height = 36,
  className,
}: Props) {
  if (!values.length) return null;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = width / (values.length - 1 || 1);

  const points = values.map((v, i) => {
    const x = i * step;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return [x, y] as const;
  });

  const path = points
    .map(([x, y], i) => (i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`))
    .join(" ");

  const area = `${path} L ${width} ${height} L 0 ${height} Z`;
  const last = points[points.length - 1];

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      aria-hidden
    >
      <defs>
        <linearGradient id="sparkline-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#5e4cff" stopOpacity={0.3} />
          <stop offset="100%" stopColor="#5e4cff" stopOpacity={0} />
        </linearGradient>
      </defs>
      <motion.path
        d={area}
        fill="url(#sparkline-grad)"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.4 }}
      />
      <motion.path
        d={path}
        fill="none"
        stroke="#5e4cff"
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        whileInView={{ pathLength: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      />
      {last && (
        <circle
          cx={last[0]}
          cy={last[1]}
          r={2.5}
          fill="#5e4cff"
        />
      )}
    </svg>
  );
}
