"""Invariantes estructurales del cromosoma y la reparacion (cf. §11 del contexto).

Se prueban las garantias que el codigo ACTUAL realmente mantiene:
  - >=1 especie activa; `tanque` en rango.
  - activa  -> C >= min_cardumen (>=1) y D >= 0.
  - inactiva -> C == 0 y D == 0.
  - Sum(D sobre activas) == 1 (normalizada).
  - kappa: cuadrada y alineada al catalogo, simetrica, en [-1, 1].

Nota: la coherencia documentada incluye "D > 0 si activa", pero la reparacion
solo garantiza la *normalizacion* (suma 1), no la positividad estricta: la
mutacion `p_m4` puede dejar en 0 la proporcion de una activa y la reparacion no
la corrige. Por eso aqui se exige D >= 0 (comportamiento real, no se altera en
Fase 0 para no romper la reproducibilidad del golden output).
"""
import numpy as np
import pytest

from src.operadores import (FuncionInicializacion, FuncionReparacion,
                            FuncionMutacion, CruzaUniforme)
from src.cromosoma import EspeciesActivas, CrearIndividuoVacio
from tests.golden_lib import cargar_peces, SEED


@pytest.fixture(scope="module")
def datos():
    return cargar_peces()


def _check_invariantes(ind, catalogo, n_tanques):
    activas = EspeciesActivas(ind)
    assert len(activas) >= 1
    assert 0 <= ind["tanque"] < n_tanques
    for i in range(len(ind["B"])):
        if ind["B"][i] == 1:
            c_min = max(int(catalogo.iloc[i]["min_cardumen"]), 1)
            assert ind["C"][i] >= c_min
            assert ind["D"][i] >= 0.0
        else:
            assert ind["C"][i] == 0
            assert ind["D"][i] == 0.0
    suma = sum(float(ind["D"][i]) for i in activas)
    assert abs(suma - 1.0) < 1e-9


def test_kappa_simetrica_alineada(datos):
    catalogo, _tanques, kappa = datos
    n = len(catalogo)
    assert kappa.shape == (n, n)
    assert np.allclose(kappa, kappa.T)
    assert np.all(kappa >= -1.0) and np.all(kappa <= 1.0)


def test_inicializacion_invariantes(datos):
    catalogo, tanques, _kappa = datos
    np.random.seed(SEED)
    pob = FuncionInicializacion(50, catalogo, tanques,
                                min_especies=3, max_especies=15)
    for ind in pob:
        _check_invariantes(ind, catalogo, len(tanques))


def test_reparacion_corrige_individuo_roto(datos):
    catalogo, tanques, _kappa = datos
    n = len(catalogo)
    ind = CrearIndividuoVacio(n)
    ind["tanque"] = 999                       # fuera de rango
    ind["B"][5] = 1
    ind["C"][5] = 0                           # activa con C bajo el minimo
    ind["B"][10] = 0
    ind["C"][10] = 7
    ind["D"][10] = 0.5                        # inactiva con C/D != 0
    ind["B"][20] = 1
    ind["C"][20] = 9
    ind["D"][20] = 0.5                        # D sin normalizar
    FuncionReparacion(ind, catalogo, tanques)
    _check_invariantes(ind, catalogo, len(tanques))


def test_reparacion_garantiza_una_activa(datos):
    catalogo, tanques, _kappa = datos
    np.random.seed(SEED)
    ind = CrearIndividuoVacio(len(catalogo))  # cero activas
    FuncionReparacion(ind, catalogo, tanques)
    assert len(EspeciesActivas(ind)) >= 1
    _check_invariantes(ind, catalogo, len(tanques))


def test_mutacion_preserva_invariantes(datos):
    catalogo, tanques, _kappa = datos
    np.random.seed(SEED)
    pob = FuncionInicializacion(30, catalogo, tanques,
                                min_especies=3, max_especies=15)
    for ind in pob:
        m = FuncionMutacion(ind, catalogo, tanques)
        _check_invariantes(m, catalogo, len(tanques))


def test_cruza_preserva_invariantes(datos):
    catalogo, tanques, _kappa = datos
    np.random.seed(SEED)
    pob = FuncionInicializacion(30, catalogo, tanques,
                                min_especies=3, max_especies=15)
    for a, b in zip(pob[::2], pob[1::2]):
        h1, h2 = CruzaUniforme(a, b, catalogo, tanques)
        _check_invariantes(h1, catalogo, len(tanques))
        _check_invariantes(h2, catalogo, len(tanques))
