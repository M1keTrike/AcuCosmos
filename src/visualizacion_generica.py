"""Visualizacion y salida GENERICAS multi-dominio (Fase 5).

Independiente del dominio: usa el historial (apt_* + claves de reporte de las
metricas del esquema), el EsquemaDominio (estratos) y el catalogo. Produce tablas
Top-K y graficas de evolucion de aptitud, evolucion de metricas y distribucion
por estratos (con el NUMERO DE ESTRATOS de cada dominio). La visualizacion rica
de acuario (mapa por estratos, salud pH/temp) sigue en src/visualizacion.py para
peces_ornamental.

No fija backend de matplotlib: las graficas se guardan con savefig (funciona en
cualquier backend); usa MPLBACKEND=Agg en entornos sin pantalla.
"""
import os

import matplotlib.pyplot as plt
import pandas as pd

from src.cromosoma import EspeciesActivas


def _col_nombre(catalogo, esquema):
    for c in ("nombre_comun", "nombre_cientifico", esquema.id_col):
        if c in catalogo.columns:
            return c
    return esquema.id_col


def tabla_individuo(individuo, catalogo, esquema):
    nom = _col_nombre(catalogo, esquema)
    filas = [{
        "id": catalogo.iloc[i][esquema.id_col],
        "nombre": catalogo.iloc[i][nom],
        "cantidad": int(individuo["C"][i]),
        "D": round(float(individuo["D"][i]), 3),
    } for i in EspeciesActivas(individuo)]
    return pd.DataFrame(filas)


def grafica_aptitud(historial, titulo, ruta):
    gen = [h["generacion"] for h in historial]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(gen, [h["apt_mejor"] for h in historial], label="mejor")
    ax.plot(gen, [h["apt_promedio"] for h in historial], label="promedio")
    ax.plot(gen, [h["apt_peor"] for h in historial], label="peor", alpha=0.5)
    ax.set_xlabel("generacion")
    ax.set_ylabel("aptitud (F)")
    ax.set_title(titulo)
    ax.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=110)
    plt.close(fig)
    return ruta


def grafica_metricas(historial, claves, titulo, ruta):
    gen = [h["generacion"] for h in historial]
    fig, ax = plt.subplots(figsize=(7, 4))
    for k in claves:
        ys = [h.get(k) for h in historial]
        if all(isinstance(y, (int, float)) for y in ys):
            ax.plot(gen, ys, label=k)
    ax.set_xlabel("generacion")
    ax.set_ylabel("valor de metrica")
    ax.set_title(titulo)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=110)
    plt.close(fig)
    return ruta


def grafica_estratos(individuo, catalogo, esquema, titulo, ruta):
    """Distribucion de individuos por estrato, respetando el nº de estratos del
    dominio (esquema.estratos.orden)."""
    orden = [str(o) for o in esquema.estratos.get("orden", [])]
    col = esquema.estratos.get("col")
    conteo = {o: 0 for o in orden}
    for i in EspeciesActivas(individuo):
        val = str(catalogo.iloc[i][col])
        conteo[val] = conteo.get(val, 0) + int(individuo["C"][i])
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(orden, [conteo.get(o, 0) for o in orden], color="#3a7")
    ax.set_ylabel("individuos")
    ax.set_title(titulo)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(ruta, dpi=110)
    plt.close(fig)
    return ruta


def resumen_dominio(esquema, mejor, historial, top_inds, top_apts, top_mets,
                    catalogo, dir_salida, nombre="escenario", mostrar=False):
    """Genera graficas (aptitud, metricas, estratos) y tablas Top-K en dir_salida.
    Devuelve {'rutas': {...}, 'resumen': DataFrame}."""
    os.makedirs(dir_salida, exist_ok=True)
    pref = os.path.join(dir_salida, f"{esquema.dominio}_{nombre}")
    claves = [mc.clave_reporte for mc in esquema.metricas]
    titulo = f"{esquema.dominio} / {nombre}"
    rutas = {
        "aptitud": grafica_aptitud(historial, titulo, f"{pref}_aptitud.png"),
        "metricas": grafica_metricas(historial, claves, titulo,
                                     f"{pref}_metricas.png"),
        "estratos": grafica_estratos(mejor, catalogo, esquema, titulo,
                                     f"{pref}_estratos.png"),
    }
    for k, ind in enumerate(top_inds, 1):
        tabla_individuo(ind, catalogo, esquema).to_csv(
            f"{pref}_top{k}.csv", index=False, encoding="utf-8-sig")

    filas = []
    for k, (apt, met) in enumerate(zip(top_apts, top_mets), 1):
        fila = {"ranking": k, "F": round(float(apt), 4),
                "factible": met.get("factible"), "costo": met.get("costo"),
                "n_especies": met.get("n_especies")}
        for c in claves:
            v = met.get(c)
            fila[c] = round(float(v), 4) if isinstance(v, (int, float)) else v
        filas.append(fila)
    resumen = pd.DataFrame(filas)
    resumen.to_csv(f"{pref}_top_resumen.csv", index=False, encoding="utf-8-sig")
    if mostrar:
        plt.show()
    return {"rutas": rutas, "resumen": resumen}
