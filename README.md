# AcuCosmos

**Diseño óptimo de acuarios mediante Algoritmos Genéticos.**

AcuCosmos es un sistema de **optimización multiobjetivo** que diseña automáticamente
el acuario "perfecto": decide **qué especies**, **cuántos ejemplares de cada una** y
**en qué tanque** combinarlas, maximizando estética y biodiversidad mientras respeta
restricciones biológicas reales (pH, temperatura, capacidad del filtro, agresividad
entre especies y presupuesto).

El algoritmo genético está implementado **desde cero en Python** (sin librerías de
optimización), sobre un catálogo de **100 especies** y **10 tipos de tanque**.

---

##  Características

- **Algoritmo genético propio** con operadores a medida: inicialización con distribución
  de Dirichlet, selección por torneo, cruza uniforme y 4 tipos de mutación.
- **Función de reparación** que mantiene cada individuo dentro del espacio factible
  (cardúmenes mínimos, reasignación de tanque si el filtro se sobrecarga).
- **Elitismo (μ+λ)** + **Hall of Fame** para conservar el Top-3 histórico.
- **Anti-estancamiento:** reinicio parcial de la población y paro temprano por convergencia.
- **Interfaz gráfica (Tkinter)** con 5 pestañas, ejecución en hilo aparte (no congela la UI),
  modo de réplicas para análisis estadístico, import/export de escenarios en CSV y
  visor de gráficas integrado.
- **Visualizaciones con Matplotlib:** evolución de la aptitud, evolución de métricas,
  acuario por estratos, distribución por estratos y métricas de salud del ecosistema.

---

##  El problema de optimización

Cada solución (cromosoma) codifica un acuario completo:

| Componente | Descripción |
|---|---|
| `tanque` | Índice del tanque elegido (1 de 10) |
| `B` | Vector binario: qué especies están presentes |
| `C` | Número de ejemplares de cada especie |
| `D` | Proporción relativa de cada especie |

La **función de aptitud** `F_total` combina 6 métricas:

| Métrica | Qué mide | Objetivo |
|---|---|---|
| **A_e** | Estética (rareza + variedad cromática) | maximizar |
| **I_b** | Biodiversidad (índice de Shannon normalizado) | maximizar |
| **R_v** | Comodidad (volumen del tanque / volumen requerido) | maximizar |
| **N_c** | Conflicto interespecífico (agresividad × incompatibilidad × solape de estratos) | minimizar |
| **M_s** | Sobrecarga biológica (desechos / capacidad del filtro) | minimizar |
| **B_div** | Bonus por diversidad de especies | maximizar |

```
F_total = A_e + I_b + R_v_hat − N_c − M_s_hat + B_div
```

**Restricciones duras** (vuelven la solución inviable, `F_total = 0`):
- pH de referencia fuera del rango tolerado por alguna especie.
- Filtro sobrecargado (`M_s ≥ 1`).
- Tanque demasiado pequeño (`R_v < 1`).
- Costo total por encima del presupuesto.

---

##  Estructura del proyecto

```
AcuCosmos/
├── main.py                 # Ejecución por consola (3 escenarios por defecto)
├── gui.py                  # Interfaz gráfica (Tkinter)
├── requirements.txt        # Dependencias
├── data/                   # Datos de entrada (CSV)
│   ├── catalogo_especies.csv       # 100 especies con sus parámetros
│   ├── catalogo_tanques.csv        # 10 tanques (volumen, filtro, precio)
│   ├── matriz_compatibilidad.csv   # Matriz 100×100 de compatibilidad (κ)
│   └── escenarios.csv              # Escenarios de prueba
├── src/
│   ├── cromosoma.py        # Representación del individuo y utilidades
│   ├── aptitud.py          # Función de aptitud y las 6 métricas
│   ├── operadores.py       # Inicialización, selección, cruza, mutación, reparación
│   ├── ga_acucosmos.py     # Bucle principal del algoritmo genético
│   └── visualizacion.py    # Gráficas y tablas de resultados
└── resultados/             # Salidas generadas (PNG + CSV)
```

