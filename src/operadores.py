import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from src.cromosoma import CrearIndividuoVacio, EspeciesActivas


def _cmin(catalogo: pd.DataFrame, esquema, i: int) -> int:
    """Cardumen/agrupacion minima de la especie i (rol 'min_agrupacion').

    Devuelve 1 si el dominio no declara ese rasgo (columna ausente / None).
    """
    col = esquema.col("min_agrupacion")
    if col is None:
        return 1
    return max(int(catalogo.iloc[i][col]), 1)


def FuncionInicializacion(tam_poblacion: int, catalogo: pd.DataFrame,
                          tanques: pd.DataFrame, esquema,
                          min_especies: int = 3,
                          max_especies: int = 15,
                          tanques_permitidos: List[int] = None
                          ) -> List[Dict]:
    n_cat = len(catalogo)
    if tanques_permitidos is None:
        tanques_permitidos = list(range(len(tanques)))
    poblacion = []
    for idx in range(tam_poblacion):
        ind = CrearIndividuoVacio(n_cat)
        if idx < len(tanques_permitidos):
            ind['tanque'] = int(tanques_permitidos[idx])
        else:
            ind['tanque'] = int(np.random.choice(tanques_permitidos))
        k = np.random.randint(min_especies, max_especies + 1)
        idx_sp = np.random.choice(n_cat, size=k, replace=False)
        ind['B'][idx_sp] = 1
        for i in idx_sp:
            c_min = _cmin(catalogo, esquema, i)
            ind['C'][i] = int(np.random.randint(c_min, max(c_min + 1, 2 * c_min + 1)))
        alpha = np.ones(k)
        d = np.random.dirichlet(alpha)
        for pos, i in enumerate(idx_sp):
            ind['D'][i] = float(d[pos])
        poblacion.append(ind)
    return poblacion


def FuncionReparacion(individuo: Dict, catalogo: pd.DataFrame,
                      tanques: pd.DataFrame, esquema,
                      tanques_permitidos: List[int] = None) -> Dict:
    n_cat = len(catalogo)
    n_tanques = len(tanques)

    if individuo['tanque'] < 0 or individuo['tanque'] >= n_tanques:
        individuo['tanque'] = int(np.random.randint(0, n_tanques))

    for i in range(n_cat):
        if individuo['B'][i] == 1:
            c_min = _cmin(catalogo, esquema, i)
            if individuo['C'][i] < c_min:
                individuo['C'][i] = c_min
        else:
            individuo['C'][i] = 0
            individuo['D'][i] = 0.0

    activas = EspeciesActivas(individuo)
    if not activas:
        i = int(np.random.randint(0, n_cat))
        individuo['B'][i] = 1
        individuo['C'][i] = _cmin(catalogo, esquema, i)
        individuo['D'][i] = 1.0
        activas = [i]

    suma_d = float(sum(individuo['D'][i] for i in activas))
    if suma_d <= 1e-12:
        val = 1.0 / len(activas)
        for i in activas:
            individuo['D'][i] = val
    else:
        for i in activas:
            individuo['D'][i] = float(individuo['D'][i]) / suma_d

    # Reasignacion por sobrecarga de capacidad (rol carga vs capacidad del sitio).
    # Si el dominio no declara esos rasgos, se omite (no hay concepto de carga).
    col_carga = esquema.col("carga_individuo")
    col_cap = esquema.col("capacidad_sitio")
    if tanques_permitidos is None:
        tanques_permitidos = list(range(n_tanques))
    if col_carga is not None and col_cap is not None:
        desechos = float(sum(
            float(catalogo.iloc[i][col_carga]) * int(individuo['C'][i])
            for i in activas
        ))
        f_max_actual = float(tanques.iloc[individuo['tanque']][col_cap])
        if f_max_actual > 0 and desechos / f_max_actual >= 1.0:
            candidatos = [
                (t, float(tanques.iloc[t][col_cap]))
                for t in tanques_permitidos
            ]
            candidatos.sort(key=lambda x: x[1])
            for t, f in candidatos:
                if f > 0 and desechos / f < 1.0:
                    individuo['tanque'] = int(t)
                    break

    return individuo


def SeleccionTorneo(poblacion: List[Dict], aptitudes: List[float],
                    t: int = 3) -> Dict:
    idx = np.random.choice(len(poblacion), size=t, replace=False)
    mejor = idx[0]
    for k in idx[1:]:
        if aptitudes[k] > aptitudes[mejor]:
            mejor = k
    return poblacion[mejor]


