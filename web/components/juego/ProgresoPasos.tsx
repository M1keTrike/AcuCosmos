"use client";

import type { PasoId } from "@/lib/narrativa";

// Pasos visibles en la barra de progreso (la bienvenida no cuenta).
const PASOS: { id: PasoId; etiqueta: string }[] = [
  { id: "mundo", etiqueta: "Mundo" },
  { id: "mision", etiqueta: "Misión" },
  { id: "evolucion", etiqueta: "Evolución" },
  { id: "equipo", etiqueta: "Equipo" },
  { id: "reveal", etiqueta: "Listo" },
];

export function ProgresoPasos({ actual, acento }: { actual: PasoId; acento: string }) {
  const idx = PASOS.findIndex((p) => p.id === actual);

  return (
    <ol className="flex items-center justify-center gap-2 sm:gap-3" aria-label="Progreso">
      {PASOS.map((p, i) => {
        const hecho = i < idx;
        const activo = i === idx;
        return (
          <li key={p.id} className="flex items-center gap-2 sm:gap-3">
            <div className="flex items-center gap-2">
              <span
                className="grid h-7 w-7 place-items-center rounded-full text-xs font-semibold transition-colors"
                style={{
                  background: activo || hecho ? acento : "var(--panel-2)",
                  color: activo || hecho ? "#04121f" : "var(--muted)",
                  border: `1px solid ${activo || hecho ? acento : "var(--borde)"}`,
                }}
              >
                {hecho ? "✓" : i + 1}
              </span>
              <span
                className={`hidden text-sm sm:inline ${
                  activo ? "font-semibold text-white" : "text-white/55"
                }`}
              >
                {p.etiqueta}
              </span>
            </div>
            {i < PASOS.length - 1 && (
              <span
                className="h-px w-5 sm:w-8"
                style={{ background: hecho ? acento : "var(--borde)" }}
              />
            )}
          </li>
        );
      })}
    </ol>
  );
}