---

## Puesta en marcha

### Requisitos
- **Python 3.10+** (probado con 3.12)
- Sistema operativo: Windows, macOS o Linux

### 1. Clonar / situarse en el proyecto

```bash
cd AcuCosmos
```

### 2. Crear y activar un entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> Para la interfaz gráfica se recomienda además **Pillow** (escalado de imágenes):
> ```bash
> pip install pillow
> ```
> Tkinter viene incluido con la mayoría de instalaciones de Python. En Linux puede
> requerir: `sudo apt install python3-tk`.

---

##  Uso

### Opción A — Por consola

Ejecuta los 3 escenarios predefinidos y guarda gráficas y tablas en `resultados/`:

```bash
python main.py
```

### Opción B — Interfaz gráfica (recomendada)

```bash
python gui.py
```

La GUI tiene 5 pestañas:

1. **Datos** — carga los CSV de entrada (por defecto desde `data/`).
2. **Parámetros del AG** — ajusta todos los hiperparámetros (población, generaciones,
   probabilidades de mutación, etc.).
3. **Escenarios** — agrega, edita, importa o exporta escenarios.
4. **Ejecutar AG** — corrida única o modo réplicas; muestra el log en vivo.
5. **Gráficas** — visor integrado de los resultados (aptitud, métricas, acuario, estratos, salud).

---

##  Parámetros principales del AG

| Parámetro | Por defecto | Descripción |
|---|---|---|
| `tam_poblacion` | 80 | Tamaño de la población |
| `generaciones_max` | 150 | Número máximo de generaciones |
| `estancamiento_max` | 30 | Generaciones sin mejora antes de parar |
| `t_torneo` | 3 | Tamaño del torneo de selección |
| `min_especies` / `max_especies` | 5 / 15 | Rango de especies por acuario |
| `delta_pH` | 0.5 | Tolerancia de pH |
| `peso_diversidad` | 0.5 | Peso del bonus de diversidad |
| `p_m1..p_m4` | 0.15 / 0.10 / 0.15 / 0.15 | Probabilidades de las 4 mutaciones |

---

## Resultados de ejemplo

| Escenario | Aptitud F | Especies | Tanque | Costo | Factible |
|---|---|---|---|---|---|
| Comunitario tropical (pH 7.0) | ~2.46 | 5 | Comunitario 150 L | $6,330 | ✅ |
| Biotopo amazónico ácido (pH 5.5) | ~2.56 | 6 | Semi-Pro 200 L | $9,350 | ✅ |
| Nano-acuario 20 L | ~2.35 | 2 | Nano Rectangular | $1,285 | ✅ |

El AG converge en **~30–80 generaciones** (≈16 s por escenario), con **100 % de
cumplimiento de pH y temperatura** y el filtro siempre dentro de su capacidad.

> Los valores pueden variar ligeramente entre corridas por la naturaleza estocástica
> del algoritmo.

---

##  Salidas generadas

Por cada escenario se generan en `resultados/`:

- `<escenario>_aptitud.png` — evolución de la aptitud (mejor / promedio / peor)
- `<escenario>_metricas.png` — evolución de las 5 métricas
- `<escenario>_acuario.png` — visualización del mejor acuario por estratos
- `<escenario>_estratos.png` — distribución de ejemplares por estrato (Top 3)
- `<escenario>_salud.png` — agresividad, carga del filtro y cumplimiento de pH/temperatura
- `<escenario>_top1..3.csv` — composición detallada de los mejores individuos
- `<escenario>_top3_resumen.csv` — resumen comparativo del Top 3

---

## Framework multi-dominio (extensión)

Sobre la rama `feature/framework-multidominio`, AcuCosmos se generaliza a un
**framework de diseño de ensamblajes biológicos**: el **mismo motor genético**
resuelve cinco dominios a partir de **datos (CSV) + un archivo de configuración
YAML**, sin tocar el motor (patrón Strategy + Registry; filosofía DEAP).

