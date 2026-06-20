import os
import sys
import time
import queue
import threading
from collections import Counter
from typing import Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

import matplotlib
matplotlib.use('Agg')  # thread-safe, no display backend

import pandas as pd

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ga_acucosmos import EjecutarAG
from src.esquema import cargar_esquema
from src.metricas import REGISTRO_METRICAS, ContextoEvaluacion
from src.cromosoma import EspeciesActivas
from src.visualizacion import ResumenEscenario
from src import operadores

RUTA_ESQUEMA = 'config/peces_ornamental.yaml'


GRAPH_TYPES = [
    ('aptitud',  'Aptitud'),
    ('metricas', 'Metricas'),
    ('acuario',  'Acuario'),
    ('estratos', 'Estratos'),
    ('salud',    'Salud'),
]


DEFAULT_PARAMS = {
    'tam_poblacion': 80,
    'generaciones_max': 150,
    'estancamiento_max': 30,
    't_torneo': 3,
    'min_especies': 5,
    'max_especies': 15,
    'top_k': 3,
    'delta_pH': 0.5,
    'peso_diversidad': 0.5,
    'p_m1': 0.15,
    'p_m2': 0.10,
    'p_m3': 0.15,
    'p_m4': 0.15,
}

PARAM_LABELS = {
    'tam_poblacion':    'Tamano de poblacion',
    'generaciones_max': 'Generaciones maximas',
    'estancamiento_max':'Estancamiento maximo',
    't_torneo':         'Tamano de torneo (t)',
    'min_especies':     'Min. especies (global)',
    'max_especies':     'Max. especies (global)',
    'top_k':            'Top-K individuos',
    'delta_pH':         'Delta pH (tolerancia)',
    'peso_diversidad':  'Peso diversidad (B_div)',
    'p_m1':             'P mutacion 1 (tanque)',
    'p_m2':             'P mutacion 2 (toggle especie)',
    'p_m3':             'P mutacion 3 (cardumen)',
    'p_m4':             'P mutacion 4 (frecuencia)',
}

INT_PARAMS = {
    'tam_poblacion', 'generaciones_max', 'estancamiento_max',
    't_torneo', 'min_especies', 'max_especies', 'top_k',
}

DEFAULT_SCENARIOS = [
    {'nombre': 'E1_comunitario', 'pH_ref': 7.0, 'temp_ref': 25.0,
     'presupuesto': 8000.0, 'tanques_permitidos': '',
     'min_especies': 5, 'max_especies': 15},
    {'nombre': 'E2_amazonico', 'pH_ref': 5.5, 'temp_ref': 27.0,
     'presupuesto': 12000.0, 'tanques_permitidos': '',
     'min_especies': 5, 'max_especies': 15},
    {'nombre': 'E3_nano', 'pH_ref': 7.0, 'temp_ref': 24.0,
     'presupuesto': 3000.0, 'tanques_permitidos': '0,1',
     'min_especies': 2, 'max_especies': 6},
]

SCENARIO_FIELDS = [
    ('nombre',             'Nombre',              str),
    ('pH_ref',             'pH ref.',             float),
    ('temp_ref',           'Temp. ref (C)',       float),
    ('presupuesto',        'Presupuesto (MXN)',   float),
    ('tanques_permitidos', 'Tanques permitidos',  str),
    ('min_especies',       'Min. especies',       int),
    ('max_especies',       'Max. especies',       int),
]


class QueueWriter:
    def __init__(self, q: queue.Queue):
        self.q = q

    def write(self, s: str) -> int:
        if s:
            self.q.put(s)
        return len(s)

    def flush(self) -> None:
        pass



def parse_tanques_permitidos(txt: str, n_tanques: int) -> Optional[List[int]]:
    txt = (txt or '').strip()
    if not txt:
        return None
    out: List[int] = []
    for tok in txt.replace(';', ',').split(','):
        tok = tok.strip()
        if not tok:
            continue
        idx = int(tok)
        if idx < 0 or idx >= n_tanques:
            raise ValueError(
                f"Indice de tanque fuera de rango: {idx} (0..{n_tanques - 1})"
            )
        out.append(idx)
    return out or None


def aplicar_probabilidades_mutacion(p1: float, p2: float,
                                    p3: float, p4: float) -> None:
    operadores.FuncionMutacion.__defaults__ = (p1, p2, p3, p4, None)

