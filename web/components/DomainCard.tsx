"use client";

import { motion } from "framer-motion";
import type { DominioMeta } from "@/lib/types";
import { Icono } from "./Icono";

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
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05 * index, duration: 0.35, ease: [0.23, 1, 0.32, 1] }}
      whileHover={{ y: -3 }}
      whileTap={{ scale: 0.99 }}
      className="tarjeta group relative flex flex-col items-start gap-3 p-5 text-left transition-colors hover:border-foreground/20"
    >
      <div className="flex w-full items-center justify-between">
        <span
          className="flex h-11 w-11 items-center justify-center rounded-xl border"
          style={{
            borderColor: `${t.acento}40`,
            background: `${t.acento}14`,
            color: t.acento,
          }}
        >
          <Icono forma={t.forma} size={24} />
        </span>
        <span className="rounded-full border border-borde px-2.5 py-1 text-[11px] font-medium text-foreground/55">
          {dominio.agregacion.replace("_", " ")}
        </span>
      </div>
      <div>
        <h3 className="text-lg font-semibold text-foreground">{dominio.etiqueta}</h3>
        <p className="mt-1 text-sm leading-snug text-foreground/65">{dominio.descripcion}</p>
      </div>
      <div className="mt-1 flex items-center gap-3 text-xs text-foreground/50">
        <span>{dominio.n_especies} especies</span>
        <span className="opacity-40">•</span>
        <span>{dominio.estratos.length} estratos</span>
      </div>
      <span
        className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-foreground/75 transition-transform group-hover:translate-x-1"
        style={{ color: t.acento2 }}
      >
        Diseñar en vivo →
      </span>
    </motion.button>
  );
}
