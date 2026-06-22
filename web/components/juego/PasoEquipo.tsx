"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";
import type { DominioMeta, DoneEvento } from "@/lib/types";
import type { EspecieMapa } from "@/components/tipos-escena";
import {
  metaMetrica,
  metricaMenorEsMejor,
  type Narrativa,
} from "@/lib/narrativa";
import { amigosYRivales, fortalezas } from "@/lib/juego";
import { fmtDinero } from "@/lib/format";
import { EscenaEcosistema } from "./EscenaEcosistema";

const EASE = [0.23, 1, 0.32, 1] as const;

export function PasoEquipo({
  dominio,
  narr,
  especies,
  done,
  onContinuar,
}: {
  dominio: DominioMeta;
  narr: Narrativa;
  especies: EspecieMapa;
  done: DoneEvento | null;
  onContinuar: () => void;
}) {
  const acento = dominio.tema.acento;

  const cartas = useMemo(() => {
    if (!done) return [];
    return done.mejor.activas
      .map((a) => ({ esp: especies.get(a.i), C: a.C }))
      .filter((x): x is { esp: NonNullable<ReturnType<EspecieMapa["get"]>>; C: number } => !!x.esp)
      .sort((a, b) => b.C - a.C);
  }, [done, especies]);

  const { amigos, rivales } = useMemo(
    () => amigosYRivales(done?.kappa_activas ?? []),
    [done]
  );
  const forts = useMemo(() => fortalezas(done, metricaMenorEsMejor), [done]);

  if (!done) {
    return (
      <p className="py-10 text-center text-white/50">No hay resultados todavía.</p>
    );
  }

  const nombre = (idx: number) => especies.get(idx)?.nombre ?? `#${idx}`;
  const color = (idx: number) => especies.get(idx)?.color ?? "#888";
  const factible = done.mejor.metricas.factible;
  const costo = done.mejor.metricas.costo;
  const totalInd = cartas.reduce((s, c) => s + c.C, 0);

  const aparece = (delay: number) => ({
    initial: { opacity: 0, y: 14 },
    animate: { opacity: 1, y: 0 },
    transition: { delay, duration: 0.34, ease: EASE },
  });

  const relaciones = [
    ...amigos.map((r) => ({ ...r, tipo: "amigo" as const })),
    ...rivales.map((r) => ({ ...r, tipo: "rival" as const })),
  ];

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col">
      <motion.h2
        {...aparece(0)}
        className="text-center text-2xl font-bold text-white sm:text-3xl"
      >
        Tu equipo ganador
      </motion.h2>
      <motion.p
        {...aparece(0.06)}
        className="mx-auto mt-2 max-w-lg text-center text-white/60"
      >
        {cartas.length} {narr.unidad} distintas · {totalInd} en total
      </motion.p>

      {/* Tu ecosistema ganador en 3D */}
      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.12, duration: 0.45, ease: EASE }}
        className="mt-5 h-[300px] sm:h-[380px]"
      >
        <EscenaEcosistema
          forma={dominio.tema.forma}
          estratos={dominio.estratos}
          especies={especies}
          ensamblaje={done.mejor.activas}
          tema={dominio.tema}
        />
      </motion.div>

      {/* Cartas de especies */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {cartas.map(({ esp, C }, i) => (
          <motion.div
            key={esp.idx}
            initial={{ opacity: 0, y: 14, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.25 + Math.min(i * 0.04, 0.4), duration: 0.3, ease: EASE }}
            className="relative overflow-hidden rounded-xl border border-borde bg-panel-2 p-3"
          >
            <div className="absolute inset-x-0 top-0 h-1" style={{ background: esp.color }} />
            <div className="flex items-center gap-2">
              <span
                className="h-3 w-3 shrink-0 rounded-full"
                style={{ background: esp.color }}
              />
              <span className="truncate text-sm font-medium text-white" title={esp.nombre}>
                {esp.nombre}
              </span>
            </div>
            <div className="mt-2 flex items-baseline justify-between">
              <span className="text-[11px] uppercase tracking-wide text-white/40">
                {esp.estrato}
              </span>
              <span className="font-mono text-lg" style={{ color: acento }}>
                ×{C}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Costo + cumple misión */}
      <motion.div
        {...aparece(0.4)}
        className="mt-6 flex flex-wrap items-center justify-center gap-3"
      >
        <span className="rounded-xl border border-borde bg-panel-2 px-4 py-2 text-sm text-white/80">
          💰 Costo: <span className="font-mono text-white">${fmtDinero(costo)}</span>
        </span>
        <motion.span
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.48, type: "spring", stiffness: 320, damping: 18 }}
          className="rounded-xl px-4 py-2 text-sm font-medium"
          style={{
            background: factible ? "#15803d33" : "#b91c1c33",
            color: factible ? "#86efac" : "#fca5a5",
          }}
        >
          {factible ? "✅ Cumple tu misión" : "⚠️ Se pasó de los límites"}
        </motion.span>
      </motion.div>

      {/* Amigos y rivales + Fortalezas */}
      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <motion.div
          {...aparece(0.5)}
          className="rounded-2xl border border-borde bg-panel-2 p-5"
        >
          <h3 className="text-sm font-semibold text-white">¿Quién se lleva con quién?</h3>
          <div className="mt-3 flex flex-col gap-2">
            {relaciones.map((r, i) => (
              <Relacion
                key={`${r.tipo}${i}`}
                a={nombre(r.i)}
                b={nombre(r.j)}
                ca={color(r.i)}
                cb={color(r.j)}
                tipo={r.tipo}
                delay={0.58 + i * 0.06}
              />
            ))}
            {relaciones.length === 0 && (
              <p className="text-sm text-white/45">
                Este equipo es tranquilo: nadie destaca como gran amigo ni rival.
              </p>
            )}
          </div>
        </motion.div>

        <motion.div
          {...aparece(0.56)}
          className="rounded-2xl border border-borde bg-panel-2 p-5"
        >
          <h3 className="text-sm font-semibold text-white">Fortalezas de tu diseño</h3>
          <div className="mt-3 flex flex-col gap-3">
            {forts.map((f, i) => {
              const m = metaMetrica(f.clave);
              const pct = Math.round(f.nivel * 100);
              return (
                <div key={f.clave}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-white/80">
                      <span aria-hidden>{m.emoji}</span> {m.etiqueta}
                    </span>
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.7 + i * 0.08, duration: 0.4 }}
                      className="font-mono text-xs text-white/50"
                    >
                      {pct}%
                    </motion.span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-panel">
                    <motion.div
                      className="h-full rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ delay: 0.64 + i * 0.08, duration: 0.7, ease: EASE }}
                      style={{ background: acento }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>
      </div>

      <motion.div {...aparece(0.7)} className="mt-8 flex justify-center">
        <button
          type="button"
          onClick={onContinuar}
          className="boton-juego rounded-2xl px-8 py-4 text-lg font-semibold text-[#04121f] shadow-lg"
          style={{ background: acento }}
        >
          ¿Cómo funcionó esto? →
        </button>
      </motion.div>
    </div>
  );
}

function Relacion({
  a,
  b,
  ca,
  cb,
  tipo,
  delay,
}: {
  a: string;
  b: string;
  ca: string;
  cb: string;
  tipo: "amigo" | "rival";
  delay: number;
}) {
  const amigo = tipo === "amigo";
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.3, ease: EASE }}
      className="flex items-center gap-2 text-sm"
    >
      <span
        className="grid h-6 w-6 shrink-0 place-items-center rounded-full text-xs"
        style={{ background: amigo ? "#15803d33" : "#b91c1c33" }}
        aria-hidden
      >
        {amigo ? "🟢" : "🔴"}
      </span>
      <span className="inline-flex items-center gap-1 truncate text-white/85">
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: ca }} />
        <span className="truncate">{a}</span>
      </span>
      <span className="text-white/40">{amigo ? "+" : "×"}</span>
      <span className="inline-flex items-center gap-1 truncate text-white/85">
        <span className="h-2.5 w-2.5 rounded-full" style={{ background: cb }} />
        <span className="truncate">{b}</span>
      </span>
    </motion.div>
  );
}
