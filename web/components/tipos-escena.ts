import type { EspecieCat } from "@/lib/types";

// Mapa idx_de_especie -> ficha de catálogo (lo consumen la escena y otras vistas).
export type EspecieMapa = Map<number, EspecieCat>;
