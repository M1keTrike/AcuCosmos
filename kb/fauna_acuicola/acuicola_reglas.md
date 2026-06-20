# Reglas y heurísticas — Dominio FAUNA ACUÍCOLA (policultivo de agua dulce)

Base de conocimiento para alimentar un Algoritmo Genético (AG) que selecciona un subconjunto
de especies, con densidades, en un sitio (estanque/tanque/jaula), sujeto a tolerancia de
calidad de agua, compatibilidad por pares, capacidad de carga y presupuesto, maximizando
producción y/o equilibrio ecológico.

## 1. Principio rector del policultivo: complementariedad de nicho trófico

El policultivo es productivo cuando las especies **reparten el alimento y el espacio** en lugar
de competir. Dos ejes definen el nicho:

- `nicho_trofico`: `filtrador_plancton` | `herbivoro` | `detritivoro` | `iliofago` | `omnivoro` | `carnivoro`
- `estrato_agua`: `superficie` | `columna` | `fondo` | `toda_la_columna`

Combinaciones clásicas que funcionan (todas con nichos distintos): carpa plateada (fito) +
cabezona (zoo) + herbívora (macrófitas) + común (fondo); o catla (superficie) + rohu (columna)
+ mrigal (fondo), regla india de proporción **4:2:3:1** (superficie : columna : fondo : macrófitas).

## 2. Escala del valor de interacción (columna `valor`)

| valor | relación | significado |
|------:|----------|-------------|
| +2 | complementariedad | nichos claramente distintos; sinergia fuerte (uno aprovecha lo que el otro no usa, o limpia sus desechos) |
| +1 | complementariedad | solape parcial pero coexistencia beneficiosa o de bajo conflicto |
| 0 | neutral | sin interacción relevante (no se suele almacenar; se asume por defecto) |
| −1 | competencia | mismo nicho/estrato; solape parcial por alimento o espacio |
| −2 | competencia / depredación | conflicto fuerte: depredación directa, territorialidad, o **incompatibilidad ambiental** (rango térmico opuesto) |

La matriz es **simétrica**: `valor(a,b) = valor(b,a)`. El AG la lee como penalización/bonus en el fitness.

## 3. Heurísticas para DERIVAR pares no documentados (procedencia = `derivado`)

Sólo ~37 pares están investigados/documentados. El resto se deriva con estas reglas a partir de
los rasgos de `acuicola_especies.csv`:

- **H1 — Mismo nicho_trofico Y mismo estrato_agua → competencia (−1).** Ej. dos detritívoros de
  fondo (bocachico × sábalo). Si además hay sobredensidad, el AG puede intensificar a −2.
- **H2 — Nichos distintos Y/O estratos distintos → complementariedad (+1 a +2).** +2 si ambos
  ejes difieren (p. ej. filtrador de columna × detritívoro de fondo); +1 si sólo uno difiere.
- **H3 — Carnívoro/piscívoro + especie pequeña o de talla de presa → depredación (−2).** Aplica a
  paiche, tucunaré, surubí, pejelagarto, bagre africano (sobre alevines). Modula por talla: si la
  presa potencial alcanza talla de escape (cachama adulta), baja a −1.
- **H4 — Detritívoro/iliófago o filtrador + especie alimentada con balanceado → +2 (`limpia_desechos`).**
  El detritívoro/filtrador recicla heces y alimento no consumido, mejorando la calidad de agua.
- **H5 — Rangos térmicos sin solape → incompatibilidad (−2).** Si `[temp_min,temp_max]` de A y B no
  se solapan (trucha 9–20 °C vs cachama 23–34 °C), no pueden ir en el mismo sitio. **Nota:** esto
  normalmente lo resuelve el AG con las tolerancias (categoría 2) al filtrar por sitio; los pares
  −2 por `incompatibilidad_termica` se incluyen sólo como ejemplo explícito.

