"use client";

import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";
import { apiCatalogo, apiEscenarios, apiKappa, apiSitios } from "@/lib/api";
import type {
  Catalogo,
  DominioMeta,
  Escenario,
  Kappa,
  Metricas,
  Sitio,
} from "@/lib/types";
import { useRunStream } from "@/lib/useRunStream";
import type { EspecieMapa } from "./tipos-escena";
import { AssemblyScene } from "./AssemblyScene";
import { AssemblySummary, type VistaEnsamblaje } from "./AssemblySummary";
import { ConvergenceChart } from "./ConvergenceChart";
import { GenerationScrubber } from "./GenerationScrubber";
import { KappaHeatmap } from "./KappaHeatmap";
import { MetricsRadar } from "./MetricsRadar";
import { RunControls, type ConfigRun } from "./RunControls";
import { StrataBars } from "./StrataBars";
import { Icono } from "./Icono";

// Quita las claves agregadas (n_especies/costo/factible) de las métricas del
// evento `done` para quedarse solo con las métricas del dominio (las que se
// pintan como chips). Las del GenEvento ya vienen sin ellas.
function soloMetricasDominio(m: Metricas): Record<string, number | null> {
  const out: Record<string, number | null> = {};
  for (const [k, v] of Object.entries(m)) {
    if (k === "n_especies" || k === "costo" || k === "factible") continue;
    out[k] = typeof v === "number" ? v : null;
  }
  return out;
}

export function DomainPanel({
  dominio,
  onBack,
}: {
  dominio: DominioMeta;
  onBack: () => void;
}) {
  const [escenarios, setEscenarios] = useState<Escenario[]>([]);
  const [sitios, setSitios] = useState<Sitio[]>([]);
  const [catalogo, setCatalogo] = useState<Catalogo | null>(null);
  const [kappa, setKappa] = useState<Kappa | null>(null);
  const [cargando, setCargando] = useState(true);
  const [errorCarga, setErrorCarga] = useState<string | null>(null);
  const [genIdx, setGenIdx] = useState(0);

  const run = useRunStream();
  const acento = dominio.tema.acento;

  // Carga de metadatos del dominio.
  useEffect(() => {
    let vivo = true;
    setCargando(true);
    setErrorCarga(null);
    Promise.all([
      apiEscenarios(dominio.id),
      apiCatalogo(dominio.id),
      apiKappa(dominio.id),
      apiSitios(dominio.id),
    ])
      .then(([esc, cat, kap, sit]) => {
        if (!vivo) return;
        setEscenarios(esc);
        setCatalogo(cat);
        setKappa(kap);
        setSitios(sit);
      })
      .catch((e) => vivo && setErrorCarga(String(e)))
      .finally(() => vivo && setCargando(false));
    return () => {
      vivo = false;
    };
  }, [dominio.id]);

  const especies: EspecieMapa = useMemo(() => {
    const m = new Map();
    catalogo?.especies.forEach((e) => m.set(e.idx, e));
    return m;
  }, [catalogo]);

  // Mientras corre: seguir la última generación en vivo.
  useEffect(() => {
    if (run.estado === "corriendo" && run.gens.length > 0) {
      setGenIdx(run.gens.length - 1);
    }
  }, [run.gens.length, run.estado]);

  // Al iniciar una nueva corrida, volver al inicio.
  useEffect(() => {
    if (run.estado === "corriendo" && run.gens.length === 0) setGenIdx(0);
  }, [run.estado, run.gens.length]);

  const genActual = run.gens[Math.min(genIdx, run.gens.length - 1)] ?? null;

  // Ensamblaje MOSTRADO, único para todos los paneles: el mejor global cuando la
  // corrida terminó y el scrubber está al final; la generación scrubeada si no.
  // Evita que "Mejor ensamblaje" (genActual) y κ/estratos (mejor global) difieran.
  const enFinal = !!run.done && genIdx >= run.gens.length - 1;
  const vista: VistaEnsamblaje | null =
    enFinal && run.done
      ? {
          ensamblaje: run.done.mejor.activas,
          apt: run.done.mejor.F,
          metricasDominio: soloMetricasDominio(run.done.mejor.metricas),
          costo: run.done.mejor.metricas.costo,
          factible: run.done.mejor.metricas.factible,
          sitioNombre: run.done.mejor.sitio_nombre,
        }
      : genActual
        ? {
            ensamblaje: genActual.ensamblaje,
            apt: genActual.apt_mejor,
            metricasDominio: genActual.metricas,
            costo: genActual.costo,
            factible: genActual.factible,
            sitioNombre: run.done?.mejor.sitio_nombre ?? null,
          }
        : null;
  const ensamblaje = vista?.ensamblaje ?? [];
  const activas = ensamblaje.map((a) => a.i);

  const lanzar = (c: ConfigRun) =>
    run.correr({
      dom: dominio.id,
      escenario: c.escenario,
      seed: c.seed,
      generaciones: c.generaciones,
      poblacion: c.poblacion,
      presupuesto: c.presupuesto,
      minEspecies: c.minEspecies,
      maxEspecies: c.maxEspecies,
      sitio: c.sitio,
      fijas: c.fijas,
      capacidad: c.capacidad,
    });

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.35 }}
      className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6"
    >
      {/* Cabecera */}
      <div className="mb-5 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onBack}
          className="boton-acento rounded-full border border-borde bg-panel px-3 py-2 text-sm text-foreground/80"
        >
          ← Dominios
        </button>
        <span
          className="flex h-10 w-10 items-center justify-center rounded-xl border"
          style={{
            borderColor: `${acento}40`,
            background: `${acento}14`,
            color: acento,
          }}
        >
          <Icono forma={dominio.tema.forma} size={22} />
        </span>
        <div className="mr-auto">
          <h2 className="text-xl font-semibold text-foreground">{dominio.etiqueta}</h2>
          <p className="text-xs text-foreground/50">
            {dominio.n_especies} especies · {dominio.estratos.length} estratos ·{" "}
            agregación {dominio.agregacion.replace("_", " ")}
          </p>
        </div>
        <EstadoPill estado={run.estado} acento={acento} error={run.error} />
      </div>

      {errorCarga && (
        <div className="mb-5 rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-700">
          No se pudo cargar el dominio ({errorCarga}). ¿Está corriendo el backend?
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-[330px_1fr]">
        <aside className="flex flex-col gap-5">
          <RunControls
            escenarios={escenarios}
            sitios={sitios}
            especies={catalogo?.especies ?? []}
            capacidadMeta={dominio.capacidad}
            acento={acento}
            estado={run.estado}
            onCorrer={lanzar}
          />
          {catalogo && <LeyendaGrupos catalogo={catalogo} />}
        </aside>

        <main className="flex min-w-0 flex-col gap-5">
          <p className="text-xs text-foreground/45">
            Las especies no están predefinidas: el algoritmo las elige y dosifica
            entre las {dominio.n_especies} candidatas del catálogo, según el sitio y
            los límites que configures.
          </p>
          <div className="h-[360px] sm:h-[440px]">
            <AssemblyScene
              forma={dominio.tema.forma}
              estratos={dominio.estratos}
              especies={especies}
              ensamblaje={ensamblaje}
              tema={dominio.tema}
            />
          </div>

          {run.gens.length > 0 && (
            <GenerationScrubber
              gens={run.gens}
              genIdx={Math.min(genIdx, run.gens.length - 1)}
              onChange={setGenIdx}
              acento={acento}
              disabled={run.estado === "corriendo"}
            />
          )}

          <div className="grid gap-5 xl:grid-cols-2">
            <ConvergenceChart
              gens={run.gens}
              genIdx={Math.min(genIdx, Math.max(0, run.gens.length - 1))}
              acento={acento}
            />
            <AssemblySummary vista={vista} especies={especies} acento={acento} />
          </div>

          <div className="grid gap-5 xl:grid-cols-2">
            {kappa && (
              <KappaHeatmap kappa={kappa} especies={especies} activas={activas} />
            )}
            <MetricsRadar topK={run.done?.topK ?? []} acento={acento} />
          </div>

          <StrataBars
            estratos={dominio.estratos}
            especies={especies}
            ensamblaje={ensamblaje}
            acento={acento}
          />
        </main>
      </div>

      {cargando && (
        <p className="mt-4 text-center text-sm text-foreground/40">Cargando dominio…</p>
      )}
    </motion.div>
  );
}

