"""Cargador disperso->denso (2.2) + heuristicas H1..Hn de derivacion de pares.

Las bases de Cowork dan una **lista dispersa** de pares investigados
(`especie_a, especie_b, valor` con valor en [-2,+2]) mas reglas de derivacion en
`*_reglas.md`. `cargar_interacciones_disperso`:
  1. matriz n×n a 0 (neutro), indexada por el ORDEN del catalogo (id slug -> i);
  2. rellena los pares investigados;
  3. aplica las heuristicas del dominio para los pares faltantes (marca derivado);
  4. reescala [-2,+2]->[-1,1] (÷2), simetrica y alineada al catalogo.

Se implementa un SUBCONJUNTO representativo de las reglas de cada `*_reglas.md`
(las basadas en rasgos de especie); las reglas que dependen del sitio o de fase
sucesional se documentan como pendientes (ver INFORME_REFACTOR).
"""
import numpy as np
import pandas as pd

REGLAS_DERIVACION = {}      # dominio -> funcion(catalogo) -> {(i,j): valor[-2,2]}


def regla(dominio):
    def _reg(fn):
        REGLAS_DERIVACION[dominio] = fn
        return fn
    return _reg


def _n(v):
    return str(v).strip().lower()


def _si(v):
    return _n(v) in ("si", "sí", "s", "1", "true", "yes")


def cargar_interacciones_disperso(esquema, catalogo):
    from src.esquema import _abs
    ids = [str(x) for x in catalogo[esquema.id_col].tolist()]
    idx = {s: i for i, s in enumerate(ids)}
    n = len(ids)
    kappa = np.zeros((n, n), dtype=float)

    df = pd.read_csv(_abs(esquema.rutas["interacciones"]), encoding="utf-8-sig")
    investigados = set()
    for _, r in df.iterrows():
        a, b = str(r["especie_a"]), str(r["especie_b"])
        if a in idx and b in idx and a != b:
            i, j = idx[a], idx[b]
            v = float(r["valor"])
            kappa[i, j] = kappa[j, i] = v
            investigados.add((min(i, j), max(i, j)))

    fn = REGLAS_DERIVACION.get(esquema.dominio)
    if fn:
        for (i, j), v in fn(catalogo).items():
            key = (min(i, j), max(i, j))
            if i == j or key in investigados or v == 0:
                continue
            kappa[i, j] = kappa[j, i] = float(v)

    if list(esquema.params.get("escala_origen", [-2, 2])) == [-2, 2]:
        kappa = kappa / 2.0
    np.fill_diagonal(kappa, 0.0)
    return kappa


# --------------------------------------------------------------------------- #
# PLANTAS (companion planting): H2 fijacion-N, H3 repelencia, H4 estrato/luz
# --------------------------------------------------------------------------- #
@regla("plantas_jardin")
def _plantas(cat):
    der = {}
    tipo = [_n(x) for x in cat["tipo"]]
    luz = [_n(x) for x in cat["luz"]]
    estr = [_n(x) for x in cat["estrato"]]
    fija = [_si(x) for x in cat["fija_nitrogeno"]]
    dem = [_n(x) for x in cat["demanda_nutrientes"]]
    com = [_si(x) for x in cat["comestible"]]
    n = len(tipo)

    def h2(a, b):   # leguminosa fijadora + cultivo exigente comestible
        if fija[a] and tipo[a] == "leguminosa" and com[b]:
            return 2 if dem[b] == "alta" else (1 if dem[b] == "media" else 0)
        return 0

    def h3(a, b):   # aromatica + hortaliza susceptible -> repele plagas
        if tipo[a] == "aromatica" and tipo[b] in ("hortaliza_fruto",
                                                  "hortaliza_hoja") and dem[b] != "baja":
            return 1
        return 0

    def h4(a, b):   # alta heliofila + baja/rastrera de sombra -> complementariedad
        if (estr[a] == "alto" and luz[a] == "pleno_sol"
                and estr[b] in ("bajo", "rastrero")
                and luz[b] in ("sol_parcial", "sombra")):
            return 1
        return 0

    for i in range(n):
        for j in range(i + 1, n):
            s = max(h2(i, j), h2(j, i), h3(i, j), h3(j, i), h4(i, j), h4(j, i))
            if s > 0:
                der[(i, j)] = s
            elif (estr[i] == "alto" and estr[j] == "alto"
                  and luz[i] == "pleno_sol" and luz[j] == "pleno_sol"):
                der[(i, j)] = -1            # dos altas heliofilas compiten por luz
    return der


