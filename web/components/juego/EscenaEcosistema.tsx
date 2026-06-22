"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { AssemblyScene } from "@/components/AssemblyScene";
import type { EspecieMapa } from "@/components/tipos-escena";
import type { EstratoMeta, Forma, ItemEnsamblaje } from "@/lib/types";

// La escena 3D es client-only (usa WebGL): nunca se renderiza en el servidor.
const Escena3D = dynamic(() => import("./Escena3D").then((m) => m.Escena3D), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full rounded-2xl border border-borde bg-panel-2" />
  ),
});

function soportaWebGL(): boolean {
  try {
    const c = document.createElement("canvas");
    return !!(
      window.WebGLRenderingContext &&
      (c.getContext("webgl") || c.getContext("experimental-webgl"))
    );
  } catch {
    return false;
  }
}

interface Props {
  forma: Forma;
  estratos: EstratoMeta[];
  especies: EspecieMapa;
  ensamblaje: ItemEnsamblaje[];
  tema: { acento: string; acento2: string; fondo: string; fondo2: string };
}

/**
 * Render del ecosistema: 3D (Three.js) por defecto; si el equipo no soporta
 * WebGL, cae al canvas 2D original. Decide tras montar para evitar mismatches
 * de hidratación.
 */
export function EscenaEcosistema(props: Props) {
  const [modo, setModo] = useState<"cargando" | "3d" | "2d">("cargando");

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setModo(soportaWebGL() ? "3d" : "2d");
  }, []);

  if (modo === "cargando") {
    return <div className="h-full w-full rounded-2xl border border-borde bg-panel-2" />;
  }

  if (modo === "2d") {
    return <AssemblyScene {...props} />;
  }

  return (
    <div className="relative h-full w-full overflow-hidden rounded-2xl border border-borde">
      <Escena3D {...props} />
    </div>
  );
}
