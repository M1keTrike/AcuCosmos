"""Fase 2: penalizacion graduada/dinamica (3.1) + normalizacion (3.2).

- modo `mortal` reproduce Fase 1 (cubierto end-to-end por test_regresion).
- modo `graduada`: un infactible "casi bueno" puntua mejor que uno "muy malo",
  y un factible puntua igual que en mortal (penalizacion 0).
- modo `dinamica`: la penalizacion crece con la generacion.
"""
import dataclasses

import numpy as np
import pytest

from src.esquema import cargar_esquema
from src.metricas import (REGISTRO_METRICAS, ContextoEvaluacion, evaluar_aptitud,
                          _normalizar)
from src.operadores import FuncionInicializacion
from tests.golden_lib import cargar_peces, construir_ctx_peces

RUTA = "config/peces_ornamental.yaml"


def _esquema_modo(modo, **pen):
    esq = cargar_esquema(RUTA, REGISTRO_METRICAS)
    base = {"modo": modo,
            "pesos": {"presupuesto": 3.0, "capacidad": 5.0,
                      "espacio": 5.0, "ambiental": 5.0}}
    base.update(pen)
    return dataclasses.replace(esq, penalizaciones=base)


def _ctx(esquema, presupuesto):
    cat, sit, kap = cargar_peces()
    esc = {"pH_ref": 7.0, "presupuesto": presupuesto,
           "max_especies": 15, "min_especies": 2}
    return ContextoEvaluacion(esquema, cat, sit, kap, esc)


def _buscar_factible(ctx, n=500, semilla=123):
    np.random.seed(semilla)
    pob = FuncionInicializacion(n, ctx.catalogo, ctx.sitios, ctx.esquema,
                                min_especies=2, max_especies=5)
    for ind in pob:
        if evaluar_aptitud(ind, ctx)[1]["factible"]:
            return ind
    raise RuntimeError("no se encontro individuo factible para la prueba")


def test_normalizar():
    assert _normalizar(5.0, {"norm": {"min": 0.0, "max": 10.0}}) == 0.5
    assert _normalizar(-1.0, {"norm": {"min": 0.0, "max": 10.0}}) == 0.0  # clip
    assert _normalizar(20.0, {"norm": {"min": 0.0, "max": 10.0}}) == 1.0  # clip
    assert _normalizar(5.0, {}) == 5.0                                    # identidad


def test_graduada_violacion_pequena_mejor_que_grande():
    esq_g = _esquema_modo("graduada")
    # individuo factible con presupuesto enorme (solo controla cap/espacio/pH)
    ind = _buscar_factible(_ctx(esq_g, presupuesto=1e9))
    costo = evaluar_aptitud(ind, _ctx(esq_g, 1e9))[1]["costo"]

    F_sin = evaluar_aptitud(ind, _ctx(esq_g, costo * 2))[0]      # factible
    F_pequena = evaluar_aptitud(ind, _ctx(esq_g, costo * 0.95))[0]  # ~5% sobre
    F_grande = evaluar_aptitud(ind, _ctx(esq_g, costo * 0.50))[0]   # 100% sobre

    assert F_pequena > F_grande            # casi bueno > muy malo
    assert F_sin > F_pequena               # factible > infactible
    # en modo mortal ambos infactibles colapsan a 0
    ctx_mortal = construir_ctx_peces({"pH_ref": 7.0, "presupuesto": costo * 0.95,
                                      "max_especies": 15, "min_especies": 2})
    assert evaluar_aptitud(ind, ctx_mortal)[0] == 0.0


def test_graduada_no_cambia_a_los_factibles():
    cfg = {"pH_ref": 7.0, "presupuesto": 1e9, "max_especies": 15,
           "min_especies": 2}
    ctx_m = construir_ctx_peces(cfg)                  # mortal
    ind = _buscar_factible(ctx_m)
    F_mortal = evaluar_aptitud(ind, ctx_m)[0]
    esq_g = _esquema_modo("graduada")
    ctx_g = ContextoEvaluacion(esq_g, ctx_m.catalogo, ctx_m.sitios,
                               ctx_m.matriz_kappa, dict(ctx_m.escenario))
    F_grad = evaluar_aptitud(ind, ctx_g)[0]
    assert abs(F_mortal - F_grad) < 1e-12            # factible => sin penalizacion


def test_dinamica_penalizacion_crece_con_generacion():
    esq_d = _esquema_modo("dinamica", dinamica_alpha=0.5)
    ind = _buscar_factible(_ctx(esq_d, presupuesto=1e9))
    costo = evaluar_aptitud(ind, _ctx(esq_d, 1e9))[1]["costo"]
    ctx = _ctx(esq_d, presupuesto=costo * 0.5)       # viola presupuesto
    ctx.generaciones_max = 100
    ctx.generacion = 0
    F0 = evaluar_aptitud(ind, ctx)[0]
    ctx.generacion = 100
    F100 = evaluar_aptitud(ind, ctx)[0]
    assert F100 < F0                                 # mas castigo en gen tardia


def test_ag_corre_end_to_end_en_modo_dinamica():
    from src.ga_acucosmos import EjecutarAG
    esq_d = _esquema_modo("dinamica", dinamica_alpha=0.5)
    ctx = _ctx(esq_d, presupuesto=8000.0)
    mejor, hist, _ti, _ta, _tm = EjecutarAG(
        ctx, tam_poblacion=20, generaciones_max=5,
        min_especies=2, max_especies=6, verbose=False, seed=1)
    assert mejor is not None and len(hist) >= 1
    assert ctx.generaciones_max == 5                 # el motor lo fijo
