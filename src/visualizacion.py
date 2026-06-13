import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List

from src.cromosoma import DescribirIndividuo, EspeciesActivas


def GraficaEvolucionAptitud(historial: List[Dict], titulo: str,
                            ruta_salida: str,
                            mostrar: bool = False) -> None:
    gens = [h['generacion'] for h in historial]
    mejor = [h['apt_mejor'] for h in historial]
    peor = [h['apt_peor'] for h in historial]
    prom = [h['apt_promedio'] for h in historial]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(gens, mejor, label='Mejor', color='#1f77b4', linewidth=2)
    ax.plot(gens, prom, label='Promedio', color='#2ca02c', linewidth=1.5)
    ax.plot(gens, peor, label='Peor', color='#d62728',
            linewidth=1.0, alpha=0.6)
    ax.set_xlabel('Generacion')
    ax.set_ylabel('Aptitud F_total')
    ax.set_title(titulo)
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    if not mostrar:
        plt.close(fig)


def GraficaEvolucionMetricas(historial: List[Dict], titulo: str,
                             ruta_salida: str,
                             mostrar: bool = False) -> None:
    gens = [h['generacion'] for h in historial]
    A_e = [h['A_e'] for h in historial]
    I_b = [h['I_b'] for h in historial]
    R_v = [h['R_v'] for h in historial]
    N_c = [h['N_c'] for h in historial]
    M_s = [h['M_s'] for h in historial]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(gens, A_e, label='A_e (estetica) max', color='#1f77b4')
    ax.plot(gens, I_b, label='I_b (biodiversidad) max', color='#2ca02c')
    ax.plot(gens, R_v, label='R_v (comodidad) max', color='#9467bd')
    ax.plot(gens, N_c, label='N_c (conflicto) min',
            color='#d62728', linestyle='--')
    ax.plot(gens, M_s, label='M_s (sobrecarga) min',
            color='#ff7f0e', linestyle='--')
    ax.axhline(1.0, color='gray', linewidth=0.8, alpha=0.4)
    ax.set_xlabel('Generacion')
    ax.set_ylabel('Valor de la metrica')
    ax.set_title(titulo)
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    if not mostrar:
        plt.close(fig)


def TablasTopK(top_individuos: List[Dict], top_aptitudes: List[float],
               top_metricas: List[Dict],
               catalogo: pd.DataFrame, tanques: pd.DataFrame,
               nombre: str, dir_salida: str) -> List[pd.DataFrame]:
    dfs = []
    resumen_filas = []
    for k, (ind, f, met) in enumerate(zip(top_individuos, top_aptitudes,
                                          top_metricas), start=1):
        df = DescribirIndividuo(ind, catalogo)
        ruta_csv = os.path.join(dir_salida, f'{nombre}_top{k}.csv')
        df.to_csv(ruta_csv, index=False, encoding='utf-8-sig')
        dfs.append(df)

        tanque_nombre = tanques.iloc[ind['tanque']]['nombre']
        tanque_vol = int(tanques.iloc[ind['tanque']]['volumen_L'])
        resumen_filas.append({
            'ranking': k,
            'F_total': round(f, 4),
            'n_especies': met.get('n_especies', 0),
            'A_e': round(met.get('A_e', 0.0), 4),
            'I_b': round(met.get('I_b', 0.0), 4),
            'R_v': round(met.get('R_v', 0.0), 4),
            'N_c': round(met.get('N_c', 0.0), 4),
            'M_s': round(met.get('M_s', 0.0), 4),
            'costo_MXN': met.get('costo', 0),
            'tanque': f'{tanque_nombre} ({tanque_vol}L)',
            'factible': met.get('factible', False),
        })
    resumen = pd.DataFrame(resumen_filas)
    resumen.to_csv(os.path.join(dir_salida, f'{nombre}_top3_resumen.csv'),
                   index=False, encoding='utf-8-sig')
    return dfs


