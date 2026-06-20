# REPORTE DE COBERTURA — consolidado

Resumen de cobertura, verificación y metodología de compatibilidades de las cuatro bases de
conocimiento (foco tropical/subtropical de Latinoamérica). Las cifras provienen directamente de los
CSV (fuente de verdad), por lo que pueden diferir ligeramente de los textos narrativos en los
`*_cobertura.md` de cada dominio, que se conservan como notas cualitativas.

## 1. Totales

| Dominio | Especies | Sitios | Pares documentados | Archivos |
|---|---:|---:|---:|---:|
| Plantas / jardín | 40 | 9 | 31 | 6 |
| Árboles / bosque | 43 | 8 | 31 | 6 |
| Fauna acuícola | 40 | 9 | 37 | 6 |
| Fauna terrestre | 24 | 10 | 27 | 6 |
| **TOTAL** | **147** | **36** | **126** | **24** |

Cada dominio entrega: `*_especies.csv` (o `plantas.csv`/`arboles.csv`), `*_pares_documentados.csv` /
`*_interacciones.csv`, `*_sitios.csv`, `*_reglas.md`, `*_fuentes.md`, `*_cobertura.md`. A nivel raíz:
`DICCIONARIO_DE_DATOS.md`, `FUENTES.md`, `REPORTE_COBERTURA.md`.

## 2. Verificación (V / P / E)

`V` = parámetros clave contrastados en ≥2 fuentes · `P` = una fuente cuantitativa principal ·
`E` = estimado/derivado por analogía.

| Dominio | V | P | E | % V |
|---|---:|---:|---:|---:|
| Plantas | 38 | 1 | 1 | 95.0% |
| Árboles | 39 | 4 | 0 | 90.7% |
| Fauna acuícola | 17 | 22 | 1 | 42.5% |
| Fauna terrestre | 17 | 7 | 0 | 70.8% |
| **TOTAL** | **111** | **34** | **2** | **75.5%** |

- **% verificado (V) global ≈ 75.5%**, % parcial (P) ≈ 23.1%, % estimado (E) ≈ 1.4%.
- El dominio **acuícola tiene más `P`** porque se aplicó un criterio conservador: muchas especies
  (surubí, rhamdia, pejelagarto, lisa, pejerrey, tilapias secundarias, híbridos) tienen una sola
  fuente cuantitativa fuerte aunque sus parámetros son plausibles y coherentes con congéneres.
- **Campos sistemáticamente estimados** (independientes de la marca de especie): CO₂ arbóreo
  (`co2_kg_arbol_anio`, 100% E), todos los **precios** (`precio_semilla_usd`, `precio_plantula_usd`,
  `valor_mercado*`) y el **estiércol** terrestre (`estiercol_kg_dia`, mayoría). Están señalados en
  notas y en los diccionarios; no deben tomarse como dato verificado.

## 3. Metodología de las compatibilidades (Cat. 3)

Para no investigar N² pares, en cada dominio se **fijaron los pares muy conocidos** (`procedencia =
investigado`) y el resto se **deriva por reglas de rasgos** (`*_reglas.md`).

| Dominio | Pares totales | Investigado | Derivado | Pares posibles C(n,2) | % documentado |
|---|---:|---:|---:|---:|---:|
| Plantas | 31 | 31 | 0 | 780 | 4.0% |
| Árboles | 31 | 17 | 14 | 903 | 3.4% |
| Fauna acuícola | 37 | 19 | 18 | 780 | 4.7% |
| Fauna terrestre | 27 | 16 | 11 | 276 | 9.8% |

- **Escala única `valor ∈ [−2, +2]`** en los cuatro dominios (positivo = sinergia/facilitación/
  complementariedad; negativo = competencia/depredación/incompatibilidad). Matriz simétrica.
