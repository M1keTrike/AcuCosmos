"""Registro de metricas + contexto de evaluacion + evaluador generico.

Cada metrica:  ``metrica(individuo, ctx, params) -> float``  (valor CRUDO del
dominio). El agregador aplica transform (saturacion/cap, via `params`) + peso +
signo. Con el `EsquemaDominio` de peces, `evaluar_aptitud` reproduce exactamente
la formula original:  F = A_e + I_b + R_v_hat - N_c - M_s_hat + B_div.

Patron Registry [9]: el YAML invoca las metricas por nombre; aqui viven los
callables. Penalizaciones [1-4]; agregacion [3,5,6,7]; base ecologica [10,11].
"""
from __future__ import annotations

import operator as _operator
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from src.cromosoma import EspeciesActivas, FrecuenciasRelativas

REGISTRO_METRICAS = {}
REGISTRO_KERNELS = {}

_OPS = {">=": _operator.ge, ">": _operator.gt, "<": _operator.lt,
        "<=": _operator.le}


def metrica(nombre):
    """Decorador: registra una metrica bajo `nombre` en REGISTRO_METRICAS."""
    def _reg(fn):
        REGISTRO_METRICAS[nombre] = fn
        return fn
    return _reg


def kernel(nombre):
    """Decorador: registra un kernel de solape de estratos."""
    def _reg(fn):
        REGISTRO_KERNELS[nombre] = fn
        return fn
    return _reg


@dataclass
class ContextoEvaluacion:
    """Todo lo que una metrica necesita, plegado en un objeto (decision aprobada)."""
    esquema: "object"            # EsquemaDominio (sin import para evitar ciclos)
    catalogo: pd.DataFrame
    sitios: pd.DataFrame
    matriz_kappa: np.ndarray
    escenario: dict              # refs ambientales + presupuesto + max_especies
    generacion: int = 0
    _pos_estr: Optional[dict] = field(default=None, repr=False)

    def col(self, rol):
        return self.esquema.rasgos.get(rol)

    def sitio_actual(self, individuo):
        return self.sitios.iloc[int(individuo["tanque"])]

    def pos_estratos(self):
        if self._pos_estr is None:
            orden = self.esquema.estratos.get("orden", [])
            self._pos_estr = {v: i for i, v in enumerate(orden)}
        return self._pos_estr


# --------------------------------------------------------------------------- #
# Kernels de solape de estratos (2.3)
# --------------------------------------------------------------------------- #
@kernel("legacy_peces")
def _kernel_legacy(diff):
    """3 estratos: 1.0 si mismo; exp(-1) si vecino; None (sin solape) si diff>=2."""
    if diff == 0:
        return 1.0
    if diff == 1:
        return float(np.exp(-1.0))
    return None


@kernel("exp_neg")
def _kernel_exp(diff):
    """N estratos, decaimiento continuo O(diff) = exp(-diff) (sin corte)."""
    return float(np.exp(-float(diff)))


# --------------------------------------------------------------------------- #
# Factibilidad por ejes ambientales (generaliza EsCompatiblePH a N ejes)
# --------------------------------------------------------------------------- #
def ejes_factibles(individuo, ctx):
    """Devuelve (factible, violacion_total). Factible si el ref del escenario cae
    en [min - tol, max + tol] para TODA especie activa en TODOS los ejes."""
    cat = ctx.catalogo
    activas = EspeciesActivas(individuo)
    ok = True
    viol = 0.0
    for eje in ctx.esquema.ejes_ambientales:
        if eje.ref not in ctx.escenario or ctx.escenario[eje.ref] is None:
            raise ValueError(
                f"el escenario no define la referencia '{eje.ref}' "
                f"requerida por un eje ambiental")
        ref = float(ctx.escenario[eje.ref])
        for i in activas:
            lo = float(cat.iloc[i][eje.col_min]) - eje.tol
            hi = float(cat.iloc[i][eje.col_max]) + eje.tol
            if ref < lo:
                ok = False
                viol += (lo - ref)
            elif ref > hi:
                ok = False
                viol += (ref - hi)
    return ok, viol


# --------------------------------------------------------------------------- #
# Metricas registradas
# --------------------------------------------------------------------------- #
@metrica("estetica_rareza_cromatica")
def m_estetica(individuo, ctx, params):
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0
    cat = ctx.catalogo
    p = FrecuenciasRelativas(individuo)
    col_rar = ctx.col("rareza")
    col_grupo = ctx.col("grupo_cromatico")
    n_grupos = float(params.get("n_grupos_cromaticos", 1))
    rarezas = np.array([cat.iloc[i][col_rar] for i in activas])
    termino_rareza = float(np.sum(rarezas * p))
    grupos = set(int(cat.iloc[i][col_grupo]) for i in activas)
    termino_cromatico = len(grupos) / n_grupos
    return 0.5 * (termino_rareza + termino_cromatico)


@metrica("biodiversidad_shannon")
def m_biodiversidad(individuo, ctx, params):
    p = FrecuenciasRelativas(individuo)
    n = len(p)
    if n <= 1:
        return 0.0
    p_pos = p[p > 0]
    shannon = -float(np.sum(p_pos * np.log(p_pos)))
    return shannon / np.log(n)


@metrica("comodidad_espacio")
def m_comodidad(individuo, ctx, params):
    cat = ctx.catalogo
    col_vol = ctx.col("espacio_unidad")
    activas = EspeciesActivas(individuo)
    v_req = float(sum(cat.iloc[i][col_vol] * individuo["C"][i] for i in activas))
    if v_req <= 0:
        return 0.0
    sitio = ctx.sitio_actual(individuo)
    return float(sitio[ctx.col("capacidad_espacio")]) / v_req


