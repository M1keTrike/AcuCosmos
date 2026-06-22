"use client";

import { useMemo } from "react";
import { useReducedMotion } from "framer-motion";

// Pseudo-aleatorio determinista y puro (sin Math.random): apto para render.
function frand(n: number): number {
  const x = Math.sin(n * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

/**
 * Confeti ligero (sin dependencias): piezas absolutas que caen con un keyframe
 * CSS. Patrón determinista por índice. Respeta prefers-reduced-motion.
 */
export function Confeti({
  activo,
  colores,
  piezas = 80,
}: {
  activo: boolean;
  colores: string[];
  piezas?: number;
}) {
  const reduce = useReducedMotion();

  const trozos = useMemo(
    () =>
      Array.from({ length: piezas }, (_, i) => ({
        left: frand(i + 1) * 100,
        delay: frand(i + 2) * 0.6,
        dur: 2.4 + frand(i + 3) * 1.8,
        size: 6 + frand(i + 4) * 8,
        color: colores[i % colores.length],
        rot: frand(i + 5) * 360,
        redondo: frand(i + 6) < 0.5,
      })),
    [piezas, colores]
  );

  if (!activo || reduce) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden" aria-hidden>
      {trozos.map((t, i) => (
        <span
          key={i}
          style={{
            position: "absolute",
            top: 0,
            left: `${t.left}%`,
            width: t.size,
            height: t.size,
            background: t.color,
            borderRadius: t.redondo ? "50%" : "2px",
            transform: `rotate(${t.rot}deg)`,
            animation: `confeti-caida ${t.dur}s var(--ease-out) ${t.delay}s forwards`,
          }}
        />
      ))}
    </div>
  );
}
