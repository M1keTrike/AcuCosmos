"""Casos borde y robustez/fuzz: el sistema maneja con gracia escenarios extremos
y entradas malformadas (sin excepciones inesperadas; errores claros donde toca)."""
import numpy as np
import pytest
import yaml

from src.esquema import cargar_esquema, cargar_tablas
from src.metricas import REGISTRO_METRICAS, ContextoEvaluacion, evaluar_aptitud
from src.ga_acucosmos import EjecutarAG
from src.operadores import FuncionInicializacion


def _carga(dom):
    esq = cargar_esquema(f"config/{dom}.yaml", REGISTRO_METRICAS)
    cat, sit, kap = cargar_tablas(esq)
    return esq, cat, sit, kap


def test_escenario_imposible_no_crashea():
    esq, cat, sit, kap = _carga("fauna_acuicola")
    esc = {"temp_ref": 80, "ph_ref": 7.0, "od_ref": 5.0, "presupuesto": 5000,
           "max_especies": 5, "min_especies": 3}                 # 80 °C: imposible
    ctx = ContextoEvaluacion(esq, cat, sit, kap, esc)
    mejor, _h, *_ = EjecutarAG(ctx, tam_poblacion=20, generaciones_max=8,
                               min_especies=3, max_especies=5, verbose=False, seed=1)
    f, m = evaluar_aptitud(mejor, ctx)
    assert not m["factible"] and f == 0.0


def test_presupuesto_diminuto_infactible():
    esq, cat, sit, kap = _carga("arboles_bosque")
    esc = {"temp_ref": 25, "precip_ref": 2000, "ph_ref": 6.0, "zona_ref": 11,
           "presupuesto": 1.0, "max_especies": 5, "min_especies": 3}   # $1
    ctx = ContextoEvaluacion(esq, cat, sit, kap, esc)
    mejor, _h, *_ = EjecutarAG(ctx, tanques_permitidos=[0], tam_poblacion=20,
                               generaciones_max=6, min_especies=3,
                               max_especies=5, verbose=False, seed=1)
    f, m = evaluar_aptitud(mejor, ctx)
    assert not m["factible"] and f == 0.0


def test_min_igual_max_corre():
    esq, cat, sit, kap = _carga("plantas_jardin")
    esc = {"temp_ref": 24, "ph_ref": 6.5, "zona_ref": 11, "presupuesto": 300,
           "max_especies": 4, "min_especies": 4}
    ctx = ContextoEvaluacion(esq, cat, sit, kap, esc)
    mejor, _h, *_ = EjecutarAG(ctx, tanques_permitidos=[2, 3], tam_poblacion=20,
                               generaciones_max=6, min_especies=4,
                               max_especies=4, verbose=False, seed=1)
    assert mejor is not None


def test_yaml_columna_inexistente_falla_claro(tmp_path):
    cfg = {
        "dominio": "x",
        "rutas": {"catalogo": "kb/plantas/plantas.csv",
                  "sitios": "kb/plantas/plantas_sitios.csv",
                  "interacciones": "kb/plantas/plantas_pares_documentados.csv"},
        "id_col": "id",
        "rasgos": {"carga_individuo": "columna_que_no_existe"},
        "estratos": {"col": "estrato", "orden": ["bajo"], "kernel": "exp_neg"},
        "ejes_ambientales": [],
        "metricas": [{"nombre": "biodiversidad_shannon", "peso": 1, "signo": 1,
                      "clave_reporte": "I_b"}],
        "agregacion": "suma_simple",
        "params": {"interacciones_formato": "disperso", "escala_origen": [-2, 2]},
    }
    p = tmp_path / "malo.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="no existe"):
        cargar_esquema(str(p), REGISTRO_METRICAS)


def test_evaluador_no_crashea_con_aleatorios():
    esc = {"temp_ref": 25, "ph_ref": 6.5, "zona_ref": 11, "precip_ref": 2000,
           "od_ref": 5.0, "presupuesto": 5000, "max_especies": 6,
           "min_especies": 2}
    for dom in ("plantas_jardin", "arboles_bosque", "fauna_acuicola",
                "fauna_terrestre"):
        esq, cat, sit, kap = _carga(dom)
        ctx = ContextoEvaluacion(esq, cat, sit, kap, esc)
        np.random.seed(0)
        pob = FuncionInicializacion(80, cat, sit, esq,
                                    min_especies=2, max_especies=6)
        for ind in pob:
            f, m = evaluar_aptitud(ind, ctx)
            assert isinstance(f, float)
            assert "factible" in m and "n_especies" in m
