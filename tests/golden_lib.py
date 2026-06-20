"""Utilidades compartidas para el *golden output* de regresión (Fase 0).

El golden output fija el comportamiento del AcuCosmos original (dominio
`peces_ornamental`) con **semilla fija**, de modo que la Fase 1 (motor genérico
vía `EsquemaDominio`) deba reproducirlo idéntico (mismo seed) como criterio de
aceptación. Configuración y escenarios son los de `main.py`.
"""
import os
import json

import numpy as np
import pandas as pd

from src.ga_acucosmos import EjecutarAG
from src.aptitud import FuncionAptitud

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")

# Semilla fija de la línea base. No cambiar sin regenerar el golden output.
SEED = 12345

# Configuracion del AG identica a main.py.
GA = dict(tam_poblacion=80, generaciones_max=150, estancamiento_max=30,
          delta_pH=0.5, top_k=3)

# Los 3 escenarios que corre main.py (parametros que SI afectan al motor).
ESCENARIOS = [
    dict(nombre="escenario_1", pH_ref=7.0, presupuesto=8000.0,
         tanques_permitidos=None, min_especies=5, max_especies=15),
    dict(nombre="escenario_2", pH_ref=5.5, presupuesto=12000.0,
         tanques_permitidos=None, min_especies=5, max_especies=15),
    dict(nombre="escenario_3", pH_ref=7.0, presupuesto=3000.0,
         tanques_permitidos=[0, 1], min_especies=2, max_especies=6),
]

REDONDEO = 10


def cargar_peces(dir_data=None):
    """Carga catalogo, tanques y matriz kappa del dominio peces (idem main.py)."""
    d = dir_data or os.path.join(RAIZ, "data")
    catalogo = pd.read_csv(os.path.join(d, "catalogo_especies.csv"),
                           encoding="utf-8-sig")
    tanques = pd.read_csv(os.path.join(d, "catalogo_tanques.csv"),
                          encoding="utf-8-sig")
    kappa = pd.read_csv(os.path.join(d, "matriz_compatibilidad.csv"),
                        encoding="utf-8-sig", index_col=0).to_numpy(dtype=float)
    return catalogo, tanques, kappa


def _activas(ind):
    return [[i, int(ind["C"][i]), round(float(ind["D"][i]), REDONDEO)]
            for i in range(len(ind["B"])) if ind["B"][i] == 1]


def _num(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return round(float(v), REDONDEO)
    return v


def correr_escenario(cfg, seed=SEED):
    """Corre un escenario y devuelve una representacion canonica comparable."""
    catalogo, tanques, kappa = cargar_peces()
    mejor, _hist, top_inds, top_apts, _top_mets = EjecutarAG(
        catalogo=catalogo, tanques=tanques, matriz_kappa=kappa,
        pH_ref=cfg["pH_ref"], delta_pH=GA["delta_pH"],
        presupuesto=cfg["presupuesto"],
        tanques_permitidos=cfg["tanques_permitidos"],
        tam_poblacion=GA["tam_poblacion"],
        generaciones_max=GA["generaciones_max"],
        estancamiento_max=GA["estancamiento_max"],
        min_especies=cfg["min_especies"], max_especies=cfg["max_especies"],
        top_k=GA["top_k"], verbose=False, seed=seed)
    f_final, met = FuncionAptitud(
        mejor, catalogo, tanques, kappa, pH_ref=cfg["pH_ref"],
        delta_pH=GA["delta_pH"], presupuesto=cfg["presupuesto"],
        max_especies=cfg["max_especies"])
    claves_cfg = ("nombre", "pH_ref", "presupuesto", "tanques_permitidos",
                  "min_especies", "max_especies")
    return {
        "config": {"seed": seed, **GA, **{k: cfg[k] for k in claves_cfg}},
        "f_final": round(float(f_final), REDONDEO),
        "mejor": {"tanque": int(mejor["tanque"]), "activas": _activas(mejor)},
        "metricas": {k: _num(v) for k, v in met.items()},
        "top_apts": [round(float(x), REDONDEO) for x in top_apts],
        "top_estructuras": [
            {"tanque": int(t["tanque"]), "activas": _activas(t)}
            for t in top_inds],
    }


def ruta_golden(nombre):
    return os.path.join(DIR_GOLDEN, f"{nombre}.json")


def guardar_golden(nombre, data):
    os.makedirs(DIR_GOLDEN, exist_ok=True)
    with open(ruta_golden(nombre), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def cargar_golden(nombre):
    with open(ruta_golden(nombre), "r", encoding="utf-8") as fh:
        return json.load(fh)


def _num_iguales(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol


def comparar_canon(esperado, obtenido, tol=1e-9):
    """Devuelve la lista de diferencias (vacia = identico dentro de tol)."""
    difs = []
    if esperado["mejor"]["tanque"] != obtenido["mejor"]["tanque"]:
        difs.append(
            f"tanque {esperado['mejor']['tanque']} != "
            f"{obtenido['mejor']['tanque']}")
    ea, oa = esperado["mejor"]["activas"], obtenido["mejor"]["activas"]
    if [x[:2] for x in ea] != [x[:2] for x in oa]:
        difs.append(f"estructura activas distinta: {[x[:2] for x in ea]} "
                    f"!= {[x[:2] for x in oa]}")
    else:
        for (i, _c, d_e), (_j, _c2, d_o) in zip(ea, oa):
            if not _num_iguales(d_e, d_o, tol):
                difs.append(f"D[{i}] {d_e} != {d_o}")
    if not _num_iguales(esperado["f_final"], obtenido["f_final"], tol):
        difs.append(f"f_final {esperado['f_final']} != {obtenido['f_final']}")
    for k, v in esperado["metricas"].items():
        ov = obtenido["metricas"].get(k)
        if isinstance(v, bool) or isinstance(v, int):
            if v != ov:
                difs.append(f"metrica {k} {v} != {ov}")
        elif ov is None or not _num_iguales(v, ov, tol):
            difs.append(f"metrica {k} {v} != {ov}")
    if len(esperado["top_apts"]) != len(obtenido["top_apts"]):
        difs.append("len(top_apts) distinto")
    else:
        for i, (ve, vo) in enumerate(zip(esperado["top_apts"],
                                         obtenido["top_apts"])):
            if not _num_iguales(ve, vo, tol):
                difs.append(f"top_apts[{i}] {ve} != {vo}")
    estr = lambda c: [(e["tanque"], [x[:2] for x in e["activas"]])
                      for e in c["top_estructuras"]]
    if estr(esperado) != estr(obtenido):
        difs.append("top_estructuras distintas")
    return difs