@metrica("conflicto_pares")
def m_conflicto_pares(individuo, ctx, params):
    activas = EspeciesActivas(individuo)
    n = len(activas)
    if n <= 1:
        return 0.0
    cat = ctx.catalogo
    col_agr = ctx.col("agresividad")
    col_estr = ctx.esquema.estratos["col"]
    pos = ctx.pos_estratos()
    kern = REGISTRO_KERNELS[ctx.esquema.estratos["kernel"]]
    agr = [float(cat.iloc[i][col_agr]) for i in activas]
    est = [pos[cat.iloc[i][col_estr]] for i in activas]
    total = 0.0
    for a in range(n):
        for b in range(a + 1, n):
            i, j = activas[a], activas[b]
            penal = max(0.0, -float(ctx.matriz_kappa[i, j]))
            if penal == 0.0:
                continue
            diff = abs(int(est[a]) - int(est[b]))
            O = kern(diff)
            if O is None:
                continue
            agr_prom = (agr[a] + agr[b]) / 2.0
            total += agr_prom * penal * O
    return (2.0 / (n * (n - 1))) * total


@metrica("equilibrio_pares")
def m_equilibrio_pares(individuo, ctx, params):
    """Sinergia neta del ensamblaje: suma de kappa CON signo sobre pares activos
    (positivos suben, negativos bajan). Para dominios productivos. Promedia por
    par si params['promediar'] (por defecto suma). [10]"""
    activas = EspeciesActivas(individuo)
    n = len(activas)
    if n <= 1:
        return 0.0
    total = 0.0
    for a in range(n):
        for b in range(a + 1, n):
            total += float(ctx.matriz_kappa[activas[a], activas[b]])
    if params.get("promediar", False):
        return (2.0 / (n * (n - 1))) * total
    return total


@metrica("sobrecarga_capacidad")
def m_sobrecarga(individuo, ctx, params):
    cat = ctx.catalogo
    col_carga = ctx.col("carga_individuo")
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0
    carga = float(sum(float(cat.iloc[i][col_carga]) * int(individuo["C"][i])
                      for i in activas))
    cap = float(ctx.sitio_actual(individuo)[ctx.col("capacidad_sitio")])
    if cap <= 0:
        return float("inf")
    return carga / cap


@metrica("bonus_diversidad")
def m_bonus_diversidad(individuo, ctx, params):
    """Numero relativo de especies; el cap a 1 y el peso (0.5) los aplica el
    agregador (transform cap + peso). max_especies viene del escenario."""
    n = len(EspeciesActivas(individuo))
    max_esp = float(ctx.escenario.get("max_especies",
                                      params.get("max_especies", 1)))
    return n / max_esp


# --------------------------------------------------------------------------- #
# Costo (restriccion de presupuesto; no entra en la suma de objetivos de peces)
# --------------------------------------------------------------------------- #
def costo_total(individuo, ctx):
    cat = ctx.catalogo
    col_precio = ctx.col("precio_unidad")
    activas = EspeciesActivas(individuo)
    costo_esp = sum(int(cat.iloc[i][col_precio]) * int(individuo["C"][i])
                    for i in activas)
    costo_sitio = int(ctx.sitio_actual(individuo)[ctx.col("costo_sitio")])
    return costo_esp + costo_sitio


# --------------------------------------------------------------------------- #
# Agregador + evaluador
# --------------------------------------------------------------------------- #
def _transform(v, params):
    """Saturacion declarada: min(v / saturacion, cap). Sin params => identidad."""
    sat = float(params.get("saturacion", 1.0))
    t = v / sat
    cap = params.get("cap", None)
    if cap is not None:
        t = min(t, float(cap))
    return t


def _viola_restriccion(r, individuo, ctx, met, costo):
    if r.tipo == "ambiental":
        ok, _ = ejes_factibles(individuo, ctx)
        return not ok
    if r.tipo == "presupuesto":
        pres = ctx.escenario.get("presupuesto")
        return pres is not None and costo > pres
    # capacidad / espacio: comparan una clave de metricas con un umbral
    return _OPS[r.op](met.get(r.clave), r.umbral)


def evaluar_aptitud(individuo, ctx):
    """Evaluador generico dirigido por el EsquemaDominio.

    Fase 1: agregacion `suma_simple` + penalizacion `mortal` (reproduce la
    death-penalty). Devuelve (F_total, metricas) con las claves de reporte del
    esquema mas costo / n_especies / factible.
    """
    esquema = ctx.esquema
    activas = EspeciesActivas(individuo)
    met = {}
    if not activas:
        for mc in esquema.metricas:
            met[mc.clave_reporte] = 0.0
        met["costo"] = 0
        met["factible"] = False
        met["n_especies"] = 0
        return 0.0, met

    F = 0.0
    for mc in esquema.metricas:
        raw = REGISTRO_METRICAS[mc.nombre](individuo, ctx, mc.params)
        trans = _transform(raw, mc.params)
        F += mc.signo * mc.peso * trans
        met[mc.clave_reporte] = raw if mc.reporte == "raw" else mc.peso * trans

    costo = costo_total(individuo, ctx)
    met["costo"] = costo
    met["n_especies"] = len(activas)
    met["factible"] = True

    modo = esquema.penalizaciones.get("modo", "mortal")
    violado = any(_viola_restriccion(r, individuo, ctx, met, costo)
                  for r in esquema.restricciones)
    if modo == "mortal":
        if violado:
            met["factible"] = False
            return 0.0, met
        return float(F), met

    # Modos graduada/dinamica: Fase 2 (se implementaran sobre este mismo punto).
    if violado:
        met["factible"] = False
    return float(F), met
