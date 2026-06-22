"use client";

import { useState } from "react";
import { JuegoGuiado } from "@/components/juego/JuegoGuiado";
import { ExpertoApp } from "@/components/experto/ExpertoApp";

type Modo = "juego" | "experto";

export default function Home() {
  const [modo, setModo] = useState<Modo>("juego");

  if (modo === "experto") {
    return (
      <div className="relative flex flex-1 flex-col">
        <button
          type="button"
          onClick={() => setModo("juego")}
          className="boton-acento fixed right-4 top-4 z-40 rounded-full border border-borde bg-panel px-3 py-1.5 text-xs text-white/70"
          title="Volver al modo guiado"
        >
          ← Modo juego
        </button>
        <ExpertoApp />
      </div>
    );
  }

  return <JuegoGuiado onExperto={() => setModo("experto")} />;
}
