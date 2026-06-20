"""Fase 5: la salida generica multi-dominio corre end-to-end y genera archivos."""
import os

from main import ejecutar_dominio


def test_ejecutar_dominio_genera_salidas(tmp_path):
    salida = ejecutar_dominio(
        "config/plantas_jardin.yaml", nombre_escenario="huerto_familiar",
        dir_salida=str(tmp_path), seed=5, generaciones=8, poblacion=20,
        mostrar=False)
    assert len(salida) == 1
    d = os.path.join(str(tmp_path), "plantas_jardin")
    base = os.path.join(d, "plantas_jardin_huerto_familiar")
    for suf in ("_aptitud.png", "_metricas.png", "_estratos.png",
                "_top_resumen.csv", "_top1.csv"):
        assert os.path.exists(base + suf), f"falta {suf}"
