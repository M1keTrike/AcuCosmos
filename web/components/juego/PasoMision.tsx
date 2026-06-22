"use client";

import {
  AnimatePresence,
  animate,
  motion,
  useMotionValue,
  useReducedMotion,
  useTransform,
} from "framer-motion";
import { useEffect } from "react";
import type { DominioMeta, Escenario } from "@/lib/types";
import type { Narrativa } from "@/lib/narrativa";
import { briefingDeEscenario } from "@/lib/juego";

const EASE = [0.23, 1, 0.32, 1] as const;

export function PasoMision({
  dominio,
  narr,
  escenarios,
  escenarioSel,
  onElegirEscenario,
  cargando,
  onAtras,
  onComenzar,
}: {
  dominio: DominioMeta;
  narr: Narrativa;
  escenarios: Escenario[];
  escenarioSel: string;
  onElegirEscenario: (nombre: string) => void;
  cargando: boolean;
  onAtras: () => void;
  onComenzar: () => void;
}) {
  const acento = dominio.tema.acento;
  const esc = escenarios.find((e) => String(e.nombre ?? "") === escenarioSel);
  const brief = briefingDeEscenario(esc);

  // Entrada por bloques con un retardo creciente (stagger manual).
  const aparece = (delay: number) => ({
    initial: { opacity: 0, y: 14 },
    animate: { opacity: 1, y: 0 },
    transition: { delay, duration: 0.34, ease: EASE },
  });

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col">
      <motion.div {...aparece(0)} className="flex items-center gap-3">
        <span className="text-4xl" aria-hidden>
          {dominio.emoji}
        </span>
        <div>
          <h2 className="text-2xl font-bold text-white">{narr.misionTitulo}</h2>
          <p className="text-sm text-white/55">Elige tu reto y empezamos.</p>
        </div>
      </motion.div>

      {/* Retos (escenarios) */}
      <motion.h3
        {...aparece(0.08)}
        className="mt-8 text-sm font-semibold uppercase tracking-wider text-muted"
      >
        Tu reto
      </motion.h3>
      {cargando ? (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <div
              key={i}
              className="h-16 animate-pulse rounded-xl border border-borde bg-panel-2"
            />
          ))}
        </div>
      ) : (
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          {escenarios.map((e, i) => {
            const nombre = String(e.nombre ?? `Reto ${i + 1}`);
            const activo = nombre === escenarioSel;
            return (
              <motion.button
                key={i}
                type="button"
                onClick={() => onElegirEscenario(nombre)}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.14 + i * 0.05, duration: 0.3, ease: EASE }}
                whileTap={{ scale: 0.98 }}
                className="boton-juego flex items-center gap-3 rounded-xl border p-4 text-left"
                style={{
                  borderColor: activo ? acento : "var(--borde)",
                  background: activo ? `${acento}1a` : "var(--panel-2)",
                  boxShadow: activo ? `0 0 0 1px ${acento}, 0 8px 24px ${acento}22` : "none",
                  transition: "border-color 180ms, background 180ms, box-shadow 220ms",
                }}
              >
                <span
                  className="grid h-6 w-6 shrink-0 place-items-center rounded-full text-xs"
                  style={{
                    border: `2px solid ${activo ? acento : "var(--borde)"}`,
                    background: activo ? acento : "transparent",
                    color: "#04121f",
                    transition: "background 180ms, border-color 180ms",
                  }}
                >
                  <AnimatePresence>
                    {activo && (
                      <motion.span
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        transition={{ duration: 0.2, ease: EASE }}
                      >
                        ✓
                      </motion.span>
                    )}
                  </AnimatePresence>
                </span>
                <span className="font-medium capitalize text-white">{nombre}</span>
              </motion.button>
            );
          })}
        </div>
      )}

      {/* Briefing del reto elegido */}
      <motion.h3
        {...aparece(0.24)}
        className="mt-8 text-sm font-semibold uppercase tracking-wider text-muted"
      >
        Tu misión
      </motion.h3>
      <div className="mt-3 grid gap-3 sm:grid-cols-3">
        <motion.div {...aparece(0.28)}>
          <Dato etiqueta="Presupuesto" emoji="💰">
            {brief.presupuesto != null ? (
              <Contador valor={brief.presupuesto} prefijo="$" />
            ) : (
              <ValorTexto valor="Libre" />
            )}
          </Dato>
        </motion.div>
        <motion.div {...aparece(0.33)}>
          <Dato etiqueta={`Mín. ${narr.unidad}`} emoji="🔽">
            <ValorTexto valor={brief.minEspecies != null ? String(brief.minEspecies) : "—"} />
          </Dato>
        </motion.div>
        <motion.div {...aparece(0.38)}>
          <Dato etiqueta={`Máx. ${narr.unidad}`} emoji="🔼">
            <ValorTexto valor={brief.maxEspecies != null ? String(brief.maxEspecies) : "—"} />
          </Dato>
        </motion.div>
      </div>

      <motion.div
        {...aparece(0.46)}
        className="mt-auto flex items-center justify-between gap-3 pt-10"
      >
        <button
          type="button"
          onClick={onAtras}
          className="boton-acento rounded-full border border-borde bg-panel px-4 py-2.5 text-sm text-white/70"
        >
          ← Otro mundo
        </button>
        <button
          type="button"
          onClick={onComenzar}
          disabled={cargando || !escenarioSel}
          className="boton-juego rounded-2xl px-8 py-4 text-lg font-semibold text-[#04121f] shadow-lg"
          style={{ background: acento }}
        >
          ¡Que evolucione! →
        </button>
      </motion.div>
    </div>
  );
}

function Dato({
  etiqueta,
  emoji,
  children,
}: {
  etiqueta: string;
  emoji: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-borde bg-panel-2 p-4">
      <div className="text-2xl" aria-hidden>
        {emoji}
      </div>
      <div className="mt-1 text-[11px] uppercase tracking-wide text-white/45">
        {etiqueta}
      </div>
      <div className="font-mono text-lg text-white">{children}</div>
    </div>
  );
}

// Valor de texto que hace crossfade al cambiar (p.ej. al elegir otro reto).
function ValorTexto({ valor }: { valor: string }) {
  return (
    <AnimatePresence mode="wait">
      <motion.span
        key={valor}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.2, ease: EASE }}
        className="inline-block"
      >
        {valor}
      </motion.span>
    </AnimatePresence>
  );
}

// Número con count-up animado (respeta reduced-motion).
function Contador({ valor, prefijo = "" }: { valor: number; prefijo?: string }) {
  const reduce = useReducedMotion();
  const mv = useMotionValue(0);
  const salida = useTransform(mv, (v) => prefijo + Math.round(v).toLocaleString("es-MX"));

  useEffect(() => {
    if (reduce) {
      mv.set(valor);
      return;
    }
    const control = animate(mv, valor, { duration: 0.6, ease: EASE });
    return () => control.stop();
  }, [valor, reduce, mv]);

  return <motion.span>{salida}</motion.span>;
}
