/**
 * SECOP II API client.
 * Sin fallback a mock data — si el upstream falla, el error sube al
 * boundary `error.tsx` de Next.js.
 */

import type {
  Anomalia,
  BrechaGenero,
  DepartamentoTop,
  DistribucionTemporal,
  EntidadTop,
  MapaDepto,
  ModalidadStat,
  ParetoPunto,
  StatsTotal,
  TipoContratoStat,
} from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const TIMEOUT_MS = 30_000;

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Internal fetch with timeout + JSON parsing.
 * Throws ApiError on non-2xx, timeout, or network failure.
 * No silent fallback — errors propagate to error.tsx boundary.
 */
async function request<T>(path: string): Promise<T> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      signal: ctl.signal,
      headers: { Accept: "application/json" },
      next: { revalidate: 60 },
    });
    if (!res.ok) {
      throw new ApiError(`HTTP ${res.status} on ${path}`, res.status);
    }
    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    const msg = err instanceof Error ? err.message : String(err);
    throw new ApiError(`Network error on ${path}: ${msg}`);
  } finally {
    clearTimeout(timer);
  }
}

// ============================================================
// Public API surface
// ============================================================

export const api = {
  statsTotal: () => request<StatsTotal>("/api/v1/stats/total"),

  departamentosTop: () =>
    request<DepartamentoTop[]>("/api/v1/departamentos/top"),

  modalidades: () => request<ModalidadStat[]>("/api/v1/modalidades"),

  tiposContrato: () =>
    request<TipoContratoStat[]>("/api/v1/tipos-contrato"),

  entidadesTop: () => request<EntidadTop[]>("/api/v1/entidades/top"),

  distribucionTemporal: () =>
    request<DistribucionTemporal[]>("/api/v1/temporal"),

  pareto: () => request<ParetoPunto[]>("/api/v1/pareto/entidades"),

  brechaGenero: () => request<BrechaGenero[]>("/api/v1/genero/brecha"),

  anomalias: () => request<Anomalia[]>("/api/v1/anomalias"),

  mapaDeptos: () => request<MapaDepto[]>("/api/v1/mapa/deptos"),
};

export type Api = typeof api;
