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

// Convierte un nombre técnico ("E1_comunitario", "reforestacion_humeda") en algo
// legible si el escenario no trae una `etiqueta` propia: quita un prefijo de código
// tipo "E1_", reemplaza guiones bajos por espacios y capitaliza.
export function prettyNombre(nombre: string): string {
  const sinCodigo = nombre.replace(/^[A-Za-z]?\d+[_-]/, "");
  const limpio = sinCodigo.replace(/[_-]+/g, " ").trim();
  if (!limpio) return nombre;
  return limpio.charAt(0).toUpperCase() + limpio.slice(1);
}

// Etiqueta a mostrar para un escenario: usa `etiqueta` si existe, si no embellece
// el `nombre`. Acepta un índice de respaldo para escenarios sin nombre.
export function nombreEscenario(
  e: { etiqueta?: string; nombre?: string },
  i = 0
): string {
  if (e.etiqueta && e.etiqueta.trim()) return e.etiqueta;
  if (e.nombre && e.nombre.trim()) return prettyNombre(e.nombre);
  return `Escenario ${i + 1}`;
}
