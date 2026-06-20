"use client";

import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";
import type { TopKItem } from "@/lib/types";
import { etiquetaMetrica } from "@/lib/format";

const COLORES = ["#38bdf8", "#a78bfa", "#94a3b8"];
const OMITIR = new Set(["n_especies", "costo", "factible"]);

export function MetricsRadar({ topK, acento }: { topK: TopKItem[]; acento: string }) {
  if (topK.length === 0) {
    return (
      <div className="tarjeta flex h-full min-h-[220px] items-center justify-center p-5 text-sm text-white/45">
        El radar de métricas aparece al terminar la corrida.
      </div>
    );
  }

  const claves = Object.keys(topK[0].metricas).filter(
    (k) => !OMITIR.has(k) && typeof topK[0].metricas[k] === "number"
  );

  const maxAbs: Record<string, number> = {};
  for (const k of claves) {
    maxAbs[k] = Math.max(
      ...topK.map((t) => Math.abs(Number(t.metricas[k] ?? 0))),
      1e-9
    );
  }

  const data = claves.map((k) => {
    const fila: Record<string, number | string> = { metrica: etiquetaMetrica(k) };
    topK.forEach((t, i) => {
      fila[`t${i}`] = Math.abs(Number(t.metricas[k] ?? 0)) / maxAbs[k];
    });
    return fila;
  });

  return (
    <div className="tarjeta p-5">
      <div className="mb-1 flex items-baseline justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted">
          Perfil de métricas
        </h3>
        <span className="text-xs text-white/45">magnitud normalizada</span>
      </div>
      <div className="h-60 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="72%">
            <PolarGrid stroke="#1e2a44" />
            <PolarAngleAxis dataKey="metrica" tick={{ fill: "#9fb2cf", fontSize: 11 }} />
            <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />
            {topK.map((_, i) => (
              <Radar
                key={i}
                name={`Top ${i + 1}`}
                dataKey={`t${i}`}
                stroke={i === 0 ? acento : COLORES[i % COLORES.length]}
                fill={i === 0 ? acento : COLORES[i % COLORES.length]}
                fillOpacity={i === 0 ? 0.35 : 0.12}
                strokeWidth={i === 0 ? 2 : 1}
                isAnimationActive={false}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-1 flex justify-center gap-4 text-xs text-white/55">
        {topK.map((_, i) => (
          <span key={i} className="inline-flex items-center gap-1.5">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ background: i === 0 ? acento : COLORES[i % COLORES.length] }}
            />
            Top {i + 1}
          </span>
        ))}
      </div>
    </div>
  );
}
