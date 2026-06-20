// Tipos que reflejan el JSON del backend FastAPI (api/).

export interface EstratoMeta {
  idx: number;
  valor: string;
  etiqueta: string;
}

export interface TemaResumen {
  acento: string;
  acento2: string;
  fondo: string;
  fondo2: string;
  forma: Forma;
}

export type Forma = "pez" | "planta" | "arbol" | "animal";

export interface DominioMeta {
  id: string;
  dominio: string;
  etiqueta: string;
  descripcion: string;
  emoji: string;
  agregacion: string;
  n_especies: number;
  estratos: EstratoMeta[];
  tema: TemaResumen;
  error?: string;
}

export interface Escenario {
  nombre?: string;
  presupuesto?: number | null;
  min_especies?: number | null;
  max_especies?: number | null;
  [k: string]: unknown;
}

export interface EspecieCat {
  idx: number;
  id: string;
  nombre: string;
  estrato: string;
  estrato_idx: number;
  grupo: string;
  color: string;
  tamano: number | null;
}

export interface GrupoCat {
  valor: string;
  etiqueta: string;
  color: string;
}

export interface Catalogo {
  dominio: string;
  forma: Forma;
  grupo_col: string | null;
  grupos: GrupoCat[];
  especies: EspecieCat[];
}

export interface ParKappa {
  i: number;
  j: number;
  valor: number;
  procedencia?: "investigado" | "derivado";
}

export interface Kappa {
  n: number;
  pares: ParKappa[];
}

export interface ItemEnsamblaje {
  i: number;
  C: number;
}

export interface GenEvento {
  generacion: number;
  apt_mejor: number | null;
  apt_promedio: number | null;
  apt_peor: number | null;
  factible: boolean;
  costo: number | null;
  metricas: Record<string, number | null>;
  ensamblaje: ItemEnsamblaje[];
}

export interface Metricas {
  n_especies: number;
  costo: number | null;
  factible: boolean;
  [clave: string]: number | boolean | null;
}

export interface MejorDone {
  sitio_idx: number;
  sitio_nombre: string;
  F: number | null;
  metricas: Metricas;
  activas: ItemEnsamblaje[];
}

export interface TopKItem {
  F: number | null;
  metricas: Metricas;
  activas: ItemEnsamblaje[];
}

export interface DoneEvento {
  mejor: MejorDone;
  topK: TopKItem[];
  kappa_activas: { i: number; j: number; valor: number }[];
}