def GraficaAcuarioMejor(mejor: Dict, metricas: Dict, f_total: float,
                        catalogo: pd.DataFrame, tanques: pd.DataFrame,
                        titulo: str, ruta_salida: str,
                        mostrar: bool = False) -> None:
    t = tanques.iloc[mejor['tanque']]
    largo = float(t['largo_cm'])
    alto = float(t['alto_cm'])
    tanque_nombre = str(t['nombre'])
    tanque_vol = int(t['volumen_L'])

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.add_patch(plt.Rectangle((0, 0), largo, alto,
                               facecolor='#d9edf7', edgecolor='#1f4e79',
                               linewidth=2.5, zorder=1))
    ax.add_patch(plt.Rectangle((0, 0), largo, alto * 0.08,
                               facecolor='#c49a6c', edgecolor='none',
                               alpha=0.6, zorder=2))

    bandas = {
        1: (alto * 0.08, alto / 3),
        2: (alto / 3, 2 * alto / 3),
        3: (2 * alto / 3, alto),
    }
    nombres_banda = {1: 'Fondo', 2: 'Medio', 3: 'Superficie'}
    for y in (alto / 3, 2 * alto / 3):
        ax.axhline(y, color='#1f4e79', linestyle='--',
                   alpha=0.35, linewidth=1.0, zorder=3)
    for est, (y_low, y_high) in bandas.items():
        ax.text(largo + 1.5, (y_low + y_high) / 2, nombres_banda[est],
                rotation=90, va='center', ha='left', fontsize=10,
                color='#1f4e79', fontweight='bold')

    activas = EspeciesActivas(mejor)
    n_sp = len(activas)
    cmap = plt.colormaps.get_cmap('tab20')
    colores = [cmap(i / max(n_sp, 1)) for i in range(n_sp)]
    rng = np.random.default_rng(42)

    for k, i in enumerate(activas):
        esp = catalogo.iloc[i]
        e = int(esp['estrato'])
        n = int(mejor['C'][i])
        tam = float(esp['tamano_max_cm'])
        y_low, y_high = bandas.get(e, bandas[2])
        margen_x = max(1.5, largo * 0.02)
        margen_y = max(0.8, (y_high - y_low) * 0.12)
        xs = rng.uniform(margen_x, largo - margen_x, n)
        ys = rng.uniform(y_low + margen_y, y_high - margen_y, n)
        ax.scatter(xs, ys, s=max(40, tam * 18), color=colores[k],
                   alpha=0.85, edgecolors='black', linewidth=0.6,
                   zorder=5,
                   label=f"{esp['nombre_comun']} x{n} "
                         f"({esp.get('grupo_cromatico_nombre', '')})")

    info = (
        f"Tanque: {tanque_nombre} ({tanque_vol} L)\n"
        f"F_total = {f_total:.4f}\n"
        f"n_especies = {metricas.get('n_especies', 0)}\n"
        f"A_e = {metricas.get('A_e', 0.0):.3f}    "
        f"I_b = {metricas.get('I_b', 0.0):.3f}\n"
        f"R_v = {metricas.get('R_v', 0.0):.2f}    "
        f"N_c = {metricas.get('N_c', 0.0):.3f}\n"
        f"M_s = {metricas.get('M_s', 0.0):.3f}\n"
        f"Costo = ${metricas.get('costo', 0):,} MXN"
    )
    ax.text(0.5, alto + max(2, alto * 0.05), info,
            fontsize=9, va='bottom', ha='left',
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='white', edgecolor='#1f4e79', alpha=0.9))

    ax.set_xlim(-2, largo + 14)
    ax.set_ylim(-2, alto + alto * 0.32)
    ax.set_aspect('equal')
    ax.set_xlabel('Largo (cm)')
    ax.set_ylabel('Alto (cm)')
    ax.set_title(titulo, fontsize=12)
    ax.legend(loc='upper left', bbox_to_anchor=(1.08, 1.0),
              fontsize=8, framealpha=0.9)
    ax.grid(False)

    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150, bbox_inches='tight')
    if not mostrar:
        plt.close(fig)


