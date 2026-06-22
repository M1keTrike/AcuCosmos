"use client";

import { AnimatePresence, MotionConfig, motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { apiCatalogo, apiDominios, apiEscenarios } from "@/lib/api";
import type { Catalogo, DominioMeta, Escenario } from "@/lib/types";
import { narrativa, type PasoId } from "@/lib/narrativa";
import { DEFAULTS_RUN, semillaAleatoria } from "@/lib/juego";
import { useRunStream } from "@/lib/useRunStream";
import type { EspecieMapa } from "@/components/tipos-escena";
import { GuiaMascota } from "./GuiaMascota";
import { ProgresoPasos } from "./ProgresoPasos";
import { Confeti } from "./Confeti";
import { PasoBienvenida } from "./PasoBienvenida";
import { PasoMundo } from "./PasoMundo";
import { PasoMision } from "./PasoMision";
import { PasoEvolucion } from "./PasoEvolucion";
import { PasoEquipo } from "./PasoEquipo";
import { PasoReveal } from "./PasoReveal";

const ACENTO_BASE = "#38bdf8";

export function JuegoGuiado({ onExperto }: { onExperto: () => void }) {
  const [paso, setPaso] = useState<PasoId>("bienvenida");

  const [dominios, setDominios] = useState<DominioMeta[]>([]);
  const [cargandoDom, setCargandoDom] = useState(true);
  const [errorDom, setErrorDom] = useState<string | null>(null);

  const [sel, setSel] = useState<DominioMeta | null>(null);
  const [escenarios, setEscenarios] = useState<Escenario[]>([]);
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [cargandoDatos, setCargandoDatos] = useState(false);
  const [escenarioSel, setEscenarioSel] = useState<string>("");

  const run = useRunStream();

  // Catálogo de dominios al montar.
  useEffect(() => {
    apiDominios()
      .then((d) => setDominios(d.filter((x) => !x.error)))
      .catch((e) => setErrorDom(String(e)))
      .finally(() => setCargandoDom(false));
  }, []);

  // Carga de datos del dominio elegido (el loading se enciende en el handler).
  useEffect(() => {
    if (!sel) return;
    let vivo = true;
    Promise.all([apiEscenarios(sel.id), apiCatalogo(sel.id)])
      .then(([esc, cat]) => {
        if (!vivo) return;
        setEscenarios(esc);
        setCatalogo(cat);
        setEscenarioSel(String(esc[0]?.nombre ?? ""));
      })
      .catch(() => vivo && setEscenarios([]))
      .finally(() => vivo && setCargandoDatos(false));
    return () => {
      vivo = false;
    };
  }, [sel]);

  const especies: EspecieMapa = useMemo(() => {
    const m = new Map();
    catalogo?.especies.forEach((e) => m.set(e.idx, e));
    return m;
  }, [catalogo]);

  const narr = useMemo(() => (sel ? narrativa(sel) : null), [sel]);
  const acento = sel?.tema.acento ?? ACENTO_BASE;

  // --- navegación --------------------------------------------------------- //
  const elegirMundo = (d: DominioMeta) => {
    setCargandoDatos(true);
    setSel(d);
    run.reset();
    setPaso("mision");
  };

  const empezarMision = () => {
    if (!sel) return;
    run.correr({
      dom: sel.id,
      escenario: escenarioSel || undefined,
      seed: semillaAleatoria(),
      generaciones: DEFAULTS_RUN.generaciones,
      poblacion: DEFAULTS_RUN.poblacion,
    });
    setPaso("evolucion");
  };

  const reiniciar = () => {
    run.reset();
    setSel(null);
    setCatalogo(null);
    setEscenarios([]);
    setPaso("mundo");
  };

  // --- mascota ------------------------------------------------------------ //
  const mascNombre = narr?.mascota ?? "Eco";
  const mascEmoji = narr?.emoji ?? "🌍";
  const mascTexto = (() => {
    if (paso === "bienvenida")
      return "¡Hola! Soy tu guía. Vamos a diseñar juntos el ecosistema perfecto: tú eliges qué quieres y la computadora prueba miles de combinaciones por ti.";
    if (paso === "mundo")
      return "Elige el mundo que quieras diseñar. Cada uno es un reto distinto.";
    return narr?.dialogos[paso] ?? "";
  })();

  const conProgreso = paso !== "bienvenida";

  return (
    <MotionConfig reducedMotion="user">
    <div className="relative mx-auto flex min-h-[100dvh] w-full max-w-6xl flex-col px-4 py-5 sm:px-6">
      <Confeti
        activo={paso === "equipo"}
        colores={[acento, sel?.tema.acento2 ?? "#a78bfa", "#fde047", "#ffffff"]}
      />

      {/* Cabecera: progreso + botón modo experto */}
      <div className="mb-4 flex items-center gap-3">
        <div className="min-w-0 flex-1">
          {conProgreso && <ProgresoPasos actual={paso} acento={acento} />}
        </div>
        <button
          type="button"
          onClick={onExperto}
          className="boton-acento shrink-0 rounded-full border border-borde bg-panel px-3 py-1.5 text-xs text-white/60"
          title="Ver la versión técnica con gráficas y datos"
        >
          Modo experto →
        </button>
      </div>

      {/* Mascota guía */}
      <div className="mb-5">
        <GuiaMascota
          nombre={mascNombre}
          emoji={mascEmoji}
          texto={mascTexto}
          acento={acento}
          textoKey={paso}
        />
      </div>

      {/* Pantalla del paso actual */}
      <div className="flex flex-1 flex-col">
        <AnimatePresence mode="wait">
          <motion.div
            key={paso}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.28, ease: [0.23, 1, 0.32, 1] }}
            className="flex flex-1 flex-col"
          >
            {paso === "bienvenida" && (
              <PasoBienvenida onComenzar={() => setPaso("mundo")} acento={acento} />
            )}

            {paso === "mundo" && (
              <PasoMundo
                dominios={dominios}
                cargando={cargandoDom}
                error={errorDom}
                onElegir={elegirMundo}
              />
            )}

            {paso === "mision" && sel && narr && (
              <PasoMision
                dominio={sel}
                narr={narr}
                escenarios={escenarios}
                escenarioSel={escenarioSel}
                onElegirEscenario={setEscenarioSel}
                cargando={cargandoDatos}
                onAtras={reiniciar}
                onComenzar={empezarMision}
              />
            )}

            {paso === "evolucion" && sel && (
              <PasoEvolucion
                dominio={sel}
                especies={especies}
                run={run}
                onVerEquipo={() => setPaso("equipo")}
              />
            )}

            {paso === "equipo" && sel && narr && (
              <PasoEquipo
                dominio={sel}
                narr={narr}
                especies={especies}
                done={run.done}
                onContinuar={() => setPaso("reveal")}
              />
            )}

            {paso === "reveal" && sel && narr && (
              <PasoReveal
                narr={narr}
                acento={acento}
                onReiniciar={reiniciar}
                onExperto={onExperto}
              />
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
    </MotionConfig>
  );
}
