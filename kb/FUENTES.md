# FUENTES — consolidado por dominio y tipo de dato

Fuentes principales por dominio. Cada dominio tiene además un archivo detallado con todas las URL:
`plantas/plantas_fuentes.md`, `arboles/arboles_fuentes.md`, `fauna_acuicola/acuicola_fuentes.md`,
`fauna_terrestre/terrestre_fuentes.md`. Las claves cortas (p. ej. `FAO`, `FishBase`) son las que
aparecen en la columna `fuente` de los CSV.

---

## DOMINIO 1 — PLANTAS / JARDÍN

### Identidad y tolerancia ambiental
- Useful Tropical Plants Database — https://tropical.theferns.info/
- Plants For A Future (PFAF) — https://pfaf.org/
- NCSU Extension Gardener Plant Toolbox — https://plants.ces.ncsu.edu/
- ECHO Community (fichas tropicales) — https://www.echocommunity.org/
- FAO (agroecología, cultivos tropicales) — https://www.fao.org/ · https://www.fao.org/agroecology/database/detail/zh/c/1711829
- CABI Compendium — https://www.cabidigitallibrary.org/
- EMBRAPA — https://www.embrapa.br/ · INTA Argentina — https://www.argentina.gob.ar/inta

### Companion planting y compatibilidad (Cat. 3)
- Albahaca–tomate (señalización volátil) — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11263239/
- Tagetes–mosca blanca (limoneno) — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6396911/
- Milpa, complementariedad de raíces (three sisters) — https://pmc.ncbi.nlm.nih.gov/articles/PMC4416130/
- Tagetes como nematicida (revisión) — https://www.sciencedirect.com/science/article/abs/pii/S092913931000168X
- Fijación de N en Cajanus cajan (gandul) — https://link.springer.com/article/10.1007/s10457-026-01520-9
- Mucuna, fijación de N — https://cgspace.cgiar.org/items/45ab98f1-2fd1-4625-8e60-4ce3111afa7c
- Milpa en Guatemala (diversidad) — https://www.nature.com/articles/s41598-021-82784-2
- Alelopatía en huerto (girasol) — https://extension.psu.edu/allelopathy-in-the-home-garden

### Precios y disponibilidad (estimados)
- Contexto de mercado de semillas LatAm — https://www.statista.com/statistics/790164/seed-market-value-latin-america/
- Precios `precio_semilla_usd`: estimados (marcados `E`/notas) a partir de catálogos regionales.

---

## DOMINIO 2 — ÁRBOLES / BOSQUE

### Identidad, ecología y crecimiento
- World Agroforestry (ICRAF) — Agroforestree DB / Switchboard — https://apps.worldagroforestry.org/products/switchboard/
- Useful Tropical Plants — https://tropical.theferns.info/ · PFAF — https://pfaf.org/
- Winrock International Factnet (fijadoras de N) — https://winrock.org/
- CABI Compendium — https://www.cabidigitallibrary.org/ (Cordia, Gmelina, Samanea, Tabebuia…)
- CATIE (repositorio) — https://repositorio.catie.ac.cr/
- USDA Forest Service, Silvics — https://www.srs.fs.usda.gov/ · RNGR — https://rngr.net/
- FAO forestal — https://openknowledge.fao.org/

### Agroforestería y sombra (Cat. 3)
- Sombra de café/cacao (Inga, Erythrina, Gliricidia) — https://link.springer.com/article/10.1023/A:1005956528316
- Gliricidia, fijación de N con cacao — https://pmc.ncbi.nlm.nih.gov/articles/PMC10143777/
- Inga alley cropping (callejones) — https://rainforestsaver.org/how-to-and-the-science/inga-alley-cropping-manual/
- Silvopastoril con Leucaena — https://www.lrrd.org/lrrd32/4/murhu32057.html

### Alelopatía (Cat. 3)
- Eucalyptus (fenoles/terpenos) — https://link.springer.com/article/10.1007/s11676-023-01606-5 · https://www.sciencedirect.com/science/article/abs/pii/S0378112709004617
- Pinus (revisión) — https://www.scielo.cl/scielo.php?pid=S0718-58392020000300452&script=sci_arttext
- Juglans neotropica (juglona, inferida de J. nigra) — https://pfaf.org/User/Plant.aspx?LatinName=Juglans+neotropica

### Conservación (Cat. 6)
- IUCN Red List — https://www.iucnredlist.org/ (Swietenia VU, Cedrela VU, Juglans neotropica EN, Dalbergia retusa VU…)
- CITES (Swietenia, Apéndice II) — https://cites.org/eng/prog/mwg.php

### CO₂ y precios (estimados)
- `co2_kg_arbol_anio` **todos estimados** (rangos de literatura): p. ej. https://www.unm.edu/~jbrink/365/Documents/Calculating_tree_carbon.pdf
- Precios `precio_plantula_usd`: estimados por país/vivero (0.20–10 USD).

---

## DOMINIO 3 — FAUNA ACUÍCOLA

### Identidad y biología
- FishBase — https://fishbase.se / https://fishbase.org
- FAO — Biology of Major Cultivated Fishes / Pond Culture — https://www.fao.org/4/ac264e/ac264e01.htm · https://www.fao.org/4/ac264e/AC264E05.htm
- The Fish Site — Cultured Aquatic Species — https://thefishsite.com/articles/cultured-aquatic-species-silver-carp

