"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { urlRun, type ParamsRun } from "./api";
import type { DoneEvento, GenEvento } from "./types";

export type EstadoRun = "inactivo" | "corriendo" | "listo" | "error";

export interface RunStream {
  estado: EstadoRun;
  gens: GenEvento[];
  done: DoneEvento | null;
  error: string | null;
  correr: (p: ParamsRun) => void;
  reset: () => void;
}

export function useRunStream(): RunStream {
  const [estado, setEstado] = useState<EstadoRun>("inactivo");
  const [gens, setGens] = useState<GenEvento[]>([]);
  const [done, setDone] = useState<DoneEvento | null>(null);
  const [error, setError] = useState<string | null>(null);
  const esRef = useRef<EventSource | null>(null);

  const cerrar = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    cerrar();
    setEstado("inactivo");
    setGens([]);
    setDone(null);
    setError(null);
  }, [cerrar]);

  const correr = useCallback(
    (p: ParamsRun) => {
      cerrar();
      setGens([]);
      setDone(null);
      setError(null);
      setEstado("corriendo");

      const es = new EventSource(urlRun(p));
      esRef.current = es;

      es.addEventListener("gen", (ev) => {
        const data = JSON.parse((ev as MessageEvent).data) as GenEvento;
        setGens((prev) => [...prev, data]);
      });

      es.addEventListener("done", (ev) => {
        const data = JSON.parse((ev as MessageEvent).data) as DoneEvento;
        setDone(data);
        setEstado("listo");
        cerrar(); // corrida de un solo uso: evita el reintento de EventSource
      });

      es.addEventListener("error", (ev) => {
        const raw = (ev as MessageEvent).data;
        // El cierre normal del stream tras 'done' también dispara 'error'.
        setEstado((prevEstado) => {
          if (prevEstado === "listo") return prevEstado;
          if (raw) {
            try {
              setError((JSON.parse(raw) as { mensaje?: string }).mensaje ?? raw);
            } catch {
              setError(String(raw));
            }
          } else {
            setError("Se perdió la conexión con el backend.");
          }
          return "error";
        });
        cerrar();
      });
    },
    [cerrar]
  );

  useEffect(() => cerrar, [cerrar]);

  return { estado, gens, done, error, correr, reset };
}
