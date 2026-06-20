"""Fase 3: agregacion configurable (2.4) — NSGA-II [3][5], Borda [7].

(a) suma reproduce Fase 2 (cubierto por test_regresion). (b)/(c) producen
frentes/ordenes coherentes sobre un escenario de juguete de objetivos en
conflicto (objetivos orientados a MAXIMIZAR).
"""
import dataclasses

import pytest

from src.agregacion import (domina, clasificacion_no_dominada, crowding_distance,
                            puntajes_nsga2, puntajes_borda,
                            puntos_referencia_das_dennis, puntuar_seleccion)
from src.esquema import cargar_esquema
from src.metricas import REGISTRO_METRICAS, ContextoEvaluacion
from src.ga_acucosmos import EjecutarAG
from tests.golden_lib import cargar_peces

RUTA = "config/peces_ornamental.yaml"

INF = float("inf")


def _m(obj, viol=0.0, factible=True):
    return {"_obj": tuple(obj), "_viol": viol, "factible": factible}


# --------------------------- dominancia de Deb [3] -------------------------- #
def test_domina_pareto():
    assert domina(_m([2, 2]), _m([1, 1]))
    assert not domina(_m([2, 1]), _m([1, 2]))     # no comparables
    assert not domina(_m([1, 2]), _m([2, 1]))
    assert not domina(_m([1, 1]), _m([1, 1]))     # iguales: no domina


def test_domina_con_restricciones():
    assert domina(_m([0, 0]), _m([9, 9], factible=False))      # factible >- infactible
    assert domina(_m([0, 0], viol=1, factible=False),
                  _m([0, 0], viol=2, factible=False))          # menor violacion gana


# ----------------------- ordenamiento no-dominado --------------------------- #
def test_clasificacion_no_dominada():
    pob = [_m([3, 1]), _m([1, 3]), _m([2, 2]), _m([1, 1])]      # A B C D
    frentes = clasificacion_no_dominada(pob)
    assert sorted(frentes[0]) == [0, 1, 2]                      # A,B,C no dominados
    assert frentes[1] == [3]                                    # D dominado por todos


def test_crowding_extremos_infinito():
    pob = [_m([3, 1]), _m([1, 3]), _m([2, 2])]                  # A,B extremos; C interior
    dist = crowding_distance([0, 1, 2], pob)
    assert dist[0] == INF and dist[1] == INF
    assert dist[2] < INF


def test_puntajes_nsga2_frente0_supera_frente1():
    pob = [_m([3, 1]), _m([1, 3]), _m([2, 2]), _m([1, 1])]
    s = puntajes_nsga2(pob)
    assert min(s[0], s[1], s[2]) > s[3]                         # frente 0 > frente 1


# --------------------------------- Borda [7] -------------------------------- #
def test_borda_gana_el_dominante():
    pob = [_m([3, 3]), _m([2, 1]), _m([1, 2])]                  # A domina a B y C
    s = puntajes_borda(pob)
    assert s[0] == max(s)                                       # A el mejor


# ------------------------ NSGA-III: puntos de referencia -------------------- #
def test_das_dennis():
    pts = puntos_referencia_das_dennis(3, 4)
    assert len(pts) == 15                                       # C(6,4)
    assert all(abs(sum(p) - 1.0) < 1e-9 for p in pts)


def test_suma_devuelve_aptitud_intacta():
    apt = [1.0, 2.0, 0.5]
    assert puntuar_seleccion(apt, [{}, {}, {}], "suma_simple") == apt
    assert puntuar_seleccion(apt, [{}, {}, {}], "suma_normalizada") == apt


# ------------------------- integracion end-to-end --------------------------- #
def _ctx(agregacion):
    esq = cargar_esquema(RUTA, REGISTRO_METRICAS)
    esq = dataclasses.replace(esq, agregacion=agregacion)
    cat, sit, kap = cargar_peces()
    esc = {"pH_ref": 7.0, "presupuesto": 8000.0,
           "max_especies": 15, "min_especies": 2}
    return ContextoEvaluacion(esq, cat, sit, kap, esc)


@pytest.mark.parametrize("agregacion", ["pareto_nsga2", "borda", "nsga3"])
def test_ag_corre_en_modo(agregacion):
    ctx = _ctx(agregacion)
    mejor, hist, top_inds, top_apts, _tm = EjecutarAG(
        ctx, tam_poblacion=30, generaciones_max=8,
        min_especies=2, max_especies=6, verbose=False, seed=3)
    assert mejor is not None
    assert len(hist) >= 1
    assert len(top_inds) >= 1
    # en modo multiobjetivo el evaluador expone el vector de objetivos
    assert "_obj" in _tm_primer_met(ctx)


def _tm_primer_met(ctx):
    from src.operadores import FuncionInicializacion
    from src.metricas import evaluar_aptitud
    import numpy as np
    np.random.seed(0)
    ind = FuncionInicializacion(1, ctx.catalogo, ctx.sitios, ctx.esquema,
                                min_especies=2, max_especies=4)[0]
    return evaluar_aptitud(ind, ctx)[1]
