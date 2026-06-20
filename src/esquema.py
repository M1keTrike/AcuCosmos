"""EsquemaDominio: configuracion declarativa por dominio (patron Strategy [9]).

El motor recibe un `EsquemaDominio` ya cargado y validado; NO lee YAML ni nombres
de columna directamente. Cada dominio = datos (CSV) + un YAML declarativo. La
filosofia (motor reutilizable + evaluacion registrada por nombre) sigue a DEAP [8].

Carga: `cargar_esquema(ruta_yaml, registro_metricas)` valida el YAML contra el
esquema esperado (campos obligatorios, que cada metrica nombrada exista en el
registro, que las columnas referenciadas existan en el CSV) y falla con mensaje
claro. `cargar_tablas(esquema)` carga catalogo/sitios/matriz alineada al catalogo.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

import yaml
import numpy as np
import pandas as pd

# Raiz del repo (este modulo vive en src/).
RAIZ_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Roles de rasgo que se leen de la tabla de SITIOS (no del catalogo de especies).
ROLES_SITIO = {"capacidad_sitio", "capacidad_espacio", "costo_sitio"}

AGREGACIONES_VALIDAS = {"suma_simple", "suma_normalizada", "pareto_nsga2",
                        "nsga3", "borda"}
MODOS_PENAL = {"mortal", "graduada", "dinamica"}
KERNELS_VALIDOS = {"legacy_peces", "exp_neg", "tabla"}
CAMPOS_OBLIGATORIOS = ("dominio", "rutas", "id_col", "metricas", "agregacion")


def _abs(ruta: str) -> str:
    return ruta if os.path.isabs(ruta) else os.path.join(RAIZ_REPO, ruta)


@dataclass(frozen=True)
class EjeAmbiental:
    col_min: str          # columna del catalogo (limite inferior tolerado)
    col_max: str          # columna del catalogo (limite superior tolerado)
    ref: str              # CLAVE del escenario que da el valor de referencia
    tol: float            # factible si ref in [min - tol, max + tol]


@dataclass(frozen=True)
class MetricaCfg:
    nombre: str           # debe existir en REGISTRO_METRICAS
    peso: float
    signo: int            # +1 maximizar, -1 minimizar
    clave_reporte: str    # clave bajo la cual se reporta en el dict de metricas
    reporte: str = "raw"  # "raw" (valor crudo) | "agregado" (peso*transform)
    params: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RestriccionCfg:
    tipo: str                       # capacidad | espacio | ambiental | presupuesto
    clave: Optional[str] = None     # clave de metrica a comparar (capacidad/espacio)
    op: Optional[str] = None        # ">=" | ">" | "<" | "<="
    umbral: Optional[float] = None
    peso: float = 1.0               # peso de la penalizacion graduada (Fase 2)


@dataclass(frozen=True)
class EsquemaDominio:
    dominio: str
    rutas: dict
    id_col: str
    rasgos: dict
    estratos: dict
    ejes_ambientales: tuple
    metricas: tuple
    restricciones: tuple
    penalizaciones: dict
    agregacion: str
    params: dict
    pesos_defecto: dict = field(default_factory=dict)

    def col(self, rol: str) -> Optional[str]:
        """Columna asignada a un rol del motor, o None si el rasgo esta ausente."""
        return self.rasgos.get(rol)


def _err(msg: str):
    raise ValueError(f"[cargar_esquema] {msg}")


def _construir(cfg: dict) -> EsquemaDominio:
    ejes = tuple(
        EjeAmbiental(col_min=e["min"] if "min" in e else e["col_min"],
                     col_max=e["max"] if "max" in e else e["col_max"],
                     ref=e["ref"], tol=float(e.get("tol", 0.0)))
        for e in cfg.get("ejes_ambientales", []))
    metricas = tuple(
        MetricaCfg(nombre=m["nombre"], peso=float(m.get("peso", 1.0)),
                   signo=int(m.get("signo", 1)),
                   clave_reporte=m.get("clave_reporte", m["nombre"]),
                   reporte=m.get("reporte", "raw"),
                   params=dict(m.get("params", {})))
        for m in cfg["metricas"])
    restr = tuple(
        RestriccionCfg(tipo=r["tipo"], clave=r.get("clave"), op=r.get("op"),
                       umbral=(None if r.get("umbral") is None
                               else float(r["umbral"])),
                       peso=float(r.get("peso", 1.0)))
        for r in cfg.get("restricciones", []))
    return EsquemaDominio(
        dominio=cfg["dominio"], rutas=dict(cfg["rutas"]), id_col=cfg["id_col"],
        rasgos=dict(cfg.get("rasgos", {})), estratos=dict(cfg.get("estratos", {})),
        ejes_ambientales=ejes, metricas=metricas, restricciones=restr,
        penalizaciones=dict(cfg.get("penalizaciones", {"modo": "mortal"})),
        agregacion=cfg["agregacion"], params=dict(cfg.get("params", {})),
        pesos_defecto=dict(cfg.get("pesos_defecto", {})))


def cargar_esquema(ruta_yaml: str, registro_metricas: Optional[dict] = None,
                   validar_columnas: bool = True) -> EsquemaDominio:
    ruta_yaml = _abs(ruta_yaml)
    if not os.path.exists(ruta_yaml):
        _err(f"no existe el YAML: {ruta_yaml}")
    with open(ruta_yaml, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)          # safe_load (nunca yaml.load)
    if not isinstance(cfg, dict):
        _err("el YAML no es un mapeo de nivel superior")
    for c in CAMPOS_OBLIGATORIOS:
        if c not in cfg:
            _err(f"falta el campo obligatorio '{c}'")

    esquema = _construir(cfg)

    # Validaciones semanticas.
    if esquema.agregacion not in AGREGACIONES_VALIDAS:
        _err(f"agregacion invalida: {esquema.agregacion!r} "
             f"(validas: {sorted(AGREGACIONES_VALIDAS)})")
    modo = esquema.penalizaciones.get("modo", "mortal")
    if modo not in MODOS_PENAL:
        _err(f"penalizaciones.modo invalido: {modo!r}")
    if esquema.estratos:
        k = esquema.estratos.get("kernel")
        if k not in KERNELS_VALIDOS:
            _err(f"estratos.kernel invalido: {k!r} "
                 f"(validos: {sorted(KERNELS_VALIDOS)})")
        if "orden" not in esquema.estratos:
            _err("estratos requiere 'orden' (lista de niveles)")
    for m in esquema.metricas:
        if m.signo not in (1, -1):
            _err(f"metrica {m.nombre}: signo debe ser +1 o -1 (es {m.signo})")
        if registro_metricas is not None and m.nombre not in registro_metricas:
            _err(f"metrica '{m.nombre}' no existe en el registro "
                 f"(registradas: {sorted(registro_metricas)})")
    for r in esquema.restricciones:
        if r.tipo in ("capacidad", "espacio"):
            if r.clave is None or r.op is None or r.umbral is None:
                _err(f"restriccion '{r.tipo}' requiere clave, op y umbral")

    if validar_columnas:
        _validar_columnas(esquema)
    return esquema


def _validar_columnas(esquema: EsquemaDominio):
    ruta_cat = _abs(esquema.rutas.get("catalogo", ""))
    if not os.path.exists(ruta_cat):
        _err(f"no existe el catalogo: {ruta_cat}")
    cols_cat = list(pd.read_csv(ruta_cat, encoding="utf-8-sig", nrows=0).columns)
    if esquema.id_col not in cols_cat:
        _err(f"id_col '{esquema.id_col}' no esta en el catalogo")

    cols_sit = []
    ruta_sit = esquema.rutas.get("sitios")
    if ruta_sit and os.path.exists(_abs(ruta_sit)):
        cols_sit = list(pd.read_csv(_abs(ruta_sit), encoding="utf-8-sig",
                                    nrows=0).columns)

    for rol, col in esquema.rasgos.items():
        if col is None:
            continue
        destino = cols_sit if rol in ROLES_SITIO else cols_cat
        nombre_tabla = "sitios" if rol in ROLES_SITIO else "catalogo"
        if col not in destino:
            _err(f"rasgo '{rol}' -> columna '{col}' no existe en {nombre_tabla}")

    if esquema.estratos:
        ce = esquema.estratos.get("col")
        if ce and ce not in cols_cat:
            _err(f"estratos.col '{ce}' no existe en el catalogo")
    for eje in esquema.ejes_ambientales:
        for c in (eje.col_min, eje.col_max):
            if c not in cols_cat:
                _err(f"eje ambiental -> columna '{c}' no existe en el catalogo")


def cargar_tablas(esquema: EsquemaDominio):
    """Carga (catalogo, sitios, matriz_kappa) segun las rutas del esquema.

    En Fase 1 solo el formato 'densa' (peces). El disperso->denso con heuristicas
    H1..Hn (Fase 2.2) se conecta en Fase 4.
    """
    catalogo = pd.read_csv(_abs(esquema.rutas["catalogo"]), encoding="utf-8-sig")
    sitios = pd.read_csv(_abs(esquema.rutas["sitios"]), encoding="utf-8-sig")
    formato = esquema.params.get("interacciones_formato", "densa")
    ruta_int = _abs(esquema.rutas["interacciones"])
    if formato == "densa":
        kappa = pd.read_csv(ruta_int, encoding="utf-8-sig",
                            index_col=0).to_numpy(dtype=float)
    else:
        raise NotImplementedError(
            "cargador disperso->denso (Fase 4); usa interacciones_formato: densa")
    n = len(catalogo)
    if kappa.shape != (n, n):
        _err(f"matriz {kappa.shape} no alineada con catalogo ({n} especies)")
    return catalogo, sitios, kappa