def GraficaEstratosTopK(top_individuos: List[Dict],
                        catalogo: pd.DataFrame,
                        titulo: str, ruta_salida: str,
                        mostrar: bool = False) -> None:
    nombre_estrato = {}
    for _, row in catalogo.iterrows():
        nombre_estrato[int(row['estrato'])] = str(row['estrato_nombre'])
    estratos_ordenados = sorted(nombre_estrato.keys())
    etiquetas = [nombre_estrato[e] for e in estratos_ordenados]

    conteos = []
    for ind in top_individuos:
        activas = EspeciesActivas(ind)
        total_por_estrato = {e: 0 for e in estratos_ordenados}
        for i in activas:
            e = int(catalogo.iloc[i]['estrato'])
            total_por_estrato[e] += int(ind['C'][i])
        conteos.append([total_por_estrato[e] for e in estratos_ordenados])

    x = np.arange(len(etiquetas))
    n_top = len(top_individuos)
    ancho = 0.8 / max(n_top, 1)
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd']

    fig, ax = plt.subplots(figsize=(8, 5))
    for k in range(n_top):
        ax.bar(x + (k - (n_top - 1) / 2) * ancho, conteos[k],
               width=ancho, label=f'Top {k+1}', color=colores[k % len(colores)])
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas)
    ax.set_ylabel('Numero de ejemplares')
    ax.set_xlabel('Estrato de nado')
    ax.set_title(titulo)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    if not mostrar:
        plt.close(fig)


def CumplimientoRangos(individuo: Dict, catalogo: pd.DataFrame,
                       pH_ref: float, temp_ref: float,
                       delta_pH: float = 0.5) -> Dict[str, float]:
    activas = EspeciesActivas(individuo)
    if not activas:
        return {'cumpl_pH': 0.0, 'cumpl_T': 0.0}
    ok_ph = 0
    ok_t = 0
    for i in activas:
        pH_min = float(catalogo.iloc[i]['pH_min'])
        pH_max = float(catalogo.iloc[i]['pH_max'])
        T_min = float(catalogo.iloc[i]['temp_min_C'])
        T_max = float(catalogo.iloc[i]['temp_max_C'])
        if pH_min - delta_pH <= pH_ref <= pH_max + delta_pH:
            ok_ph += 1
        if T_min <= temp_ref <= T_max:
            ok_t += 1
    n = len(activas)
    return {'cumpl_pH': ok_ph / n, 'cumpl_T': ok_t / n}


def AgresividadTotal(individuo: Dict, catalogo: pd.DataFrame) -> float:
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0
    return float(sum(
        float(catalogo.iloc[i]['agresividad']) * int(individuo['C'][i])
        for i in activas
    ))


def CargaBiologicaTotal(individuo: Dict, catalogo: pd.DataFrame) -> float:
    activas = EspeciesActivas(individuo)
    if not activas:
        return 0.0
    return float(sum(
        float(catalogo.iloc[i]['tasa_desechos_ghr']) * int(individuo['C'][i])
        for i in activas
    ))


