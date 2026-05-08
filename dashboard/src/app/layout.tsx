import type { Metadata } from "next";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/montserrat/500.css";
import "@fontsource/montserrat/600.css";
import "@fontsource/montserrat/700.css";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import "./globals.css";

import { ThemeProvider } from "next-themes";
import { Providers } from "@/lib/query-client";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "SECOP II — Transparencia en contratación pública",
  description:
    "Dashboard de análisis SECOP II: 1M+ contratos, brecha de género, Pareto, anomalías y choropleth.",
  metadataBase: new URL("https://secop.tikno.pro"),
  openGraph: {
    title: "SECOP II — Transparencia",
    description:
      "Dashboard analítico sobre 1M+ registros de contratación pública en Colombia.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="min-h-screen bg-canvas-white text-midnight-ink antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="light"
          forcedTheme="light"
          enableSystem={false}
        >
          <Providers>
            <Nav />
            <main className="flex min-h-[calc(100vh-64px)] flex-col">{children}</main>
            <Footer />
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}
