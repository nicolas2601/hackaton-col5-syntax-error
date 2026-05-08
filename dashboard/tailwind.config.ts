import type { Config } from "tailwindcss";

// Tailwind v4: la mayor parte de la configuración vive en `globals.css` con @theme.
// Este archivo es mínimo y solo declara content paths.
const config: Config = {
  content: ["./src/**/*.{ts,tsx,mdx}"],
};

export default config;
