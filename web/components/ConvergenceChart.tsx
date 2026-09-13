"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { GenEvento } from "@/lib/types";

export function ConvergenceChart({
  gens,
  genIdx,
  acento,
}: {
  gens: GenEvento[];
  genIdx: number;
  acento: string;
}) {
  const data = gens.map((g) => ({
    gen: g.generacion,
    mejor: g.apt_mejor,
    promedio: g.apt_promedio,
    peor: g.apt_peor,
  }));
  const genMarca = gens[genIdx]?.generacion;

  return (
    <div className="tarjeta p-4">
      <div className="mb-2 flex items-baseline justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted">
          Convergencia del AG
        </h3>
        <span className="text-xs text-foreground/45">aptitud F por generación</span>
      </div>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 6, right: 10, bottom: 0, left: -18 }}>
            <CartesianGrid stroke="#c9d6d1" strokeDasharray="3 3" />
            <XAxis
              dataKey="gen"
              stroke="#4a5c58"
              fontSize={11}
              tickLine={false}
              minTickGap={24}
            />
            <YAxis stroke="#4a5c58" fontSize={11} tickLine={false} width={48} />
            <Tooltip
              contentStyle={{
                background: "#ffffff",
                border: "1px solid #c9d6d1",
                borderRadius: 10,
                fontSize: 12,
              }}
              labelStyle={{ color: "#4a5c58" }}
              labelFormatter={(v) => `Generación ${v}`}
            />
            {genMarca !== undefined && (
              <ReferenceLine x={genMarca} stroke={acento} strokeDasharray="4 4" />
            )}
            <Line
              type="monotone"
              dataKey="peor"
              name="peor"
              stroke="#94a3b8"
              strokeWidth={1}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="promedio"
              name="promedio"
              stroke="#e0922b"
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="mejor"
              name="mejor"
              stroke={acento}
              strokeWidth={2.4}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-1 flex gap-4 text-xs text-foreground/55">
        <Leyenda color={acento} label="mejor" />
        <Leyenda color="#e0922b" label="promedio" />
        <Leyenda color="#94a3b8" label="peor" />
      </div>
    </div>
  );
}

function Leyenda({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}
