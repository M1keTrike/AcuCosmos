"use client";

import { motion } from "framer-motion";
import type { DominioMeta } from "@/lib/types";
import { DomainCard } from "./DomainCard";

export function HeroSelector({
  dominios,
  cargando,
  error,
  onSelect,
}: {
  dominios: DominioMeta[];
  cargando: boolean;
  error: string | null;
  onSelect: (d: DominioMeta) => void;
}) {
  return (
    <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-6 py-10 sm:py-16">
      <motion.div
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <p className="mb-3 text-sm font-medium uppercase tracking-[0.3em] text-cyan-300/70">
          Algoritmo genético · ensamblajes biológicos
        </p>
        <h1 className="titulo-grad text-balance text-5xl font-bold tracking-tight sm:text-6xl">
          BioNexo
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-pretty text-lg text-white/65">
          Un mismo motor evolutivo, cinco mundos. Elige un dominio y mira cómo el
          algoritmo arma el mejor ensamblaje, generación a generación.
        </p>
      </motion.div>

      <div className="mt-12 flex-1">
        {error && (
          <div className="mx-auto max-w-xl rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-center text-sm text-red-200">
            No se pudo conectar con el backend ({error}).<br />
            Levántalo con <code className="font-mono">uvicorn api.app:app --reload</code> en la
            raíz del repo.
          </div>
        )}

        {cargando && (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="h-48 animate-pulse rounded-2xl border border-borde bg-panel/60"
              />
            ))}
          </div>
        )}

        {!cargando && !error && (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {dominios.map((d, i) => (
              <DomainCard key={d.id} dominio={d} index={i} onSelect={onSelect} />
            ))}
          </div>
        )}
      </div>

      <p className="mt-10 text-center text-xs text-white/35">
        Reutiliza el motor genético (Python) sin modificarlo · datos en vivo por SSE
      </p>
    </div>
  );
}
