"use client";

import { useMemo, useState } from "react";
import type { EspecieMapa } from "./tipos-escena";
import type { Kappa } from "@/lib/types";

function colorKappa(v: number): string {
  if (v > 0) return `rgba(34,197,94,${0.18 + 0.82 * Math.min(1, v)})`;
  if (v < 0) return `rgba(239,68,68,${0.18 + 0.82 * Math.min(1, -v)})`;
  return "#16223a";
}

export function KappaHeatmap({
  kappa,
  especies,
  activas,
}: {
  kappa: Kappa;
  especies: EspecieMapa;
  activas: number[];
}) {
  const [hover, setHover] = useState<{ r: number; c: number } | null>(null);

  const filas = useMemo(() => {
    const lista = activas
      .map((idx) => especies.get(idx))
      .filter((e): e is NonNullable<typeof e> => !!e);
    lista.sort((a, b) => a.estrato_idx - b.estrato_idx || a.nombre.localeCompare(b.nombre));
    return lista;
  }, [activas, especies]);

  const lookup = useMemo(() => {
    const m = new Map<string, { v: number; proc?: string }>();
    for (const p of kappa.pares) {
      m.set(`${p.i}-${p.j}`, { v: p.valor, proc: p.procedencia });
    }
    return m;
  }, [kappa]);

  const par = (a: number, b: number) => {
    if (a === b) return { v: NaN, proc: undefined };
    const k = a < b ? `${a}-${b}` : `${b}-${a}`;
    return lookup.get(k) ?? { v: 0, proc: undefined };
  };

  if (filas.length === 0) {
    return (
      <div className="tarjeta flex h-full min-h-[220px] items-center justify-center p-5 text-sm text-white/45">
        Corre el AG para ver la matriz de compatibilidad de las especies elegidas.
      </div>
    );
  }

  const k = filas.length;
  const cell = 26;
  const labelW = 104;
  const W = labelW + k * cell + 8;
  const H = k * cell + 8;

  const fr = hover ? filas[hover.r] : undefined;
  const fc = hover ? filas[hover.c] : undefined;
  const h = fr && fc ? par(fr.idx, fc.idx) : null;

  return (
    <div className="tarjeta p-5">
      <div className="mb-1 flex items-baseline justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted">
          Compatibilidad κ
        </h3>
        <span className="text-xs text-white/45">{k} especies activas</span>
      </div>
      <div className="mb-3 flex items-center gap-3 text-xs text-white/55">
        <span className="inline-flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-sm" style={{ background: "rgba(34,197,94,0.9)" }} />
          sinergia
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-sm" style={{ background: "rgba(239,68,68,0.9)" }} />
          antagonismo
        </span>
      </div>

      <div className="relative w-full overflow-x-auto">
        <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full" style={{ maxWidth: W }}>
          {filas.map((fa, r) => (
            <g key={fa.idx}>
              <text
                x={labelW - 8}
                y={r * cell + cell / 2 + 4}
                textAnchor="end"
                fontSize={11}
                fill="#9fb2cf"
              >
                {fa.nombre.length > 16 ? fa.nombre.slice(0, 15) + "…" : fa.nombre}
              </text>
              {filas.map((fb, c) => {
                const p = par(fa.idx, fb.idx);
                const esDiag = r === c;
                return (
                  <rect
                    key={fb.idx}
                    x={labelW + c * cell}
                    y={r * cell}
                    width={cell - 2}
                    height={cell - 2}
                    rx={3}
                    fill={esDiag ? "#0a1120" : colorKappa(p.v)}
                    stroke={hover && hover.r === r && hover.c === c ? "#e8eef7" : "transparent"}
                    strokeWidth={1.5}
                    onMouseEnter={() => !esDiag && setHover({ r, c })}
                    onMouseLeave={() => setHover(null)}
                  />
                );
              })}
            </g>
          ))}
        </svg>
      </div>

      <div className="mt-2 h-10 text-sm">
        {h && fr && fc ? (
          <p className="text-white/80">
            <span className="font-medium">{fr.nombre}</span>
            <span className="mx-1.5 text-white/40">×</span>
            <span className="font-medium">{fc.nombre}</span>
            {" → "}
            <span
              className="font-mono"
              style={{ color: h.v > 0 ? "#86efac" : h.v < 0 ? "#fca5a5" : "#94a3b8" }}
            >
              {h.v.toFixed(2)}
            </span>
            {h.proc && (
              <span className="ml-2 rounded bg-white/10 px-1.5 py-0.5 text-[11px] text-white/60">
                {h.proc}
              </span>
            )}
          </p>
        ) : (
          <p className="text-white/40">Pasa el cursor sobre una celda para ver el par.</p>
        )}
      </div>
    </div>
  );
}