- **Reglas de derivación por dominio** (resumen; detalle en cada `*_reglas.md`):
  - *Plantas*: misma familia → plagas compartidas/competencia; leguminosa + exigente → fijación;
    aromática ↔ susceptible → repelencia; alto heliófilo + sombra → complementariedad; alelopatías.
  - *Árboles*: fijadora + exigente/pionera → facilitación; pionera bajo dosel cerrado → competencia
    de luz; sotobosque + emergente → complementariedad de estrato; alelopáticas → antagonismo;
    misma demanda hídrica en seco → competencia de agua.
  - *Acuícola*: mismo nicho+estrato → competencia; nichos/estratos distintos → complementariedad;
    carnívoro + presa → depredación; detritívoro/filtrador + balanceado → limpieza; rango térmico
    sin solape → incompatibilidad.
  - *Terrestre*: distinto estrato de forraje → complementariedad; misma dieta + sobrecarga →
    competencia; aves tras rumiantes → sinergia sanitaria; patógenos compartidos → riesgo;
    polinizadores → sinergia general.
- **Consistencia verificada por script**: integridad referencial (todos los ids de pares existen en
  el catálogo), coherencia de signo (sinergias > 0, antagonismos/depredaciones < 0) y ausencia de
  contradicciones nicho↔relación. (Ver §5.)

## 4. Vacíos e incertidumbres conocidas

**Plantas.** Faltan *Allium* (cebolla/ajo → el par clásico zanahoria-cebolla queda fuera) y la mayor
parte de Brassicaceae (solo rábano). Índices 0–3 cualitativos; precios estimados; `ciclo_dias` en
perennes = primera cosecha.

**Árboles.** `co2_kg_arbol_anio` 100% estimado (requiere alometría por especie). 4 especies en `P`
(Acaciella, Sterculia, Virola, Acrocarpus/Hyeronima). Sólo 31 de ~900 pares documentados; juglona de
*Juglans neotropica* inferida de *J. nigra*. Nota: los textos narrativos del `arboles_cobertura.md`
mencionan 45 especies/32 pares; el conteo real de los CSV es **43 especies / 31 pares** (autoridad: CSV).

**Fauna acuícola.** Densidades y precios referenciales; FCA/peso de cosecha como promedios. La
incompatibilidad térmica se modela mejor con tolerancias (Cat. 2) que con la matriz (sólo 2 pares
ilustrativos). Especies `P` (surubí, rhamdia, pejelagarto, lisa, pejerrey, matrinxa) requieren
verificación adicional antes de uso productivo.

**Fauna terrestre.** `estiercol_kg_dia` y `consumo_alimento_kg_dia` (rumiantes extensivos) son
promedios sensibles a la calidad del forraje. `espacio_min_m2` = instalación de manejo, no área de
pastoreo. Razas no incluidas (Blackbelly, Anglo-nubia, ecotipos de cerdo criollo) y vacíos geográficos
(Bolivia, Ecuador, Paraguay).

**Transversal.** Sólo se modelan interacciones por **pares**; el AG debe componer la sinergia de un
ensamblaje como suma de pares (no hay tríadas). Las interacciones de manejo humano no se modelan.

## 5. Checklist de calidad (autovalidación)

- [x] Cada categoría 1–9 del AG está cubierta en los 4 dominios o su ausencia se justifica.
- [x] La estructura está documentada y es mapeable a 1–9 (`DICCIONARIO_DE_DATOS.md`).
- [x] Matrices/listas de compatibilidad internamente consistentes (validación por script: integridad
      referencial 100%, signos coherentes, sin contradicciones nicho↔relación); rango y significado
      del `valor` explicados.
- [x] Todo valor estimado está marcado (`E`/`P` y/o notas); las afirmaciones duras tienen fuente.
- [x] Unidades consistentes por campo; rangos plausibles; carga total no excede siempre la capacidad
      (modelos carga/capacidad en cada `*_reglas.md`).

## 6. Dominios propuestos adicionales (no desarrollados)

Como extensión natural del mismo patrón abstracto del AG, podrían añadirse: **acuaponía** (acopla
plantas + peces, uniendo los dominios 1 y 3), **polinizadores/insectos benéficos** para control
biológico en jardín, y **hongos/micorrizas** como capa de facilitación del suelo. Se documentan aquí
como oportunidades, no como entregables de esta versión.
