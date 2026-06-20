# DICCIONARIO DE DATOS — Bases de conocimiento para el AG de ensamblajes biológicos

Este repositorio adapta un Algoritmo Genético (AG), originalmente para diseñar acuarios, a cuatro
dominios de ensamblaje: **PLANTAS/JARDÍN**, **ÁRBOLES/BOSQUE**, **FAUNA ACUÍCOLA** y
**FAUNA TERRESTRE** (foco tropical/subtropical de Latinoamérica). Documenta qué significa cada
archivo y campo, su unidad y rango, su fuente y a cuál de las **9 categorías del AG** corresponde.

## El patrón abstracto que alimenta el AG

> Seleccionar un subconjunto de un catálogo, con cantidades, colocado en un contenedor/sitio,
> sujeto a tolerancia ambiental, compatibilidad por pares, capacidad de carga y presupuesto;
> maximizando uno o varios objetivos del dominio.

### Las 9 categorías (referenciadas como "Cat. N" en las tablas)

1. **Identidad** — nombre científico/común, descripción.
2. **Tolerancia ambiental** — rangos del sitio que la especie soporta (temperatura, pH, luz, agua, clima, calidad de agua…).
3. **Compatibilidad por pares** — sinergias/antagonismos (companion planting, alelopatía, fijación de N, competencia, depredación).
4. **Carga vs. capacidad** — lo que cada especie consume/aporta frente a la capacidad del sitio.
5. **Nicho / estrato** — posición física o trófica (porte, estrato de dosel, nicho de agua, gremio de forraje).
6. **Objetivo / valor** — lo que se maximiza (producción, valor de mercado, CO₂, biodiversidad, estética).
7. **Restricciones prácticas** — densidad, precio, disponibilidad.
8. **Sitios / contenedores** — tipos, dimensiones, capacidad, costo.
9. **Reglas / heurísticas** — criterios para derivar compatibilidades y calibrar (archivos `*_reglas.md`).

## Convenciones comunes a todos los archivos

- **Formato CSV**: UTF-8, separador coma, primera fila de encabezados, decimales con punto. Los
  campos de texto con comas van entre comillas dobles; dentro de listas se usa `;` como separador.
- **Rangos numéricos**: se expresan en **dos columnas** `*_min` / `*_max` (ambos inclusive).
- **Columna `verificacion`** (calidad del dato): `V` = parámetros clave contrastados en ≥2 fuentes ·
  `P` = una sola fuente cuantitativa principal · `E` = estimado/derivado por analogía. Lo estimado
  también se aclara en `notas`.
- **Columna `fuente`**: claves cortas (p. ej. `FAO`, `FishBase`, `UsefulTropicalPlants`); las URL
  completas están en cada `*_fuentes.md` y en `FUENTES.md`.
- **Escala de compatibilidad** (`valor`, en los archivos de pares/interacciones): entero de **−2 a +2**.
  Positivo = sinergia/facilitación/complementariedad; negativo = antagonismo/competencia/depredación;
  `0` = neutral (normalmente no se almacena). La relación es **simétrica**: `valor(a,b)=valor(b,a)`.
- **Columna `procedencia`** (pares): `investigado` = documentado en literatura · `derivado` = inferido
  por las reglas de rasgos del dominio. Esto implementa el requisito de no investigar N² pares: se
  fijan los pares muy conocidos y el resto se deriva con `*_reglas.md`.

---

# DOMINIO 1 — PLANTAS / JARDÍN  (carpeta `plantas/`)

Huerto/jardín tropical-subtropical (milpa, huerto familiar, agroecología). 40 especies.

