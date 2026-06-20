"""Fase 4: aceptacion por dominio (plantas, arboles, acuicola, terrestre).

Por dominio:
  - la matriz disperso->denso es cuadrada, simetrica, alineada y en [-1, 1];
  - el AG encuentra un mejor ensamblaje FACTIBLE que respeta tolerancias
    ambientales y capacidad de carga;
  - las sinergias suben y los antagonismos bajan la aptitud (equilibrio_pares).
"""
import numpy as np
import pandas as pd
import pytest

from src.esquema import (cargar_esquema, cargar_tablas, cargar_escenarios, _abs)
from src.metricas import (REGISTRO_METRICAS, ContextoEvaluacion, evaluar_aptitud,
                          ejes_factibles)
from src.ga_acucosmos import EjecutarAG
from src.cromosoma import CrearIndividuoVacio

DOMS = {
    "plantas_jardin": "config/plantas_jardin.yaml",
    "arboles_bosque": "config/arboles_bosque.yaml",
    "fauna_acuicola": "config/fauna_acuicola.yaml",
    "fauna_terrestre": "config/fauna_terrestre.yaml",
}


@pytest.fixture(params=list(DOMS), ids=list(DOMS))
def dominio(request):
    esq = cargar_esquema(DOMS[request.param], REGISTRO_METRICAS)
    cat, sit, kap = cargar_tablas(esq)
    escs = cargar_escenarios(esq)
    return request.param, esq, cat, sit, kap, escs


def test_matriz_disperso_denso(dominio):
    _, _esq, cat, _sit, kap, _ = dominio
    n = len(cat)
    assert kap.shape == (n, n)                 # alineada al catalogo
    assert np.allclose(kap, kap.T)             # simetrica
    assert kap.min() >= -1.0 and kap.max() <= 1.0   # reescalada [-2,2]->[-1,1]


def test_ag_encuentra_ensamblaje_factible(dominio):
    nombre, esq, cat, sit, kap, escs = dominio
    e = escs[0]
    ctx = ContextoEvaluacion(esq, cat, sit, kap, e)
    mejor, _hist, _ti, _ta, _tm = EjecutarAG(
        ctx, tanques_permitidos=e["sitios_permitidos"],
        tam_poblacion=40, generaciones_max=25,
        min_especies=e["min_especies"], max_especies=e["max_especies"],
        verbose=False, seed=7)
    _f, m = evaluar_aptitud(mejor, ctx)
    assert m["factible"], f"{nombre}: el mejor no es factible"
    assert m["carga"] < 1.0, f"{nombre}: sobrecarga de capacidad"
    ok, _viol = ejes_factibles(mejor, ctx)
    assert ok, f"{nombre}: viola tolerancia ambiental"


def test_sinergia_supera_antagonismo(dominio):
    nombre, esq, cat, sit, kap, escs = dominio
    ctx = ContextoEvaluacion(esq, cat, sit, kap, escs[0])
    n = len(cat)
    idx = {str(s): i for i, s in enumerate(cat[esq.id_col])}
    df = pd.read_csv(_abs(esq.rutas["interacciones"]), encoding="utf-8-sig")

    def primer_par(cond):
        for _, r in df.iterrows():
            a, b = str(r["especie_a"]), str(r["especie_b"])
            if a in idx and b in idx and cond(float(r["valor"])):
                return idx[a], idx[b]
        return None

    pos = primer_par(lambda v: v > 0)
    neg = primer_par(lambda v: v < 0)
    assert pos and neg, f"{nombre}: faltan pares + y - documentados"

    def equilibrio(par):
        i, j = par
        ind = CrearIndividuoVacio(n)
        ind["tanque"] = 0
        for k in (i, j):
            ind["B"][k] = 1
            ind["C"][k] = 1
            ind["D"][k] = 0.5
        return REGISTRO_METRICAS["equilibrio_pares"](ind, ctx, {"promediar": True})

    assert equilibrio(pos) > equilibrio(neg)
