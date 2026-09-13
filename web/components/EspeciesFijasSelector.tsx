"use client";

import { useMemo, useState } from "react";
import type { EspecieCat } from "@/lib/types";

// Selector de "especies base (fijas)": el usuario marca especies del catálogo que
// el AG SIEMPRE incluirá. Lista buscable con chips de lo seleccionado.
export function EspeciesFijasSelector({
  especies,
  seleccion,
  onChange,
  disabled,
  acento,
}: {
  especies: EspecieCat[];
  seleccion: number[];
  onChange: (idx: number[]) => void;
  disabled?: boolean;
  acento: string;
}) {
  const [abierto, setAbierto] = useState(false);
  const [q, setQ] = useState("");
  const sel = new Set(seleccion);

  const filtradas = useMemo(() => {
    const t = q.trim().toLowerCase();
    if (!t) return especies;
    return especies.filter(
      (e) =>
        e.nombre.toLowerCase().includes(t) ||
        (e.grupo ?? "").toLowerCase().includes(t)
    );
  }, [especies, q]);

  const toggle = (i: number) => {
    const s = new Set(seleccion);
    if (s.has(i)) s.delete(i);
    else s.add(i);
    onChange([...s].sort((a, b) => a - b));
  };

  return (
    <div className="flex flex-col gap-1.5 text-sm">
      <button
        type="button"
        disabled={disabled}
        onClick={() => setAbierto((v) => !v)}
        className="flex items-center justify-between text-foreground/70"
      >
        <span>Especies base (fijas)</span>
        <span className="flex items-center gap-2">
          {seleccion.length > 0 && (
            <span
              className="rounded-full px-2 py-0.5 text-[11px] font-medium"
              style={{ background: `${acento}22`, color: acento }}
            >
              {seleccion.length}
            </span>
          )}
          <span className="text-foreground/40">{abierto ? "▲" : "▼"}</span>
        </span>
      </button>

      {seleccion.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {seleccion.map((i) => {
            const e = especies.find((x) => x.idx === i);
            if (!e) return null;
            return (
              <span
                key={i}
                className="inline-flex items-center gap-1 rounded-full border border-borde bg-panel-2 py-0.5 pl-1.5 pr-0.5 text-xs"
              >
                <span className="h-2 w-2 rounded-full" style={{ background: e.color }} />
                <span className="max-w-[110px] truncate text-foreground/85">{e.nombre}</span>
                <button
                  type="button"
                  disabled={disabled}
                  onClick={() => toggle(i)}
                  className="px-1 text-foreground/40 hover:text-foreground/90"
                  aria-label={`Quitar ${e.nombre}`}
                >
                  ×
                </button>
              </span>
            );
          })}
        </div>
      )}

      {abierto && (
        <div className="flex flex-col gap-2 rounded-lg border border-borde bg-panel-2 p-2">
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Buscar especie…"
            disabled={disabled}
            className="rounded-md border border-borde bg-panel px-2 py-1 text-sm text-foreground outline-none focus:border-foreground/40"
          />
          <div className="flex max-h-52 flex-col overflow-y-auto">
            {filtradas.map((e) => (
              <label
                key={e.idx}
                className="flex cursor-pointer items-center gap-2 rounded px-1 py-1 hover:bg-foreground/5"
              >
                <input
                  type="checkbox"
                  checked={sel.has(e.idx)}
                  onChange={() => toggle(e.idx)}
                  disabled={disabled}
                  style={{ accentColor: acento }}
                />
                <span
                  className="h-2.5 w-2.5 shrink-0 rounded-full"
                  style={{ background: e.color }}
                />
                <span className="truncate text-foreground/85">{e.nombre}</span>
                <span className="ml-auto truncate pl-2 text-[11px] text-foreground/40">
                  {e.grupo}
                </span>
              </label>
            ))}
            {filtradas.length === 0 && (
              <span className="px-1 py-2 text-xs text-foreground/40">Sin coincidencias.</span>
            )}
          </div>
          {seleccion.length > 0 && (
            <button
              type="button"
              disabled={disabled}
              onClick={() => onChange([])}
              className="self-start text-xs text-foreground/45 hover:text-foreground/80"
            >
              Limpiar selección
            </button>
          )}
        </div>
      )}

      <span className="text-xs text-foreground/40">
        El AG siempre incluirá estas especies y optimizará el resto a su alrededor.
      </span>
    </div>
  );
}