> Aclaración sobre `nicho_trofico`: es la **etiqueta primaria**. Un omnívoro puede solapar con un
> especialista (p. ej. tilapia omnívora vs carpa plateada filtradora ambas explotan fitoplancton →
> competencia −1). Por eso algunas competencias enlazan etiquetas distintas: prevalece el recurso
> realmente disputado, indicado en `mecanismo`/`notas`.

## 4. Modelo CARGA vs CAPACIDAD

Para un ensamblaje en un sitio:

1. **Biomasa a cosecha** de cada especie = `densidad_siembra_ind_m3 × peso_cosecha_g / 1000` (kg/m³).
   Biomasa total del ensamblaje = Σ por especie. **Restricción dura:** biomasa_total ≤
   `capacidad_carga_kg_m3` del sitio (`acuicola_sitios.csv`).
2. **Oxígeno limitante:** la especie con mayor `od_min_mg_l` fija el piso de oxígeno que el sitio
   debe sostener. Especies con respiración aérea (clarias, paiche, gurami, pejelagarto, pangasius)
   relajan esta restricción (`od_min` 1–2 mg/L) y permiten mayor densidad.
3. **Aporte/limpieza:** detritívoros, iliófagos y filtradores tienen un *crédito* de calidad de
   agua (reducen carga orgánica). El AG puede modelarlo como bonus que aumenta la capacidad
   efectiva del sitio cuando el ensamblaje incluye ≥1 especie de fondo/filtradora.
4. **Alimento/FCA:** costo de alimento ≈ Σ (biomasa_producida × `fca` × precio_balanceado). Entra
   en la restricción de presupuesto. Carnívoros (FCA alto, proteína cara) penalizan el costo.

## 5. Función objetivo sugerida (multiobjetivo)

```
maximizar  F = w1·Produccion + w2·ValorMercado + w3·EquilibrioEcologico − w4·Costo
donde:
  Produccion        = Σ biomasa_cosecha (kg) de las especies seleccionadas
  ValorMercado      = Σ (biomasa_cosecha · valor_mercado_usd_kg)
  EquilibrioEcologico = Σ valor(par) sobre todos los pares del ensamblaje (matriz)   # sinergias suben, conflictos bajan
  Costo             = costo_sitio + costo_alevines + costo_alimento (vía FCA)
sujeto a:
  - temp/pH/OD/salinidad del sitio dentro de la tolerancia de TODA especie elegida   # categoria 2
  - biomasa_total ≤ capacidad_carga_kg_m3 · volumen_m3                               # categoria 4
  - ningún par con valor=−2 por depredación (restricción dura opcional)              # categoria 3
  - Costo ≤ presupuesto                                                              # categoria 7
```

## 6. Mapeo de archivos a las 9 categorías del AG

| Categoría AG | Dónde está | Campos |
|---|---|---|
| 1. Identidad | `acuicola_especies.csv` | id, nombre_cientifico, nombre_comun, grupo, descripcion_breve |
| 2. Tolerancia ambiental (=calidad de agua) | `acuicola_especies.csv` | temp_min/max_c, ph_min/max, od_min_mg_l, salinidad_tol |
| 3. Compatibilidad por pares | `acuicola_interacciones.csv` + estas reglas | relacion, valor, mecanismo, procedencia |
| 4. Carga vs capacidad | `acuicola_especies.csv` (densidad, peso, fca, od_min) + `acuicola_sitios.csv` (capacidad_carga_kg_m3, volumen_m3) | ver §4 |
| 5. Nicho / estrato | `acuicola_especies.csv` | nicho_trofico, estrato_agua |
| 6. Objetivo / valor | `acuicola_especies.csv` | rendimiento_rel, valor_mercado_usd_kg, peso_cosecha_g |
| 7. Restricciones prácticas | `acuicola_especies.csv` | densidad_siembra_ind_m3, fca, valor_mercado_usd_kg (precio); disponibilidad implícita en notas |
| 8. Sitios | `acuicola_sitios.csv` | tipo, area_m2, profundidad_m, volumen_m3, capacidad_carga_kg_m3, recambio_agua, costo_usd |
| 9. Reglas / heurísticas | este archivo | §1–§5 |