# --------------------------------------------------------------------------- #
# ARBOLES: B1 fijacion-N, B3 estrato, B8 nodriza+fruto, B6 nodriza climax,
#          B4 alelopatia, B7 misma familia (plaga compartida)
# --------------------------------------------------------------------------- #
@regla("arboles_bosque")
def _arboles(cat):
    der = {}
    fam = [_n(x) for x in cat["familia"]]
    fija = [_si(x) for x in cat["fija_nitrogeno"]]
    suc = [_n(x) for x in cat["estado_sucesional"]]
    estr = [_n(x) for x in cat["estrato_dosel"]]
    somb = [int(x) for x in cat["tolerancia_sombra"]]
    uso = [_n(x) for x in cat["uso"]]
    tasa = [_n(x) for x in cat["tasa_crecimiento"]]
    ids = [_n(x) for x in cat["id"]]
    alelo = {"eucalyptus_grandis", "pinus_oocarpa", "juglans_neotropica"}
    n = len(fam)

    def b1(a, b):
        if fija[a] and suc[b] in ("pionera", "secundaria_temprana"):
            return 2 if ("madera" in uso[b] and tasa[b] == "rapida") else 1
        return 0

    def b3(a, b):
        if estr[a] == "sotobosque" and estr[b] == "emergente":
            return 2 if somb[a] >= 2 else 1
        return 0

    def b8(a, b):
        return 2 if (fija[a] and somb[a] >= 1 and "fruto" in uso[b]
                     and somb[b] >= 2) else 0

    def b6(a, b):
        return 1 if (suc[a] == "pionera" and suc[b] == "climax"
                     and somb[b] >= 1) else 0

    def b4(a, b):
        return -2 if (ids[a] in alelo and estr[b] in ("sotobosque", "subdosel")
                      and somb[b] <= 1) else 0

    for i in range(n):
        for j in range(i + 1, n):
            s = max(b1(i, j), b1(j, i), b3(i, j), b3(j, i),
                    b8(i, j), b8(j, i), b6(i, j), b6(j, i))
            neg = min(b4(i, j), b4(j, i))
            if fam[i] == fam[j] and fam[i] != "fabaceae":
                neg = min(neg, -1)          # B7: misma familia comparte plaga
            if neg <= -2:
                der[(i, j)] = neg
            elif s > 0:
                der[(i, j)] = s
            elif neg < 0:
                der[(i, j)] = neg
    return der


# --------------------------------------------------------------------------- #
# ACUICOLA: H5 incompat. termica, H3 depredacion, H1 mismo nicho, H4 limpieza,
#           H2 complementariedad de nicho/estrato
# --------------------------------------------------------------------------- #
@regla("fauna_acuicola")
def _acuicola(cat):
    der = {}
    nicho = [_n(x) for x in cat["nicho_trofico"]]
    estr = [_n(x) for x in cat["estrato_agua"]]
    tmin = [float(x) for x in cat["temp_min_c"]]
    tmax = [float(x) for x in cat["temp_max_c"]]
    peso = [float(x) for x in cat["peso_cosecha_g"]]
    limpia = ("detritivoro", "iliofago", "filtrador_plancton")
    n = len(nicho)

    def h3(a, b):   # carnivoro + presa pequena
        if nicho[a] == "carnivoro" and peso[b] < 0.30 * peso[a]:
            return -2 if peso[b] < 0.15 * peso[a] else -1
        return 0

    for i in range(n):
        for j in range(i + 1, n):
            if tmax[i] < tmin[j] or tmax[j] < tmin[i]:
                der[(i, j)] = -2                      # H5 sin solape termico
                continue
            neg = min(h3(i, j), h3(j, i))
            if nicho[i] == nicho[j] and estr[i] == estr[j]:
                neg = min(neg, -1)                    # H1 mismo nicho+estrato
            if neg < 0:
                der[(i, j)] = neg
                continue
            if nicho[i] in limpia or nicho[j] in limpia:
                der[(i, j)] = 2                       # H4 limpia desechos
            elif nicho[i] != nicho[j] and estr[i] != estr[j]:
                der[(i, j)] = 2                       # H2 nichos+estratos distintos
            elif nicho[i] != nicho[j] or estr[i] != estr[j]:
                der[(i, j)] = 1
    return der


# --------------------------------------------------------------------------- #
# TERRESTRE: H3 cerdo-ave, H4 aves distinto origen, H2 rumiante-ave, H7 control
#            plagas, H6 reciclaje estiercol, H5 polinizador, H1 estratos
# --------------------------------------------------------------------------- #
@regla("fauna_terrestre")
def _terrestre(cat):
    der = {}
    grupo = [_n(x) for x in cat["grupo"]]
    nicho = [_n(x) for x in cat["nicho"]]
    estr = [_n(x) for x in cat["estrato"]]
    raza = [_n(x) for x in cat["raza_tipo"]]
    aporte = [_n(x) for x in cat["aporte_principal"]]
    estiercol = [float(x) for x in cat["estiercol_kg_dia"]]
    ids = [_n(x) for x in cat["id"]]
    n = len(grupo)

    for i in range(n):
        for j in range(i + 1, n):
            cerdo_ave = (("cerdo" in ids[i] and grupo[j] == "ave")
                         or ("cerdo" in ids[j] and grupo[i] == "ave"))
            if cerdo_ave:
                der[(i, j)] = -2                      # H3 riesgo sanitario
                continue
            if grupo[i] == "ave" and grupo[j] == "ave" and raza[i] != raza[j]:
                der[(i, j)] = -1                      # H4 aves distinto origen
                continue
            s = 0

            def par(a, b, cond):
                return cond(a, b) or cond(b, a)

            if par(i, j, lambda a, b: grupo[a] == "rumiante"
                   and grupo[b] == "ave" and nicho[b] == "forrajeo_suelo"):
                s = max(s, 2)                          # H2 aves tras rumiantes
            if par(i, j, lambda a, b: "control_plagas" in aporte[a]
                   and grupo[b] == "rumiante"):
                s = max(s, 2)                          # H7 control de plagas
            if par(i, j, lambda a, b: estiercol[a] > 0
                   and "reciclaje" in aporte[b]):
                s = max(s, 2)                          # H6 reciclaje estiercol
            if grupo[i] == "polinizador" or grupo[j] == "polinizador":
                s = max(s, 1)                          # H5 polinizador
            if (estr[i] != estr[j] and grupo[i] == "rumiante"
                    and grupo[j] == "rumiante"):
                s = max(s, 1)                          # H1 estratos de forraje
            if s > 0:
                der[(i, j)] = s
    return der
