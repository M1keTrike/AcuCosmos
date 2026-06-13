import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from src.aptitud import FuncionAptitud
from src.operadores import (
    FuncionInicializacion, SeleccionTorneo, CruzaUniforme,
    FuncionMutacion, CopiarIndividuo
)


def EjecutarAG(catalogo: pd.DataFrame,
               tanques: pd.DataFrame,
               matriz_kappa: np.ndarray,
               pH_ref: float,
               delta_pH: float = 0.5,
               presupuesto: Optional[float] = None,
               tanques_permitidos: Optional[List[int]] = None,
               tam_poblacion: int = 80,
               generaciones_max: int = 150,
               estancamiento_max: int = 30,
               t_torneo: int = 3,
               min_especies: int = 3,
               max_especies: int = 15,
               top_k: int = 3,
               verbose: bool = True
               ) -> Tuple[Dict, List[Dict], List[Dict], List[float], List[Dict]]:
    poblacion = FuncionInicializacion(
        tam_poblacion, catalogo, tanques,
        min_especies=min_especies, max_especies=max_especies,
        tanques_permitidos=tanques_permitidos
    )
    aptitudes = []
    metricas_list = []
    for ind in poblacion:
        f, m = FuncionAptitud(ind, catalogo, tanques, matriz_kappa,
                              pH_ref, delta_pH, presupuesto,
                              max_especies=max_especies)
        aptitudes.append(f)
        metricas_list.append(m)

    historial: List[Dict] = []
    mejor_global_idx = int(np.argmax(aptitudes))
    mejor_global = CopiarIndividuo(poblacion[mejor_global_idx])
    mejor_global_apt = aptitudes[mejor_global_idx]
    mejor_global_metricas = metricas_list[mejor_global_idx]
    estancamiento = 0

    def _hash_individuo(ind: Dict) -> Tuple:
        activas = tuple(sorted(
            (i, int(ind['C'][i]))
            for i in range(len(ind['B'])) if ind['B'][i] == 1
        ))
        return (int(ind['tanque']), activas)

    hall: Dict[Tuple, Tuple[float, Dict, Dict]] = {}

    def _actualizar_hall(pob: List[Dict], apts: List[float],
                         mets: List[Dict]) -> None:
        for ind, f, m in zip(pob, apts, mets):
            if not m.get('factible', False):
                continue
            h = _hash_individuo(ind)
            if h not in hall or hall[h][0] < f:
                hall[h] = (f, CopiarIndividuo(ind), dict(m))

    _actualizar_hall(poblacion, aptitudes, metricas_list)

    m_init = metricas_list[mejor_global_idx]
    historial.append({
        'generacion': 0,
        'apt_mejor': float(max(aptitudes)),
        'apt_peor': float(min(aptitudes)),
        'apt_promedio': float(np.mean(aptitudes)),
        'A_e': m_init['A_e'],
        'I_b': m_init['I_b'],
        'R_v': m_init['R_v'],
        'N_c': m_init['N_c'],
        'M_s': m_init['M_s'],
        'costo': m_init['costo'],
        'factible': m_init['factible'],
    })
    if verbose:
        factible_str = "OK" if m_init['factible'] else "INF"
        print(f"  Gen   0 | mejor={historial[0]['apt_mejor']:.4f} "
              f"prom={historial[0]['apt_promedio']:.4f} | "
              f"A_e={m_init['A_e']:.3f} I_b={m_init['I_b']:.3f} "
              f"R_v={m_init['R_v']:.2f} N_c={m_init['N_c']:.3f} "
              f"M_s={m_init['M_s']:.3f} "
              f"${m_init['costo']} [{factible_str}]")

    sin_factibles = 0
    REINICIO_TRAS = 15
    FRAC_REINICIO = 0.5

    for g in range(generaciones_max):
        hijos: List[Dict] = []
        while len(hijos) < tam_poblacion:
            padre_a = SeleccionTorneo(poblacion, aptitudes, t=t_torneo)
            padre_b = SeleccionTorneo(poblacion, aptitudes, t=t_torneo)
            h1, h2 = CruzaUniforme(padre_a, padre_b, catalogo, tanques,
                                   tanques_permitidos=tanques_permitidos)
            h1 = FuncionMutacion(h1, catalogo, tanques,
                                 tanques_permitidos=tanques_permitidos)
            h2 = FuncionMutacion(h2, catalogo, tanques,
                                 tanques_permitidos=tanques_permitidos)
            hijos.append(h1)
            if len(hijos) < tam_poblacion:
                hijos.append(h2)

        apt_hijos = []
        met_hijos = []
        for ind in hijos:
            f, m = FuncionAptitud(ind, catalogo, tanques, matriz_kappa,
                                  pH_ref, delta_pH, presupuesto,
                                  max_especies=max_especies)
            apt_hijos.append(f)
            met_hijos.append(m)

        combinados = poblacion + hijos
        combinadas_apt = list(aptitudes) + apt_hijos
        combinadas_met = list(metricas_list) + met_hijos

        apt_mejor = float(max(combinadas_apt))
        apt_peor = float(min(combinadas_apt))
        apt_prom = float(np.mean(combinadas_apt))
        mejor_idx_pre = int(np.argmax(combinadas_apt))
        m_mejor = combinadas_met[mejor_idx_pre]

        historial.append({
            'generacion': g + 1,
            'apt_mejor': apt_mejor,
            'apt_peor': apt_peor,
            'apt_promedio': apt_prom,
            'A_e': m_mejor['A_e'],
            'I_b': m_mejor['I_b'],
            'R_v': m_mejor['R_v'],
            'N_c': m_mejor['N_c'],
            'M_s': m_mejor['M_s'],
            'costo': m_mejor['costo'],
            'factible': m_mejor['factible'],
        })

        orden = sorted(range(len(combinados)),
                       key=lambda k: combinadas_apt[k], reverse=True)
        sel = orden[:tam_poblacion]
        poblacion = [combinados[k] for k in sel]
        aptitudes = [combinadas_apt[k] for k in sel]
        metricas_list = [combinadas_met[k] for k in sel]

        _actualizar_hall(hijos, apt_hijos, met_hijos)

        hay_factible = any(m.get('factible', False) for m in metricas_list)
        if hay_factible:
            sin_factibles = 0
        else:
            sin_factibles += 1
            if sin_factibles >= REINICIO_TRAS:
                n_rein = max(1, int(tam_poblacion * FRAC_REINICIO))
                nuevos = FuncionInicializacion(
                    n_rein, catalogo, tanques,
                    min_especies=min_especies, max_especies=max_especies,
                    tanques_permitidos=tanques_permitidos
                )
                nuevas_apt = []
                nuevas_met = []
                for ind in nuevos:
                    f, m = FuncionAptitud(ind, catalogo, tanques, matriz_kappa,
                                          pH_ref, delta_pH, presupuesto,
                                          max_especies=max_especies)
                    nuevas_apt.append(f)
                    nuevas_met.append(m)
                orden_act = sorted(range(len(poblacion)),
                                   key=lambda k: aptitudes[k])
                reemplazar = orden_act[:n_rein]
                for k, (ind_n, f_n, m_n) in enumerate(
                        zip(nuevos, nuevas_apt, nuevas_met)):
                    pos = reemplazar[k]
                    poblacion[pos] = ind_n
                    aptitudes[pos] = f_n
                    metricas_list[pos] = m_n
                _actualizar_hall(nuevos, nuevas_apt, nuevas_met)
                sin_factibles = 0

        if apt_mejor > mejor_global_apt + 1e-9:
            mejor_global_apt = apt_mejor
            mejor_global = CopiarIndividuo(combinados[mejor_idx_pre])
            mejor_global_metricas = m_mejor
            estancamiento = 0
        else:
            estancamiento += 1

        if verbose and ((g + 1) % 10 == 0 or g == 0):
            factible_str = "OK" if m_mejor['factible'] else "INF"
            print(f"  Gen {g+1:3d} | mejor={apt_mejor:.4f} "
                  f"prom={apt_prom:.4f} | "
                  f"A_e={m_mejor['A_e']:.3f} I_b={m_mejor['I_b']:.3f} "
                  f"R_v={m_mejor['R_v']:.2f} N_c={m_mejor['N_c']:.3f} "
                  f"M_s={m_mejor['M_s']:.3f} "
                  f"${m_mejor['costo']} [{factible_str}]")

        if estancamiento >= estancamiento_max:
            break

    items_hall = sorted(hall.values(), key=lambda t: t[0], reverse=True)
    top_individuos: List[Dict] = []
    top_aptitudes: List[float] = []
    top_metricas: List[Dict] = []
    for f, ind, met in items_hall[:top_k]:
        top_individuos.append(CopiarIndividuo(ind))
        top_aptitudes.append(float(f))
        top_metricas.append(dict(met))

    if len(top_individuos) < top_k:
        orden_final = sorted(range(len(poblacion)),
                             key=lambda k: aptitudes[k], reverse=True)
        for i in orden_final:
            if len(top_individuos) >= top_k:
                break
            top_individuos.append(CopiarIndividuo(poblacion[i]))
            top_aptitudes.append(float(aptitudes[i]))
            top_metricas.append(dict(metricas_list[i]))

    return mejor_global, historial, top_individuos, top_aptitudes, top_metricas
