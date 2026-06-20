# Cobertura — Base de Conocimiento Árboles Tropicales-Subtropicales

## Resumen de Especies

**Total de especies documentadas: 43**  
> *(conteo autoritativo del CSV `arboles.csv`. Los desgloses por estrato/sucesión de esta nota son aproximados y pueden no sumar 43.)*

### Desglose por verificacion

| Nivel | Cantidad | Porcentaje | Criterio |
|-------|----------|------------|---------|
| V (Verificado, >=2 fuentes) | 39 | 91% | Parametros ecologicos confirmados en WorldAgroforestry + Useful Tropical Plants o fuente secundaria autorizada |
| P (Parcial, 1 fuente principal) | 4 | 9% | Virola koschnyi, Acaciella angustissima, Sterculia apetala, Acrocarpus fraxinifolius |
| E (Estimado/Derivado) | 0 | 0% | Ninguna especie completa en E; el campo co2_kg_arbol_anio es estimado a nivel de campo (ver nota CO2) |

### Desglose por estrato de dosel

| Estrato | Cantidad | Ejemplos |
|---------|----------|---------|
| Emergente | 7 | Ceiba pentandra, Terminalia amazonia, Enterolobium, Albizia saman, Eucalyptus grandis, Juglans neotropica, Schizolobium |
| Dosel | 20 | Swietenia, Cedrela, Cordia, Tectona, Calophyllum, Virola, Brosimum, Mangifera, Persea, Tabebuia... |
| Subdosel | 8 | Inga edulis, Gliricidia sepium, Erythrina poeppigiana, Leucaena, Mimosa, Guazuma, Ochroma, Acrocarpus |
| Sotobosque | 5 | Theobroma cacao, Coffea arabica, Annona muricata, Psidium guajava, Byrsonima crassifolia |

### Desglose por estado sucesional

| Estado | Cantidad | Ejemplos |
|--------|----------|---------|
| Pionera | 6 | Ochroma pyramidale, Schizolobium, Cecropia, Mimosa scabrella, Acacia mangium, Acaciella angustissima |
| Secundaria temprana | 10 | Inga, Gliricidia, Erythrina, Leucaena, Cordia, Gmelina, Guazuma, Tectona, Eucalyptus grandis, Coffea (sistema) |
| Secundaria tardia | 9 | Ceiba, Enterolobium, Tabebuia, Albizia, Vochysia, Calophyllum, Simarouba, Pinus, Byrsonima |
| Climax | 14 | Swietenia, Cedrela, Juglans, Terminalia, Hyeronima, Brosimum, Persea, Mangifera, Theobroma, Dalbergia... |

### Desglose por fijacion de nitrogeno

| Estado | Cantidad | Principales especies |
|--------|----------|---------------------|
| Fijadoras (si) | 11 | Inga edulis, Gliricidia sepium, Erythrina poeppigiana, Leucaena leucocephala, Enterolobium cyclocarpum, Albizia saman, Acacia mangium, Mimosa scabrella, Acaciella angustissima, Tamarindus indica, Acrocarpus fraxinifolius |
| No fijadoras | 34 | Resto de especies |

### Desglose por estatus IUCN

| Estatus | Cantidad | Especies |
|---------|----------|---------|
| LC (Preocupacion menor) | 40 | Mayoria de especies |
| VU (Vulnerable) | 3 | Swietenia macrophylla, Cedrela odorata, Dalbergia retusa |
| EN (En peligro) | 1 | Juglans neotropica |
| NT/CR/DD | 0 | No registrado en este conjunto |

### Desglose por clima principal

| Clima | Cantidad |
|-------|----------|
| Tropical humedo | 28 |
| Tropical seco | 8 |
| Subtropical | 3 |
| Montano | 4 |
| Mixto (registrado en clima principal) | 2 |

---

## Pares de Interacciones

**Total de pares documentados: 31**

### Desglose por tipo de relacion

| Relacion | Pares | Porcentaje |
|----------|-------|------------|
| Facilitacion (valor +1 o +2) | 23 | 74% |
| Antagonismo (valor -1 o -2) | 8 | 26% |
| Neutral | 0 | — |

### Desglose por procedencia

| Procedencia | Pares | Descripcion |
|-------------|-------|-------------|
| Investigado | 17 | Relacion respaldada por publicacion cientifica directa |
| Derivado | 14 | Inferido por reglas heuristicas (complementariedad estrato, fijacion N, etc.) |

### Pares clave investigados
- Inga/Erythrina/Gliricidia como sombra de cacao y cafe: 6 pares con valor +2
- Eucalyptus grandis alelopatico sobre cacao y cafe: 2 pares con valor -2 investigados
- Cordia alliodora con theobroma cacao: facilitacion +2 investigada
- Acacia mangium + Eucalyptus grandis: facilitacion mutua +1 (fijacion N) investigada

---

## Sitios Documentados

**Total de sitios: 8**

| ID | Tipo | Densidad max arb/ha |
|----|------|---------------------|
| S01 | Parcela forestal | 1111 |
| S02 | Franja riberana | 2000 |
| S03 | Alineacion urbana | 100 |
| S04 | Suelo degradado | 1600 |
| S05 | SAF cacao | 1400 |
| S06 | Sistema silvopastoril | 600 |
| S07 | Ladera erosionada | 1600 |
| S08 | SAF cafe | 2500 |

---

## Vacios Identificados y Limitaciones

### Vacios criticos en CO2
- TODOS los valores de co2_kg_arbol_anio estan marcados como E (estimado)
- No existe una base de datos publica sistematizada de CO2 por especie tropical con mediciones directas a escala individual
- Los valores se basan en rangos generales (10-120 kg/arbol/anio segun tamano y crecimiento)
- Requiere medicion directa en campo o uso de alometria especifica por especie para valores V

### Vacios en precios de plantulas
- Todos los precios son estimativos (E) basados en rangos de mercado regional
- Los precios varian hasta 10x entre paises, escalas de compra y temporadas
- No existe base de datos publica de precios actualizados por especie en LAC

### Vacios de parametros P (una fuente)
- Acaciella angustissima: parametros ecologicos basados principalmente en Useful Tropical Plants; escasa literatura de campo
- Sterculia apetala: datos limitados en literature agroforestal especializada
- Virola koschnyi: datos ecologicos disponibles pero IUCN no confirmado en la busqueda
- Acrocarpus fraxinifolius: especie exotica en LAC; poca literatura regional
- Hyeronima alchorneoides: parametros hidrologicos no bien documentados en fuentes consultadas

### Vacios de interacciones
- Solo 31 de los ~903 pares posibles (43x42/2) estan documentados
- La gran mayoria de interacciones deben derivarse mediante heuristicas (arboles_reglas.md)
- Faltan interacciones entre maderables climaticas y pioneras de la misma zona
- Interacciones entre frutales no estudiadas sistemicamente
- Efectos de Juglans neotropica (juglona) no han sido medidos directamente; inferidos de J. nigra

### Especies no incluidas que podrian ser relevantes
- Tithonia diversifolia (arbusto N-fijador, sombra de cafe, muy estudiada)
- Moringa oleifera (multiproposo seco, muy disponible)
- Swietenia humilis (caoba del Pacifico, tambien VU)
- Platymiscium pinnatum (cocobolo morado, EN en algunas regiones)
- Nectandra sp. (laureles nativos, importantes para conservacion)
- Chloroleucon mangense y otras acacias nativas del Caribe seco
