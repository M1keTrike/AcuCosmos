# Reglas del Sistema de Companion Planting — Base de Conocimiento Hortícola Tropical

## (a) Escala de Compatibilidad (-2 a +2)

| Valor | Etiqueta | Significado |
|-------|----------|-------------|
| +2 | Sinergia fuerte | Beneficio bien documentado en ≥2 fuentes científicas o experimentales. Mecanismo conocido (fijación de N, repelente de plaga demostrado, soporte físico, complementariedad de nicho comprobada). Recomendación activa de plantar juntas. |
| +1 | Sinergia moderada | Beneficio documentado en fuentes empíricas o extensión agrícola, pero con evidencia más limitada o condicionada. Recomendable con reservas. |
| 0 | Neutro | Sin interacción conocida positiva ni negativa; co-existencia sin efecto documentado. Valor reservado para pares derivados sin señal clara. |
| -1 | Antagonismo moderado | Competencia, alelopatía leve, o riesgo de plaga compartida con evidencia empírica. Desaconsejado en el mismo bancal; posible en la misma parcela con separación. |
| -2 | Antagonismo fuerte | Alelopatía fuerte documentada, concentración de plagas graves, o competencia severa que reduce rendimiento. Evitar en el mismo sistema salvo uso deliberado como trampa. |

---

## (b) Heurísticas para Derivar Compatibilidades por Rasgos

### H1 — Misma Familia Botánica → Comparten Plagas / Competencia (valor base: -1)

El Algoritmo Genético debe penalizar pares de la misma familia botánica principal:

| Familia | Géneros/Especies en la base |
|---------|----------------------------|
| Solanaceae | tomate, tomate_cherry, berenjena, chile_jalapeño, chile_habanero |
| Cucurbitaceae | calabaza, ayote, pepino |
| Fabaceae | frijol_negro, frijol_voluble, caraota, gandul, haba, cacahuate, jicama, mucuna, crotalaria, canavalia |
| Apiaceae | zanahoria, cilantro, culantro |
| Asteraceae | tagetes, calendula, girasol |
| Amaranthaceae | acelga, espinaca, quelites, epazote |
| Lamiaceae | albahaca, orégano, hierbabuena, romero |

**Regla H1a**: Si `familia(A) == familia(B)` y familia ∈ {Solanaceae, Cucurbitaceae}, derivar `antagonismo, valor=-1, mecanismo=comparten_plagas`.  
**Regla H1b**: Si `familia(A) == familia(B)` y familia ∈ {Fabaceae}, derivar `neutro, valor=0` (leguminosas generalmente compatibles entre sí aunque compiten).  
**Regla H1c**: Si `familia(A) == familia(B)` y familia ∈ {Apiaceae, Asteraceae, Lamiaceae, Amaranthaceae}, derivar `neutro, valor=0` (competencia leve por recursos similares pero sin plagas compartidas graves documentadas).

---

### H2 — Leguminosa + Cultivo Exigente → Sinergia por Fijación de N (valor: +1 a +2)

**Condición**: `fija_nitrogeno(A) == "si"` Y `demanda_nutrientes(B) == "alta"` Y cultivo `B` es comestible  
**Derivación**: `sinergia, valor=+2, mecanismo=fijacion_N, procedencia=derivado`  
**Ejemplo**: frijol_negro + maíz (documentado como +2), gandul + maíz (documentado como +2).

**Condición extendida**: `fija_nitrogeno(A) == "si"` Y `demanda_nutrientes(B) == "media"`  
**Derivación**: `sinergia, valor=+1, mecanismo=fijacion_N, procedencia=derivado`

**Excepciones**: No aplicar entre dos leguminosas (compiten por mismo nicho de rizobios). Tampoco entre leguminosa y otra leguminosa, ya que los beneficios de N se neutralizan.

---

### H3 — Aromática Fuerte + Hortaliza Susceptible → Repele Plagas (valor: +1)

