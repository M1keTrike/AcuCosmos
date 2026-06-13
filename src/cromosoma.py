import numpy as np
import pandas as pd
from typing import Dict, List


def CrearIndividuoVacio(n_cat: int) -> Dict:
    return {
        'tanque': 0,
        'B': np.zeros(n_cat, dtype=int),
        'C': np.zeros(n_cat, dtype=int),
        'D': np.zeros(n_cat, dtype=float)
    }


def EspeciesActivas(individuo: Dict) -> List[int]:
    return [i for i in range(len(individuo['B'])) if individuo['B'][i] == 1]


def NumeroEspeciesActivas(individuo: Dict) -> int:
    return int(individuo['B'].sum())


def PoblacionTotal(individuo: Dict) -> int:
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0
    return int(sum(individuo['C'][i] for i in activas))


def FrecuenciasRelativas(individuo: Dict) -> np.ndarray:
    activas = EspeciesActivas(individuo)
    if not activas:
        return np.array([])
    C_activas = np.array([individuo['C'][i] for i in activas])
    N = C_activas.sum()
    if N == 0:
        return np.zeros(len(activas))
    return C_activas / N


def DescribirIndividuo(individuo: Dict, catalogo: pd.DataFrame) -> pd.DataFrame:
    activas = EspeciesActivas(individuo)
    if not activas:
        return pd.DataFrame()
    filas = []
    for i in activas:
        esp = catalogo.iloc[i]
        filas.append({
            'id': int(esp['id']),
            'nombre_comun': esp['nombre_comun'],
            'cantidad': int(individuo['C'][i]),
            'estrato': esp.get('estrato_nombre', esp['estrato']),
            'grupo_cromatico': esp.get('grupo_cromatico_nombre',
                                        esp['grupo_cromatico']),
            'D_i': round(float(individuo['D'][i]), 3),
            'precio_MXN': int(esp['precio_est_MXN']) * int(individuo['C'][i])
        })
    return pd.DataFrame(filas)


def VolumenRequerido(individuo: Dict, catalogo: pd.DataFrame) -> float:
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0
    return float(sum(
        catalogo.iloc[i]['vol_por_individuo_L'] * individuo['C'][i]
        for i in activas
    ))


def CostoTotal(individuo: Dict, catalogo: pd.DataFrame,
               tanques: pd.DataFrame) -> int:
    activas = EspeciesActivas(individuo)
    costo_especies = sum(
        int(catalogo.iloc[i]['precio_est_MXN']) * int(individuo['C'][i])
        for i in activas
    )
    costo_tanque = int(tanques.iloc[individuo['tanque']]['precio_MXN'])
    return costo_especies + costo_tanque