## `plantas.csv` — catálogo de especies
| Campo | Significado | Unidad / dominio | Cat. AG |
|---|---|---|---|
| id | Identificador slug | texto | 1 |
| nombre_cientifico, nombre_comun | Identidad taxonómica | texto | 1 |
| tipo | Clase funcional: hortaliza_fruto, hortaliza_hoja, raiz_tuberculo, leguminosa, graminea, aromatica, flor, abono_verde | enum | 1, 5 |
| descripcion_breve | Descripción | texto | 1 |
| luz | Requerimiento lumínico: pleno_sol / sol_parcial / sombra | enum | 2 |
| temp_min_c, temp_max_c | Rango de temperatura tolerada | °C | 2 |
| ph_min, ph_max | Rango de pH del suelo | adimensional | 2 |
| agua | Demanda hídrica: baja / media / alta | enum | 2, 4 |
| zona_usda_min, zona_usda_max | Zona de rusticidad USDA | 1–13 | 2 |
| estrato | Porte/posición: rastrero, bajo, medio, alto, trepador | enum | 5 |
| altura_cm_min, altura_cm_max | Altura de la planta | cm | 5 |
| prof_raiz_cm | Profundidad radicular típica | cm | 5, 4 |
| ciclo_dias | Días a cosecha (en perennes: a primera cosecha — ver calibración) | días | 6, 7 |
| densidad_plantas_m2 | Densidad de plantación recomendada | plantas/m² | 4, 7 |
| espaciado_cm | Distancia entre plantas | cm | 7, 5 |
| fija_nitrogeno | Fija N atmosférico (leguminosas) | si / no | 3, 4 |
| demanda_nutrientes | Exigencia de nutrientes: baja / media / alta | enum | 4 |
| valor_polinizador | Aporte a polinizadores | índice 0–3 | 6 |
| comestible | Producto comestible | si / no | 6 |
| valor_estetico | Valor ornamental | índice 0–3 | 6 |
| rendimiento_rel | Potencial productivo relativo en huerto familiar | índice 0–3 | 6 |
| precio_semilla_usd | Precio orientativo de semilla/plántula (**estimado**) | USD | 7 |
| disponibilidad | Facilidad de obtención: alta / media / baja | enum | 7 |
| verificacion, fuente, notas | Calidad, fuente, observaciones | V/P/E · texto | — |

## `plantas_pares_documentados.csv` — compatibilidades (Cat. 3)
`especie_a, especie_b` (ids) · `relacion` (sinergia/antagonismo) · `valor` (−2…+2) · `mecanismo`
(repele_plagas, fijacion_N, sombra, soporte_fisico, atrae_polinizadores, planta_trampa, competencia,
alelopatia, comparten_plagas, cobertura_suelo) · `procedencia` (investigado/derivado) · `fuente` · `notas`.
31 pares, todos `investigado`; el resto se deriva con `plantas_reglas.md` (H1–H5).

## `plantas_sitios.csv` — contenedores (Cat. 8)
`id, tipo, descripcion` · `largo_m, ancho_m, area_m2` (m, m, m²) · `prof_suelo_cm` (cm) ·
`volumen_sustrato_l` (L) · `drenaje` (bueno/medio/malo) · `costo_usd` (USD) · `capacidad_notas`
(texto: cuántas plantas y carga de nutrientes admite) · `fuente`. 9 sitios (bancal, parcela,
maceta, jardinera, mesa de cultivo, invernadero…).

## `plantas_reglas.md` — Cat. 9
Escala de valor, heurísticas H1–H5 (misma familia→competencia/plagas compartidas; leguminosa+exigente→
fijación; aromática↔susceptible→repelencia; alto heliófilo+sombra→complementariedad de estrato;
alelopatías) y modelo carga/capacidad. **Calibración:** `ciclo_dias` en perennes = tiempo a primera
cosecha; `espaciado_cm` es radio de influencia (rastreras/trepadoras pueden requerir 2–3×); índices
0–3 son cualitativos.

---

# DOMINIO 2 — ÁRBOLES / BOSQUE  (carpeta `arboles/`)

Reforestación y agroforestería tropical/subtropical. 43 especies.

