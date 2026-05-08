"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface ElevatedCardProps {
  /**
   * Pre-rendered icon node. Pasalo como `<Database className="..." />`
   * desde el caller (Server Component) — no se puede pasar la referencia
   * al componente porque no es serializable.
   */
  icon?: ReactNode;
  title: string;
  description: string;
  delay?: number;
  className?: string;
}

/** Feature card used on the landing page (3-column grid). */
export function ElevatedCard({
  icon,
  title,
  description,
  delay = 0,
  className,
}: ElevatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -4, scale: 1.02 }}
      className={cn(
        "card-elevated flex h-full flex-col gap-4",
        className,
      )}
    >
      {icon && (
        <span className="grid h-12 w-12 place-items-center rounded-[12px] bg-lavender-mist text-electric-violet">
          {icon}
        </span>
      )}
      <h3 className="text-heading-sm">{title}</h3>
      <p className="text-body text-steel-gray">{description}</p>
    </motion.div>
  );
}
