"use client";

import { useMemo, useState } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
} from "react-simple-maps";
import { motion } from "framer-motion";
import { formatCOP, formatInt } from "@/lib/utils";
import type { MapaDepto } from "@/types";

const GEOJSON_URL = "/colombia-deptos.geojson";

interface Props {
  data: MapaDepto[];
}

function normalize(s: string): string {
  return s
    .normalize("NFD")
    // eslint-disable-next-line no-misleading-character-class
    .replace(/[̀-ͯ]/g, "")
    .toUpperCase()
    .trim();
}

/**
 * Aliases: API name (normalized) → GeoJSON NOMBRE_DPT (normalized).
 * Covers naming differences between SECOP II departamentos and the
 * IGAC GeoJSON properties used by the bundled file.
 */
const ALIASES: Record<string, string> = {
  "DISTRITO CAPITAL DE BOGOTA": "SANTAFE DE BOGOTA D.C",
  "BOGOTA D.C.": "SANTAFE DE BOGOTA D.C",
  BOGOTA: "SANTAFE DE BOGOTA D.C",
  "SAN ANDRES, PROVIDENCIA Y SANTA CATALINA":
    "ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA",
  "ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA":
    "ARCHIPIELAGO DE SAN ANDRES PROVIDENCIA Y SANTA CATALINA",
};

function resolveKey(apiName: string): string {
  const norm = normalize(apiName);
  return ALIASES[norm] ?? norm;
}

/**
 * Choropleth de Colombia. Single accent linear scale (#f8fafb → #5e4cff)
 * sobre número de contratos por departamento. Tooltip flotante + leyenda
 * gradient con marcas min · mid · max.
 */
export function ColombiaMap({ data }: Props) {
  const [hovered, setHovered] = useState<MapaDepto | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number } | null>(null);

  const byKey = useMemo(() => {
    const m = new Map<string, MapaDepto>();
    for (const d of data) m.set(resolveKey(d.nombre), d);
    return m;
  }, [data]);

  const max = useMemo(
    () => Math.max(1, ...data.map((d) => d.contratos)),
    [data],
  );

  // Linear lerp #f8fafb → #5e4cff sobre sqrt(t) para mejor distribución visual.
  const colorFor = (contratos: number) => {
    if (!contratos) return "#f6f8fa";
    const t = Math.sqrt(contratos / max);
    const r = Math.round(0xf8 + (0x5e - 0xf8) * t);
    const g = Math.round(0xfa + (0x4c - 0xfa) * t);
    const b = Math.round(0xfb + (0xff - 0xfb) * t);
    return `rgb(${r}, ${g}, ${b})`;
  };

  return (
    <div className="relative h-full w-full">
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{ scale: 1800, center: [-74, 4.5] }}
        style={{ width: "100%", height: "100%" }}
      >
        <Geographies geography={GEOJSON_URL}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const rawName: string =
                (geo.properties.NOMBRE_DPT as string) ??
                (geo.properties.nombre_dpt as string) ??
                "";
              const key = normalize(rawName);
              const depto = byKey.get(key) ?? null;
              const fill = depto ? colorFor(depto.contratos) : "#f6f8fa";

              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={fill}
                  stroke="#a4abb8"
                  strokeWidth={0.5}
                  onMouseEnter={(e) => {
                    setHovered(depto);
                    setTooltip({ x: e.clientX, y: e.clientY });
                  }}
                  onMouseMove={(e) =>
                    setTooltip({ x: e.clientX, y: e.clientY })
                  }
                  onMouseLeave={() => {
                    setHovered(null);
                    setTooltip(null);
                  }}
                  style={{
                    default: {
                      outline: "none",
                      transition: "fill 0.18s ease, opacity 0.18s ease",
                    },
                    hover: {
                      outline: "none",
                      fill: "#5e4cff",
                      cursor: "pointer",
                    },
                    pressed: { outline: "none" },
                  }}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>

      {hovered && tooltip && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.15 }}
          className="pointer-events-none fixed z-30 rounded-[8px] border border-lava-cloud bg-canvas-white px-3 py-2 shadow-[rgba(39,40,53,0.08)_0_8px_24px]"
          style={{ left: tooltip.x + 14, top: tooltip.y + 14 }}
        >
          <div className="text-[13px] font-medium text-midnight-ink">
            {hovered.nombre}
          </div>
          <div className="mt-1 text-[12px] text-deep-indigo">
            <span className="text-cloud-gray">Contratos:</span>{" "}
            <span className="font-mono">{formatInt(hovered.contratos)}</span>
          </div>
          <div className="text-[12px] text-deep-indigo">
            <span className="text-cloud-gray">Valor:</span>{" "}
            <span className="font-mono">
              {formatCOP(hovered.valor_total, { compact: true })}
            </span>
          </div>
        </motion.div>
      )}

      {/* Legend gradient con marcas */}
      <div className="absolute bottom-3 left-3 flex flex-col gap-1.5 rounded-[8px] bg-canvas-white/95 px-3 py-2 shadow-[rgba(39,40,53,0.08)_0_0_0_1px,rgba(39,40,53,0.04)_0_4px_10px]">
        <div className="flex items-center justify-between gap-3">
          <span className="text-[10px] uppercase tracking-wider text-cloud-gray">
            Contratos
          </span>
        </div>
        <div className="relative h-1.5 w-40 rounded-full">
          <div
            className="absolute inset-0 rounded-full"
            style={{
              background:
                "linear-gradient(90deg, #f8fafb 0%, #c8ccf3 50%, #5e4cff 100%)",
            }}
          />
        </div>
        <div className="flex items-center justify-between font-mono text-[10px] text-cloud-gray">
          <span>0</span>
          <span>{formatInt(Math.round(max / 2))}</span>
          <span>{formatInt(max)}</span>
        </div>
      </div>
    </div>
  );
}