function EstadoPill({
  estado,
  acento,
  error,
}: {
  estado: string;
  acento: string;
  error: string | null;
}) {
  const mapa: Record<string, { txt: string; bg: string; fg: string }> = {
    inactivo: { txt: "listo para correr", bg: "#f1f6f4", fg: "#4a5c58" },
    corriendo: { txt: "evolucionando…", bg: `${acento}22`, fg: acento },
    listo: { txt: "corrida completa", bg: "#dcefe2", fg: "#0b5f57" },
    error: { txt: error ?? "error", bg: "#fbe3e3", fg: "#b91c1c" },
  };
  const e = mapa[estado] ?? mapa.inactivo;
  return (
    <span
      className="rounded-full px-3 py-1.5 text-xs font-medium"
      style={{ background: e.bg, color: e.fg }}
    >
      {estado === "corriendo" && (
        <span
          className="mr-1.5 inline-block h-2 w-2 animate-pulse rounded-full"
          style={{ background: acento }}
        />
      )}
      {e.txt}
    </span>
  );
}

function LeyendaGrupos({ catalogo }: { catalogo: Catalogo }) {
  return (
    <div className="tarjeta p-5">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted">
        Grupos ({catalogo.grupo_col ?? "—"})
      </h3>
      <div className="flex flex-col gap-2">
        {catalogo.grupos.map((g) => (
          <div key={g.valor} className="flex items-center gap-2 text-sm">
            <span className="h-3 w-3 rounded-sm" style={{ background: g.color }} />
            <span className="truncate text-foreground/75">{g.etiqueta}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
