"use client";

import { motion } from "framer-motion";
import type { Narrativa } from "@/lib/narrativa";

const EASE = [0.23, 1, 0.32, 1] as const;

const PASOS_IA = [
  {
    emoji: "🎲",
    titulo: "Probó al azar",
    texto: "Creó cientos de combinaciones distintas, sin saber cuál era buena.",
  },
  {
    emoji: "🏆",
    titulo: "Se quedó con las mejores",
    texto: "Calificó cada una y mezcló las ganadoras, con pequeños cambios al azar.",
  },
  {
    emoji: "🔁",
    titulo: "Repitió muchas rondas",
    texto: "Ronda tras ronda fueron mejorando, igual que la evolución en la naturaleza.",
  },
];

export function PasoReveal({
  narr,
  acento,
  onReiniciar,
  onExperto,
}: {
  narr: Narrativa;
  acento: string;
  onReiniciar: () => void;
  onExperto: () => void;
}) {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col">
      <motion.h2
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.34, ease: EASE }}
        className="text-center text-2xl font-bold text-white sm:text-3xl"
      >
        ¿Cómo funcionó?
      </motion.h2>
      <motion.p
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.07, duration: 0.34, ease: EASE }}
        className="mx-auto mt-2 max-w-lg text-center text-white/60"
      >
        Acabas de usar un <span className="font-semibold text-white">algoritmo genético</span>.
        Hizo esto por ti, en segundos:
      </motion.p>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        {PASOS_IA.map((p, i) => (
          <motion.div
            key={p.titulo}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.14 + i * 0.1, duration: 0.34, ease: EASE }}
            className="rounded-2xl border border-borde bg-panel-2 p-5 text-center"
          >
            <motion.div
              initial={{ scale: 0, rotate: -20 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.24 + i * 0.1, type: "spring", stiffness: 300, damping: 16 }}
              className="text-4xl"
              aria-hidden
            >
              {p.emoji}
            </motion.div>
            <h3 className="mt-3 font-semibold text-white">{p.titulo}</h3>
            <p className="mt-1 text-sm leading-snug text-white/65">{p.texto}</p>
          </motion.div>
        ))}
      </div>

      {/* Para qué sirve en la vida real */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.45, ease: EASE }}
        className="mt-8 rounded-2xl border p-6"
        style={{ borderColor: `${acento}55`, background: `${acento}12` }}
      >
        <h3
          className="text-sm font-semibold uppercase tracking-wider"
          style={{ color: acento }}
        >
          ¿Para qué sirve en la vida real?
        </h3>
        <p className="mt-2 text-lg leading-relaxed text-white/85">{narr.paraQueSirve}</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.62, duration: 0.4, ease: EASE }}
        className="mt-8 flex flex-wrap items-center justify-center gap-3"
      >
        <button
          type="button"
          onClick={onReiniciar}
          className="boton-juego rounded-2xl px-7 py-3.5 text-base font-semibold text-[#04121f] shadow-lg"
          style={{ background: acento }}
        >
          🔄 Probar otro mundo
        </button>
        <button
          type="button"
          onClick={onExperto}
          className="boton-acento rounded-2xl border border-borde bg-panel px-6 py-3.5 text-base text-white/75"
        >
          Ver el modo experto →
        </button>
      </motion.div>
    </div>
  );
}
