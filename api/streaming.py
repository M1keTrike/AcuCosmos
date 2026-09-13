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
    # Misma regla legible que el endpoint /sitios (nombre -> tipo -> id -> "Sitio N").
    return servicio.nombre_sitio(sitios, idx)


async def stream_run(dom, escenario_nombre, seed, generaciones, poblacion,
                     presupuesto=None, min_especies=None, max_especies=None,
                     sitio=None, fijas=None, capacidad=None):
    esquema, cat, sitios, kap, escenarios = servicio.cargar_todo(dom)
    # Override de la capacidad del sitio (p.ej. capacidad del filtro del acuario).
    # Copia para no mutar la tabla cacheada (lru_cache).
    if capacidad is not None:
        col_cap = esquema.col("capacidad_sitio")
        if col_cap and col_cap in sitios.columns:
            sitios = sitios.copy()
            sitios[col_cap] = float(capacidad)
    n_cat = int(len(cat))
    # Especies ancla ("base de la busqueda"): indices validos del catalogo.
    fijas_list = []
    if fijas:
        for x in re.split(r"[;,]", str(fijas)):
            x = x.strip()
            if not x:
                continue
            try:
                v = int(x)
            except ValueError:
                continue
            if 0 <= v < n_cat:
                fijas_list.append(v)
        fijas_list = sorted(set(fijas_list))
    esc = None
    if escenario_nombre:
        esc = next((e for e in escenarios
                    if str(e.get("nombre")) == str(escenario_nombre)), None)
    if esc is None:
        esc = escenarios[0] if escenarios else {}

    # Copia para no mutar el escenario cacheado (lru_cache) al aplicar overrides.
    esc = dict(esc)
    if presupuesto is not None:
        esc["presupuesto"] = float(presupuesto)
    # min/max especies del usuario (con fallback al escenario) y coherentes.
    me_min = int(min_especies) if min_especies is not None \
        else int(esc.get("min_especies", 3) or 3)
    me_max = int(max_especies) if max_especies is not None \
        else int(esc.get("max_especies", 15) or 15)
    if me_min > me_max:
        me_min, me_max = me_max, me_min
    # Las anclas son obligatorias: el tope nunca puede ser menor que su numero.
    if fijas_list:
        me_max = max(me_max, len(fijas_list))
    # sitio explicito ("tipo de acuario") restringe la busqueda a ese unico sitio.
    if sitio is not None:
        tanques = [int(sitio)]
    else:
        tanques = _sitios_permitidos(esc)

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
                tanques_permitidos=tanques,
                tam_poblacion=int(poblacion),
                generaciones_max=int(generaciones),
                min_especies=me_min,
                max_especies=me_max,
                cap_estricto=True,     # respeta Max. especies como tope duro (GUI)
                especies_fijas=fijas_list or None,
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
