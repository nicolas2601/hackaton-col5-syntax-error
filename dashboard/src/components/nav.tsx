"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X, BarChart3 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const NAV_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/mapa", label: "Mapa" },
  { href: "/anomalias", label: "Anomalías" },
  { href: "/pareto", label: "Pareto" },
  { href: "/genero", label: "Brecha género" },
  { href: "/docs/overview", label: "Docs" },
];

export function Nav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-lava-cloud/80 bg-canvas-white/85 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-6 px-4 sm:px-6 lg:px-8">
        <Link href="/" className="group flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-[8px] bg-electric-violet text-white">
            <BarChart3 className="h-4 w-4" strokeWidth={2.2} />
          </span>
          <span className="font-display text-[18px] font-semibold tracking-[-0.020em] text-midnight-ink">
            SECOP<span className="text-electric-violet">.</span>II
          </span>
          <span className="pill ml-1 hidden sm:inline-flex">v1 · Hackathon COL 5.0</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => {
            const active =
              pathname === link.href ||
              (link.href !== "/" && pathname.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-[8px] px-3 py-2 text-[13px] font-medium transition-colors",
                  active
                    ? "bg-ghost-fill text-midnight-ink"
                    : "text-steel-gray hover:bg-ghost-fill hover:text-midnight-ink",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <Button variant="ghost" size="sm" asChild>
            <a
              href="https://api-ronda2.tikno.pro/docs"
              target="_blank"
              rel="noreferrer"
            >
              API Docs
            </a>
          </Button>
          <Button variant="primary" size="sm" asChild>
            <Link href="/dashboard">Ver dashboard</Link>
          </Button>
        </div>

        <button
          className="grid h-9 w-9 place-items-center rounded-[8px] border border-lava-cloud md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Abrir menú"
        >
          {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-lava-cloud bg-canvas-white md:hidden"
          >
            <div className="flex flex-col gap-1 px-4 py-3">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  className="rounded-[8px] px-3 py-2 text-[14px] text-midnight-ink hover:bg-ghost-fill"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
