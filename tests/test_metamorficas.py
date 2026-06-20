"""Pruebas metamorficas: relaciones que deben cumplirse sin oraculo exacto.

Se aplican al EVALUADOR / agregadores (deterministas), no al AG completo (cuyo
camino de busqueda diverge con el escenario aunque la semilla sea la misma).
"""
import dataclasses

import numpy as np
import pytest

from src.esquema import cargar_esquema, cargar_tablas
from src.metricas import REGISTRO_METRICAS, ContextoEvaluacion, evaluar_aptitud
from src.agregacion import puntajes_nsga2, puntajes_borda
from src.operadores import FuncionInicializacion
from src.cromosoma import CrearIndividuoVacio
from tests.golden_lib import cargar_peces

PEN_GRAD = {"modo": "graduada",
            "pesos": {"presupuesto": 3.0, "capacidad": 5.0,
                      "espacio": 5.0, "ambiental": 5.0}}


def _ctx_peces(escenario, agreg=None, pen=None):
    esq = cargar_esquema("config/peces_ornamental.yaml", REGISTRO_METRICAS)
    if agreg:
        esq = dataclasses.replace(esq, agregacion=agreg)
    if pen:
        esq = dataclasses.replace(esq, penalizaciones=pen)
    cat, sit, kap = cargar_peces()
    return esq, cat, sit, kap, ContextoEvaluacion(esq, cat, sit, kap, escenario)


def _factible(ctx, seed=123, n=400):
    np.random.seed(seed)
    pob = FuncionInicializacion(n, ctx.catalogo, ctx.sitios, ctx.esquema,
                                min_especies=2, max_especies=5)
    for ind in pob:
        if evaluar_aptitud(ind, ctx)[1]["factible"]:
            return ind
    raise RuntimeError("no se hallo individuo factible")


def test_presupuesto_monotono_graduada():
    esc = {"pH_ref": 7.0, "presupuesto": 1e9, "max_especies": 15, "min_especies": 2}
    esq, cat, sit, kap, ctx = _ctx_peces(esc, pen=PEN_GRAD)
    ind = _factible(ctx)
    costo = evaluar_aptitud(ind, ctx)[1]["costo"]
    Fs = []
    for b in (costo * 2, costo, costo * 0.9, costo * 0.5):
        c = ContextoEvaluacion(esq, cat, sit, kap,
                               {"pH_ref": 7.0, "presupuesto": b,
                                "max_especies": 15, "min_especies": 2})
        Fs.append(evaluar_aptitud(ind, c)[0])
    assert all(Fs[i] >= Fs[i + 1] - 1e-9 for i in range(len(Fs) - 1)), Fs


def test_carga_monotona_en_cantidad():
    esc = {"pH_ref": 7.0, "presupuesto": 1e9, "max_especies": 15, "min_especies": 2}
    _esq, _c, _s, _k, ctx = _ctx_peces(esc)
    ind = _factible(ctx)
    m1 = evaluar_aptitud(ind, ctx)[1]
    ind2 = {"tanque": ind["tanque"], "B": ind["B"].copy(),
            "C": ind["C"] * 2, "D": ind["D"].copy()}
    m2 = evaluar_aptitud(ind2, ctx)[1]
    assert m2["M_s"] >= m1["M_s"] - 1e-9          # mas individuos => mas carga


def test_signo_kappa_invierte_equilibrio():
    esq = cargar_esquema("config/fauna_acuicola.yaml", REGISTRO_METRICAS)
    cat, sit, kap = cargar_tablas(esq)
    esc = {"temp_ref": 28, "ph_ref": 7.0, "od_ref": 5.0, "presupuesto": 5000,
           "max_especies": 6, "min_especies": 3}
    nz = np.argwhere(np.triu(kap, 1) != 0)
    i, j = int(nz[0][0]), int(nz[0][1])
    ind = CrearIndividuoVacio(len(cat))
    ind["tanque"] = 0
    for k in (i, j):
        ind["B"][k] = 1
        ind["C"][k] = 1
        ind["D"][k] = 0.5
    eq1 = REGISTRO_METRICAS["equilibrio_pares"](
        ind, ContextoEvaluacion(esq, cat, sit, kap, esc), {"promediar": True})
    kap2 = kap.copy()
    kap2[i, j] *= -1
    kap2[j, i] *= -1
    eq2 = REGISTRO_METRICAS["equilibrio_pares"](
        ind, ContextoEvaluacion(esq, cat, sit, kap2, esc), {"promediar": True})
    assert eq1 != 0 and abs(eq1 + eq2) < 1e-9     # signo invertido


def test_invariancia_escala_pareto_y_borda():
    base = [{"_obj": (3.0, 1.0), "_viol": 0.0, "factible": True},
            {"_obj": (1.0, 3.0), "_viol": 0.0, "factible": True},
            {"_obj": (2.0, 2.0), "_viol": 0.0, "factible": True},
            {"_obj": (1.0, 1.0), "_viol": 0.0, "factible": True}]
    escalado = [{"_obj": (o["_obj"][0] * 1000.0, o["_obj"][1]),
                 "_viol": 0.0, "factible": True} for o in base]

    def orden(s):
        return list(np.argsort(s))

    assert orden(puntajes_nsga2(base)) == orden(puntajes_nsga2(escalado))
    assert orden(puntajes_borda(base)) == orden(puntajes_borda(escalado))
