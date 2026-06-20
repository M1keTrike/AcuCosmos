import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt

from src.ga_acucosmos import EjecutarAG
from src.esquema import cargar_esquema, cargar_tablas, cargar_escenarios
from src.metricas import REGISTRO_METRICAS, ContextoEvaluacion, evaluar_aptitud
from src.visualizacion import ResumenEscenario
from src.visualizacion_generica import resumen_dominio
from src.cromosoma import EspeciesActivas

MOSTRAR_GRAFICAS = True
RUTA_ESQUEMA = 'config/peces_ornamental.yaml'


def CargarDatos(dir_data: str = 'data'):
    catalogo = pd.read_csv(os.path.join(dir_data, 'catalogo_especies.csv'),
                           encoding='utf-8-sig')
    tanques = pd.read_csv(os.path.join(dir_data, 'catalogo_tanques.csv'),
                          encoding='utf-8-sig')
    mat = pd.read_csv(os.path.join(dir_data, 'matriz_compatibilidad.csv'),
                      encoding='utf-8-sig', index_col=0)
    matriz_kappa = mat.to_numpy(dtype=float)
    return catalogo, tanques, matriz_kappa


def EjecutarEscenario(nombre: str, descripcion: str, esquema,
                      catalogo, tanques, matriz_kappa,
                      pH_ref: float, temp_ref: float, presupuesto: float,
                      tanques_permitidos=None,
                      min_especies: int = 5,
                      max_especies: int = 15,
                      dir_salida: str = 'resultados'):
    print(f"\n=== {descripcion} ===")
    print(f"  pH_ref={pH_ref}, T_ref={temp_ref}, "
          f"presupuesto=${presupuesto:,.0f} MXN, "
          f"tanques={'todos' if tanques_permitidos is None else tanques_permitidos}")

    escenario = {'pH_ref': pH_ref, 'temp_ref': temp_ref,
                 'presupuesto': presupuesto, 'max_especies': max_especies,
                 'min_especies': min_especies}
    ctx = ContextoEvaluacion(esquema, catalogo, tanques, matriz_kappa, escenario)

    mejor, historial, top_inds, top_apts, top_mets = EjecutarAG(
        ctx,
        tanques_permitidos=tanques_permitidos,
        tam_poblacion=80,
        generaciones_max=150,
        estancamiento_max=30,
        min_especies=min_especies,
        max_especies=max_especies,
        verbose=True,
    )
    f_final, metricas = evaluar_aptitud(mejor, ctx)

    print("\n  Mejor global:")
    print(f"    F_total   = {f_final:.4f}")
    print(f"    n_especies= {metricas['n_especies']}")
    print(f"    A_e={metricas['A_e']:.3f}  I_b={metricas['I_b']:.3f}  "
          f"R_v={metricas['R_v']:.2f}  N_c={metricas['N_c']:.3f}  "
          f"M_s={metricas['M_s']:.3f}")
    print(f"    costo     = ${metricas['costo']:,} "
          f"({metricas['costo']/presupuesto*100:.0f}% del presupuesto)")
    print(f"    tanque    = #{mejor['tanque']+1} "
          f"{tanques.iloc[mejor['tanque']]['nombre']} "
          f"({tanques.iloc[mejor['tanque']]['volumen_L']} L)")
    print(f"    factible  = {metricas['factible']}")

    resumen = ResumenEscenario(nombre, mejor, historial,
                               top_inds, top_apts, top_mets,
                               catalogo, tanques, pH_ref, temp_ref,
                               dir_salida,
                               mostrar=MOSTRAR_GRAFICAS)

    print("\n  Top 3 individuos:")
    for k, (f, met) in enumerate(zip(top_apts, top_mets), start=1):
        print(f"    Top {k}: F={f:.4f}  n_sp={met['n_especies']:>2}  "
              f"A_e={met['A_e']:.3f}  I_b={met['I_b']:.3f}  "
              f"R_v={met['R_v']:.2f}  N_c={met['N_c']:.3f}  "
              f"M_s={met['M_s']:.3f}  ${met['costo']:,}")

    print("\n  Reporte de salud (Top 3):")
    print(resumen['salud'].to_string(index=False))

    return mejor, historial, metricas


