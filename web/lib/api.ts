// Cliente del backend FastAPI. La base se puede sobreescribir con
// NEXT_PUBLIC_API_BASE; por defecto el backend local en :8000.
import type { Catalogo, DominioMeta, Escenario, Kappa, Sitio } from "./types";

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
export const apiSitios = (dom: string) =>
  get<Sitio[]>(`/api/dominios/${dom}/sitios`);

export interface ParamsRun {
  dom: string;
  escenario?: string;
  seed?: number; // undefined => corrida aleatoria real (sin semilla fija)
  generaciones?: number;
  poblacion?: number;
  // Overrides opcionales de parametros del escenario.
  presupuesto?: number;
  minEspecies?: number;
  maxEspecies?: number;
  sitio?: number; // indice del sitio elegido ("tipo de acuario"); undefined => lo elige el AG
  fijas?: number[]; // indices del catalogo a anclar ("base de la busqueda")
  capacidad?: number; // override de la capacidad del sitio (filtro/superficie)
}

export function urlRun(p: ParamsRun): string {
  const q = new URLSearchParams({ dom: p.dom });
  if (p.escenario) q.set("escenario", p.escenario);
  if (p.seed !== undefined && p.seed !== null && !Number.isNaN(p.seed))
    q.set("seed", String(p.seed));
  if (p.generaciones) q.set("generaciones", String(p.generaciones));
  if (p.poblacion) q.set("poblacion", String(p.poblacion));
  if (p.presupuesto !== undefined && !Number.isNaN(p.presupuesto))
    q.set("presupuesto", String(p.presupuesto));
  if (p.minEspecies !== undefined && !Number.isNaN(p.minEspecies))
    q.set("min_especies", String(p.minEspecies));
  if (p.maxEspecies !== undefined && !Number.isNaN(p.maxEspecies))
    q.set("max_especies", String(p.maxEspecies));
  if (p.sitio !== undefined && p.sitio !== null && !Number.isNaN(p.sitio))
    q.set("sitio", String(p.sitio));
  if (p.fijas && p.fijas.length > 0) q.set("fijas", p.fijas.join(","));
  if (p.capacidad !== undefined && p.capacidad > 0 && !Number.isNaN(p.capacidad))
    q.set("capacidad", String(p.capacidad));
  return `${API_BASE}/api/run?${q.toString()}`;
}
