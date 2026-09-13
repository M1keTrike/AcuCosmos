"use client";

import { useEffect, useState } from "react";
import type { CapacidadMeta, Escenario, EspecieCat, Sitio } from "@/lib/types";
import type { EstadoRun } from "@/lib/useRunStream";
import { nombreEscenario } from "@/lib/format";
import { EspeciesFijasSelector } from "./EspeciesFijasSelector";

export interface ConfigRun {
  escenario: string;
  seed?: number; // undefined => corrida aleatoria real
  generaciones: number;
  poblacion: number;
  presupuesto?: number;
  minEspecies?: number;
  maxEspecies?: number;
  sitio?: number; // undefined => lo elige el algoritmo
  fijas?: number[]; // especies ancla ("base de la busqueda")
  capacidad?: number; // override de capacidad del sitio (filtro/superficie)
}

export function RunControls({
  escenarios,
  sitios,
  especies,
  capacidadMeta,
  acento,
  estado,
  onCorrer,
}: {
  escenarios: Escenario[];
  sitios: Sitio[];
  especies: EspecieCat[];
  capacidadMeta?: CapacidadMeta | null;
  acento: string;
  estado: EstadoRun;
  onCorrer: (c: ConfigRun) => void;
}) {
  const [escenario, setEscenario] = useState("");
  const [fijarSeed, setFijarSeed] = useState(false);
  const [seed, setSeed] = useState(7);
  const [generaciones, setGeneraciones] = useState(120);
  const [poblacion, setPoblacion] = useState(60);
  // Parámetros configurables (se inicializan desde el escenario elegido).
  const [presupuesto, setPresupuesto] = useState(0);
  const [minEsp, setMinEsp] = useState(3);
  const [maxEsp, setMaxEsp] = useState(15);
  const [sitio, setSitio] = useState<string>(""); // "" => automático
  const [fijas, setFijas] = useState<number[]>([]); // especies ancla
  const [capacidad, setCapacidad] = useState(0); // 0 => sin override (usa la del sitio)

  // Selecciona el primer escenario al cargar.
  useEffect(() => {
    if (!escenario && escenarios.length > 0) {
      setEscenario(String(escenarios[0].nombre ?? ""));
    }
  }, [escenarios, escenario]);

  const escObj =
    escenarios.find((e) => String(e.nombre ?? "") === escenario) ?? null;

  // Al cambiar de escenario, refleja sus valores por defecto en los controles.
  useEffect(() => {
    if (!escObj) return;
    setPresupuesto(Number(escObj.presupuesto ?? 0));
    setMinEsp(Number(escObj.min_especies ?? 3));
    setMaxEsp(Number(escObj.max_especies ?? 15));
    setSitio(""); // vuelve a "automático" en cada cambio de escenario
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [escenario]);

  // La capacidad por defecto sigue al sitio elegido (0 = automático: usa la del
  // sitio que toque). Al elegir un sitio concreto se precarga su valor para tunear.
  useEffect(() => {
    if (sitio === "") {
      setCapacidad(0);
    } else {
      const s = sitios.find((x) => x.idx === Number(sitio));
      setCapacidad(Number(s?.capacidad ?? 0));
    }
  }, [sitio, sitios]);

  // Sitios permitidos por el escenario (null/0 => todos).
  const permitidos =
    escObj?.sitios_permitidos ?? escObj?.tanques_permitidos ?? null;
  const sitiosOpciones =
    permitidos && permitidos.length > 0
      ? sitios.filter((s) => permitidos.includes(s.idx))
      : sitios;

  const corriendo = estado === "corriendo";

  const lanzar = () =>
    onCorrer({
      escenario,
      seed: fijarSeed ? seed : undefined,
      generaciones,
      poblacion,
      presupuesto: presupuesto > 0 ? presupuesto : undefined,
      minEspecies: minEsp,
      maxEspecies: maxEsp,
      sitio: sitio === "" ? undefined : Number(sitio),
      fijas: fijas.length > 0 ? fijas : undefined,
      capacidad: capacidad > 0 ? capacidad : undefined,
    });

  const inputCls =
    "rounded-lg border border-borde bg-panel-2 px-3 py-2 text-foreground outline-none focus:border-foreground/40";

  return (
    <div className="tarjeta flex flex-col gap-4 p-5">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-muted">
        Configuración de la corrida
      </h3>

      {/* Escenario (etiqueta legible) */}
      <label className="flex flex-col gap-1.5 text-sm">
        <span className="text-foreground/70">Escenario</span>
        <select
          value={escenario}
          onChange={(e) => setEscenario(e.target.value)}
          disabled={corriendo}
          className={inputCls}
        >
          {escenarios.map((s, i) => (
            <option key={i} value={String(s.nombre ?? i)}>
              {nombreEscenario(s, i)}
            </option>
          ))}
        </select>
      </label>

      {/* Tipo de sitio ("tipo de acuario") — F7 */}
      {sitios.length > 0 && (
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="text-foreground/70">Tipo de sitio</span>
          <select
            value={sitio}
            onChange={(e) => setSitio(e.target.value)}
            disabled={corriendo}
            className={inputCls}
          >
            <option value="">Que lo elija el algoritmo</option>
            {sitiosOpciones.map((s) => (
              <option key={s.idx} value={String(s.idx)}>
                {s.nombre}
              </option>
            ))}
          </select>
        </label>
      )}

      {/* Capacidad del sitio (en acuario = capacidad del filtro) */}
      {capacidadMeta && (
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="flex justify-between text-foreground/70">
            <span>
              {capacidadMeta.etiqueta} ({capacidadMeta.unidad})
            </span>
            <span className="font-mono text-foreground/50">0 = autom.</span>
          </span>
          <input
            type="number"
            min={0}
            step="any"
            value={capacidad}
            onChange={(e) => setCapacidad(Number(e.target.value))}
            disabled={corriendo}
            className={inputCls}
          />
        </label>
      )}

      {/* Parámetros configurables: presupuesto + límites de especies — F6 */}
      <label className="flex flex-col gap-1.5 text-sm">
        <span className="flex justify-between text-foreground/70">
          <span>Presupuesto</span>
          <span className="font-mono text-foreground/50">máx. gasto</span>
        </span>
        <input
          type="number"
          min={0}
          step={100}
          value={presupuesto}
          onChange={(e) => setPresupuesto(Number(e.target.value))}
          disabled={corriendo}
          className={inputCls}
        />
      </label>

      <div className="grid grid-cols-2 gap-3">
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="text-foreground/70">Mín. especies</span>
          <input
            type="number"
            min={1}
            max={60}
            value={minEsp}
            onChange={(e) => setMinEsp(Number(e.target.value))}
            disabled={corriendo}
            className={inputCls}
          />
        </label>
        <label className="flex flex-col gap-1.5 text-sm">
          <span className="text-foreground/70">Máx. especies</span>
          <input
            type="number"
            min={1}
            max={60}
            value={maxEsp}
            onChange={(e) => setMaxEsp(Number(e.target.value))}
            disabled={corriendo}
            className={inputCls}
          />
        </label>
      </div>

      {/* Especies base (fijas): el AG siempre las incluye */}
      {especies.length > 0 && (
        <EspeciesFijasSelector
          especies={especies}
          seleccion={fijas}
          onChange={setFijas}
          disabled={corriendo}
          acento={acento}
        />
      )}

      {/* Semilla: aleatoria por defecto (corrida 100% real), fija opcional — F5 */}
      <div className="flex flex-col gap-1.5 text-sm">
        <label className="flex items-center gap-2 text-foreground/70">
          <input
            type="checkbox"
            checked={fijarSeed}
            onChange={(e) => setFijarSeed(e.target.checked)}
            disabled={corriendo}
            style={{ accentColor: acento }}
          />
          Fijar semilla (corrida reproducible)
        </label>
        {fijarSeed ? (
          <input
            type="number"
            value={seed}
            onChange={(e) => setSeed(Number(e.target.value))}
            disabled={corriendo}
            className={inputCls}
          />
        ) : (
          <span className="text-xs text-foreground/45">
            Cada corrida explora una evolución distinta (azar real).
          </span>
        )}
      </div>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="flex justify-between text-foreground/70">
          <span>Generaciones</span>
          <span className="font-mono text-foreground/90">{generaciones}</span>
        </span>
        <input
          type="range"
          min={20}
          max={250}
          step={10}
          value={generaciones}
          onChange={(e) => setGeneraciones(Number(e.target.value))}
          disabled={corriendo}
          style={{ accentColor: acento }}
        />
      </label>

      <label className="flex flex-col gap-1.5 text-sm">
        <span className="flex justify-between text-foreground/70">
          <span>Población</span>
          <span className="font-mono text-foreground/90">{poblacion}</span>
        </span>
        <input
          type="range"
          min={20}
          max={160}
          step={10}
          value={poblacion}
          onChange={(e) => setPoblacion(Number(e.target.value))}
          disabled={corriendo}
          style={{ accentColor: acento }}
        />
      </label>

      <button
        type="button"
        disabled={corriendo || !escenario}
        onClick={lanzar}
        className="boton-acento mt-1 flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-base font-semibold text-white"
        style={{ background: acento }}
      >
        {corriendo ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Evolucionando…
          </>
        ) : (
          <>▶ Ejecutar AG</>
        )}
      </button>
    </div>
  );
}
