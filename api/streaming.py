"""Corre el AG en un hilo y transmite cada generacion por SSE.

`EjecutarAG` recibe el `callback` aditivo (default None en el motor) que empuja cada
registro a una cola asyncio; un generador asincrono los emite como eventos SSE
(`gen` por generacion, `done` al terminar).
"""
from __future__ import annotations

import asyncio
import json
import re

from src.cromosoma import EspeciesActivas
from src.ga_acucosmos import EjecutarAG
from src.metricas import ContextoEvaluacion, evaluar_aptitud
from api import servicio

_CENTINELA = object()


def _sitios_permitidos(esc):
    sp = esc.get("sitios_permitidos")
    if isinstance(sp, list):
        return sp
    raw = esc.get("tanques_permitidos") if sp is None else sp
    if raw is None or str(raw).strip() == "":
        return None
    return [int(x) for x in re.split(r"[;,]", str(raw)) if str(x).strip() != ""]


def _met(esquema, m):
    d = {mc.clave_reporte: servicio.jf(m.get(mc.clave_reporte))
         for mc in esquema.metricas}
    d["n_especies"] = int(m.get("n_especies", 0))
    d["costo"] = servicio.jf(m.get("costo"))
    d["factible"] = bool(m.get("factible", False))
    return d


def _ensamblaje(ind):
    return [{"i": int(i), "C": int(ind["C"][i])} for i in EspeciesActivas(ind)]


def _nombre_sitio(sitios, idx):
    try:
        fila = sitios.iloc[int(idx)]
    except Exception:
        return str(idx)
    for c in ("nombre", "nombre_sitio", "sitio"):
        if c in sitios.columns:
            return str(fila[c])
    return str(idx)


async def stream_run(dom, escenario_nombre, seed, generaciones, poblacion):
    esquema, cat, sitios, kap, escenarios = servicio.cargar_todo(dom)
    esc = None
    if escenario_nombre:
        esc = next((e for e in escenarios
                    if str(e.get("nombre")) == str(escenario_nombre)), None)
    if esc is None:
        esc = escenarios[0] if escenarios else {}
    ctx = ContextoEvaluacion(esquema, cat, sitios, kap, esc)

    loop = asyncio.get_running_loop()
    cola: asyncio.Queue = asyncio.Queue()

    def cb(reg, mejor_ind):
        msg = {
            "generacion": int(reg["generacion"]),
            "apt_mejor": servicio.jf(reg["apt_mejor"]),
            "apt_promedio": servicio.jf(reg["apt_promedio"]),
            "apt_peor": servicio.jf(reg["apt_peor"]),
            "factible": bool(reg.get("factible")),
            "costo": servicio.jf(reg.get("costo")),
            "metricas": {mc.clave_reporte: servicio.jf(reg.get(mc.clave_reporte))
                         for mc in esquema.metricas},
            "ensamblaje": _ensamblaje(mejor_ind),
        }
        loop.call_soon_threadsafe(cola.put_nowait, ("gen", msg))

    def construir_done(mejor, top_inds, top_apts, top_mets):
        f, m = evaluar_aptitud(mejor, ctx)
        activas = EspeciesActivas(mejor)
        kappa_activas = []
        for a in range(len(activas)):
            for b in range(a + 1, len(activas)):
                i, j = activas[a], activas[b]
                v = float(kap[i, j])
                if v != 0.0:
                    kappa_activas.append({"i": int(i), "j": int(j),
                                          "valor": round(v, 4)})
        topK = [{"F": servicio.jf(apt), "metricas": _met(esquema, met),
                 "activas": _ensamblaje(ind)}
                for ind, apt, met in zip(top_inds, top_apts, top_mets)]
        return {
            "mejor": {
                "sitio_idx": int(mejor["tanque"]),
                "sitio_nombre": _nombre_sitio(sitios, mejor["tanque"]),
                "F": servicio.jf(f),
                "metricas": _met(esquema, m),
                "activas": _ensamblaje(mejor),
            },
            "topK": topK,
            "kappa_activas": kappa_activas,
        }

    def corre():
        try:
            mejor, _hist, top_inds, top_apts, top_mets = EjecutarAG(
                ctx,
                tanques_permitidos=_sitios_permitidos(esc),
                tam_poblacion=int(poblacion),
                generaciones_max=int(generaciones),
                min_especies=int(esc.get("min_especies", 3) or 3),
                max_especies=int(esc.get("max_especies", 15) or 15),
                verbose=False,
                seed=seed,
                callback=cb,
            )
            done = construir_done(mejor, top_inds, top_apts, top_mets)
            loop.call_soon_threadsafe(cola.put_nowait, ("done", done))
        except Exception as e:                      # informa el error al cliente
            loop.call_soon_threadsafe(
                cola.put_nowait, ("error", {"mensaje": str(e)}))
        finally:
            loop.call_soon_threadsafe(cola.put_nowait, (_CENTINELA, None))

    tarea = loop.run_in_executor(None, corre)
    try:
        while True:
            ev, data = await cola.get()
            if ev is _CENTINELA:
                break
            yield {"event": ev, "data": json.dumps(data, ensure_ascii=False)}
    finally:
        await tarea
