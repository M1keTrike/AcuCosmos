"""Carga y validacion de EsquemaDominio (cargar_esquema)."""
import pytest
import yaml

from src.esquema import cargar_esquema
from src.metricas import REGISTRO_METRICAS

RUTA_PECES = "config/peces_ornamental.yaml"


def _base_cfg():
    return {
        "dominio": "prueba",
        "rutas": {
            "catalogo": "data/catalogo_especies.csv",
            "sitios": "data/catalogo_tanques.csv",
            "interacciones": "data/matriz_compatibilidad.csv",
        },
        "id_col": "id",
        "rasgos": {"agresividad": "agresividad"},
        "estratos": {"col": "estrato", "orden": [1, 2, 3],
                     "kernel": "legacy_peces"},
        "ejes_ambientales": [
            {"col_min": "pH_min", "col_max": "pH_max", "ref": "pH_ref", "tol": 0.5}],
        "metricas": [{"nombre": "biodiversidad_shannon", "peso": 1.0,
                      "signo": 1, "clave_reporte": "I_b"}],
        "restricciones": [{"tipo": "ambiental"}],
        "penalizaciones": {"modo": "mortal"},
        "agregacion": "suma_simple",
        "params": {"interacciones_formato": "densa"},
    }


def _escribir(tmp_path, cfg):
    p = tmp_path / "dom.yaml"
    p.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return str(p)


def test_carga_peces_ok():
    esq = cargar_esquema(RUTA_PECES, REGISTRO_METRICAS)
    assert esq.dominio == "peces_ornamental"
    assert len(esq.metricas) == 6
    assert len(esq.ejes_ambientales) == 1
    assert esq.col("agresividad") == "agresividad"
    assert esq.col("min_agrupacion") == "min_cardumen"
    assert esq.estratos["kernel"] == "legacy_peces"


def test_base_cfg_valida(tmp_path):
    cargar_esquema(_escribir(tmp_path, _base_cfg()), REGISTRO_METRICAS)


def test_metrica_desconocida_falla(tmp_path):
    cfg = _base_cfg()
    cfg["metricas"] = [{"nombre": "no_existe", "peso": 1.0, "signo": 1,
                        "clave_reporte": "x"}]
    with pytest.raises(ValueError, match="no existe en el registro"):
        cargar_esquema(_escribir(tmp_path, cfg), REGISTRO_METRICAS)


def test_columna_inexistente_falla(tmp_path):
    cfg = _base_cfg()
    cfg["rasgos"] = {"agresividad": "columna_fantasma"}
    with pytest.raises(ValueError, match="no existe"):
        cargar_esquema(_escribir(tmp_path, cfg), REGISTRO_METRICAS)


def test_eje_columna_inexistente_falla(tmp_path):
    cfg = _base_cfg()
    cfg["ejes_ambientales"] = [
        {"col_min": "no_col", "col_max": "pH_max", "ref": "pH_ref", "tol": 0.5}]
    with pytest.raises(ValueError, match="eje ambiental"):
        cargar_esquema(_escribir(tmp_path, cfg), REGISTRO_METRICAS)


def test_agregacion_invalida_falla(tmp_path):
    cfg = _base_cfg()
    cfg["agregacion"] = "magia"
    with pytest.raises(ValueError, match="agregacion invalida"):
        cargar_esquema(_escribir(tmp_path, cfg), REGISTRO_METRICAS)


def test_falta_campo_obligatorio(tmp_path):
    cfg = _base_cfg()
    del cfg["id_col"]
    with pytest.raises(ValueError, match="campo obligatorio"):
        cargar_esquema(_escribir(tmp_path, cfg), REGISTRO_METRICAS)