class ImagePanel(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.canvas = tk.Canvas(self, background='white',
                                highlightthickness=0, width=1, height=1)
        vs = ttk.Scrollbar(self, orient='vertical',
                           command=self.canvas.yview)
        hs = ttk.Scrollbar(self, orient='horizontal',
                           command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        vs.grid(row=0, column=1, sticky='ns')
        hs.grid(row=1, column=0, sticky='ew')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._path: Optional[str] = None
        self._photo = None
        self._last_width = 0
        self._last_height = 0
        self._pending = False
   
        self.canvas.bind('<Configure>', self._on_resize)

    def set_image(self, path: Optional[str]) -> None:
        self._path = path
        self._last_width = 0
        self._last_height = 0
        self._schedule_redraw()

    def _schedule_redraw(self) -> None:
        if self._pending:
            return
        self._pending = True
        self.after(40, self._do_redraw)

    def _do_redraw(self) -> None:
        self._pending = False
        self._redraw()

    def _on_resize(self, _ev=None) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 20 and h < 20:
            return
        if abs(w - self._last_width) < 4 and abs(h - self._last_height) < 4:
            return
        self._last_width = w
        self._last_height = h
        self._schedule_redraw()

    def _redraw(self) -> None:
        self.canvas.delete('all')
        self._photo = None

        avail_w = max(1, self.canvas.winfo_width())
        avail_h = max(1, self.canvas.winfo_height())

        if not self._path or not os.path.isfile(self._path):
            self.canvas.create_text(
                20, 20, anchor='nw',
                text='(sin grafica disponible: ejecuta el AG '
                     'en modo corrida unica)',
                fill='#888')
            self.canvas.configure(scrollregion=(0, 0, 1, 1))
            return

        if avail_w < 50 or avail_h < 50:
            self._schedule_redraw()
            return

        if not PIL_OK:
            try:
                self._photo = tk.PhotoImage(file=self._path)
            except tk.TclError:
                self.canvas.create_text(
                    20, 20, anchor='nw',
                    text='(instala Pillow para ver esta grafica: '
                         'pip install pillow)',
                    fill='#888')
                return
        else:
            try:
                img = Image.open(self._path)
            except Exception as e:
                self.canvas.create_text(
                    20, 20, anchor='nw',
                    text=f'(error cargando imagen: {e})',
                    fill='#a33')
                return
           
            pad = 12
            box_w = max(50, avail_w - pad)
            box_h = max(50, avail_h - pad)
            ratio = min(box_w / img.width, box_h / img.height)
            new_w = max(1, int(img.width * ratio))
            new_h = max(1, int(img.height * ratio))
            if (new_w, new_h) != img.size:
                img = img.resize((new_w, new_h), Image.LANCZOS)
            self._photo = ImageTk.PhotoImage(img)

        pw = self._photo.width()
        ph = self._photo.height()
        x = max(0, (avail_w - pw) // 2)
        y = 4
        self.canvas.create_image(x, y, anchor='nw', image=self._photo)
        self.canvas.configure(
            scrollregion=(0, 0, max(avail_w, pw), max(avail_h, ph + 8)))



class AcuCosmosGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AcuCosmos - Configurador del AG")
        self.geometry("1060x760")
        self.minsize(960, 640)

        self.catalogo: Optional[pd.DataFrame] = None
        self.tanques: Optional[pd.DataFrame] = None
        self.matriz_kappa = None

        self.params: Dict[str, tk.Variable] = {}
        self.path_vars: Dict[str, tk.StringVar] = {}
        self.escenarios: List[Dict] = [dict(e) for e in DEFAULT_SCENARIOS]

        self.log_queue: queue.Queue = queue.Queue()
        self.run_thread: Optional[threading.Thread] = None
        self.running = False

        self.ult_resultados: Dict[str, str] = {}
        self.graph_panels: Dict[str, ImagePanel] = {}

        self._build_ui()
        self._auto_cargar_datos()
        self.after(120, self._drain_log)

    
    def _build_ui(self) -> None:
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill='both', expand=True, padx=8, pady=(8, 4))

        self._tab_datos()
        self._tab_parametros()
        self._tab_escenarios()
        self._tab_ejecutar()
        self._tab_graficas()

        self.status = tk.StringVar(value="Listo.")
        bar = ttk.Label(self, textvariable=self.status, anchor='w',
                        relief='sunken')
        bar.pack(fill='x', side='bottom', padx=0, pady=0, ipady=2)

    def _tab_datos(self) -> None:
        frm = ttk.Frame(self.nb)
        self.nb.add(frm, text='1. Datos')

        intro = ttk.Label(
            frm,
            text=("Selecciona los CSV de entrada del AG. Por defecto se "
                  "cargan desde la carpeta 'data/'."),
            wraplength=900, justify='left'
        )
        intro.pack(fill='x', padx=10, pady=(10, 6))

        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        default_paths = {
            'catalogo':  os.path.join(base, 'catalogo_especies.csv'),
            'tanques':   os.path.join(base, 'catalogo_tanques.csv'),
            'matriz':    os.path.join(base, 'matriz_compatibilidad.csv'),
        }
        labels = {
            'catalogo': 'Catalogo de especies (.csv)',
            'tanques':  'Catalogo de tanques (.csv)',
            'matriz':   'Matriz de compatibilidad (.csv)',
        }

        box = ttk.LabelFrame(frm, text='Archivos de entrada')
        box.pack(fill='x', padx=10, pady=6)
        for i, key in enumerate(('catalogo', 'tanques', 'matriz')):
            ttk.Label(box, text=labels[key]).grid(
                row=i, column=0, sticky='w', padx=6, pady=4)
            var = tk.StringVar(value=default_paths[key])
            self.path_vars[key] = var
            ent = ttk.Entry(box, textvariable=var, width=80)
            ent.grid(row=i, column=1, sticky='ew', padx=4, pady=4)
            ttk.Button(
                box, text='Examinar...',
                command=lambda k=key: self._pick_csv(k)
            ).grid(row=i, column=2, padx=4, pady=4)
        box.columnconfigure(1, weight=1)

        btns = ttk.Frame(frm)
        btns.pack(fill='x', padx=10, pady=(4, 8))
        ttk.Button(btns, text='Cargar datos',
                   command=self._cargar_datos).pack(side='left', padx=4)
        ttk.Button(btns, text='Recargar default',
                   command=self._auto_cargar_datos).pack(side='left', padx=4)

        info = ttk.LabelFrame(frm, text='Resumen de datos cargados')
        info.pack(fill='both', expand=True, padx=10, pady=(4, 10))
        self.info_datos = tk.Text(info, height=14, wrap='word', state='disabled')
        self.info_datos.pack(fill='both', expand=True, padx=6, pady=6)

    def _pick_csv(self, key: str) -> None:
        path = filedialog.askopenfilename(
            title='Selecciona CSV',
            filetypes=[('CSV', '*.csv'), ('Todos', '*.*')]
        )
        if path:
            self.path_vars[key].set(path)

    def _auto_cargar_datos(self) -> None:
        try:
            self._cargar_datos()
        except Exception as e:
            self._escribir_info(f"(Carga default fallida: {e})\n")

    def _cargar_datos(self) -> None:
        p_cat = self.path_vars['catalogo'].get()
        p_tan = self.path_vars['tanques'].get()
        p_mat = self.path_vars['matriz'].get()
        for lbl, p in (('catalogo', p_cat), ('tanques', p_tan),
                       ('matriz', p_mat)):
            if not os.path.isfile(p):
                raise FileNotFoundError(f"{lbl}: {p}")

        catalogo = pd.read_csv(p_cat, encoding='utf-8-sig')
        tanques = pd.read_csv(p_tan, encoding='utf-8-sig')
        mat = pd.read_csv(p_mat, encoding='utf-8-sig', index_col=0)
        self.catalogo = catalogo
        self.tanques = tanques
        self.matriz_kappa = mat.to_numpy(dtype=float)

        lines = [
            f"Catalogo:  {len(catalogo)} especies "
            f"({len(catalogo.columns)} columnas)",
            f"Tanques:   {len(tanques)}",
            f"Matriz:    {self.matriz_kappa.shape[0]} x "
            f"{self.matriz_kappa.shape[1]}",
            "",
            "Tanques disponibles",
        ]
        for i, row in tanques.iterrows():
            lines.append(
                f"  [{i}] #{int(row['id'])} {row['nombre']}  "
                f"{int(row['volumen_L'])} L  filtro={row['capacidad_filtro_ghr']} g/h  "
                f"${int(row['precio_MXN']):,}"
            )
        self._escribir_info('\n'.join(lines) + '\n')
        self.status.set(
            f"Datos cargados: {len(catalogo)} especies, "
            f"{len(tanques)} tanques."
        )

    def _escribir_info(self, txt: str) -> None:
        self.info_datos.configure(state='normal')
        self.info_datos.delete('1.0', 'end')
        self.info_datos.insert('end', txt)
        self.info_datos.configure(state='disabled')

    def _tab_parametros(self) -> None:
        frm = ttk.Frame(self.nb)
        self.nb.add(frm, text='2. Parametros del AG')

        ttk.Label(
            frm,
            text=("Configura todos los hiperparametros del AG. Los valores "
                  "min/max de especies aqui son los globales; cada escenario "
                  "puede sobrescribirlos."),
            wraplength=900, justify='left'
        ).pack(fill='x', padx=10, pady=(10, 6))

        grp = ttk.LabelFrame(frm, text='Poblacion y criterios de paro')
        grp.pack(fill='x', padx=10, pady=6)
        self._grid_params(grp, [
            'tam_poblacion', 'generaciones_max',
            'estancamiento_max', 't_torneo',
            'top_k',
        ])

        grp2 = ttk.LabelFrame(frm, text='Rango de especies y aptitud')
        grp2.pack(fill='x', padx=10, pady=6)
        self._grid_params(grp2, [
            'min_especies', 'max_especies',
            'delta_pH', 'peso_diversidad',
        ])

        grp3 = ttk.LabelFrame(
            frm, text='Probabilidades de mutacion (defaults de FuncionMutacion)'
        )
        grp3.pack(fill='x', padx=10, pady=6)
        self._grid_params(grp3, ['p_m1', 'p_m2', 'p_m3', 'p_m4'])

        btns = ttk.Frame(frm)
        btns.pack(fill='x', padx=10, pady=(8, 10))
        ttk.Button(btns, text='Restablecer defaults',
                   command=self._reset_params).pack(side='left', padx=4)

    def _grid_params(self, parent: ttk.Widget, keys: List[str]) -> None:
        for i, k in enumerate(keys):
            r, c = divmod(i, 2)
            ttk.Label(parent, text=PARAM_LABELS[k] + ':').grid(
                row=r, column=c * 2, sticky='e', padx=(8, 4), pady=4)
            val = DEFAULT_PARAMS[k]
            if k in INT_PARAMS:
                var: tk.Variable = tk.IntVar(value=int(val))
            else:
                var = tk.DoubleVar(value=float(val))
            self.params[k] = var
            ent = ttk.Entry(parent, textvariable=var, width=14)
            ent.grid(row=r, column=c * 2 + 1, sticky='w', padx=(0, 16), pady=4)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(3, weight=1)

    def _reset_params(self) -> None:
        for k, var in self.params.items():
            var.set(DEFAULT_PARAMS[k])
        self.status.set("Parametros restablecidos a los defaults.")

    def _leer_params(self) -> Dict:
        out: Dict = {}
        for k, var in self.params.items():
            try:
                out[k] = var.get()
            except tk.TclError:
                raise ValueError(f"Valor invalido en '{PARAM_LABELS[k]}'")
        if out['min_especies'] < 1:
            raise ValueError("min_especies debe ser >= 1")
        if out['max_especies'] < out['min_especies']:
            raise ValueError("max_especies debe ser >= min_especies")
        if out['tam_poblacion'] < 4:
            raise ValueError("tam_poblacion debe ser >= 4")
        for k in ('p_m1', 'p_m2', 'p_m3', 'p_m4'):
            if not (0.0 <= out[k] <= 1.0):
                raise ValueError(f"{PARAM_LABELS[k]} fuera de [0, 1]")
        return out

    def _tab_escenarios(self) -> None:
        frm = ttk.Frame(self.nb)
        self.nb.add(frm, text='3. Escenarios')

        ttk.Label(
            frm,
            text=("Lista de escenarios que ejecutara el AG. Puedes agregar, "
                  "editar o eliminar filas, o importar/exportar un CSV. "
                  "Formato CSV: nombre,pH_ref,temp_ref,presupuesto,"
                  "tanques_permitidos,min_especies,max_especies. "
                  "El campo tanques_permitidos puede ir vacio (todos) o "
                  "como '0;1;2'."),
            wraplength=950, justify='left'
        ).pack(fill='x', padx=10, pady=(10, 6))

        cols = [f[0] for f in SCENARIO_FIELDS]
        headers = [f[1] for f in SCENARIO_FIELDS]
        tv_frm = ttk.Frame(frm)
        tv_frm.pack(fill='both', expand=True, padx=10, pady=6)
        self.tv = ttk.Treeview(tv_frm, columns=cols, show='headings',
                               height=10)
        for c, h in zip(cols, headers):
            self.tv.heading(c, text=h)
            w = 160 if c == 'nombre' else 120
            self.tv.column(c, width=w, anchor='w')
        vs = ttk.Scrollbar(tv_frm, orient='vertical', command=self.tv.yview)
        self.tv.configure(yscrollcommand=vs.set)
        self.tv.pack(side='left', fill='both', expand=True)
        vs.pack(side='right', fill='y')
        self.tv.bind('<Double-1>', lambda _e: self._editar_escenario())

        btns = ttk.Frame(frm)
        btns.pack(fill='x', padx=10, pady=(4, 10))
        ttk.Button(btns, text='Agregar',
                   command=self._agregar_escenario).pack(side='left', padx=3)
        ttk.Button(btns, text='Editar',
                   command=self._editar_escenario).pack(side='left', padx=3)
        ttk.Button(btns, text='Eliminar',
                   command=self._eliminar_escenario).pack(side='left', padx=3)
        ttk.Separator(btns, orient='vertical').pack(
            side='left', fill='y', padx=8)
        ttk.Button(btns, text='Importar CSV...',
                   command=self._importar_csv).pack(side='left', padx=3)
        ttk.Button(btns, text='Exportar CSV...',
                   command=self._exportar_csv).pack(side='left', padx=3)
        ttk.Separator(btns, orient='vertical').pack(
            side='left', fill='y', padx=8)
        ttk.Button(btns, text='Restaurar defaults',
                   command=self._restaurar_escenarios_default
                   ).pack(side='left', padx=3)

        self._refrescar_tv()

    def _refrescar_tv(self) -> None:
        self.tv.delete(*self.tv.get_children())
        for i, esc in enumerate(self.escenarios):
            vals = [esc.get(f[0], '') for f in SCENARIO_FIELDS]
            self.tv.insert('', 'end', iid=str(i), values=vals)

    def _sel_idx(self) -> Optional[int]:
        sel = self.tv.selection()
        if not sel:
            return None
        return int(sel[0])

    def _agregar_escenario(self) -> None:
        nuevo = {
            'nombre': f'E{len(self.escenarios) + 1}',
            'pH_ref': 7.0, 'temp_ref': 25.0, 'presupuesto': 8000.0,
            'tanques_permitidos': '',
            'min_especies': 5, 'max_especies': 15,
        }
        if self._dialogo_escenario(nuevo, "Nuevo escenario"):
            self.escenarios.append(nuevo)
            self._refrescar_tv()

    def _editar_escenario(self) -> None:
        idx = self._sel_idx()
        if idx is None:
            messagebox.showinfo("Editar", "Selecciona un escenario.")
            return
        copia = dict(self.escenarios[idx])
        if self._dialogo_escenario(copia, "Editar escenario"):
            self.escenarios[idx] = copia
            self._refrescar_tv()

    def _eliminar_escenario(self) -> None:
        idx = self._sel_idx()
        if idx is None:
            messagebox.showinfo("Eliminar", "Selecciona un escenario.")
            return
        del self.escenarios[idx]
        self._refrescar_tv()

    def _restaurar_escenarios_default(self) -> None:
        if messagebox.askyesno(
                "Restaurar",
                "Reemplazar la lista por los 3 escenarios por defecto?"):
            self.escenarios = [dict(e) for e in DEFAULT_SCENARIOS]
            self._refrescar_tv()

    def _dialogo_escenario(self, esc: Dict, titulo: str) -> bool:
        dlg = tk.Toplevel(self)
        dlg.title(titulo)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)

        vars_: Dict[str, tk.Variable] = {}
        for i, (k, lbl, typ) in enumerate(SCENARIO_FIELDS):
            ttk.Label(dlg, text=lbl + ':').grid(
                row=i, column=0, sticky='e', padx=8, pady=5)
            if typ is int:
                v: tk.Variable = tk.IntVar(value=int(esc.get(k, 0) or 0))
            elif typ is float:
                v = tk.DoubleVar(value=float(esc.get(k, 0.0) or 0.0))
            else:
                v = tk.StringVar(value=str(esc.get(k, '')))
            vars_[k] = v
            ttk.Entry(dlg, textvariable=v, width=28).grid(
                row=i, column=1, sticky='we', padx=8, pady=5)

        hint = ttk.Label(
            dlg,
            text=("tanques_permitidos: vacio = todos, o '0,1,2' (indices).\n"
                  "El CSV se guarda con ';' para evitar conflictos."),
            foreground='gray'
        )
        hint.grid(row=len(SCENARIO_FIELDS), column=0, columnspan=2,
                  sticky='w', padx=8, pady=(0, 6))

        ok = {'v': False}

        def _aceptar():
            try:
                for k, _, typ in SCENARIO_FIELDS:
                    val = vars_[k].get()
                    if typ is int:
                        esc[k] = int(val)
                    elif typ is float:
                        esc[k] = float(val)
                    else:
                        esc[k] = str(val).strip()
                if not esc['nombre']:
                    raise ValueError("El nombre no puede estar vacio.")
                if esc['min_especies'] > esc['max_especies']:
                    raise ValueError("min_especies > max_especies.")
                ok['v'] = True
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)

        btns = ttk.Frame(dlg)
        btns.grid(row=len(SCENARIO_FIELDS) + 1, column=0, columnspan=2,
                  pady=8)
        ttk.Button(btns, text='Aceptar', command=_aceptar
                   ).pack(side='left', padx=6)
        ttk.Button(btns, text='Cancelar', command=dlg.destroy
                   ).pack(side='left', padx=6)

        dlg.wait_window()
        return ok['v']

    def _importar_csv(self) -> None:
        path = filedialog.askopenfilename(
            title='Importar escenarios',
            filetypes=[('CSV', '*.csv'), ('Todos', '*.*')]
        )
        if not path:
            return
        try:
            df = pd.read_csv(path, encoding='utf-8-sig', dtype=str).fillna('')
            cols_req = {'nombre', 'pH_ref', 'temp_ref', 'presupuesto',
                        'min_especies', 'max_especies'}
            faltan = cols_req - set(df.columns)
            if faltan:
                raise ValueError(f"Columnas faltantes: {sorted(faltan)}")
            if 'tanques_permitidos' not in df.columns:
                df['tanques_permitidos'] = ''
            nuevos: List[Dict] = []
            for _, row in df.iterrows():
                nuevos.append({
                    'nombre': str(row['nombre']).strip(),
                    'pH_ref': float(row['pH_ref']),
                    'temp_ref': float(row['temp_ref']),
                    'presupuesto': float(row['presupuesto']),
                    'tanques_permitidos':
                        str(row['tanques_permitidos']).strip(),
                    'min_especies': int(float(row['min_especies'])),
                    'max_especies': int(float(row['max_especies'])),
                })
            if not nuevos:
                raise ValueError("El CSV no contiene filas.")
            if messagebox.askyesno(
                    "Importar",
                    f"Se leyeron {len(nuevos)} escenarios. "
                    f"Reemplazar la lista actual?"):
                self.escenarios = nuevos
            else:
                self.escenarios.extend(nuevos)
            self._refrescar_tv()
            self.status.set(f"Importados {len(nuevos)} escenarios desde CSV.")
        except Exception as e:
            messagebox.showerror("Importar CSV", f"Error: {e}")

    def _exportar_csv(self) -> None:
        if not self.escenarios:
            messagebox.showinfo("Exportar", "No hay escenarios que exportar.")
            return
        path = filedialog.asksaveasfilename(
            title='Exportar escenarios',
            defaultextension='.csv',
            filetypes=[('CSV', '*.csv')]
        )
        if not path:
            return
        try:
            df = pd.DataFrame(self.escenarios,
                              columns=[f[0] for f in SCENARIO_FIELDS])
            df.to_csv(path, index=False, encoding='utf-8-sig')
            self.status.set(f"Escenarios exportados a {path}")
        except Exception as e:
            messagebox.showerror("Exportar CSV", f"Error: {e}")

    def _tab_ejecutar(self) -> None:
        frm = ttk.Frame(self.nb)
        self.nb.add(frm, text='4. Ejecutar AG')

        top = ttk.LabelFrame(frm, text='Modo de ejecucion')
        top.pack(fill='x', padx=10, pady=(10, 6))

        self.modo = tk.StringVar(value='unico')
        ttk.Radiobutton(top, text='Corrida unica (1 run por escenario)',
                        variable=self.modo, value='unico'
                        ).grid(row=0, column=0, sticky='w', padx=8, pady=4)
        ttk.Radiobutton(top, text='Replicas (multiples runs por escenario)',
                        variable=self.modo, value='replicas'
                        ).grid(row=1, column=0, sticky='w', padx=8, pady=4)

        ttk.Label(top, text='N replicas:').grid(
            row=1, column=1, sticky='e', padx=(24, 4))
        self.n_replicas = tk.IntVar(value=10)
        ttk.Entry(top, textvariable=self.n_replicas, width=8
                  ).grid(row=1, column=2, sticky='w', padx=4)

        ttk.Label(top, text='Carpeta salida:').grid(
            row=2, column=0, sticky='e', padx=(8, 4), pady=4)
        self.dir_salida = tk.StringVar(
            value=os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'resultados'))
        ttk.Entry(top, textvariable=self.dir_salida, width=60
                  ).grid(row=2, column=1, columnspan=2, sticky='we',
                         padx=4, pady=4)
        ttk.Button(top, text='Examinar...',
                   command=self._pick_outdir
                   ).grid(row=2, column=3, padx=4, pady=4)
        top.columnconfigure(2, weight=1)

        btns = ttk.Frame(frm)
        btns.pack(fill='x', padx=10, pady=(4, 6))
        self.btn_run = ttk.Button(btns, text='Ejecutar',
                                  command=self._on_run)
        self.btn_run.pack(side='left', padx=4)
        ttk.Button(btns, text='Limpiar log',
                   command=self._clear_log).pack(side='left', padx=4)

        log_frm = ttk.LabelFrame(frm, text='Salida')
        log_frm.pack(fill='both', expand=True, padx=10, pady=(4, 10))
        self.log = scrolledtext.ScrolledText(
            log_frm, height=18, wrap='none',
            font=('Consolas', 9), state='disabled'
        )
        self.log.pack(fill='both', expand=True, padx=6, pady=6)

    def _pick_outdir(self) -> None:
        d = filedialog.askdirectory(title='Carpeta de salida')
        if d:
            self.dir_salida.set(d)

    def _clear_log(self) -> None:
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')

    def _append_log(self, txt: str) -> None:
        self.log.configure(state='normal')
        self.log.insert('end', txt)
        self.log.see('end')
        self.log.configure(state='disabled')

    def _drain_log(self) -> None:
        try:
            while True:
                self._append_log(self.log_queue.get_nowait())
        except queue.Empty:
            pass
        self.after(120, self._drain_log)

    def _tab_graficas(self) -> None:
        frm = ttk.Frame(self.nb)
        self.nb.add(frm, text='5. Graficas')

        top = ttk.Frame(frm)
        top.pack(fill='x', padx=10, pady=(10, 6))
        ttk.Label(top, text='Escenario:').pack(side='left', padx=(0, 6))
        self.graph_cbo = ttk.Combobox(top, state='readonly', width=32,
                                      values=[])
        self.graph_cbo.pack(side='left')
        self.graph_cbo.bind('<<ComboboxSelected>>',
                            lambda _e: self._actualizar_graficas())
        ttk.Button(top, text='Abrir carpeta',
                   command=self._abrir_carpeta_salida
                   ).pack(side='left', padx=8)
        if not PIL_OK:
            ttk.Label(
                top, foreground='#a33',
                text='  (Instala Pillow para escalado: pip install pillow)'
            ).pack(side='left', padx=8)

        self.graph_nb = ttk.Notebook(frm)
        self.graph_nb.pack(fill='both', expand=True, padx=10, pady=(4, 10))
        self.graph_panels = {}
        for key, label in GRAPH_TYPES:
            panel = ImagePanel(self.graph_nb)
            self.graph_nb.add(panel, text=label)
            self.graph_panels[key] = panel
            panel.set_image(None)

    def _abrir_carpeta_salida(self) -> None:
        d = self.dir_salida.get().strip()
        if not d or not os.path.isdir(d):
            messagebox.showinfo("Carpeta", "La carpeta de salida no existe.")
            return
        try:
            if sys.platform.startswith('win'):
                os.startfile(d)  # type: ignore[attr-defined]
            elif sys.platform == 'darwin':
                os.system(f'open "{d}"')
            else:
                os.system(f'xdg-open "{d}"')
        except Exception as e:
            messagebox.showerror("Carpeta", f"No se pudo abrir: {e}")

    def _refrescar_escenarios_graficas(self) -> None:
        nombres = list(self.ult_resultados.keys())
        self.graph_cbo.configure(values=nombres)
        if nombres:
            self.graph_cbo.current(0)
            self._actualizar_graficas()
        else:
            self.graph_cbo.set('')
            for p in self.graph_panels.values():
                p.set_image(None)

    def _actualizar_graficas(self) -> None:
        sel = self.graph_cbo.get()
        if not sel or sel not in self.ult_resultados:
            return
        out_dir = self.ult_resultados[sel]
        for key, _label in GRAPH_TYPES:
            path = os.path.join(out_dir, f'{sel}_{key}.png')
            self.graph_panels[key].set_image(path if os.path.isfile(path)
                                             else None)

    def _on_run(self) -> None:
        if self.running:
            messagebox.showinfo("En curso", "Ya hay una ejecucion corriendo.")
            return
        if self.catalogo is None or self.tanques is None:
            messagebox.showerror(
                "Datos", "Primero carga los datos en la pestana '1. Datos'.")
            return
        if not self.escenarios:
            messagebox.showerror(
                "Escenarios", "Agrega al menos un escenario.")
            return
        try:
            params = self._leer_params()
        except Exception as e:
            messagebox.showerror("Parametros", str(e))
            return

        try:
            n_tanques = len(self.tanques)
            escenarios_parsed: List[Dict] = []
            for esc in self.escenarios:
                escenarios_parsed.append({
                    'nombre': esc['nombre'],
                    'pH_ref': float(esc['pH_ref']),
                    'temp_ref': float(esc['temp_ref']),
                    'presupuesto': float(esc['presupuesto']),
                    'tanques_permitidos': parse_tanques_permitidos(
                        esc.get('tanques_permitidos', ''), n_tanques),
                    'min_especies': int(esc['min_especies']),
                    'max_especies': int(esc['max_especies']),
                })
        except Exception as e:
            messagebox.showerror("Escenarios", f"Error: {e}")
            return

        out_dir = self.dir_salida.get().strip()
        if not out_dir:
            messagebox.showerror("Salida", "Especifica una carpeta de salida.")
            return
        os.makedirs(out_dir, exist_ok=True)

        modo = self.modo.get()
        n_rep = max(1, int(self.n_replicas.get())) if modo == 'replicas' else 1

        self._clear_log()
        self.running = True
        self.btn_run.configure(state='disabled')
        self.status.set(f"Ejecutando ({modo})...")

        args = (params, escenarios_parsed, out_dir, modo, n_rep)
        self.run_thread = threading.Thread(
            target=self._worker, args=args, daemon=True)
        self.run_thread.start()

    def _worker(self, params: Dict, escenarios: List[Dict],
                out_dir: str, modo: str, n_rep: int) -> None:
        old_stdout = sys.stdout
        sys.stdout = QueueWriter(self.log_queue)
        try:
            aplicar_probabilidades_mutacion(
                params['p_m1'], params['p_m2'],
                params['p_m3'], params['p_m4'])

            print(f"Modo: {modo}" +
                  (f"  |  Replicas/escenario: {n_rep}"
                   if modo == 'replicas' else ""))
            print(f"Escenarios: {len(escenarios)}")
            print(f"Salida: {out_dir}")
            print("-" * 70)

            if modo == 'unico':
                self._ejecutar_modo_unico(params, escenarios, out_dir)
            else:
                self._ejecutar_modo_replicas(
                    params, escenarios, out_dir, n_rep)

            print("\nHecho.")
            self.after(0, lambda: self.status.set("Ejecucion finalizada."))
            self.after(0, self._refrescar_escenarios_graficas)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.after(0, lambda: self.status.set(f"Error: {e}"))
        finally:
            sys.stdout = old_stdout
            self.running = False
            self.after(0, lambda: self.btn_run.configure(state='normal'))

    def _obtener_esquema(self):
        if getattr(self, '_esquema', None) is None:
            self._esquema = cargar_esquema(RUTA_ESQUEMA, REGISTRO_METRICAS)
        return self._esquema

    def _ejecutar_ag(self, params: Dict, esc: Dict,
                     verbose: bool) -> tuple:
        # delta_pH ahora vive como tolerancia del eje ambiental en el YAML
        # (Fase 1); el control delta_pH de la GUI queda inerte hasta la Fase 5.
        escenario = {
            'pH_ref': esc['pH_ref'], 'temp_ref': esc.get('temp_ref'),
            'presupuesto': esc['presupuesto'],
            'max_especies': esc['max_especies'],
            'min_especies': esc['min_especies'],
        }
        ctx = ContextoEvaluacion(self._obtener_esquema(), self.catalogo,
                                 self.tanques, self.matriz_kappa, escenario)
        return EjecutarAG(
            ctx,
            tanques_permitidos=esc['tanques_permitidos'],
            tam_poblacion=params['tam_poblacion'],
            generaciones_max=params['generaciones_max'],
            estancamiento_max=params['estancamiento_max'],
            t_torneo=params['t_torneo'],
            min_especies=esc['min_especies'],
            max_especies=esc['max_especies'],
            top_k=params['top_k'],
            verbose=verbose,
        )

    def _ejecutar_modo_unico(self, params: Dict, escenarios: List[Dict],
                             out_dir: str) -> None:
        resumen = []
        self.ult_resultados = {}
        for esc in escenarios:
            tp = esc['tanques_permitidos']
            print(f"\n=== {esc['nombre']} "
                  f"(pH={esc['pH_ref']}, T={esc['temp_ref']}, "
                  f"${esc['presupuesto']:,.0f}, "
                  f"tanques={'todos' if tp is None else tp}) ===")
            mejor, historial, top_inds, top_apts, top_mets = \
                self._ejecutar_ag(params, esc, verbose=True)
            met = top_mets[0]
            print(f"\n  Mejor: F={top_apts[0]:.4f}  "
                  f"n_sp={met['n_especies']}  "
                  f"A_e={met['A_e']:.3f}  I_b={met['I_b']:.3f}  "
                  f"R_v={met['R_v']:.2f}  N_c={met['N_c']:.3f}  "
                  f"M_s={met['M_s']:.3f}  "
                  f"${met['costo']:,}  "
                  f"factible={met['factible']}")

            filas_top = []
            for k, (f, m) in enumerate(zip(top_apts, top_mets), start=1):
                filas_top.append({
                    'ranking': k, 'F_total': round(f, 4),
                    'n_especies': m['n_especies'],
                    'A_e': round(m['A_e'], 4), 'I_b': round(m['I_b'], 4),
                    'R_v': round(m['R_v'], 4), 'N_c': round(m['N_c'], 4),
                    'M_s': round(m['M_s'], 4),
                    'costo_MXN': m['costo'], 'factible': m['factible'],
                })
            pd.DataFrame(filas_top).to_csv(
                os.path.join(out_dir, f"gui_{esc['nombre']}_top.csv"),
                index=False, encoding='utf-8-sig')

            try:
                ResumenEscenario(
                    nombre=esc['nombre'],
                    mejor=mejor, historial=historial,
                    top_individuos=top_inds,
                    top_aptitudes=top_apts,
                    top_metricas=top_mets,
                    catalogo=self.catalogo, tanques=self.tanques,
                    pH_ref=esc['pH_ref'], temp_ref=esc['temp_ref'],
                    dir_salida=out_dir, mostrar=False,
                )
                self.ult_resultados[esc['nombre']] = out_dir
                print(f"  Graficas generadas en {out_dir}")
            except Exception as e:
                print(f"  [WARN] No se pudieron generar graficas: {e}")

            resumen.append({
                'escenario': esc['nombre'],
                'F_total': round(top_apts[0], 4),
                'n_especies': met['n_especies'],
                'A_e': round(met['A_e'], 4),
                'I_b': round(met['I_b'], 4),
                'R_v': round(met['R_v'], 4),
                'N_c': round(met['N_c'], 4),
                'M_s': round(met['M_s'], 4),
                'costo_MXN': met['costo'],
                'factible': met['factible'],
            })

        if resumen:
            pd.DataFrame(resumen).to_csv(
                os.path.join(out_dir, 'gui_resumen.csv'),
                index=False, encoding='utf-8-sig')
            print("\n=== RESUMEN ===")
            print(pd.DataFrame(resumen).to_string(index=False))

    def _ejecutar_modo_replicas(self, params: Dict, escenarios: List[Dict],
                                out_dir: str, n_rep: int) -> None:
        resumen_general = []
        for esc in escenarios:
            tp = esc['tanques_permitidos']
            print(f"\n=== {esc['nombre']} "
                  f"(pH={esc['pH_ref']}, T={esc['temp_ref']}, "
                  f"${esc['presupuesto']:,.0f}, "
                  f"tanques={'todos' if tp is None else tp}) ===")
            filas = []
            for r in range(n_rep):
                t0 = time.time()
                mejor, historial, top_inds, top_apts, top_mets = \
                    self._ejecutar_ag(params, esc, verbose=False)
                dt = time.time() - t0
                met = top_mets[0]
                activas = EspeciesActivas(mejor)
                apt_hist = [h['apt_mejor'] for h in historial]
                max_apt = max(apt_hist)
                gen_opt = next(
                    (int(historial[i]['generacion'])
                     for i, v in enumerate(apt_hist)
                     if abs(v - max_apt) < 1e-9),
                    int(historial[-1]['generacion'])
                )
                filas.append({
                    'F_total': round(top_apts[0], 4),
                    'n_especies': met['n_especies'],
                    'A_e': round(met['A_e'], 4),
                    'I_b': round(met['I_b'], 4),
                    'R_v': round(met['R_v'], 4),
                    'N_c': round(met['N_c'], 4),
                    'M_s': round(met['M_s'], 4),
                    'costo': met['costo'],
                    'factible': met['factible'],
                    'tanque_idx': int(mejor['tanque']),
                    'generaciones': len(historial),
                    'gen_optimo': gen_opt,
                    'especies_ids': ','.join(
                        str(int(self.catalogo.iloc[i]['id']))
                        for i in activas),
                    'tiempo_s': round(dt, 2),
                })
                print(f"  rep {r+1:02d}: F={filas[-1]['F_total']:.4f}  "
                      f"n_sp={filas[-1]['n_especies']:>2}  "
                      f"gens={filas[-1]['generaciones']:>3}  "
                      f"opt@{filas[-1]['gen_optimo']:>3}  "
                      f"factible={filas[-1]['factible']}  "
                      f"({filas[-1]['tiempo_s']:.1f}s)")

            df = pd.DataFrame(filas)
            df.to_csv(
                os.path.join(out_dir, f"gui_replicas_{esc['nombre']}.csv"),
                index=False, encoding='utf-8-sig')
            numericas = ['F_total', 'n_especies', 'A_e', 'I_b',
                         'R_v', 'N_c', 'M_s', 'costo',
                         'generaciones', 'gen_optimo']
            stats = df[numericas].agg(['mean', 'std', 'min', 'max']).round(3)
            print(f"\n  --- Resumen {esc['nombre']} (n={len(df)}) ---")
            print(stats.to_string())
            factibles = int(df['factible'].sum())
            print(f"  Factibilidad: {factibles}/{len(df)} "
                  f"({factibles/len(df)*100:.0f}%)")
            print(f"  Tiempo total: {df['tiempo_s'].sum():.1f} s  "
                  f"(prom {df['tiempo_s'].mean():.2f} s/replica)")

            cnt_tanques = Counter(df['tanque_idx'])
            print("\n  Tanques elegidos:")
            for idx, c in sorted(cnt_tanques.items(), key=lambda x: -x[1]):
                nombre_t = self.tanques.iloc[idx]['nombre']
                vol = int(self.tanques.iloc[idx]['volumen_L'])
                print(f"    [{c}x] #{idx+1} {nombre_t} ({vol}L)")

            cnt_sp: Counter = Counter()
            for ids_str in df['especies_ids']:
                if not ids_str:
                    continue
                cnt_sp.update(
                    int(x) for x in str(ids_str).split(',') if x
                )
            print("\n  Especies top 10 (frec. en mejores individuos):")
            for sp_id, c in cnt_sp.most_common(10):
                fila = self.catalogo[self.catalogo['id'] == sp_id]
                if fila.empty:
                    continue
                fila = fila.iloc[0]
                print(f"    [{c:2d}x] #{sp_id:3d} {fila['nombre_comun']} "
                      f"(estrato={fila['estrato_nombre']}, "
                      f"pH={fila['pH_min']}-{fila['pH_max']}, "
                      f"T={fila['temp_min_C']}-{fila['temp_max_C']})")

            tanque_top_idx = cnt_tanques.most_common(1)[0][0]
            resumen_general.append({
                'escenario': esc['nombre'],
                'F_mean': float(stats.loc['mean', 'F_total']),
                'F_std': float(stats.loc['std', 'F_total']),
                'F_min': float(stats.loc['min', 'F_total']),
                'F_max': float(stats.loc['max', 'F_total']),
                'n_sp_mean': float(stats.loc['mean', 'n_especies']),
                'n_sp_std': float(stats.loc['std', 'n_especies']),
                'factibles': f'{factibles}/{len(df)}',
                'gen_optimo_mean': float(stats.loc['mean', 'gen_optimo']),
                'tanque_mas_frec':
                    str(self.tanques.iloc[tanque_top_idx]['nombre']),
            })

        if resumen_general:
            df_r = pd.DataFrame(resumen_general)
            df_r.to_csv(os.path.join(out_dir, 'gui_replicas_resumen.csv'),
                        index=False, encoding='utf-8-sig')
            print("\n\n=== RESUMEN GENERAL ===")
            print(df_r.to_string(index=False))


def main() -> None:
    app = AcuCosmosGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
