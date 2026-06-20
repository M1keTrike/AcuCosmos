export function fmt(v: number | null | undefined, dec = 3): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  if (Math.abs(v) >= 1000) return v.toLocaleString("es-MX", { maximumFractionDigits: 0 });
  return v.toFixed(dec);
}

export function fmtDinero(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return v.toLocaleString("es-MX", { maximumFractionDigits: 0 });
}

// Etiqueta legible para una clave de métrica (cae al propio nombre si no hay mapa).
const ETIQUETAS: Record<string, string> = {
  A_e: "Estética",
  I_b: "Biodiversidad",
  R_v: "Comodidad",
  N_c: "Conflicto",
  M_s: "Sobrecarga",
  B_div: "Bono diversidad",
  co2: "CO₂",
  biodiv: "Biodiversidad",
  eq_pares: "Sinergia",
  carga: "Carga",
  valor: "Valor",
};

export function etiquetaMetrica(clave: string): string {
  return ETIQUETAS[clave] ?? clave;
}
