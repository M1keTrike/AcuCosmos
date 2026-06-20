"use client";

import { motion } from "framer-motion";
import type { DominioMeta } from "@/lib/types";

export function DomainCard({
  dominio,
  index,
  onSelect,
}: {
  dominio: DominioMeta;
  index: number;
  onSelect: (d: DominioMeta) => void;
}) {
  const t = dominio.tema;
  return (
    <motion.button
      type="button"
      data-dom={dominio.id}
      onClick={() => onSelect(dominio)}
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.06 * index, type: "spring", stiffness: 120, damping: 16 }}
      whileHover={{ y: -6, scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
      className="group relative flex flex-col items-start gap-3 overflow-hidden rounded-2xl border p-5 text-left"
      style={{
        borderColor: `${t.acento}55`,
        background: `linear-gradient(160deg, ${t.fondo} 0%, ${t.fondo2} 100%)`,
      }}
    >
      {/* halo de acento */}
      <div
        className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full opacity-40 blur-2xl transition-opacity group-hover:opacity-70"
        style={{ background: t.acento }}
      />
      <div className="flex w-full items-center justify-between">
        <span className="text-4xl drop-shadow">{dominio.emoji}</span>
        <span
          className="rounded-full px-2.5 py-1 text-[11px] font-medium"
          style={{ background: `${t.acento}22`, color: t.acento2 }}
        >
          {dominio.agregacion.replace("_", " ")}
        </span>
      </div>
      <div>
        <h3 className="text-lg font-semibold text-white">{dominio.etiqueta}</h3>
        <p className="mt-1 text-sm leading-snug text-white/70">{dominio.descripcion}</p>
      </div>
      <div className="mt-1 flex items-center gap-3 text-xs text-white/55">
        <span>{dominio.n_especies} especies</span>
        <span className="opacity-40">•</span>
        <span>{dominio.estratos.length} estratos</span>
      </div>
      <span
        className="mt-2 inline-flex items-center gap-1 text-sm font-medium transition-transform group-hover:translate-x-1"
        style={{ color: t.acento2 }}
      >
        Diseñar en vivo →
      </span>
    </motion.button>
  );
}
