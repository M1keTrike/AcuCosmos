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
    generaciones_max: int = 1    # G, para penalizacion dinamica w(g)=w0(1+alpha*g/G)
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
            hi = (float(cat.iloc[i][eje.col_max]) + eje.tol
                  if eje.col_max is not None else float("inf"))  # cota sup. abierta (OD)
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


def _es_si(v):
    return str(v).strip().lower() in ("si", "sí", "s", "1", "true", "yes")


@metrica("valor_indices")
def m_valor_indices(individuo, ctx, params):
    """Objetivo de valor por indices cualitativos (Cat. 6): suma de las columnas
    `params['cols']` por especie, media sobre activas (por defecto). Bono opcional
    si alguna activa tiene `params['bono_col']` en "si" (p.ej. fijacion de N).
    Plantas: rendimiento+polinizador+estetico (base de LER [12]); arboles:
    valor_biodiversidad [10][11]."""
    cat = ctx.catalogo
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0
    cols = params.get("cols", [])
    total = sum(float(cat.iloc[i][c]) for i in activas for c in cols)
    if params.get("media", True):
        total /= len(activas)
    bono_col = params.get("bono_col")
    if bono_col and any(_es_si(cat.iloc[i][bono_col]) for i in activas):
        total += float(params.get("bono", 0.0))
    return total


@metrica("valor_produccion")
def m_valor_produccion(individuo, ctx, params):
    """Produccion*valor de mercado (Cat. 6): Sum_i C_i * prod_i * factor * valor_i.
    Acuicola: prod=peso_cosecha_g (factor 0.001 -> kg) * valor_mercado_usd_kg [15]."""
    cat = ctx.catalogo
    col_prod = params["col_prod"]
    col_valor = params["col_valor"]
    factor = float(params.get("factor", 1.0))
    total = 0.0
    for i in EspeciesActivas(individuo):
        kg = float(cat.iloc[i][col_prod]) * int(individuo["C"][i]) * factor
        total += kg * float(cat.iloc[i][col_valor])
    return total


@metrica("co2_alometria_chave")
def m_co2_alometria_chave(individuo, ctx, params):
    """Secuestro de CO2 por alometria pantropical de Chave [14], en lugar del
    co2_kg_arbol_anio 100% estimado: AGB = 0.0673*(rho*D^2*H)^0.976 (kg).

    Densidad de madera `rho` DERIVADA (default por dominio; aprobado por el
    usuario) y DBH estimado del diametro de copa (factor_dbh) por falta de DBH en
    la base — aproximacion documentada (ver INFORME_REFACTOR). CO2 = AGB*0.47*44/12.
    """
    cat = ctx.catalogo
    col_diam = params.get("col_diam", "diam_copa_m")
    col_h = params.get("col_altura", "altura_madura_m_max")
    rho = float(params.get("densidad_madera", 0.6))
    f_dbh = float(params.get("factor_dbh_cm_por_m_copa", 10.0))
    total = 0.0
    for i in EspeciesActivas(individuo):
        H = float(cat.iloc[i][col_h])
        D = float(cat.iloc[i][col_diam]) * f_dbh                # DBH (cm) estimado
        agb = 0.0673 * (rho * D * D * H) ** 0.976              # kg biomasa aerea
        total += agb * 0.47 * (44.0 / 12.0) * int(individuo["C"][i])
    return total


# --------------------------------------------------------------------------- #
# Costo (restriccion de presupuesto; no entra en la suma de objetivos de peces)
# --------------------------------------------------------------------------- #
def costo_total(individuo, ctx):
    cat = ctx.catalogo
    activas = EspeciesActivas(individuo)
    costo = 0.0
    col_precio = ctx.col("precio_unidad")          # None si el dominio no tiene precio/unidad
    if col_precio is not None:
        costo += sum(float(cat.iloc[i][col_precio]) * int(individuo["C"][i])
                     for i in activas)
    col_sitio = ctx.col("costo_sitio")
    if col_sitio is not None:
        costo += float(ctx.sitio_actual(individuo)[col_sitio])
    return costo


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


def _normalizar(v, params):
    """Normalizacion declarada a [0,1] via params['norm']={'min','max'} (3.2).

    Sin 'norm' declarado devuelve v sin cambios. La usa la agregacion
    'suma_normalizada' para poner objetivos de escalas dispares en rango comun
    (corrige el sesgo donde el objetivo de numeros grandes domina).
    """
    norm = params.get("norm")
    if not norm:
        return v
    lo, hi = float(norm["min"]), float(norm["max"])
    if hi <= lo:
        return v
    return min(max((v - lo) / (hi - lo), 0.0), 1.0)


