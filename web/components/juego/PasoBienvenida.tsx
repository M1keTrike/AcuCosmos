"use client";

import { motion } from "framer-motion";
import { Icono, type IconoNombre } from "@/components/Icono";
import { LogoBioNexo } from "@/components/LogoBioNexo";

const MUNDOS: IconoNombre[] = ["pez", "planta", "arbol", "animal", "default"];
const EASE = [0.23, 1, 0.32, 1] as const;

export function PasoBienvenida({
  onComenzar,
  acento,
}: {
  onComenzar: () => void;
  acento: string;
}) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center text-center">
      {/* Marca BioNexo */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: EASE }}
        className="mb-7 flex items-center gap-2.5"
      >
        <LogoBioNexo size={44} />
        <span className="titulo-grad text-2xl font-bold tracking-tight">BioNexo</span>
      </motion.div>

      {/* Iconos de los mundos: entran escalonados y luego flotan */}
      <div className="mb-8 flex items-end gap-5 sm:gap-8" style={{ color: acento }}>
        {MUNDOS.map((nombre, i) => (
          <motion.span
            key={nombre}
            initial={{ opacity: 0, y: 24, scale: 0.6 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: i * 0.08, duration: 0.5, ease: EASE }}
          >
            <span
              className="mascota-bob inline-block"
              style={{ animationDelay: `${i * 0.25}s` }}
              aria-hidden
            >
              <Icono forma={nombre} size={44} />
            </span>
          </motion.span>
        ))}
      </div>

      <motion.h1
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5, ease: EASE }}
        className="max-w-3xl text-balance text-4xl font-bold leading-tight text-foreground sm:text-6xl"
      >
        Diseña el ecosistema perfecto
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.5, ease: EASE }}
        className="mt-5 max-w-xl text-pretty text-lg leading-relaxed text-foreground/70"
      >
        Tú dices qué quieres. Una computadora prueba{" "}
        <span className="font-semibold text-foreground">miles de combinaciones</span> y te
        entrega el mejor equipo de especies. Sin saber nada técnico: solo juega.
      </motion.p>

      <motion.button
        type="button"
        onClick={onComenzar}
        initial={{ opacity: 0, y: 14, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ delay: 0.62, duration: 0.45, ease: EASE }}
        className="boton-juego mt-10 rounded-2xl px-8 py-4 text-lg font-semibold text-white shadow-lg"
        style={{ background: acento }}
      >
        Empezar a diseñar →
      </motion.button>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.5 }}
        className="mt-6 text-sm text-foreground/40"
      >
        5 mundos · listo en menos de 2 minutos
      </motion.p>
    </div>
  );
}
