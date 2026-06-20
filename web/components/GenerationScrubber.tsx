"use client";

import { useEffect, useRef, useState } from "react";
import type { GenEvento } from "@/lib/types";
import { fmt } from "@/lib/format";

export function GenerationScrubber({
  gens,
  genIdx,
  onChange,
  acento,
  disabled,
}: {
  gens: GenEvento[];
  genIdx: number;
  onChange: (idx: number) => void;
  acento: string;
  disabled: boolean;
}) {
  const [playing, setPlaying] = useState(false);
  const idxRef = useRef(genIdx);
  idxRef.current = genIdx;

  const total = gens.length;
  const max = Math.max(0, total - 1);

  useEffect(() => {
    if (!playing || total <= 1) return;
    const id = setInterval(() => {
      const sig = idxRef.current >= max ? 0 : idxRef.current + 1;
      onChange(sig);
    }, 110);
    return () => clearInterval(id);
  }, [playing, total, max, onChange]);

  useEffect(() => {
    if (disabled) setPlaying(false);
  }, [disabled]);

  const actual = gens[genIdx];

  return (
    <div className="tarjeta flex items-center gap-4 p-4">
      <button
        type="button"
        disabled={disabled || total <= 1}
        onClick={() => setPlaying((p) => !p)}
        className="boton-acento flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-black"
        style={{ background: acento }}
        aria-label={playing ? "Pausar" : "Reproducir evolución"}
      >
        {playing ? "❚❚" : "▶"}
      </button>

      <div className="flex-1">
        <div className="mb-1 flex justify-between text-xs text-white/55">
          <span>
            Generación{" "}
            <span className="font-mono text-white/90">{actual?.generacion ?? 0}</span>
            {" / "}
            {gens[max]?.generacion ?? 0}
          </span>
          <span>
            F ={" "}
            <span className="font-mono" style={{ color: acento }}>
              {fmt(actual?.apt_mejor)}
            </span>
            {actual && (
              <span
                className="ml-2 rounded px-1.5 py-0.5 text-[10px]"
                style={{
                  background: actual.factible ? "#15803d33" : "#b91c1c33",
                  color: actual.factible ? "#86efac" : "#fca5a5",
                }}
              >
                {actual.factible ? "factible" : "inviable"}
              </span>
            )}
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={max}
          value={genIdx}
          disabled={disabled || total <= 1}
          onChange={(e) => {
            setPlaying(false);
            onChange(Number(e.target.value));
          }}
          className="w-full"
          style={{ accentColor: acento }}
        />
      </div>
    </div>
  );
}