def _viola_restriccion(r, individuo, ctx, met, costo):
    """Booleano EXACTO (mismas comparaciones que la death-penalty de Fase 1)."""
    if r.tipo == "ambiental":
        ok, _ = ejes_factibles(individuo, ctx)
        return not ok
    if r.tipo == "presupuesto":
        pres = ctx.escenario.get("presupuesto")
        return pres is not None and costo > pres
    return _OPS[r.op](met.get(r.clave), r.umbral)


def _magnitud_violacion(r, individuo, ctx, met, costo):
    """Magnitud (>=0) de la violacion, para penalizacion graduada [1-4]."""
    if r.tipo == "ambiental":
        _ok, viol = ejes_factibles(individuo, ctx)
        return viol
    if r.tipo == "presupuesto":
        pres = ctx.escenario.get("presupuesto")
        if pres is None or pres <= 0:
            return 0.0
        return max(0.0, costo / pres - 1.0)
    val = met.get(r.clave)
    if r.op in (">=", ">"):
        return max(0.0, val - r.umbral)
    return max(0.0, r.umbral - val)


def _peso_penalizacion(r, esquema, ctx, modo):
    """Peso de la restriccion; en modo dinamico crece con la generacion:
    w(g) = w0 * (1 + alpha * g / G)  ([1], [2])."""
    pesos = esquema.penalizaciones.get("pesos", {})
    w0 = float(pesos.get(r.tipo, r.peso))
    if modo == "dinamica":
        alpha = float(esquema.penalizaciones.get("dinamica_alpha", 0.0))
        G = max(int(getattr(ctx, "generaciones_max", 1)), 1)
        return w0 * (1.0 + alpha * int(ctx.generacion) / G)
    return w0


def evaluar_aptitud(individuo, ctx):
    """Evaluador generico dirigido por el EsquemaDominio.

    Agregacion: `suma_simple` | `suma_normalizada` (3.2).
    Penalizacion:  `mortal` (death-penalty, reproduce Fase 1) | `graduada` |
    `dinamica` (3.1). Devuelve (F_total, metricas) con las claves de reporte del
    esquema mas costo / n_especies / factible.
    """
    esquema = ctx.esquema
    # Vector de objetivos (_obj) y violacion total (_viol) solo se necesitan para
    # agregaciones multiobjetivo (pareto/borda/nsga3); en modos de suma se omiten
    # para no anadir trabajo (peces queda identico).
    necesita_obj = esquema.agregacion not in ("suma_simple", "suma_normalizada")
    activas = EspeciesActivas(individuo)
    met = {}
    if not activas:
        for mc in esquema.metricas:
            met[mc.clave_reporte] = 0.0
        met["costo"] = 0
        met["factible"] = False
        met["n_especies"] = 0
        if necesita_obj:
            met["_obj"] = tuple(0.0 for _ in esquema.metricas)
            met["_viol"] = float("inf")
        return 0.0, met

    norm_on = esquema.agregacion == "suma_normalizada"
    F_obj = 0.0
    obj = []
    for mc in esquema.metricas:
        raw = REGISTRO_METRICAS[mc.nombre](individuo, ctx, mc.params)
        trans = _transform(raw, mc.params)
        val = _normalizar(trans, mc.params) if norm_on else trans
        F_obj += mc.signo * mc.peso * val
        met[mc.clave_reporte] = raw if mc.reporte == "raw" else mc.peso * trans
        if necesita_obj:
            obj.append(mc.signo * trans)   # orientado a maximizar

    costo = costo_total(individuo, ctx)
    met["costo"] = costo
    met["n_especies"] = len(activas)

    violado = any(_viola_restriccion(r, individuo, ctx, met, costo)
                  for r in esquema.restricciones)
    met["factible"] = not violado
    if necesita_obj:
        met["_obj"] = tuple(obj)
        met["_viol"] = sum(_magnitud_violacion(r, individuo, ctx, met, costo)
                           for r in esquema.restricciones)

    modo = esquema.penalizaciones.get("modo", "mortal")
    if modo == "mortal":
        if violado:
            return 0.0, met
        return float(F_obj), met

    # graduada / dinamica: F = objetivos - penalizacion proporcional a la violacion.
    # Conserva las penalizaciones blandas (N_c, M_s_hat) que ya van en F_obj.
    pen = 0.0
    for r in esquema.restricciones:
        mag = _magnitud_violacion(r, individuo, ctx, met, costo)
        if mag > 0:
            pen += _peso_penalizacion(r, esquema, ctx, modo) * mag
    return float(F_obj - pen), met
