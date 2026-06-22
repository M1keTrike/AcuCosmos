// Capa de juego: defaults ocultos + helpers para traducir los datos crudos
// del AG a conceptos amigables (puntaje, estrellas, amigos/rivales, fortalezas).
import type { DoneEvento, Escenario, Metricas, TopKItem } from "./types";

// --- Defaults de corrida (ocultos al visitante) --------------------------- //
// Una demo vistosa pero rápida: suficientes rondas para ver mejora clara.
export const DEFAULTS_RUN = {
  generaciones: 90,
  poblacion: 80,
} as const;

/** Semilla distinta por corrida para que cada demo se sienta nueva. */
export function semillaAleatoria(): number {
  return Math.floor(Math.random() * 100000);
}

// --- Puntaje y estrellas --------------------------------------------------- //
/**
 * Convierte la aptitud F del mejor individuo a un puntaje "humano".
 * F no tiene tope fijo entre dominios, así que mostramos el valor directo
 * (escalado x100 para que se sienta como "puntos") y reservamos las estrellas
 * para una valoración cualitativa basada en factibilidad + percentil del topK.
 */
export function puntajeDesdeF(f: number | null | undefined): number {
  if (f == null || Number.isNaN(f)) return 0;
  return Math.max(0, Math.round(f * 100));
}

/** 0..3 estrellas: 1 por terminar, +1 si es factible, +1 si destaca en su topK. */
export function estrellas(done: DoneEvento | null): number {
  if (!done) return 0;
  let s = 1;
  if (done.mejor.metricas.factible) s += 1;
  const fs = done.topK
    .map((t) => t.F)
    .filter((v): v is number => typeof v === "number");
  const fMejor = done.mejor.F;
  if (typeof fMejor === "number" && fs.length > 1) {
    const max = Math.max(...fs);
    if (max > 0 && fMejor >= max - 1e-9) s += 1;
  } else if (typeof fMejor === "number") {
    s += 1;
  }
  return Math.min(3, s);
}

// --- Amigos / rivales (κ traducido) --------------------------------------- //
export interface Relacion {
  i: number;
  j: number;
  valor: number;
}

/**
 * Separa las relaciones entre especies activas en "amigos" (sinergia > 0) y
 * "rivales" (antagonismo < 0), ordenadas por intensidad. Limita a `tope` cada
 * lista para no abrumar en pantalla.
 */
export function amigosYRivales(
  kappaActivas: { i: number; j: number; valor: number }[],
  tope = 4
): { amigos: Relacion[]; rivales: Relacion[] } {
  const amigos: Relacion[] = [];
  const rivales: Relacion[] = [];
  for (const r of kappaActivas) {
    if (r.valor > 0.05) amigos.push(r);
    else if (r.valor < -0.05) rivales.push(r);
  }
  amigos.sort((a, b) => b.valor - a.valor);
  rivales.sort((a, b) => a.valor - b.valor);
  return { amigos: amigos.slice(0, tope), rivales: rivales.slice(0, tope) };
}

// --- Fortalezas (métricas normalizadas y orientadas) ----------------------- //
const OMITIR = new Set(["n_especies", "costo", "factible"]);

export interface Fortaleza {
  clave: string;
  /** 0..1 — qué tan fuerte es este aspecto en el mejor diseño vs. su topK. */
  nivel: number;
}

/**
 * Normaliza cada métrica del mejor diseño contra el rango del topK (igual que el
 * radar experto) para obtener un 0..1. Las métricas "mejor si es baja" (conflicto,
 * sobrecarga, carga) se invierten para que más barra = mejor siempre.
 */
export function fortalezas(
  done: DoneEvento | null,
  menorEsMejor: (clave: string) => boolean
): Fortaleza[] {
  if (!done) return [];
  const topK: TopKItem[] = done.topK.length ? done.topK : [done.mejor];
  const base: Metricas = done.mejor.metricas;
  const claves = Object.keys(base).filter(
    (k) => !OMITIR.has(k) && typeof base[k] === "number"
  );

  return claves.map((k) => {
    const vals = topK
      .map((t) => Number(t.metricas[k] ?? 0))
      .filter((v) => !Number.isNaN(v));
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    const v = Number(base[k] ?? 0);
    let nivel = max - min < 1e-9 ? 0.7 : (v - min) / (max - min);
    if (menorEsMejor(k)) nivel = 1 - nivel;
    return { clave: k, nivel: Math.max(0, Math.min(1, nivel)) };
  });
}

// --- Briefing del escenario ------------------------------------------------ //
export interface Briefing {
  presupuesto: number | null;
  minEspecies: number | null;
  maxEspecies: number | null;
}

export function briefingDeEscenario(esc: Escenario | undefined): Briefing {
  return {
    presupuesto: (esc?.presupuesto as number | null) ?? null,
    minEspecies: (esc?.min_especies as number | null) ?? null,
    maxEspecies: (esc?.max_especies as number | null) ?? null,
  };
}
