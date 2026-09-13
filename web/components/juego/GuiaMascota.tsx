"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Icono } from "@/components/Icono";
import type { Forma } from "@/lib/types";

/**
 * Mascota guía: ícono + burbuja de diálogo. Bloque autocontenido que cada
 * paso coloca donde corresponda (no es fijo, para evitar solapes y problemas
 * responsive). El texto cambia por paso; la burbuja hace crossfade.
 */
export function GuiaMascota({
  nombre,
  forma,
  texto,
  acento,
  textoKey,
}: {
  nombre: string;
  forma?: Forma;
  texto: string;
  acento: string;
  /** clave que dispara el crossfade de la burbuja al cambiar de texto */
  textoKey?: string;
}) {
  return (
    <div className="flex items-end gap-3">
      <div
        className="mascota-bob grid h-16 w-16 shrink-0 place-items-center rounded-full shadow-lg"
        style={{
          background: `radial-gradient(circle at 35% 30%, ${acento}33, ${acento}14)`,
          border: `2px solid ${acento}`,
        }}
        aria-hidden
      >
        <Icono forma={forma} size={30} style={{ color: acento }} />
      </div>
      <div className="relative min-w-0 flex-1">
        <div
          className="mb-1 text-xs font-semibold uppercase tracking-wider"
          style={{ color: acento }}
        >
          {nombre}
        </div>
        <div className="relative rounded-2xl rounded-bl-sm border border-borde bg-panel-2 px-4 py-3 text-[15px] leading-snug text-foreground/90">
          <AnimatePresence mode="wait">
            <motion.p
              key={textoKey ?? texto}
              initial={{ opacity: 0, y: 6, filter: "blur(2px)" }}
              animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, y: -4, filter: "blur(2px)" }}
              transition={{ duration: 0.22, ease: [0.23, 1, 0.32, 1] }}
            >
              {texto}
            </motion.p>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
