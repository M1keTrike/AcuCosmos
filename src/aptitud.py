import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

from src.cromosoma import (
    EspeciesActivas, FrecuenciasRelativas, VolumenRequerido, CostoTotal
)


def AptitudEstetica(individuo: Dict, catalogo: pd.DataFrame) -> float:
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0
    p = FrecuenciasRelativas(individuo)
    rarezas = np.array([catalogo.iloc[i]['rareza'] for i in activas])
    termino_rareza = float(np.sum(rarezas * p))
    grupos = set(int(catalogo.iloc[i]['grupo_cromatico']) for i in activas)
    termino_cromatico = len(grupos) / 9.0
    return 0.5 * (termino_rareza + termino_cromatico)


def IndiceBiodiversidad(individuo: Dict) -> float:
    p = FrecuenciasRelativas(individuo)
    n = len(p)
    if n <= 1:
        return 0.0
    p_pos = p[p > 0]
    shannon = -float(np.sum(p_pos * np.log(p_pos)))
    return shannon / np.log(n)


def RatioComodidad(individuo: Dict, catalogo: pd.DataFrame,
                   tanques: pd.DataFrame) -> float:
    v_req = VolumenRequerido(individuo, catalogo)
    if v_req <= 0:
        return 0.0
    v_tanque = float(tanques.iloc[individuo['tanque']]['volumen_L'])
    return v_tanque / v_req


def ConflictoInterespecifico(individuo: Dict, catalogo: pd.DataFrame,
                             matriz_kappa: np.ndarray) -> float:
    activas = EspeciesActivas(individuo)
    n = len(activas)
    if n <= 1:
        return 0.0
    agresividad = np.array([catalogo.iloc[i]['agresividad'] for i in activas])
    estratos = np.array([catalogo.iloc[i]['estrato'] for i in activas])
    total = 0.0
    for a in range(n):
        for b in range(a + 1, n):
            i, j = activas[a], activas[b]
            kappa = float(matriz_kappa[i, j])
            penal_kappa = max(0.0, -kappa)
            if penal_kappa == 0.0:
                continue
            diff_estrato = abs(int(estratos[a]) - int(estratos[b]))
            if diff_estrato == 0:
                O = 1.0
            elif diff_estrato == 1:
                O = float(np.exp(-1.0))
            else:
                continue
            agr_prom = (float(agresividad[a]) + float(agresividad[b])) / 2.0
            total += agr_prom * penal_kappa * O
    factor = 2.0 / (n * (n - 1))
    return factor * total


def SobrecargaBiologica(individuo: Dict, catalogo: pd.DataFrame,
                        tanques: pd.DataFrame) -> float:
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0
    desechos = sum(
        float(catalogo.iloc[i]['tasa_desechos_ghr']) * int(individuo['C'][i])
        for i in activas
    )
    f_max = float(tanques.iloc[individuo['tanque']]['capacidad_filtro_ghr'])
    if f_max <= 0:
        return float('inf')
    return desechos / f_max


def EsCompatiblePH(individuo: Dict, catalogo: pd.DataFrame,
                   pH_ref: float, delta_pH: float = 0.5) -> bool:
    activas = EspeciesActivas(individuo)
    for i in activas:
        pH_min = float(catalogo.iloc[i]['pH_min'])
        pH_max = float(catalogo.iloc[i]['pH_max'])
        if not (pH_min - delta_pH <= pH_ref <= pH_max + delta_pH):
            return False
    return True


def FuncionAptitud(individuo: Dict, catalogo: pd.DataFrame,
                   tanques: pd.DataFrame, matriz_kappa: np.ndarray,
                   pH_ref: float, delta_pH: float = 0.5,
                   presupuesto: Optional[float] = None,
                   max_especies: int = 15,
                   peso_diversidad: float = 0.5
                   ) -> Tuple[float, Dict[str, float]]:
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0, {
            'A_e': 0.0, 'I_b': 0.0, 'R_v': 0.0, 'N_c': 0.0, 'M_s': 0.0,
            'costo': 0, 'factible': False,
            'n_especies': 0, 'B_div': 0.0,
        }

    A_e = AptitudEstetica(individuo, catalogo)
    I_b = IndiceBiodiversidad(individuo)
    R_v = RatioComodidad(individuo, catalogo, tanques)
    N_c = ConflictoInterespecifico(individuo, catalogo, matriz_kappa)
    M_s = SobrecargaBiologica(individuo, catalogo, tanques)
    costo = CostoTotal(individuo, catalogo, tanques)
    n_activas = len(activas)
    B_div = peso_diversidad * min(n_activas / float(max_especies), 1.0)

    metricas = {
        'A_e': A_e, 'I_b': I_b, 'R_v': R_v, 'N_c': N_c, 'M_s': M_s,
        'costo': costo, 'factible': True,
        'n_especies': n_activas, 'B_div': B_div,
    }

    if M_s >= 1.0:
        metricas['factible'] = False
        return 0.0, metricas
    if R_v < 1.0:
        metricas['factible'] = False
        return 0.0, metricas
    if not EsCompatiblePH(individuo, catalogo, pH_ref, delta_pH):
        metricas['factible'] = False
        return 0.0, metricas
    if presupuesto is not None and costo > presupuesto:
        metricas['factible'] = False
        return 0.0, metricas

    R_v_hat = min(R_v / 2.0, 1.0)
    M_s_hat = min(M_s, 1.0)
    F_total = A_e + I_b + R_v_hat - N_c - M_s_hat + B_div
    return float(F_total), metricas