def CopiarIndividuo(individuo: Dict) -> Dict:
    return {
        'tanque': int(individuo['tanque']),
        'B': individuo['B'].copy(),
        'C': individuo['C'].copy(),
        'D': individuo['D'].copy()
    }


def CruzaUniforme(padre_a: Dict, padre_b: Dict,
                  catalogo: pd.DataFrame,
                  tanques: pd.DataFrame, esquema,
                  tanques_permitidos: List[int] = None
                  ) -> Tuple[Dict, Dict]:
    n_cat = len(padre_a['B'])
    hijo_1 = CrearIndividuoVacio(n_cat)
    hijo_2 = CrearIndividuoVacio(n_cat)

    if np.random.rand() < 0.5:
        hijo_1['tanque'] = int(padre_a['tanque'])
        hijo_2['tanque'] = int(padre_b['tanque'])
    else:
        hijo_1['tanque'] = int(padre_b['tanque'])
        hijo_2['tanque'] = int(padre_a['tanque'])

    mascara = np.random.rand(n_cat) < 0.5
    for i in range(n_cat):
        if mascara[i]:
            hijo_1['B'][i] = padre_a['B'][i]
            hijo_1['C'][i] = padre_a['C'][i]
            hijo_1['D'][i] = padre_a['D'][i]
            hijo_2['B'][i] = padre_b['B'][i]
            hijo_2['C'][i] = padre_b['C'][i]
            hijo_2['D'][i] = padre_b['D'][i]
        else:
            hijo_1['B'][i] = padre_b['B'][i]
            hijo_1['C'][i] = padre_b['C'][i]
            hijo_1['D'][i] = padre_b['D'][i]
            hijo_2['B'][i] = padre_a['B'][i]
            hijo_2['C'][i] = padre_a['C'][i]
            hijo_2['D'][i] = padre_a['D'][i]

    hijo_1 = FuncionReparacion(hijo_1, catalogo, tanques, esquema,
                               tanques_permitidos)
    hijo_2 = FuncionReparacion(hijo_2, catalogo, tanques, esquema,
                               tanques_permitidos)
    return hijo_1, hijo_2


def FuncionMutacion(individuo: Dict, catalogo: pd.DataFrame,
                    tanques: pd.DataFrame, esquema,
                    p_m1: float = 0.15, p_m2: float = 0.10,
                    p_m3: float = 0.15, p_m4: float = 0.15,
                    tanques_permitidos: List[int] = None) -> Dict:
    n_cat = len(catalogo)
    n_tanques = len(tanques)
    if tanques_permitidos is None:
        tanques_permitidos = list(range(n_tanques))

    if np.random.rand() < p_m1:
        individuo['tanque'] = int(np.random.choice(tanques_permitidos))

    if np.random.rand() < p_m2:
        i = int(np.random.randint(0, n_cat))
        if individuo['B'][i] == 1:
            individuo['B'][i] = 0
            individuo['C'][i] = 0
            individuo['D'][i] = 0.0
        else:
            individuo['B'][i] = 1
            individuo['C'][i] = _cmin(catalogo, esquema, i)
            individuo['D'][i] = 0.05

    if np.random.rand() < p_m3:
        activas = EspeciesActivas(individuo)
        if activas:
            i = int(np.random.choice(activas))
            delta = int(np.random.randint(-3, 4))
            if delta != 0:
                individuo['C'][i] = max(0, int(individuo['C'][i]) + delta)
                if individuo['C'][i] == 0:
                    individuo['B'][i] = 0
                    individuo['D'][i] = 0.0

    if np.random.rand() < p_m4:
        activas = EspeciesActivas(individuo)
        if len(activas) >= 2:
            i, j = np.random.choice(activas, size=2, replace=False)
            eps = float(np.random.uniform(0.0, 0.1))
            eps = min(eps, float(individuo['D'][i]))
            individuo['D'][i] = float(individuo['D'][i]) - eps
            individuo['D'][j] = float(individuo['D'][j]) + eps

    individuo = FuncionReparacion(individuo, catalogo, tanques, esquema,
                                  tanques_permitidos)
    return individuo


def PodaElitista(padres: List[Dict], hijos: List[Dict],
                 apt_padres: List[float], apt_hijos: List[float],
                 tam_poblacion: int
                 ) -> Tuple[List[Dict], List[float]]:
    combinados = padres + hijos
    aptitudes = list(apt_padres) + list(apt_hijos)
    orden = sorted(range(len(combinados)), key=lambda k: aptitudes[k],
                   reverse=True)
    seleccion = orden[:tam_poblacion]
    nueva_pob = [combinados[k] for k in seleccion]
    nuevas_apt = [aptitudes[k] for k in seleccion]
    return nueva_pob, nuevas_apt