def main():
    catalogo, tanques, matriz_kappa = CargarDatos('data')
    esquema = cargar_esquema(RUTA_ESQUEMA, REGISTRO_METRICAS)
    print(f"Dominio:  {esquema.dominio}")
    print(f"Catalogo: {len(catalogo)} especies")
    print(f"Tanques:  {len(tanques)}")
    print(f"Matriz:   {matriz_kappa.shape}")

    dir_salida = 'resultados'
    os.makedirs(dir_salida, exist_ok=True)

    resultados = {}

    resultados['E1'] = EjecutarEscenario(
        nombre='escenario_1',
        descripcion='Escenario 1: Acuario comunitario tropical',
        esquema=esquema, catalogo=catalogo, tanques=tanques,
        matriz_kappa=matriz_kappa,
        pH_ref=7.0, temp_ref=25.0, presupuesto=8000.0,
        tanques_permitidos=None,
        dir_salida=dir_salida,
    )

    resultados['E2'] = EjecutarEscenario(
        nombre='escenario_2',
        descripcion='Escenario 2: Biotopo amazonico acido',
        esquema=esquema, catalogo=catalogo, tanques=tanques,
        matriz_kappa=matriz_kappa,
        pH_ref=5.5, temp_ref=27.0, presupuesto=12000.0,
        tanques_permitidos=None,
        dir_salida=dir_salida,
    )

    resultados['E3'] = EjecutarEscenario(
        nombre='escenario_3',
        descripcion='Escenario 3: Nano-acuario 20L',
        esquema=esquema, catalogo=catalogo, tanques=tanques,
        matriz_kappa=matriz_kappa,
        pH_ref=7.0, temp_ref=24.0, presupuesto=3000.0,
        tanques_permitidos=[0, 1],
        min_especies=2,
        max_especies=6,
        dir_salida=dir_salida,
    )

    print("\n\n=== RESUMEN COMPARATIVO ===")
    print(f"{'Escenario':<12} {'F_total':>8} {'n_sp':>5} {'A_e':>6} "
          f"{'I_b':>6} {'R_v':>6} {'N_c':>6} {'M_s':>6} {'Costo':>10}")
    for k, (mejor, hist, m) in resultados.items():
        print(f"{k:<12} {hist[-1]['apt_mejor']:>8.4f} "
              f"{m['n_especies']:>5d} {m['A_e']:>6.3f} {m['I_b']:>6.3f} "
              f"{m['R_v']:>6.2f} {m['N_c']:>6.3f} {m['M_s']:>6.3f} "
              f"${m['costo']:>9,}")

    if MOSTRAR_GRAFICAS:
        plt.show()


def ejecutar_dominio(ruta_config, nombre_escenario=None, dir_salida='resultados',
                     seed=None, generaciones=150, poblacion=80, mostrar=False):
    """Corre CUALQUIER dominio (config YAML) en uno o todos sus escenarios y
    guarda graficas/tablas genericas en resultados/<dominio>/."""
    esquema = cargar_esquema(ruta_config, REGISTRO_METRICAS)
    catalogo, sitios, kappa = cargar_tablas(esquema)
    escenarios = cargar_escenarios(esquema)
    if nombre_escenario:
        escenarios = [e for e in escenarios
                      if str(e.get('nombre')) == nombre_escenario]
        if not escenarios:
            raise SystemExit(f"escenario '{nombre_escenario}' no existe")

    print(f"Dominio: {esquema.dominio} | {len(catalogo)} especies, "
          f"{len(sitios)} sitios | agregacion={esquema.agregacion}")
    salida = []
    for e in escenarios:
        ctx = ContextoEvaluacion(esquema, catalogo, sitios, kappa, e)
        print(f"\n=== {esquema.dominio} / {e['nombre']} ===")
        mejor, hist, top_inds, top_apts, top_mets = EjecutarAG(
            ctx, tanques_permitidos=e.get('sitios_permitidos'),
            tam_poblacion=poblacion, generaciones_max=generaciones,
            min_especies=int(e.get('min_especies', 3)),
            max_especies=int(e.get('max_especies', 15)),
            verbose=True, seed=seed)
        f, m = evaluar_aptitud(mejor, ctx)
        nom = ('nombre_comun' if 'nombre_comun' in catalogo.columns
               else esquema.id_col)
        sp = [f"{catalogo.iloc[i][nom]} x{int(mejor['C'][i])}"
              for i in EspeciesActivas(mejor)]
        print(f"  Mejor: F={f:.4f} factible={m['factible']} "
              f"n_sp={m['n_especies']} costo={m['costo']:.2f} "
              f"carga={m.get('carga')}")
        print("  Ensamblaje:", ", ".join(sp))
        out = os.path.join(dir_salida, esquema.dominio)
        res = resumen_dominio(esquema, mejor, hist, top_inds, top_apts, top_mets,
                              catalogo, out, nombre=e['nombre'], mostrar=mostrar)
        salida.append((e['nombre'], mejor, m, res))
    return salida


def _cli():
    ap = argparse.ArgumentParser(
        description="AcuCosmos — framework de ensamblajes multi-dominio")
    ap.add_argument('--dominio',
                    help="nombre o ruta del config (p.ej. arboles_bosque o "
                         "config/arboles_bosque.yaml). Sin esto: demo peces.")
    ap.add_argument('--escenario', default=None,
                    help="nombre del escenario; por defecto, todos")
    ap.add_argument('--seed', type=int, default=None)
    ap.add_argument('--generaciones', type=int, default=150)
    ap.add_argument('--poblacion', type=int, default=80)
    ap.add_argument('--no-graficas', action='store_true')
    args = ap.parse_args()
    if not args.dominio:
        main()                       # demo retrocompatible (peces, 3 escenarios)
        return
    ruta = args.dominio
    if not ruta.endswith('.yaml'):
        ruta = os.path.join('config', f"{ruta}.yaml")
    ejecutar_dominio(ruta, args.escenario, seed=args.seed,
                     generaciones=args.generaciones, poblacion=args.poblacion,
                     mostrar=not args.no_graficas)


if __name__ == '__main__':
    _cli()