## `arboles.csv` — catálogo de especies
| Campo | Significado | Unidad / dominio | Cat. AG |
|---|---|---|---|
| id, nombre_cientifico, nombre_comun, familia, descripcion_breve | Identidad | texto | 1 |
| clima | tropical_humedo / tropical_seco / subtropical / montano | enum | 2 |
| temp_min_c, temp_max_c | Rango térmico | °C | 2 |
| precip_min_mm, precip_max_mm | Precipitación anual tolerada | mm/año | 2 |
| ph_min, ph_max | Rango de pH del suelo | adimensional | 2 |
| tolerancia_sequia | baja / media / alta | enum | 2 |
| tolerancia_sombra | 0 (heliófila/pionera) … 3 (umbrófila) | índice 0–3 | 2, 5 |
| zona_usda_min, zona_usda_max | Zona de rusticidad | 1–13 | 2 |
| estrato_dosel | emergente / dosel / subdosel / sotobosque | enum | 5 |
| altura_madura_m_min, altura_madura_m_max | Altura adulta | m | 5 |
| diam_copa_m | Diámetro de copa | m | 5, 4 |
| sistema_raiz | superficial / pivotante / profundo / tablar | enum | 5 |
| tasa_crecimiento | lenta / media / rapida | enum | 6 |
| fija_nitrogeno | Fijadora de N | si / no | 3, 4 |
| co2_kg_arbol_anio | Secuestro anual de CO₂ por árbol (**estimado, todos E**) | kg CO₂/año | 6 |
| estado_sucesional | pionera / secundaria_temprana / secundaria_tardia / climax | enum | 5, 3 |
| valor_biodiversidad | Recurso/hábitat para fauna | índice 0–3 | 6 |
| uso | madera / fruto / forraje / sombra / restauracion / fijadora_N / ornamental / multiuso | enum (`;`) | 6 |
| estatus_iucn | LC / NT / VU / EN / CR / DD / NE | enum | 6 |
| densidad_arboles_ha | Densidad de plantación típica | árboles/ha | 4, 7 |
| precio_plantula_usd | Precio de plántula (**estimado**) | USD | 7 |
| disponibilidad | alta / media / baja | enum | 7 |
| verificacion, fuente, notas | Calidad, fuente, notas | V/P/E · texto | — |

## `arboles_interacciones.csv` — compatibilidades (Cat. 3)
`especie_a, especie_b` · `relacion` (facilitacion/antagonismo/neutral) · `valor` (−2…+2) · `mecanismo`
(nodriza_sombra, fijacion_N, alelopatia, competencia_luz, competencia_agua, complementariedad_estrato,
atrae_fauna, comparte_plaga) · `procedencia` · `fuente` · `notas`. 31 pares (17 investigado / 14 derivado).

## `arboles_sitios.csv` — sitios (Cat. 8)
`id, tipo, descripcion` · `superficie_ha` (ha) · `densidad_max_arboles_ha` (árboles/ha, capacidad) ·
`suelo` (texto) · `restricciones` (texto) · `costo_establecimiento_usd_ha` (USD/ha) · `capacidad_notas` ·
`fuente`. 8 sitios (parcela forestal, ribera, urbano, suelo degradado, SAF cacao/café, silvopastoril, ladera).

## `arboles_reglas.md` — Cat. 9
Escala de valor; derivación (fijadora+exigente→facilitación; pionera bajo dosel cerrado→competencia de
luz; sotobosque+emergente→complementariedad; alelopáticas eucalipto/pino/nogal→antagonismo; misma
demanda hídrica en sitio seco→competencia de agua) y modelo solape de copas / agua vs precipitación.
**Calibración:** `co2_kg_arbol_anio` es estimado (rango 10–120 según tamaño/crecimiento), requiere
alometría por especie; precios varían hasta 10× por país.

---

# DOMINIO 3 — FAUNA ACUÍCOLA  (carpeta `fauna_acuicola/`)

Policultivo de agua dulce (carpas, tilapias, carácidos, bagres, nativos neotropicales, crustáceos). 40 especies.

