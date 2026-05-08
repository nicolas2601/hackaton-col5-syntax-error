"use client";

import { motion } from "framer-motion";
import { formatPct } from "@/lib/utils";

interface Props {
  pct: number;
  label?: string;
}

/**
 * Donut gauge for the Pymes percentage. Uses pure SVG to avoid pulling in
 * extra Recharts overhead — also lets us customize the typography precisely.
 */
export function PymesGauge({ pct, label = "Pymes" }: Props) {
  const size = 200;
  const stroke = 18;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const dash = (pct / 100) * c;

  return (
    <div className="flex flex-col items-center justify-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} stroke="#eceff3" strokeWidth={stroke} fill="none" />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke="#5e4cff"
          strokeWidth={stroke}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={`${dash} ${c - dash}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          initial={{ strokeDasharray: `0 ${c}` }}
          animate={{ strokeDasharray: `${dash} ${c - dash}` }}
          transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
        />
        <text
          x="50%"
          y="50%"
          dy="0.1em"
          textAnchor="middle"
          fontFamily="var(--font-display)"
          fontWeight="600"
          fontSize="36"
          fill="#1a1b25"
          letterSpacing="-0.02em"
        >
          {formatPct(pct, 1)}
        </text>
        <text
          x="50%"
          y="62%"
          textAnchor="middle"
          fontSize="11"
          fill="#666d80"
          letterSpacing="0.05em"
        >
          {label.toUpperCase()}
        </text>
      </svg>
    </div>
  );
}
