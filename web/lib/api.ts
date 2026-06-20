// Cliente del backend FastAPI. La base se puede sobreescribir con
// NEXT_PUBLIC_API_BASE; por defecto el backend local en :8000.
import type { Catalogo, DominioMeta, Escenario, Kappa } from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://localhost:8000";

async function get<T>(ruta: string): Promise<T> {
  const r = await fetch(`${API_BASE}${ruta}`, { cache: "no-store" });
  if (!r.ok) {
    throw new Error(`API ${ruta} → ${r.status}`);
  }
  return (await r.json()) as T;
}

export const apiDominios = () => get<DominioMeta[]>("/api/dominios");
export const apiEscenarios = (dom: string) =>
  get<Escenario[]>(`/api/dominios/${dom}/escenarios`);
export const apiCatalogo = (dom: string) =>
  get<Catalogo>(`/api/dominios/${dom}/catalogo`);
export const apiKappa = (dom: string) => get<Kappa>(`/api/dominios/${dom}/kappa`);

export interface ParamsRun {
  dom: string;
  escenario?: string;
  seed?: number;
  generaciones?: number;
  poblacion?: number;
}

export function urlRun(p: ParamsRun): string {
  const q = new URLSearchParams({ dom: p.dom });
  if (p.escenario) q.set("escenario", p.escenario);
  if (p.seed !== undefined && p.seed !== null && !Number.isNaN(p.seed))
    q.set("seed", String(p.seed));
  if (p.generaciones) q.set("generaciones", String(p.generaciones));
  if (p.poblacion) q.set("poblacion", String(p.poblacion));
  return `${API_BASE}/api/run?${q.toString()}`;
}