def GraficaSaludTopK(top_individuos: List[Dict],
                     top_metricas: List[Dict],
                     catalogo: pd.DataFrame,
                     tanques: pd.DataFrame,
                     pH_ref: float, temp_ref: float,
                     titulo: str, ruta_salida: str,
                     mostrar: bool = False) -> pd.DataFrame:
    n_top = len(top_individuos)
    filas = []
    for k, (ind, met) in enumerate(zip(top_individuos, top_metricas),
                                   start=1):
        agr = AgresividadTotal(ind, catalogo)
        carga = CargaBiologicaTotal(ind, catalogo)
        f_max = float(tanques.iloc[ind['tanque']]['capacidad_filtro_ghr'])
        cumpl = CumplimientoRangos(ind, catalogo, pH_ref, temp_ref)
        filas.append({
            'top': f'Top {k}',
            'agresividad_total': round(agr, 3),
            'carga_biologica_gh': round(carga, 3),
            'capacidad_filtro_gh': f_max,
            'M_s': round(met.get('M_s', 0.0), 3),
            'cumpl_pH_pct': round(cumpl['cumpl_pH'] * 100, 1),
            'cumpl_T_pct': round(cumpl['cumpl_T'] * 100, 1),
        })
    df = pd.DataFrame(filas)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    etiquetas = df['top'].tolist()
    x = np.arange(n_top)
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd']

    ax = axes[0, 0]
    ax.bar(x, df['agresividad_total'], color=colores[:n_top])
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas)
    ax.set_ylabel('Agresividad acumulada')
    ax.set_title('Agresividad total (sum a_i * C_i)')
    ax.grid(axis='y', alpha=0.3)

    ax = axes[0, 1]
    ax.bar(x - 0.2, df['carga_biologica_gh'], width=0.4,
           label='Carga generada', color='#d62728')
    ax.bar(x + 0.2, df['capacidad_filtro_gh'], width=0.4,
           label='Capacidad filtro', color='#2ca02c')
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas)
    ax.set_ylabel('g/h')
    ax.set_title('Carga biologica vs capacidad del filtro')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

    ax = axes[1, 0]
    ax.bar(x, df['cumpl_pH_pct'], color='#1f77b4')
    ax.axhline(100, color='gray', linewidth=0.8, linestyle='--')
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas)
    ax.set_ylim(0, 110)
    ax.set_ylabel('% especies en rango')
    ax.set_title(f'Cumplimiento de pH (ref={pH_ref})')
    ax.grid(axis='y', alpha=0.3)

    ax = axes[1, 1]
    ax.bar(x, df['cumpl_T_pct'], color='#ff7f0e')
    ax.axhline(100, color='gray', linewidth=0.8, linestyle='--')
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas)
    ax.set_ylim(0, 110)
    ax.set_ylabel('% especies en rango')
    ax.set_title(f'Cumplimiento de temperatura (ref={temp_ref} C)')
    ax.grid(axis='y', alpha=0.3)

    fig.suptitle(titulo, fontsize=13)
    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=150)
    if not mostrar:
        plt.close(fig)
    return df


def ResumenEscenario(nombre: str,
                     mejor: Dict, historial: List[Dict],
                     top_individuos: List[Dict],
                     top_aptitudes: List[float],
                     top_metricas: List[Dict],
                     catalogo: pd.DataFrame, tanques: pd.DataFrame,
                     pH_ref: float, temp_ref: float,
                     dir_salida: str,
                     mostrar: bool = False) -> Dict[str, object]:
    os.makedirs(dir_salida, exist_ok=True)

    GraficaEvolucionAptitud(
        historial, f'{nombre}: evolucion de la aptitud',
        os.path.join(dir_salida, f'{nombre}_aptitud.png'),
        mostrar=mostrar)

    GraficaEvolucionMetricas(
        historial, f'{nombre}: evolucion de las metricas',
        os.path.join(dir_salida, f'{nombre}_metricas.png'),
        mostrar=mostrar)

    dfs_top = TablasTopK(top_individuos, top_aptitudes, top_metricas,
                         catalogo, tanques, nombre, dir_salida)

    GraficaEstratosTopK(
        top_individuos, catalogo,
        f'{nombre}: distribucion por estratos (Top 3)',
        os.path.join(dir_salida, f'{nombre}_estratos.png'),
        mostrar=mostrar)

    if top_individuos:
        GraficaAcuarioMejor(
            top_individuos[0], top_metricas[0], top_aptitudes[0],
            catalogo, tanques,
            f'{nombre}: acuario del mejor individuo',
            os.path.join(dir_salida, f'{nombre}_acuario.png'),
            mostrar=mostrar)

    df_salud = GraficaSaludTopK(
        top_individuos, top_metricas, catalogo, tanques,
        pH_ref, temp_ref,
        f'{nombre}: metricas de salud del ecosistema (Top 3)',
        os.path.join(dir_salida, f'{nombre}_salud.png'),
        mostrar=mostrar)
    df_salud.to_csv(os.path.join(dir_salida, f'{nombre}_salud.csv'),
                    index=False, encoding='utf-8-sig')

    return {
        'tablas_top': dfs_top,
        'salud': df_salud,
    }
