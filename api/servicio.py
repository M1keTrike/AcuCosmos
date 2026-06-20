"""Capa de servicio: carga (y cachea) dominios/tablas y los serializa a JSON.

Reutiliza el motor sin tocarlo: `cargar_esquema`, `cargar_tablas`,
`cargar_escenarios` de src/esquema.py y el REGISTRO_METRICAS de src/metricas.py.
"""
from __future__ import annotations

import math
import os
from functools import lru_cache

import numpy as np
import pandas as pd

from src.esquema import (RAIZ_REPO, _abs, cargar_esquema, cargar_tablas,
                         cargar_escenarios)
from src.metricas import REGISTRO_METRICAS
from api import temas

DIR_CONFIG = os.path.join(RAIZ_REPO, "config")


# --------------------------------------------------------------------------- #
# Utilidades de serializacion
# --------------------------------------------------------------------------- #
def jf(v):
    """float JSON-safe (NaN/inf -> None)."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def jsonable(v):
    if v is None:
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return jf(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if isinstance(v, dict):
        return {str(k): jsonable(x) for k, x in v.items()}
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


# --------------------------------------------------------------------------- #
# Carga cacheada por dominio
# --------------------------------------------------------------------------- #
def lista_ids():
    if not os.path.isdir(DIR_CONFIG):
        return []
    ids = []
    for f in sorted(os.listdir(DIR_CONFIG)):
        if f.endswith(".yaml") and not f.startswith("_"):
            ids.append(f[:-5])
    return ids


@lru_cache(maxsize=None)
def _cargar(dom: str):
    ruta = os.path.join(DIR_CONFIG, f"{dom}.yaml")
    if not os.path.exists(ruta):
        raise KeyError(dom)
    esquema = cargar_esquema(ruta, REGISTRO_METRICAS)
    catalogo, sitios, kappa = cargar_tablas(esquema)
    escenarios = cargar_escenarios(esquema)
    return esquema, catalogo, sitios, kappa, escenarios


def cargar_todo(dom: str):
    return _cargar(dom)


# --------------------------------------------------------------------------- #
# Helpers de catalogo
# --------------------------------------------------------------------------- #
def _col_nombre(catalogo, esquema):
    for c in ("nombre_comun", "nombre_cientifico", esquema.id_col):
        if c in catalogo.columns:
            return c
    return esquema.id_col


def _estratos_meta(esquema, t):
    orden = [str(o) for o in esquema.estratos.get("orden", [])]
    et = t.get("estrato_etiquetas", {}) or {}
    return [{"idx": i, "valor": v, "etiqueta": et.get(v, v.replace("_", " ").capitalize())}
            for i, v in enumerate(orden)]


# --------------------------------------------------------------------------- #
# Endpoints (datos)
# --------------------------------------------------------------------------- #
def dominios():
    out = []
    for dom in lista_ids():
        try:
            esquema, catalogo, _sitios, _kappa, _esc = _cargar(dom)
        except Exception as e:                       # dominio mal configurado
            out.append({"id": dom, "error": str(e)})
            continue
        t = temas.tema(dom)
        out.append({
            "id": dom,
            "dominio": esquema.dominio,
            "etiqueta": t["etiqueta"],
            "descripcion": t["descripcion"],
            "emoji": t["emoji"],
            "agregacion": esquema.agregacion,
            "n_especies": int(len(catalogo)),
            "estratos": _estratos_meta(esquema, t),
            "tema": {
                "acento": t["acento"], "acento2": t["acento2"],
                "fondo": t["fondo"], "fondo2": t["fondo2"],
                "forma": t["forma"],
            },
        })
    return out


def escenarios(dom: str):
    _esq, _cat, _sit, _kap, escs = _cargar(dom)
    return [jsonable(e) for e in escs]


def catalogo(dom: str):
    esquema, cat, _sit, _kap, _esc = _cargar(dom)
    t = temas.tema(dom)
    nom_col = _col_nombre(cat, esquema)
    grupo_col = t.get("grupo_col")
    etq_col = t.get("grupo_etiqueta_col")
    tam_col = t.get("tamano_col")
    estr_col = esquema.estratos.get("col")
    orden = [str(o) for o in esquema.estratos.get("orden", [])]
    pos = {v: i for i, v in enumerate(orden)}

    # valores de grupo + etiqueta legible (p.ej. peces: grupo_cromatico_nombre)
    vistos = []
    etiqueta_grupo = {}
    for _, fila in cat.iterrows():
        g = temas.valor_grupo(t, fila[grupo_col]) if grupo_col else ""
        if g not in vistos:
            vistos.append(g)
        if g not in etiqueta_grupo:
            if etq_col and etq_col in cat.columns:
                etiqueta_grupo[g] = str(fila[etq_col])
            else:
                etiqueta_grupo[g] = g if g else "—"
    colores = temas.asignar_colores_tema(t, vistos, etiqueta_grupo)

    especies = []
    for i, fila in cat.iterrows():
        g = temas.valor_grupo(t, fila[grupo_col]) if grupo_col else ""
        estr_val = str(fila[estr_col]) if estr_col else ""
        especies.append({
            "idx": int(i),
            "id": str(fila[esquema.id_col]),
            "nombre": str(fila[nom_col]),
            "estrato": estr_val,
            "estrato_idx": pos.get(estr_val, 0),
            "grupo": g,
            "color": colores.get(g, "#94a3b8"),
            "tamano": jf(fila[tam_col]) if (tam_col and tam_col in cat.columns) else 1.0,
        })

    grupos = [{"valor": v, "etiqueta": etiqueta_grupo.get(v, v), "color": colores[v]}
              for v in vistos]
    return {
        "dominio": esquema.dominio,
        "forma": t["forma"],
        "grupo_col": grupo_col,
        "grupos": grupos,
        "especies": especies,
    }


def kappa(dom: str):
    esquema, cat, _sit, kap, _esc = _cargar(dom)
    n = int(kap.shape[0])
    investigados = _pares_investigados(esquema, cat)
    pares = []
    for i in range(n):
        for j in range(i + 1, n):
            v = float(kap[i, j])
            if v == 0.0:
                continue
            key = (i, j)
            proc = "investigado" if (investigados is None or key in investigados) \
                else "derivado"
            pares.append({"i": i, "j": j, "valor": round(v, 4), "procedencia": proc})
    return {"n": n, "pares": pares}


def _pares_investigados(esquema, cat):
    """Conjunto {(i,j)} de pares con valor investigado (lista dispersa). None si el
    formato es denso (todos se consideran investigados)."""
    if esquema.params.get("interacciones_formato", "densa") != "disperso":
        return None
    ids = [str(x) for x in cat[esquema.id_col].tolist()]
    idx = {s: i for i, s in enumerate(ids)}
    df = pd.read_csv(_abs(esquema.rutas["interacciones"]), encoding="utf-8-sig")
    s = set()
    for _, r in df.iterrows():
        a, b = str(r["especie_a"]), str(r["especie_b"])
        if a in idx and b in idx and a != b:
            i, j = idx[a], idx[b]
            s.add((min(i, j), max(i, j)))
    return s
