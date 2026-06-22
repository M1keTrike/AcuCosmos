"use client";

import { motion } from "framer-motion";
import type { DominioMeta } from "@/lib/types";
import { narrativa } from "@/lib/narrativa";

export function PasoMundo({
  dominios,
  cargando,
  error,
  onElegir,
}: {
  dominios: DominioMeta[];
  cargando: boolean;
  error: string | null;
  onElegir: (d: DominioMeta) => void;
}) {
  return (
    <div className="flex flex-1 flex-col">
      <h2 className="text-center text-2xl font-bold text-white sm:text-3xl">
        Elige tu mundo
      </h2>
      <p className="mx-auto mt-2 max-w-md text-center text-white/60">
        Cada mundo es una misión distinta. ¿Cuál quieres diseñar hoy?
      </p>

      {error && (
        <div className="mx-auto mt-6 max-w-md rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-center text-sm text-red-200">
          No pude conectar con el motor. ¿Está corriendo el backend en el puerto 8000?
        </div>
      )}

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cargando
          ? Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="h-44 animate-pulse rounded-2xl border border-borde bg-panel-2"
              />
            ))
          : dominios.map((d, i) => (
              <TarjetaMundo key={d.id} dominio={d} index={i} onElegir={onElegir} />
            ))}
      </div>
    </div>
  );
}

function TarjetaMundo({
  dominio,
  index,
  onElegir,
}: {
  dominio: DominioMeta;
  index: number;
  onElegir: (d: DominioMeta) => void;
}) {
  const t = dominio.tema;
  const narr = narrativa(dominio);
  return (
    <motion.button
      type="button"
      onClick={() => onElegir(dominio)}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.05, 0.3), duration: 0.34, ease: [0.23, 1, 0.32, 1] }}
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.98 }}
      className="group relative flex flex-col items-start gap-3 overflow-hidden rounded-2xl border p-5 text-left"
      style={{
        borderColor: `${t.acento}55`,
        background: `linear-gradient(160deg, ${t.fondo} 0%, ${t.fondo2} 100%)`,
      }}
    >
      <div
        className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full opacity-40 blur-2xl transition-opacity group-hover:opacity-70"
        style={{ background: t.acento }}
      />
      <span className="text-5xl drop-shadow" aria-hidden>
        {dominio.emoji}
      </span>
      <div>
        <h3 className="text-lg font-semibold text-white">{dominio.etiqueta}</h3>
        <p className="mt-1 text-sm leading-snug text-white/75">{narr.objetivo}</p>
      </div>
      <span
        className="mt-auto inline-flex items-center gap-1 text-sm font-medium transition-transform group-hover:translate-x-1"
        style={{ color: t.acento2 }}
      >
        {dominio.n_especies} {narr.unidad} para elegir →
      </span>
    </motion.button>
  );
}
