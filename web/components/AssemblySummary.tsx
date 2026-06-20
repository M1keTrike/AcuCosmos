"use client";

import { useMemo } from "react";
import type { EspecieMapa } from "./tipos-escena";
import type { DoneEvento, GenEvento } from "@/lib/types";
import { etiquetaMetrica, fmt, fmtDinero } from "@/lib/format";

export function AssemblySummary({
  gen,
  done,
  especies,
  acento,
}: {
  gen: GenEvento | null;
  done: DoneEvento | null;
  especies: EspecieMapa;
  acento: string;
}) {
  const chips = useMemo(() => {
    if (!gen) return [];
    return gen.ensamblaje
      .map((it) => ({ esp: especies.get(it.i), C: it.C }))
      .filter((x): x is { esp: NonNullable<ReturnType<EspecieMapa["get"]>>; C: number } => !!x.esp)
      .sort((a, b) => b.esp.estrato_idx - a.esp.estrato_idx || b.C - a.C);
  }, [gen, especies]);

  if (!gen) {
    return (
      <div className="tarjeta flex h-full min-h-[220px] items-center justify-center p-5 text-sm text-white/45">
        Aquí verás el mejor ensamblaje y sus métricas.
      </div>
    );
  }

  const totalInd = gen.ensamblaje.reduce((s, it) => s + it.C, 0);
  const metricas = Object.entries(gen.metricas);

  return (
    <div className="tarjeta flex flex-col gap-4 p-5">
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted">
          Mejor ensamblaje
        </h3>
        {done && (
          <span className="text-xs text-white/45">sitio: {done.mejor.sitio_nombre}</span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
        <Stat label="Aptitud F" valor={fmt(gen.apt_mejor)} color={acento} />
        <Stat label="Especies" valor={String(gen.ensamblaje.length)} />
        <Stat label="Individuos" valor={String(totalInd)} />
        <Stat label="Costo" valor={fmtDinero(gen.costo)} />
      </div>

      <div className="flex flex-wrap gap-1.5">
        {metricas.map(([k, v]) => (
          <span
            key={k}
            className="rounded-lg border border-borde bg-panel-2 px-2.5 py-1 text-xs"
          >
            <span className="text-white/55">{etiquetaMetrica(k)}</span>{" "}
            <span className="font-mono text-white/90">{fmt(typeof v === "number" ? v : null)}</span>
          </span>
        ))}
        <span
          className="rounded-lg px-2.5 py-1 text-xs font-medium"
          style={{
            background: gen.factible ? "#15803d33" : "#b91c1c33",
            color: gen.factible ? "#86efac" : "#fca5a5",
          }}
        >
          {gen.factible ? "factible" : "inviable"}
        </span>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {chips.map(({ esp, C }) => (
          <span
            key={esp.idx}
            className="inline-flex items-center gap-1.5 rounded-full border border-borde bg-panel-2 py-1 pl-2 pr-2.5 text-xs"
            title={`${esp.nombre} · ${esp.estrato}`}
          >
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: esp.color }} />
            <span className="max-w-[140px] truncate text-white/85">{esp.nombre}</span>
            <span className="font-mono text-white/55">×{C}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function Stat({ label, valor, color }: { label: string; valor: string; color?: string }) {
  return (
    <div className="rounded-xl border border-borde bg-panel-2 px-3 py-2">
      <div className="text-[11px] uppercase tracking-wide text-white/45">{label}</div>
      <div className="font-mono text-lg" style={{ color: color ?? "#e8eef7" }}>
        {valor}
      </div>
    </div>
  );
}