### Tolerancia ambiental (temperatura, pH, OD, salinidad)
- Tilapia (límites térmicos/OD) — https://mweafish.com/aquaculture-articles/25-temperature-and-low-dissolved-oxygen-tolerances-for-tilapia.html · https://www.sciencedirect.com/science/article/pii/S0306456522000213
- Cyprinus carpio (3–35 °C, pH 6.5–9) — https://fishbase.org/summary/Cyprinus-carpio+carpio.html · https://www.tandfonline.com/doi/full/10.1080/09712119.2011.620269
- Cachama/tambaquí (pH 6–7.5, alta densidad) — https://www.fao.org/4/i1773s/i1773s.pdf · https://ve.scielo.org/scielo.php?script=sci_arttext&pid=S0798-72692011000200008
- Paiche/Arapaima (28–32 °C, respiración aérea) — http://www.iiap.org.pe/upload/publicacion/articmaryry.pdf
- Clarias gariepinus (8–35 °C, OD<1) — https://www.researchgate.net/publication/338385066
- Pangasius (pH 7.2–7.5, OD 5.7–6.2) — https://www.researchsquare.com/article/rs-3467660/v1

### Nicho trófico y policultivo (Cat. 3)
- FAO — reparto de nicho silver/bighead/grass/common — https://www.fao.org/4/ac264e/ac264e01.htm
- Indian major carp polyculture (regla 4:2:3:1) — https://www.globalseafood.org/advocate/carp-polyculture-in-india/ · https://www.globalseafood.org/advocate/a-review-of-indian-major-carp-species/
- Policultivo bocachico–tilapia (perifiton) — http://www.scielo.org.co/scielo.php?script=sci_arttext&pid=S0120-29522011000200002
- Macrobrachium + carpas/tilapia/bagre — https://www.sciencedirect.com/science/article/abs/pii/0044848686900803

### Densidad, capacidad y mercado
- FAO — tipos de estanque/jaula/raceway — https://www.fao.org/4/ac264e/AC264E05.htm
- Capacidad de carga 10–30 kg/m³ (semi-intensivo/intensivo): síntesis de fuentes de acuicultura.
- Precios `valor_mercado_usd_kg`: **estimaciones** de precio de granja en LatAm.

---

## DOMINIO 4 — FAUNA TERRESTRE

### Identidad y manejo
- FAO — Feeding pigs in the tropics — https://www.fao.org/4/w3647e/w3647e07.htm · Geese — https://www.fao.org/4/y4359e/y4359e0b.htm · Rabbits — https://www.fao.org/4/u4900t/u4900t0m.htm
- Agrodok 33 — Duck keeping in the tropics — https://journeytoforever.org/farm_library/AD33.pdf
- Cornell — Duck housing & management — https://www.vet.cornell.edu/animal-health-diagnostic-center/programs/duck-research-laboratory/duck-housing-and-management
- Codorniz tropical — https://pmc.ncbi.nlm.nih.gov/articles/PMC10113653/ · Pintada — https://naerls.gov.ng/wp-content/uploads/2022/11/The-Production-of-Guinea-Fowl-in-Nigeria.pdf
- Búfalo de agua (trópico de México) — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8909038/ · Girolando — https://www.tandfonline.com/doi/full/10.1080/1828051X.2017.1335180
- Feedipedia (alimentación animal) — https://www.feedipedia.org/

### Carga animal y capacidad (Cat. 4, 8)
- NRCS-USDA — Carrying capacity & stocking rates — https://www.nrcs.usda.gov/sites/default/files/2022-10/Determining%20Carry%20Capacity%20and%20Stocking%20Rates%20_ND.pdf
- Silvopastoril (beneficios y carga) — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8066609/ · https://link.springer.com/article/10.1007/s10457-024-01093-5

### Integración, sanidad y polinización (Cat. 3)
- Pastoreo mixto bovino/ovino (parásitos) — https://eu-cap-network.ec.europa.eu/projects/practice-abstracts/mixed-grazing-cattlesheep-reduce-parasite-infestation_en
- Riesgo influenza en granjas mixtas cerdo-aves — https://www.frontiersin.org/journals/veterinary-science/articles/10.3389/fvets.2023.1310303/full
- Tilapia en sistemas integrados (estanque-dique) — https://www.sciencedirect.com/science/article/abs/pii/S0044848611000676
- Abejas: densidad de colonias / pérdidas LatAm — https://pmc.ncbi.nlm.nih.gov/articles/PMC10568204/ · https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11066017/ · Meliponas — https://www.annualreviews.org/content/journals/10.1146/annurev-ento-120120-103938
- Vermicompost (Eisenia) — https://link.springer.com/article/10.1007/s40093-016-0119-5

### Mercado
- `valor_mercado` (cualitativo/USD): estimaciones; varían por mercado local.

---

## Nota de verificación
Para las especies marcadas `V`, los parámetros clave se contrastaron en ≥2 de las fuentes anteriores.
Las marcadas `P` se apoyan en una fuente cuantitativa principal; las `E` son estimaciones por analogía.
Los campos sistemáticamente estimados (CO₂ arbóreo, precios, estiércol) se señalan como tales en cada
dominio y NO deben tomarse como dato verificado de una fuente única.