| Dominio | Config | Objetivo |
|---|---|---|
| `peces_ornamental` | `config/peces_ornamental.yaml` | acuario estético (el AcuCosmos original, idéntico) |
| `plantas_jardin` | `config/plantas_jardin.yaml` | huerto/companion planting (valor + polinizadores + sinergia) |
| `arboles_bosque` | `config/arboles_bosque.yaml` | reforestación (CO₂ por alometría + biodiversidad + facilitación) |
| `fauna_acuicola` | `config/fauna_acuicola.yaml` | policultivo productivo (biomasa·valor + equilibrio ecológico) |
| `fauna_terrestre` | `config/fauna_terrestre.yaml` | integración cultivo‑ganado (producción + sinergias) |

**Piezas nuevas** (todas fuera del motor): `src/esquema.py` (`EsquemaDominio` +
`cargar_esquema`/`cargar_tablas`/`cargar_escenarios`), `src/metricas.py` (registro
de métricas `nombre→callable`, `ContextoEvaluacion`, evaluador genérico con
penalización mortal/graduada/dinámica y normalización), `src/agregacion.py`
(suma / NSGA‑II con dominancia‑con‑restricciones de Deb / Borda / esqueleto
NSGA‑III), `src/heuristicas.py` (cargador disperso→denso + heurísticas H1..Hn) y
`src/visualizacion_generica.py`. Las bases de conocimiento por dominio están en
`kb/<dominio>/`.

### Correr un dominio

```bash
python main.py                                   # demo peces (3 escenarios, idéntico al original)
python main.py --dominio arboles_bosque          # todos los escenarios del dominio
python main.py --dominio fauna_acuicola --escenario policultivo_calido --seed 7
```

Salidas genéricas en `resultados/<dominio>/`: evolución de aptitud, evolución de
métricas, distribución por estratos (respeta el nº de estratos del dominio) y
tablas Top‑K.

### Receta: añadir un dominio nuevo (sin tocar el motor)

1. Coloca los CSV en `kb/<dominio>/`: catálogo de especies, sitios (capacidad +
   costo), interacciones (lista dispersa de pares `especie_a,especie_b,valor`
   en `[-2,+2]`) y escenarios (refs ambientales + presupuesto + sitios + rango).
2. Copia `config/_plantilla.yaml` a `config/<dominio>.yaml` y rellena: `rutas`,
   `id_col`, `rasgos` (papel del motor → columna; `null` si ausente), `estratos`
   (`col`/`orden`/`kernel`), `ejes_ambientales`, `metricas` (cada una por su
   nombre en el registro + `peso`/`signo`/`clave_reporte`/`params`),
   `restricciones`, `penalizaciones`, `agregacion` y `params` (formato de
   interacciones, `escala_origen`, `columnas_derivadas`).
3. Si necesitas una **métrica** o **heurística** nuevas, regístralas con
   `@metrica` en `src/metricas.py` o `@regla` en `src/heuristicas.py`.
4. Ejecuta `python main.py --dominio <dominio>`.

Decisiones de diseño, validación del YAML y simplificaciones conocidas: ver
`INFORME_REFACTOR.md`.

---

##  Stack técnico

- **Python** — lenguaje principal
- **NumPy** — operaciones vectoriales y aleatoriedad
- **Pandas** — manejo de catálogos y resultados
- **Matplotlib** — visualizaciones
- **Tkinter** — interfaz gráfica
- **Pillow** *(opcional)* — escalado de imágenes en la GUI

---

##  Licencia

Distribuido bajo la **Licencia MIT**. Eres libre de usar, copiar, modificar y
distribuir el proyecto conservando el aviso de copyright. Consulta el archivo
[LICENSE](LICENSE) para más detalles.

© 2026 Miguel Ángel Molina Gómez