## `acuicola_especies.csv` — catálogo
| Campo | Significado | Unidad / dominio | Cat. AG |
|---|---|---|---|
| id, nombre_cientifico, nombre_comun, grupo, descripcion_breve | Identidad (grupo: carpa/tilapia/caracido/bagre/nativo/crustaceo/otro) | texto/enum | 1 |
| nicho_trofico | filtrador_plancton / herbivoro / detritivoro / iliofago / omnivoro / carnivoro | enum | 5, 3 |
| estrato_agua | superficie / columna / fondo / toda_la_columna | enum | 5, 3 |
| temp_min_c, temp_max_c | Rango térmico | °C | 2 |
| ph_min, ph_max | Rango de pH del agua | adimensional | 2 |
| od_min_mg_l | Oxígeno disuelto mínimo tolerado | mg/L | 2, 4 |
| salinidad_tol | dulce / eurihalino | enum | 2 |
| densidad_siembra_ind_m3 | Densidad de siembra representativa | individuos/m³ | 4, 7 |
| peso_cosecha_g | Peso individual a cosecha | g | 4, 6 |
| ciclo_meses | Duración del ciclo de engorde | meses | 6, 7 |
| fca | Factor de conversión alimenticia (FCR) | adimensional | 4, 7 |
| alimento | Dieta principal | texto (`;`) | 4, 5 |
| rendimiento_rel | Productividad relativa | índice 0–3 | 6 |
| valor_mercado_usd_kg | Precio de granja (**estimado**) | USD/kg | 6, 7 |
| verificacion, fuente, notas | Calidad, fuente, notas | V/P/E · texto | — |

## `acuicola_interacciones.csv` — compatibilidades (Cat. 3)
`relacion` (complementariedad/competencia/depredacion/neutral) · `valor` (−2…+2) · `mecanismo`
(nicho_distinto, mismo_nicho, mismo_estrato, depreda, limpia_desechos, controla_superpoblacion,
incompatibilidad_termica) · `procedencia` · `fuente` · `notas`. 37 pares (19 investigado / 18 derivado).

## `acuicola_sitios.csv` — sitios (Cat. 8)
`id, tipo, descripcion` · `area_m2` (m²) · `profundidad_m` (m) · `volumen_m3` (m³) ·
`capacidad_carga_kg_m3` (kg/m³ de biomasa) · `recambio_agua` (texto) · `costo_usd` · `capacidad_notas` ·
`fuente`. 9 sitios (estanques de tierra, tanques revestido/concreto/biofloc, jaula, raceway, RAS).

## `acuicola_reglas.md` — Cat. 9
Principio de complementariedad de nicho; escala de valor; H1–H5; modelo carga/capacidad (biomasa =
densidad×peso ≤ capacidad; OD limitante por la especie más exigente; respiración aérea relaja OD;
detritívoros/filtradores como crédito de calidad de agua; costo vía FCA). **Calibración:** densidad y
precios son referenciales; incompatibilidad térmica suele resolverse con tolerancias (Cat. 2).

---

# DOMINIO 4 — FAUNA TERRESTRE  (carpeta `fauna_terrestre/`)

Policultivo/integración de granja tropical (aves, rumiantes, monogástricos, polinizadores). 24 especies/razas.

