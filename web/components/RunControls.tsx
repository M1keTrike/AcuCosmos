"use client";

import { useEffect, useState } from "react";
import type { Escenario } from "@/lib/types";
import type { EstadoRun } from "@/lib/useRunStream";

export interface ConfigRun {
  escenario: string;
  seed: number;
  generaciones: number;
  poblacion: number;
}

export function RunControls({
  escenarios,
  acento,
  estado,
  onCorrer,
}: {
  escenarios: Escenario[];
  acento: string;
  estado: EstadoRun;
  onCorrer: (c: ConfigRun) => void;
}) {
  const [escenario, setEscenario] = useState("");
  const [seed, setSeed] = useState(7);
  const [generaciones, setGeneraciones] = useState(120);
  const [poblacion, setPoblacion] = useState(60);

  useEffect(() => {
    if (!escenario && escenarios.length > 0) {
      setEscenario(String(escenarios[0].nombre ?? ""));
    }
  }, [escenarios, escenario]);

  const corriendo = estado === "corriendo";

  return (
    <div className="tarjeta flex flex-col gap-4 p-5">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-muted">
        Configuración de la corrida
      </h3>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="text-white/70">Escenario</span>
        <select
          value={escenario}
          onChange={(e) => setEscenario(e.target.value)}
          disabled={corriendo}
          className="rounded-lg border border-borde bg-panel-2 px-3 py-2 text-white outline-none focus:border-white/40"
        >
          {escenarios.map((s, i) => (
            <option key={i} value={String(s.nombre ?? i)}>
              {String(s.nombre ?? `escenario ${i + 1}`)}
            </option>
          ))}
        </select>
      </label>

      <div className="grid grid-cols-2 gap-3">
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="text-white/70">Semilla</span>
          <input
            type="number"
            value={seed}
            onChange={(e) => setSeed(Number(e.target.value))}
            disabled={corriendo}
            className="rounded-lg border border-borde bg-panel-2 px-3 py-2 text-white outline-none focus:border-white/40"
          />
        </label>
        <div className="flex flex-col justify-end text-xs text-white/45">
          <span>Semilla fija ⇒ corrida reproducible (ideal para la demo).</span>
        </div>
      </div>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="flex justify-between text-white/70">
          <span>Generaciones</span>
          <span className="font-mono text-white/90">{generaciones}</span>
        </span>
        <input
          type="range"
          min={20}
          max={250}
          step={10}
          value={generaciones}
          onChange={(e) => setGeneraciones(Number(e.target.value))}
          disabled={corriendo}
          style={{ accentColor: acento }}
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="flex justify-between text-white/70">
          <span>Población</span>
          <span className="font-mono text-white/90">{poblacion}</span>
        </span>
        <input
          type="range"
          min={20}
          max={160}
          step={10}
          value={poblacion}
          onChange={(e) => setPoblacion(Number(e.target.value))}
          disabled={corriendo}
          style={{ accentColor: acento }}
        />
      </label>

      <button
        type="button"
        disabled={corriendo || !escenario}
        onClick={() => onCorrer({ escenario, seed, generaciones, poblacion })}
        className="boton-acento mt-1 flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-base font-semibold text-black"
        style={{ background: acento }}
      >
        {corriendo ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-black/30 border-t-black" />
            Evolucionando…
          </>
        ) : (
          <>▶ Ejecutar AG</>
        )}
      </button>
    </div>
  );
}
