"""Estrategias de agregacion/seleccion multiobjetivo (2.4).

Convierten la lista de metricas de la poblacion en una **aptitud de seleccion**
escalar por individuo, que el motor (mu+lambda con torneo) usa tal cual:

- ``suma_simple`` / ``suma_normalizada``: usa el escalar F (suma ponderada de
  metricas.py). No necesita la poblacion -> reproduce el comportamiento previo.
- ``pareto_nsga2``: ordenamiento no-dominado + crowding con **dominancia con
  restricciones de Deb [3]**; el score escalar (frente, crowding) reproduce la
  presion selectiva de NSGA-II sin reescribir el bucle. **NSGA-III [5]** queda
  preparado via ``puntos_referencia_das_dennis`` para >3 objetivos.
- ``borda``: cada objetivo ordena la poblacion y vota por rango; score = suma de
  votos [7]. Elimina el problema de escalas.

Cada metrica de la poblacion debe traer ``_obj`` (vector de objetivos orientado a
MAXIMIZAR), ``_viol`` (violacion total >=0) y ``factible`` (los pone evaluar_aptitud
cuando la agregacion no es de suma).
"""
import itertools

import numpy as np


def _obj(met):
    return met.get("_obj", ())


def _viol(met):
    return float(met.get("_viol", 0.0))


def _factible(met):
    return bool(met.get("factible", True))


def domina(a, b):
    """Dominancia CON restricciones de Deb [3]: ¿`a` domina a `b`?

    Objetivos orientados a maximizar. Reglas:
      - factible ≻ infactible;
      - entre infactibles, gana el de menor violacion;
      - entre factibles, dominancia de Pareto estandar.
    """
    fa, fb = _factible(a), _factible(b)
    if fa != fb:
        return fa                      # el factible domina al infactible
    if not fa and not fb:
        return _viol(a) < _viol(b)     # menor violacion domina
    oa, ob = _obj(a), _obj(b)
    mejor_en_alguno = False
    for x, y in zip(oa, ob):
        if x < y:
            return False
        if x > y:
            mejor_en_alguno = True
    return mejor_en_alguno


def clasificacion_no_dominada(metricas_list):
    """Fast non-dominated sort (NSGA-II): lista de frentes (listas de indices)."""
    n = len(metricas_list)
    dominados = [[] for _ in range(n)]   # soluciones que i domina
    n_dom = [0] * n                       # cuantas dominan a i
    frentes = [[]]
    for p in range(n):
        for q in range(n):
            if p == q:
                continue
            if domina(metricas_list[p], metricas_list[q]):
                dominados[p].append(q)
            elif domina(metricas_list[q], metricas_list[p]):
                n_dom[p] += 1
        if n_dom[p] == 0:
            frentes[0].append(p)
    i = 0
    while frentes[i]:
        siguiente = []
        for p in frentes[i]:
            for q in dominados[p]:
                n_dom[q] -= 1
                if n_dom[q] == 0:
                    siguiente.append(q)
        i += 1
        frentes.append(siguiente)
    frentes.pop()                         # ultimo frente vacio
    return frentes


def crowding_distance(indices, metricas_list):
    """Distancia de hacinamiento NSGA-II para los indices de un frente."""
    dist = {i: 0.0 for i in indices}
    m = len(indices)
    if m == 0:
        return dist
    n_obj = len(_obj(metricas_list[indices[0]]))
    for k in range(n_obj):
        orden = sorted(indices, key=lambda i: _obj(metricas_list[i])[k])
        dist[orden[0]] = float("inf")
        dist[orden[-1]] = float("inf")
        f_min = _obj(metricas_list[orden[0]])[k]
        f_max = _obj(metricas_list[orden[-1]])[k]
        rango = f_max - f_min
        if rango <= 0:
            continue
        for idx in range(1, m - 1):
            prev = _obj(metricas_list[orden[idx - 1]])[k]
            nxt = _obj(metricas_list[orden[idx + 1]])[k]
            dist[orden[idx]] += (nxt - prev) / rango
    return dist


def puntajes_nsga2(metricas_list):
    """Score escalar por individuo: mejor frente y mayor crowding => mayor score.

    score = (n_frentes - rango_frente) * BASE + crowding_normalizado, de modo que
    el motor (torneo / truncamiento por mayor aptitud) imite a NSGA-II.
    """
    n = len(metricas_list)
    if n == 0:
        return []
    frentes = clasificacion_no_dominada(metricas_list)
    nf = len(frentes)
    base = 1.0e6
    score = [0.0] * n
    for r, frente in enumerate(frentes):
        dist = crowding_distance(frente, metricas_list)
        finitos = [d for d in dist.values() if d != float("inf")]
        dmax = max(finitos) if finitos else 0.0
        for i in frente:
            d = dist[i]
            if d == float("inf"):
                cd = 1.0
            else:
                cd = (d / dmax) * 0.999 if dmax > 0 else 0.0
            score[i] = (nf - r) * base + cd
    return score


def puntajes_borda(metricas_list):
    """Borda [7]: cada objetivo ordena la poblacion; score = suma de posiciones
    (peor=0 ... mejor=n-1). Mayor score = mejor. Si hay infactibles, agrega un
    objetivo extra de menor-violacion-mejor."""
    n = len(metricas_list)
    if n == 0:
        return []
    n_obj = len(_obj(metricas_list[0])) if _obj(metricas_list[0]) else 0
    score = [0.0] * n
    for k in range(n_obj):
        orden = sorted(range(n), key=lambda i: _obj(metricas_list[i])[k])
        for pos, i in enumerate(orden):
            score[i] += pos
    if any(not _factible(m) for m in metricas_list):
        orden = sorted(range(n), key=lambda i: -_viol(metricas_list[i]))
        for pos, i in enumerate(orden):
            score[i] += pos
    return score


def puntos_referencia_das_dennis(n_obj, divisiones):
    """Puntos de referencia de Das-Dennis para NSGA-III [5] (esqueleto).

    Combinaciones en el simplex (componentes >=0 que suman 1) con `divisiones`
    pasos: C(n_obj+divisiones-1, divisiones) puntos. Listos para cuando se active
    el modo con >3 objetivos; la asociacion individuo->punto de referencia se
    conectara al activar nsga3.
    """
    puntos = []
    for comb in itertools.combinations_with_replacement(range(n_obj), divisiones):
        vec = [0] * n_obj
        for c in comb:
            vec[c] += 1
        puntos.append(tuple(v / divisiones for v in vec))
    return puntos


def puntuar_seleccion(aptitudes_suma, metricas_list, agregacion):
    """Devuelve el array de aptitud de SELECCION segun la agregacion del esquema."""
    if agregacion in ("suma_simple", "suma_normalizada"):
        return list(aptitudes_suma)
    if agregacion == "pareto_nsga2":
        return puntajes_nsga2(metricas_list)
    if agregacion == "borda":
        return puntajes_borda(metricas_list)
    if agregacion == "nsga3":
        # Esqueleto: hasta conectar la asociacion por puntos de referencia,
        # usa la presion de NSGA-II (frentes + crowding).
        return puntajes_nsga2(metricas_list)
    return list(aptitudes_suma)