**Condición**: `tipo(A) == "aromatica"` Y `tipo(B) ∈ {hortaliza_fruto, hortaliza_hoja}` Y `demanda_nutrientes(B) != "baja"`  
**Derivación**: `sinergia, valor=+1, mecanismo=repele_plagas, procedencia=derivado`  
**Justificación**: Las aromáticas de las familias Lamiaceae y Apiaceae liberan volátiles que confunden insectos fitófagos. La evidencia para albahaca-tomate y romero-zanahoria es científica (+2); para pares análogos se estima +1.

**Aromáticas con mayor evidencia de repelencia**: albahaca > romero > hierbabuena > orégano > epazote > cilantro (en floración)

---

### H4 — Planta Alta Heliófila + Planta de Sombra → Complementariedad de Estrato (valor: +1)

**Condición**: `estrato(A) ∈ {alto}` Y `luz(A) == "pleno_sol"` Y `estrato(B) ∈ {bajo, rastrero}` Y `luz(B) ∈ {sol_parcial, sombra}`  
**Derivación**: `sinergia, valor=+1, mecanismo=sombra, procedencia=derivado`  
**Ejemplo**: maíz (alto, pleno_sol) + lechuga (bajo, sol_parcial) → lechuga tolera sombra del maíz en trópico.

**Condición contraria** (dos plantas altas heliófila juntas):  
`estrato(A) == "alto"` Y `estrato(B) == "alto"` Y `luz(A) == "pleno_sol"` Y `luz(B) == "pleno_sol"`  
**Derivación**: `antagonismo, valor=-1, mecanismo=competencia, procedencia=derivado`

---

### H5 — Alelopatías Conocidas (Ajustes Específicos)

Las siguientes alelopatías están documentadas y deben sobrescribir las heurísticas genéricas:

| Planta Alelopática | Afecta a | Efecto | Valor | Mecanismo | Fuente |
|-------------------|----------|--------|-------|-----------|--------|
| Helianthus annuus (girasol) | Phaseolus spp. (frijoles) | Inhibición de raíz y crecimiento | -2 | alelopatia | PSU Extension; Organic Gardening 101 |
| Helianthus annuus (girasol) | Cucumis sativus (pepino) | Inhibición moderada | -1 | alelopatia | Community Roots Ohio |
| Dysphania ambrosioides (epazote) | Plantas vecinas (<30 cm) | Inhibición por ascaridole | -1 | alelopatia | NCSU Extension; PVAMU |
| Tagetes spp. | Nematodos en suelo (no plantas) | Nematicida de raíz | +1 | alelopatia | ScienceDirect; ResearchGate |

---

## (c) Modelo CARGA vs. CAPACIDAD

### Variables de Carga (demanda total del ensamble)

Para cada especie `i` en el ensamble con densidad `d_i` (plantas/m²):

```
carga_agua_total    = Σ (agua_i × d_i × factor_agua)
carga_nutrientes    = Σ (demanda_nutrientes_i × d_i × factor_N)
carga_volumen_raiz  = Σ (prof_raiz_cm_i × d_i)
carga_estrato       = conteo de plantas por estrato (rastrero|bajo|medio|alto|trepador)
```

**Factores de conversión sugeridos** (escalar baja=1, media=2, alta=3):
- `factor_agua`: 1 L/día/planta por unidad de escala
- `factor_N`: índice relativo; alta=3, media=2, baja=1

### Variables de Capacidad del Sitio

Desde `plantas_sitios.csv`:
- `area_m2`: área disponible para densidad
- `volumen_sustrato_l`: volumen total de sustrato (limita raíces en contenedores)
- `prof_suelo_cm`: profundidad máxima de raíces
- `drenaje`: condiciona la carga de agua (bueno=puede tolerar alta demanda hídrica; moderado=limitar plantas de agua alta)

### Reglas de Balance CARGA ≤ CAPACIDAD

1. **Densidad total**: `Σ d_i ≤ area_m2 × densidad_maxima_por_estrato`  
   - Estrato bajo: máx. 9 plantas/m²  
   - Estrato medio: máx. 4 plantas/m²  
   - Estrato alto: máx. 1-2 plantas/m²  
   - Trepador: cuenta el área de soporte, no del suelo

