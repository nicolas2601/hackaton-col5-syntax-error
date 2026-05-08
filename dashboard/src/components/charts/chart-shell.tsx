"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface ChartShellProps {
  title: string;
  hint?: string;
  className?: string;
  children: React.ReactNode;
  badge?: React.ReactNode;
  height?: number;
  elevated?: boolean;
  delay?: number;
}

/** Wrapper card around every chart — gives consistent header + animation. */
export function ChartShell({
  title,
  hint,
  className,
  children,
  badge,
  height = 280,
  elevated = false,
  delay = 0,
}: ChartShellProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.4, delay, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        elevated ? "card-elevated" : "card-simple",
        "flex flex-col",
        className,
      )}
    >
      <header className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="text-subheading">{title}</h3>
          {hint && <p className="mt-1 text-[12px] text-steel-gray">{hint}</p>}
        </div>
        {badge && <span className="pill pill-violet shrink-0">{badge}</span>}
      </header>
      <div style={{ height }}>{children}</div>
    </motion.section>
  );
}
