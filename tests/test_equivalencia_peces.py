"""Equivalencia Fase 1: el evaluador generico (esquema + registro de metricas)
reproduce EXACTAMENTE la `FuncionAptitud` original (frozen) para `peces_ornamental`.

Es la garantia a nivel de evaluacion (independiente del stream del AG) de que la
generalizacion no cambia la semantica de peces. La reproducibilidad end-to-end la
verifica `test_regresion.py` (golden output).
"""
import numpy as np
import pytest

from src.esquema import cargar_esquema
from src.metricas import REGISTRO_METRICAS, ContextoEvaluacion, evaluar_aptitud
from src.aptitud import FuncionAptitud
from src.operadores import FuncionInicializacion
from src.cromosoma import CrearIndividuoVacio
from tests.golden_lib import cargar_peces

ESCENARIOS = [
    {"pH_ref": 7.0, "presupuesto": 8000.0, "max_especies": 15, "min_especies": 5},
    {"pH_ref": 5.5, "presupuesto": 12000.0, "max_especies": 15, "min_especies": 5},
    {"pH_ref": 7.0, "presupuesto": 3000.0, "max_especies": 6, "min_especies": 2},
]


@pytest.fixture(scope="module")
def base():
    esquema = cargar_esquema("config/peces_ornamental.yaml", REGISTRO_METRICAS)
    catalogo, sitios, kappa = cargar_peces()
    return esquema, catalogo, sitios, kappa


def _igual(a, b, tol=1e-12):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if a == float("inf") or b == float("inf"):
        return a == b
    return abs(float(a) - float(b)) <= tol


def _comparar(individuo, ctx, cfg, catalogo, sitios, kappa):
    F_new, m_new = evaluar_aptitud(individuo, ctx)
    F_old, m_old = FuncionAptitud(
        individuo, catalogo, sitios, kappa, pH_ref=cfg["pH_ref"],
        delta_pH=0.5, presupuesto=cfg["presupuesto"],
        max_especies=cfg["max_especies"])
    assert _igual(F_new, F_old), f"F: nuevo={F_new} viejo={F_old}"
    assert set(m_new) == set(m_old), f"claves: {set(m_new)} vs {set(m_old)}"
    for k in m_old:
        assert _igual(m_new[k], m_old[k]), f"metrica {k}: {m_new[k]} vs {m_old[k]}"


@pytest.mark.parametrize("cfg", ESCENARIOS,
                         ids=["pH7_b8000", "pH5.5_b12000", "nano_pH7_b3000"])
def test_evaluar_equivale_a_funcionaptitud(base, cfg):
    esquema, catalogo, sitios, kappa = base
    ctx = ContextoEvaluacion(esquema, catalogo, sitios, kappa, dict(cfg))
    np.random.seed(7)
    poblacion = FuncionInicializacion(
        300, catalogo, sitios, esquema, min_especies=cfg["min_especies"],
        max_especies=cfg["max_especies"])
    for individuo in poblacion:
        _comparar(individuo, ctx, cfg, catalogo, sitios, kappa)


def test_individuo_vacio(base):
    esquema, catalogo, sitios, kappa = base
    cfg = ESCENARIOS[0]
    ctx = ContextoEvaluacion(esquema, catalogo, sitios, kappa, dict(cfg))
    vacio = CrearIndividuoVacio(len(catalogo))
    _comparar(vacio, ctx, cfg, catalogo, sitios, kappa)
