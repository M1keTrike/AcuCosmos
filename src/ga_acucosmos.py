import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from src.metricas import evaluar_aptitud, ContextoEvaluacion
from src.agregacion import puntuar_seleccion
from src.operadores import (
    FuncionInicializacion, SeleccionTorneo, CruzaUniforme,
    FuncionMutacion, CopiarIndividuo
)


def EjecutarAG(ctx: ContextoEvaluacion,
               tanques_permitidos: Optional[List[int]] = None,
               tam_poblacion: int = 80,
               generaciones_max: int = 150,
               estancamiento_max: int = 30,
               t_torneo: int = 3,
               min_especies: int = 3,
               max_especies: int = 15,
               top_k: int = 3,
               verbose: bool = True,
               seed: Optional[int] = None
               ) -> Tuple[Dict, List[Dict], List[Dict], List[float], List[Dict]]:
    if seed is not None:
        np.random.seed(seed)
    catalogo = ctx.catalogo
    tanques = ctx.sitios
    esquema = ctx.esquema
    ctx.generaciones_max = generaciones_max

    def _hist_reg(gen, mejor, peor, prom, m):
        # registro generico: metricas por su clave_reporte (peces conserva A_e..M_s)
        reg = {'generacion': gen, 'apt_mejor': float(mejor),
               'apt_peor': float(peor), 'apt_promedio': float(prom),
               'costo': m.get('costo', 0), 'factible': m.get('factible', False)}
        for mc in esquema.metricas:
            reg[mc.clave_reporte] = m.get(mc.clave_reporte)
        return reg

    def _linea_verbose(gen, apt_mejor, apt_prom, m):
        def _f(v):
            return f"{v:.3f}" if isinstance(v, (int, float)) else str(v)
        partes = " ".join(f"{mc.clave_reporte}={_f(m.get(mc.clave_reporte))}"
                          for mc in esquema.metricas)
        fac = "OK" if m.get('factible') else "INF"
        return (f"  Gen {gen:3d} | mejor={apt_mejor:.4f} prom={apt_prom:.4f} | "
                f"{partes} ${m.get('costo')} [{fac}]")

    poblacion = FuncionInicializacion(
        tam_poblacion, catalogo, tanques, esquema,
        min_especies=min_especies, max_especies=max_especies,
        tanques_permitidos=tanques_permitidos
    )
    aptitudes = []
    metricas_list = []
    for ind in poblacion:
        f, m = evaluar_aptitud(ind, ctx)
        aptitudes.append(f)
        metricas_list.append(m)
    # aptitud de SELECCION (suma_* -> = aptitudes; pareto/borda -> rangos)
    scores = puntuar_seleccion(aptitudes, metricas_list, esquema.agregacion)

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
    historial.append(_hist_reg(0, max(aptitudes), min(aptitudes),
                               float(np.mean(aptitudes)), m_init))
    if verbose:
        print(_linea_verbose(0, historial[0]['apt_mejor'],
                             historial[0]['apt_promedio'], m_init))

    sin_factibles = 0
    REINICIO_TRAS = 15
    FRAC_REINICIO = 0.5

    for g in range(generaciones_max):
        ctx.generacion = g + 1
        hijos: List[Dict] = []
        while len(hijos) < tam_poblacion:
            padre_a = SeleccionTorneo(poblacion, scores, t=t_torneo)
            padre_b = SeleccionTorneo(poblacion, scores, t=t_torneo)
            h1, h2 = CruzaUniforme(padre_a, padre_b, catalogo, tanques, esquema,
                                   tanques_permitidos=tanques_permitidos)
            h1 = FuncionMutacion(h1, catalogo, tanques, esquema,
                                 tanques_permitidos=tanques_permitidos)
            h2 = FuncionMutacion(h2, catalogo, tanques, esquema,
                                 tanques_permitidos=tanques_permitidos)
            hijos.append(h1)
            if len(hijos) < tam_poblacion:
                hijos.append(h2)

        apt_hijos = []
        met_hijos = []
        for ind in hijos:
            f, m = evaluar_aptitud(ind, ctx)
            apt_hijos.append(f)
            met_hijos.append(m)

        combinados = poblacion + hijos
        combinadas_apt = list(aptitudes) + apt_hijos
        combinadas_met = list(metricas_list) + met_hijos
        combinadas_scores = puntuar_seleccion(combinadas_apt, combinadas_met,
                                              esquema.agregacion)

        apt_mejor = float(max(combinadas_apt))
        apt_peor = float(min(combinadas_apt))
        apt_prom = float(np.mean(combinadas_apt))
        mejor_idx_pre = int(np.argmax(combinadas_apt))
        m_mejor = combinadas_met[mejor_idx_pre]

        historial.append(_hist_reg(g + 1, apt_mejor, apt_peor, apt_prom, m_mejor))

        orden = sorted(range(len(combinados)),
                       key=lambda k: combinadas_scores[k], reverse=True)
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
                    n_rein, catalogo, tanques, esquema,
                    min_especies=min_especies, max_especies=max_especies,
                    tanques_permitidos=tanques_permitidos
                )
                nuevas_apt = []
                nuevas_met = []
                for ind in nuevos:
                    f, m = evaluar_aptitud(ind, ctx)
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

        # recomputa la aptitud de seleccion sobre la poblacion superviviente
        scores = puntuar_seleccion(aptitudes, metricas_list, esquema.agregacion)

        if apt_mejor > mejor_global_apt + 1e-9:
            mejor_global_apt = apt_mejor
            mejor_global = CopiarIndividuo(combinados[mejor_idx_pre])
            mejor_global_metricas = m_mejor
            estancamiento = 0
        else:
            estancamiento += 1

        if verbose and ((g + 1) % 10 == 0 or g == 0):
            print(_linea_verbose(g + 1, apt_mejor, apt_prom, m_mejor))

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
