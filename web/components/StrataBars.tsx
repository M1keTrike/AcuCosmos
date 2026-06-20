"use client";

import { useMemo } from "react";
import type { EspecieMapa } from "./tipos-escena";
import type { EstratoMeta, ItemEnsamblaje } from "@/lib/types";

export function StrataBars({
  estratos,
  especies,
  ensamblaje,
  acento,
}: {
  estratos: EstratoMeta[];
  especies: EspecieMapa;
  ensamblaje: ItemEnsamblaje[];
  acento: string;
}) {
  const conteo = useMemo(() => {
    const c = new Array(estratos.length).fill(0);
    for (const it of ensamblaje) {
      const e = especies.get(it.i);
      if (e && e.estrato_idx >= 0 && e.estrato_idx < c.length) c[e.estrato_idx] += it.C;
    }
    return c;
  }, [ensamblaje, especies, estratos.length]);

  const max = Math.max(1, ...conteo);

  return (
    <div className="tarjeta p-5">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted">
        Distribución por estrato
      </h3>
      <div className="flex flex-col gap-2.5">
        {[...estratos]
          .slice()
          .reverse()
          .map((e) => {
            const n = conteo[e.idx] ?? 0;
            return (
              <div key={e.idx} className="flex items-center gap-3">
                <span className="w-28 shrink-0 truncate text-right text-xs text-white/65">
                  {e.etiqueta}
                </span>
                <div className="h-5 flex-1 overflow-hidden rounded-md bg-panel-2">
                  <div
                    className="h-full rounded-md transition-[width] duration-500 ease-out"
                    style={{ width: `${(n / max) * 100}%`, background: acento }}
                  />
                </div>
                <span className="w-8 shrink-0 text-right font-mono text-xs text-white/80">
                  {n}
                </span>
              </div>
            );
          })}
      </div>
    </div>
  );
}
