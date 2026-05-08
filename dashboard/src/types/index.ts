/**
 * SECOP II domain types — shared across pages, charts, and api client.
 */

export interface StatsTotal {
  total_registros: number;
  total_pymes: number;
  pct_pymes: number;
  total_directa: number;
  pct_directa: number;
  pareto_entidades: number;
  pareto_pct_valor: number;
  total_valor: number;
}

export interface DepartamentoTop {
  departamento: string;
  contratos: number;
  valor_total: number;
  pct: number;
}

export interface ModalidadStat {
  modalidad: string;
  contratos: number;
  pct: number;
}

export interface TipoContratoStat {
  tipo: string;
  contratos: number;
  valor_total: number;
}

export interface EntidadTop {
  entidad: string;
  valor_total: number;
  contratos: number;
}

export interface DistribucionTemporal {
  mes: string; // YYYY-MM
  contratos: number;
  valor_total: number;
}

export interface ParetoPunto {
  rank: number;
  entidad: string;
  valor: number;
  pct_acumulado: number;
}

export interface BrechaGenero {
  genero: "M" | "F" | "Otro";
  promedio: number;
  mediana: number;
  contratos: number;
}

export type AnomaliaVerdict = "VERIDICO" | "FALSO" | "REVISAR";

export interface Anomalia {
  id: string;
  entidad: string;
  contratista: string;
  valor: number;
  modalidad: string;
  fecha: string;
  verdict: AnomaliaVerdict;
  sustento: string;
}

export interface MapaDepto {
  codigo: string; // ISO depto code (e.g. "11" Bogotá)
  nombre: string;
  contratos: number;
  valor_total: number;
}
