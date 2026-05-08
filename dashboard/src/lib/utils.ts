import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format a number as Colombian peso (COP) currency.
 */
export function formatCOP(value: number, opts: { compact?: boolean } = {}) {
  if (opts.compact) {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}B`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}MM`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
    return `$${value.toFixed(0)}`;
  }
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);
}

/**
 * Format an integer with thousand separators.
 */
export function formatInt(value: number) {
  return new Intl.NumberFormat("es-CO").format(value);
}

/**
 * Format a percent value (0-100).
 */
export function formatPct(value: number, digits = 1) {
  return `${value.toFixed(digits)}%`;
}

/**
 * Truncate a string to N chars with ellipsis.
 */
export function truncate(str: string, n = 32) {
  return str.length > n ? `${str.slice(0, n - 1)}…` : str;
}
