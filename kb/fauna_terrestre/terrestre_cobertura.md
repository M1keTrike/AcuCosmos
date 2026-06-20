# Cobertura y Calidad de Datos — Base de Conocimiento Fauna Terrestre

## Resumen Numérico

| Metrica | Valor |
|---------|-------|
| Total de entradas en terrestre_especies.csv | 24 |
| Entradas verificadas (V — >=2 fuentes concordantes) | 17 |
| Entradas con 1 fuente (P — probable) | 7 |
| Entradas estimadas (E — sin fuente directa) | 0 |
| Pares de interaccion en terrestre_interacciones.csv | 27 |
| Interacciones investigadas (fuente directa) | 18 |
| Interacciones derivadas (inferidas por heuristica) | 9 |
| Sitios en terrestre_sitios.csv | 10 |
| Fuentes unicas citadas (terrestre_fuentes.md) | >50 |

---

## Desglose V/P/E por Especie

| id | Estado | Razon |
|----|--------|-------|
| gallina_ponedora | V | FAO + livestocking.net + thepoultrysite + PMC |
| pollo_engorde | V | thepoultrysite + PMC9560488 + livestocking.net |
| gallina_criolla | P | LRRD-CIPAV + tandfonline-2023; datos productivos escasos |
| pavo | P | almanac + PSU extension; datos tropicales escasos |
| pato_pekin | V | agrodok33 + cornell + FAO-y4359e |
| pato_criollo | V | springer2007 + researchgate + a-z-animals |
| ganso | P | FAO-y4359e + springer-waterfowl; datos tropicales escasos |
| codorniz | V | PMC10113653 + springer-density + echocommunity |
| pintada_guinea | P | springer-book (acceso limitado) + naerls + britannica |
| vaca_lechera_holstein | V | FAO-GLEAM + scielo + frontiersin 2023 + waterfootprint |
| vaca_lechera_girolando | V | tandfonline-girolando + scielo + EMBRAPA referencia |
| vaca_carne_cebu | V | SciDirect-zebu + cattledaily + PMC11841269 + FAO |
| bufalo_agua | V | PMC8909038 + PMC10079919 + PMC7150070 |
| oveja_pelibuey | V | sciencedirect-pelibuey (2 articulos) + roysfarm |
| cabra_criolla | V | UF/IFAS + springer-dairy-goat + sciencedirect-LA |
| cerdo_tropical | V | FAO-pig-tropics + PMC11016694 + FAO-housing |
| cuy_cobayo | V | sciencedirect-review + cambridge + tandfonline |
| conejo | V | FAO-rabbit + ATTRA + ECHO + JAS-Oxford |
| caballo | P | permaculture-brazil + FAO equine; datos tropicales LA escasos |
| burro | V | lrrd-donkey + SciDirect-donkey + veterian-key |
| abeja_melif | V | PMC10568204 + PMC11066017 (2 articulos PMC) |
| abeja_stingless | P | annualreviews + britannica; produccion miel muy variable por especie |
| lombriz_eisenia | P | springer-eisenia + oregonstate; datos de densidad de carga estimados |
| tilapia_integrada | V | scialert-rice-fish + sciencedirect-tilapia + lrrd-tilapia |

---

## Vacíos y Limitaciones Conocidas

### Datos Estimados a nivel de campo
- Ninguna especie está marcada `E` (todas son `V` o `P`). En `lombriz_eisenia` (P), los campos `densidad_carga` (0.5 kg/m2) y `estiercol_kg_dia` son estimaciones de manejo típico; los datos de campo varían ampliamente según el sistema.

### Datos con Solo Una Fuente (P)
- **Gallina criolla / pollo criollo**: la literatura cientifica sobre productividad zootecnica es escasa; la mayoria de datos son cualitativos. La densidad de carga en traspatio es estimada.
- **Ganso doméstico en tropicos**: la mayoria de referencias son de sistemas temperados; los datos de adaptacion tropical son escasos.
- **Pavo criollo en tropicos latinoamericanos**: datos de consumo basados en referencias norteamericanas de traspatio; extrapolacion al tropico sin ajuste termico especifico.
- **Abeja sin aguijón (meliponas)**: produccion de miel muy variable segun especie (>600 spp.); sin un valor fijo confiable; se uso rango amplio.
- **Caballo en sistemas tropicales latinoamericanos**: datos de consumo de forraje basados en referencias temperadas ajustadas; falta literatura tropical especifica.
- **Pintada de guinea**: el libro de referencia principal (Springer) tiene acceso restringido; datos confirmados via fuentes secundarias (NAERLS, Britannica).

### Columnas con Mayor Proporcion de Estimados
- `estiercol_kg_dia`: en la mayoria de especies los valores son estimados (E) derivados de porcentaje del peso vivo o de referencias no directas. Excepcion: bovinos, porcinos y aves comerciales con datos FAO.
- `consumo_alimento_kg_dia` en sistemas extensivos (rumiantes): depende fuertemente de la calidad del forraje disponible; los valores representan promedios en pastizal tropical mejorado.
- `agua_l_dia`: los valores globales de FAO/Waterfootprint son promedios que pueden variar 2-3x segun temperatura y humedad relativa en tropico.
- `espacio_min_m2`: para rumiantes en pastizal el espacio real es la superficie del potrero divida entre animales; los valores en CSV representan el minimo de instalacion de manejo (corral/manga), no el area de pastoreo.

### Vacíos Taxonomicos/Productivos No Cubiertos
- **Ovino Blackbelly / Dorper tropicalizado**: se priorizó Pelibuey por ser la raza tropical dominante en Mexico/Centroamerica; Blackbelly documentado pero no incluido por limite de especies.
- **Capra nubia / Anglo-nubia tropical**: raza caprina tropical lechera documentada pero no incluida.
- **Cerdo criollo iberoamericano**: se uso cerdo tropical generico; existen ecotipos locales (Cuino Mexico, Zungo Colombia, Pelado Riosucio) con datos muy escasos.
- **Alpaca / llama**: relevantes para Andes pero fuera del foco tropical/subtropical humid del alcance.
- **Gallina de Cornish Cross**: especifica de broiler intensivo, cubierta bajo pollo_engorde.

### Limitaciones de Interacciones
- Las interacciones derivadas (procedencia = derivado) son inferencias logicas basadas en heuristicas ecologicas y productivas, no interacciones especificamente documentadas para el par exacto de especies.
- No se modelaron interacciones entre mas de 2 especies simultaneas (triadas); el AG debera calcular la sinergia total de un ensamblaje como suma de pares.
- Las interacciones hombre-animal (manejo, estres por manipulacion) no estan modeladas.

---

## Calidad General del Dataset

- **Rangos de temperatura** (temp_min_c, temp_max_c): verificados en >=2 fuentes para todas las especies, con excepcion de lombriz_eisenia (1 fuente directa).
- **Densidad de carga**: verificada para aves comerciales y bovinos; estimada para gallina criolla, ganso y burro en sistemas tropicales especificos.
- **Valor de mercado**: dato cualitativo ("medio", "alto") o con rango aproximado en USD; no refleja variaciones de precio locales en mercados latinoamericanos especificos.
- **Cobertura geografica**: la mayoria de fuentes cubren Mexico, Brasil, Colombia, Peru, Venezuela y Centroamerica; datos de Bolivia, Ecuador y Paraguay son escasos.
