import * as React from "react";
import type { Forma } from "@/lib/types";

// Set de iconos de línea (estilo sobrio, sin emojis) por forma de dominio.
// Color vía `currentColor`; tamaño configurable. Reemplaza los emojis Unicode
// (inconsistentes entre sistemas) por una iconografía propia y uniforme.
export type IconoNombre = Forma | "default";

const TRAZOS: Record<IconoNombre, React.ReactNode> = {
  pez: (
    <>
      <ellipse cx="10.5" cy="12" rx="7" ry="4.3" />
      <path d="M17.5 12l4-2.6v5.2z" />
      <circle cx="7" cy="11" r="0.9" fill="currentColor" stroke="none" />
    </>
  ),
  planta: (
    <>
      <path d="M12 21v-8.5" />
      <path d="M12 12.5C12 9.5 9.4 7 6 7c0 3.4 2.6 5.5 6 5.5Z" />
      <path d="M12 12.5c0-3.4 2.6-6 6-6 0 3.4-2.6 6-6 6Z" />
    </>
  ),
  arbol: (
    <>
      <path d="M12 3l4.5 6.5h-2.7L18 16H6l4.2-6.5H7.5L12 3Z" />
      <path d="M12 16v5" />
    </>
  ),
  animal: (
    <>
      <path d="M3 10l9-5 9 5" />
      <path d="M5 10v10h14V10" />
      <path d="M10 20v-5h4v5" />
    </>
  ),
  default: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18" />
      <path d="M12 3c2.6 2.6 2.6 15.4 0 18M12 3c-2.6 2.6-2.6 15.4 0 18" />
    </>
  ),
};

export function Icono({
  forma = "default",
  size = 24,
  className,
  style,
}: {
  forma?: IconoNombre;
  size?: number;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth={1.6}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      style={style}
      aria-hidden
    >
      {TRAZOS[forma] ?? TRAZOS.default}
    </svg>
  );
}
