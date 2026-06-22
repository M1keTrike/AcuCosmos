"use client";

import { useMemo } from "react";
import type { DominioMeta } from "@/lib/types";
import type { RunStream } from "@/lib/useRunStream";
import type { EspecieMapa } from "@/components/tipos-escena";
import { EscenaEcosistema } from "./EscenaEcosistema";
import { DEFAULTS_RUN, puntajeDesdeF } from "@/lib/juego";

export function PasoEvolucion({
  dominio,
  especies,
  run,
  onVerEquipo,
}: {
  dominio: DominioMeta;
  especies: EspecieMapa;
  run: RunStream;
  onVerEquipo: () => void;
}) {
  const acento = dominio.tema.acento;
  const total = DEFAULTS_RUN.generaciones;

  const ultima = run.gens[run.gens.length - 1] ?? null;
  const ensamblaje = ultima?.ensamblaje ?? [];

  // Mejor puntaje visto (la evolución mejora ronda a ronda).
  const puntaje = useMemo(() => {
    const mejor = run.gens.reduce((m, g) => Math.max(m, g.apt_mejor ?? 0), 0);
    return puntajeDesdeF(mejor);
  }, [run.gens]);

  const ronda = Math.min(run.gens.length, total);
  const progreso = run.estado === "listo" ? 1 : Math.min(ronda / total, 0.99);
  const corriendo = run.estado === "corriendo";
  const listo = run.estado === "listo";

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col">
      <h2 className="text-center text-2xl font-bold text-white sm:text-3xl">
        {listo ? "¡Listo! La IA encontró el mejor diseño" : "La IA está diseñando…"}
      </h2>

      {/* Escena en vivo (3D Three.js, con fallback 2D) */}
      <div className="mt-5 h-[340px] sm:h-[440px]">
        <EscenaEcosistema
          forma={dominio.tema.forma}
          estratos={dominio.estratos}
          especies={especies}
          ensamblaje={ensamblaje}
          tema={dominio.tema}
        />
      </div>

      {/* Panel de progreso / puntaje */}
      <div className="mt-5 rounded-2xl border border-borde bg-panel-2 p-5">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="text-[11px] uppercase tracking-wide text-white/45">
              Puntaje del diseño
            </div>
            <div
              key={puntaje}
              className="pop-puntaje font-mono text-4xl font-bold"
              style={{ color: acento }}
            >
              {puntaje.toLocaleString("es-MX")}
            </div>
          </div>
          <div className="text-right">
            <div className="text-[11px] uppercase tracking-wide text-white/45">
              Ronda
            </div>
            <div className="font-mono text-2xl text-white">
              {ronda}
              <span className="text-white/40"> / {total}</span>
            </div>
          </div>
        </div>

        {/* Barra de progreso */}
        <div className="mt-4 h-2.5 w-full overflow-hidden rounded-full bg-panel">
          <div
            className="h-full rounded-full transition-[width] duration-300 ease-out"
            style={{ width: `${progreso * 100}%`, background: acento }}
          />
        </div>

        {run.estado === "error" && (
          <p className="mt-4 text-sm text-red-300">
            Algo salió mal con el motor. Vuelve a “Otro mundo” e inténtalo de nuevo.
          </p>
        )}
      </div>

      {/* Acción */}
      <div className="mt-6 flex justify-center">
        <button
          type="button"
          onClick={onVerEquipo}
          disabled={!listo}
          className="boton-juego rounded-2xl px-8 py-4 text-lg font-semibold text-[#04121f] shadow-lg disabled:bg-panel disabled:text-white/40"
          style={listo ? { background: acento } : undefined}
        >
          {corriendo ? "Evolucionando…" : "Conoce a tu equipo →"}
        </button>
      </div>
    </div>
  );
}