2. **Profundidad de raíz**: No plantar dos especies de raíz profunda (>60 cm) en macetas con `volumen_sustrato_l < 100`.  
   Regla: `max(prof_raiz_i) ≤ prof_suelo_cm` para cada planta `i` en sitio.

3. **Demanda de N**: Si `Σ(demanda_nutrientes × d_i) / area_m2 > 6`, el sitio requiere aporte externo de N (compost, leguminosas integradas, o fertilización).  
   Las leguminosas (`fija_nitrogeno == "si"`) descuentan su aporte estimado (≈2-3 unidades N por planta por temporada).

4. **Agua en contenedores**: Sitios con `drenaje = bueno` (contenedores) no deben combinar >2 especies de `agua = alta` sin sistema de riego automatizado.

5. **Estrato y luz**: El AG debe verificar que las plantas de estrato bajo que requieren `pleno_sol` no queden bloqueadas por una planta de estrato alto en el mismo m². Excepción: si `luz(bajo) == sol_parcial`, es compatible con sombra de planta alta.

---

## (d) Mapeo de Archivos a las 9 Categorías del AG

| Categoría AG | Archivo(s) | Columnas Clave |
|-------------|-----------|----------------|
| 1. **Identidad** | plantas.csv | id, nombre_cientifico, nombre_comun, tipo |
| 2. **Tolerancia Ambiental** | plantas.csv | temp_min_c, temp_max_c, ph_min, ph_max, agua, luz, zona_usda_min, zona_usda_max |
| 3. **Compatibilidad** | plantas_pares_documentados.csv; plantas_reglas.md | especie_a, especie_b, relacion, valor, mecanismo; Heurísticas H1-H5 |
| 4. **Carga / Capacidad** | plantas.csv + plantas_sitios.csv | demanda_nutrientes, agua, prof_raiz_cm, densidad_plantas_m2, altura_cm_max vs. area_m2, volumen_sustrato_l, prof_suelo_cm |
| 5. **Nicho / Estrato** | plantas.csv | estrato, altura_cm_min, altura_cm_max, luz |
| 6. **Objetivo / Valor** | plantas.csv | comestible, valor_polinizador, valor_estetico, rendimiento_rel, fija_nitrogeno |
| 7. **Restricciones** | plantas.csv + plantas_reglas.md | notas (toxicidad, preparación especial), Heurísticas H1-H5, pares con valor=-2 |
| 8. **Sitios** | plantas_sitios.csv | todos los campos; especialmente area_m2, prof_suelo_cm, volumen_sustrato_l, drenaje, costo_usd |
| 9. **Reglas** | plantas_reglas.md | Secciones a, b, c, d completas |

### Flujo de Evaluación del AG para un Ensamble Candidato

```
Para cada ensamble E = {planta_1, planta_2, ..., planta_n} en sitio S:

1. FILTRAR por tolerancia ambiental: temperatura del sitio ∈ [temp_min, temp_max] para cada planta
2. VERIFICAR carga: Σ prof_raiz ≤ prof_suelo_cm(S); densidad ≤ límite por estrato
3. CALCULAR fitness_compatibilidad: Σ valor(par_ij) para todos los pares i,j en E
4. CALCULAR fitness_objetivo: Σ (rendimiento_rel + valor_polinizador + valor_estetico) / n
5. PENALIZAR por antagonismos: -10 × |pares con valor ≤ -2|
6. BONIFICAR por fijación_N cuando hay planta de demanda_alta: +5 si hay ≥1 leguminosa fijadora
7. PENALIZAR si carga_N > capacidad del sitio: -5 × exceso
8. CALCULAR fitness_total = w1 × fitness_compatibilidad + w2 × fitness_objetivo - penalizaciones + bonificaciones
```

Pesos sugeridos (ajustables): w1 = 0.6, w2 = 0.4
