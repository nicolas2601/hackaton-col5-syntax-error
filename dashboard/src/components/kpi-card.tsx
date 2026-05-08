"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string | number;
  hint?: string;
  /**
   * Pre-rendered icon node. Server Components no pueden serializar
   * referencias a componentes (LucideIcon) hacia Client Components,
   * por eso recibimos el JSX ya construido.
   */
  icon?: ReactNode;
  accent?: boolean;
  delay?: number;
  className?: string;
}

/**
 * Lightdash-style KPI card. Use `accent` for the headline metric.
 * Renders with a slide-up + fade-in animation on scroll.
 */
export function KpiCard({
  label,
  value,
  hint,
  icon,
  accent = false,
  delay = 0,
  className,
}: KpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.4, delay, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -2, scale: 1.005 }}
      className={cn(
        "group relative overflow-hidden rounded-[12px] bg-canvas-white p-6 transition-shadow duration-300",
        "shadow-[rgba(39,40,53,0.1)_0_0_0_1px]",
        "hover:shadow-[rgba(39,40,53,0.05)_0_0_0_1px,rgba(39,40,53,0.06)_0_8px_24px_-8px]",
        accent && "bg-pixel-pattern",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-[11px] font-medium uppercase tracking-wider text-cloud-gray">
          {label}
        </span>
        {icon && (
          <span
            className={cn(
              "grid h-8 w-8 place-items-center rounded-[8px]",
              accent
                ? "bg-electric-violet text-white"
                : "bg-ghost-fill text-deep-indigo",
            )}
          >
            {icon}
          </span>
        )}
      </div>

      <div
        className={cn(
          "mt-3 font-display font-semibold tracking-[-0.025em]",
          accent
            ? "text-[44px] leading-none text-electric-violet"
            : "text-[32px] leading-none text-midnight-ink",
        )}
      >
        {value}
      </div>

      {hint && (
        <p className="mt-2 text-[12px] leading-snug text-steel-gray">{hint}</p>
      )}
    </motion.div>
  );
}
