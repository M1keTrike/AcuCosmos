"""Regresion Fase 0: el motor reproduce el *golden output* con la misma semilla.

En Fase 1 (motor generico via EsquemaDominio) este test DEBE seguir verde:
`peces_ornamental` == golden output (dentro de tolerancia numerica).
"""
import os

import pytest

from tests.golden_lib import (ESCENARIOS, correr_escenario, cargar_golden,
                              ruta_golden, comparar_canon)

_faltan = [c["nombre"] for c in ESCENARIOS
           if not os.path.exists(ruta_golden(c["nombre"]))]


@pytest.mark.skipif(
    bool(_faltan),
    reason="Falta golden output; corre: python -m tests.generar_golden")
@pytest.mark.parametrize("cfg", ESCENARIOS,
                         ids=[c["nombre"] for c in ESCENARIOS])
def test_regresion_golden(cfg):
    esperado = cargar_golden(cfg["nombre"])
    obtenido = correr_escenario(cfg)
    difs = comparar_canon(esperado, obtenido)
    assert not difs, "Regresion rota en {}:\n  - {}".format(
        cfg["nombre"], "\n  - ".join(difs))