## `terrestre_especies.csv` — catálogo
| Campo | Significado | Unidad / dominio | Cat. AG |
|---|---|---|---|
| id, nombre_cientifico, nombre_comun, grupo, raza_tipo, descripcion_breve | Identidad (grupo: ave/rumiante/monogastrico/polinizador/otro) | texto/enum | 1 |
| clima_tol | Tolerancia climática | texto corto | 2 |
| temp_min_c, temp_max_c | Rango térmico de confort | °C | 2 |
| nicho | pastoreo / ramoneo / forrajeo_suelo / omnivoro_traspatio / aereo_polinizador / herbivoro_jaula | enum | 5, 3 |
| estrato | pasto_bajo / arbustivo_ramoneo / suelo / aereo / confinado | enum | 5 |
| densidad_carga + unidad_carga | Carga animal y su unidad (p. ej. UA_por_ha, aves_por_m2, colmenas_por_ha) | número + enum | 4, 7 |
| espacio_min_m2 | Espacio mínimo de instalación/manejo por animal | m² | 4, 7 |
| consumo_alimento_kg_dia | Consumo de alimento | kg/día | 4 |
| agua_l_dia | Consumo de agua | L/día | 4 |
| aporte_principal | Servicio aportado: estiercol / control_plagas / control_malezas / polinizacion / reciclaje_residuos / traccion | enum (`;`) | 6, 3 |
| estiercol_kg_dia | Estiércol producido (**mayormente estimado**) | kg/día | 4, 6 |
| producto | carne / huevo / leche / miel / lana / fibra / traccion | enum (`;`) | 6 |
| rendimiento_rel | Productividad relativa | índice 0–3 | 6 |
| valor_mercado | Valor de mercado (cualitativo o USD) | texto | 6, 7 |
| verificacion, fuente, notas | Calidad, fuente, notas | V/P/E · texto | — |

## `terrestre_interacciones.csv` — compatibilidades (Cat. 3)
`relacion` (sinergia/antagonismo/neutral) · `valor` (−2…+2) · `mecanismo`
(control_parasitos_pastoreo_mixto, complementariedad_estrato_pasto, rotacion_aves_tras_ganado,
competencia_pasto, riesgo_sanitario_compartido, depredacion, polinizacion, reciclaje_estiercol,
disturbio_estres) · `procedencia` · `fuente` · `notas`. 27 pares (16 investigado / 11 derivado).

## `terrestre_sitios.csv` — sitios (Cat. 8)
`id, tipo, descripcion` · `superficie` + `unidad_superficie` (ha o m²) · `capacidad_carga` +
`unidad_capacidad` (UA_por_ha, aves_por_m2…) · `infraestructura` (texto) · `costo_usd` · `capacidad_notas` ·
`fuente`. 10 sitios (potrero, silvopastoril, corral, gallinero, chiquero, conejera, colmenar, traspatio…).

## `terrestre_reglas.md` — Cat. 9
Escala de valor; heurísticas (distinto estrato de forraje→complementariedad; misma dieta+sobrecarga→
competencia; aves tras rumiantes→sinergia sanitaria; patógenos compartidos→riesgo; polinizadores→
sinergia general) y conversión a Unidad Animal (UA) para carga/capacidad. **Calibración:** `estiercol_kg_dia`
y `consumo_alimento_kg_dia` (rumiantes extensivos) son promedios; `espacio_min_m2` es instalación de
manejo, no área de pastoreo (ésta sale de la capacidad del sitio).

---

## Cómo el AG consume estas bases (resumen de mapeo)

| Necesidad del AG | Fuente de datos |
|---|---|
| Catálogo a seleccionar | `*_especies.csv` / `plantas.csv` / `arboles.csv` (Cat. 1, 6, 7) |
| Filtro de viabilidad por sitio | columnas de tolerancia (Cat. 2) vs. parámetros del sitio (Cat. 8) |
| Bonus/penalización por convivencia | `*_interacciones.csv` + reglas de derivación (Cat. 3, 9) |
| Restricción de capacidad | columnas de carga (Cat. 4) vs. `capacidad_*` del sitio (Cat. 8) |
| Modelado de solape espacial/trófico | `estrato*` / `nicho*` (Cat. 5) |
| Función objetivo | `rendimiento_rel`, `valor_*`, `co2_*`, `valor_biodiversidad`, `valor_estetico` (Cat. 6) |
| Presupuesto | precios + costos de sitio (Cat. 7, 8) |

> **Cada `*_reglas.md` incluye una función de fitness sugerida y el detalle de la derivación de pares.**
