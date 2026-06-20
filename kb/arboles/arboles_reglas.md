# Reglas del Sistema — Base de Conocimiento Árboles Tropicales-Subtropicales

## A. Escala de Valor de Interacción (-2 a +2)

| Valor | Significado | Descripción práctica |
|-------|-------------|---------------------|
| +2 | Facilitación fuerte | Beneficio demostrado, mecanismo claro, múltiples fuentes. Ej.: Inga/Erythrina como sombra de cacao. |
| +1 | Facilitación moderada | Beneficio probable o en condiciones específicas. Ej.: complementariedad de estrato derivada. |
| 0  | Neutral | Sin interacción significativa conocida o estudiada. |
| -1 | Antagonismo leve | Competencia o inhibición moderada; manejable con distanciamiento o manejo. |
| -2 | Antagonismo fuerte | Incompatibilidad documentada; daño significativo. Ej.: eucalipto/pino sobre sotobosque sensible. |

## B. Heurísticas de Derivación de Interacciones

Las siguientes reglas permiten al Algoritmo Genético inferir interacciones para pares no investigados directamente:

### B1. Fijadora de N + Especie exigente o pionera → Facilitación (+1 o +2)
- Si `especie_a.fija_nitrogeno == "si"` AND `especie_b.estado_sucesional IN (pionera, secundaria_temprana)` → `relacion = facilitacion; valor = +1; mecanismo = fijacion_N`
- Si `especie_a.fija_nitrogeno == "si"` AND `especie_b.uso CONTAINS "madera"` AND `especie_b.tasa_crecimiento == "rapida"` → `valor = +2`

### B2. Pionera heliófila bajo dosel cerrado → Antagonismo (excepto establecimiento)
- Si `especie_a.tolerancia_sombra == 0` AND `especie_b.estrato_dosel == "emergente"` AND `fase_sucesional == "establecida"` → `relacion = antagonismo; valor = -1; mecanismo = competencia_luz`
- Excepción: Si `fase_sucesional == "establecimiento"` (primeros 2 años) → relación puede ser neutral o positiva (nodriza)

### B3. Sotobosque + Emergente → Complementariedad de estrato (+1)
- Si `especie_a.estrato_dosel == "sotobosque"` AND `especie_b.estrato_dosel == "emergente"` → `relacion = facilitacion; valor = +1; mecanismo = complementariedad_estrato`
- Si `especie_a.tolerancia_sombra >= 2` → aumentar `valor` a +2 (especie muy adaptada a sombra)

### B4. Alelopáticas → Antagonismo con sotobosque sensible
- Si `especie_a.id IN (eucalyptus_grandis, pinus_oocarpa, juglans_neotropica)` AND `especie_b.estrato_dosel IN (sotobosque, subdosel)` AND `especie_b.tolerancia_sombra <= 1` → `relacion = antagonismo; valor = -2; mecanismo = alelopatia`
- Regla suavizada: Si `especie_b.tolerancia_sequia == "alta"` (especie más robusta) → `valor = -1`
- Excepción: Acacia mangium + Eucalyptus → facilitacion (+1): Acacia fija N que eucalipto usa; interacción documentada positiva.

### B5. Misma demanda hídrica elevada en sitio seco → Competencia de agua (-1)
- Si `especie_a.tolerancia_sequia == "baja"` AND `especie_b.tolerancia_sequia == "baja"` AND `sitio.precip_media < 1200` → `relacion = antagonismo; valor = -1; mecanismo = competencia_agua`
- Agravar a -2 si `especie_a.sistema_raiz == especie_b.sistema_raiz == "profundo"` (misma zona de extracción)

### B6. Nodriza temporal para especies clímax en restauración
- Si `especie_a.estado_sucesional == "pionera"` AND `especie_b.estado_sucesional == "climax"` AND `especie_b.tolerancia_sombra >= 1` → `relacion = facilitacion; valor = +1; mecanismo = nodriza_sombra; procedencia = derivado`

### B7. Comparte plaga o enfermedad
- Si `especie_a.familia == especie_b.familia` AND ambas son hospederas conocidas de una plaga → `relacion = antagonismo; valor = -1; mecanismo = comparte_plaga`
- Caso documentado: Swietenia + Cedrela (ambas Meliaceae; comparten Hypsipyla grandella)

### B8. Especie de sombra N-fijadora + Fruto o cultivo bajo dosel → Facilitación (+2)
- Si `especie_a.fija_nitrogeno == "si"` AND `especie_a.tolerancia_sombra >= 1` AND `especie_b.uso CONTAINS "fruto"` AND `especie_b.tolerancia_sombra >= 2` → `relacion = facilitacion; valor = +2; mecanismo = nodriza_sombra;fijacion_N`

## C. Modelo CARGA vs CAPACIDAD del Sitio

### C1. Verificación de densidad y solape de copas
```
carga_copas_m2 = SUM(π × (diam_copa_m/2)² para cada árbol en parcela)
area_sitio_m2 = superficie_ha × 10000
indice_solape = carga_copas_m2 / area_sitio_m2

Si indice_solape > 1.2: SOBRECARGA → reducir densidad o usar especies de copa pequeña
Si indice_solape entre 0.6-1.2: ÓPTIMO para sistemas agroforestales de sombra
Si indice_solape < 0.4: SUBCARGA → puede tolerar más individuos o elegir copas más amplias
```

### C2. Verificación hídrica simplificada
```
demanda_hidrica_estimada_mm = SUM(especie.evapotranspiración_relativa × densidad_ha) / 1000
si especie.tolerancia_sequia == "baja": ET_relativa = 3
si especie.tolerancia_sequia == "media": ET_relativa = 2
si especie.tolerancia_sequia == "alta": ET_relativa = 1

balance_hidrico = sitio.precip_min_mm - demanda_hidrica_estimada_mm
Si balance_hidrico < 0: RIESGO DE ESTRÉS HÍDRICO en época seca → ajustar especies o densidad
```

### C3. Restricciones de pH y suelo
- Cada especie tiene `ph_min` y `ph_max`; el pH del sitio debe caer dentro del rango
- Si `sitio.suelo` incluye "anegado" → excluir especies con `sistema_raiz == "profundo"` sin tolerancia a inundación
- Si `sitio.suelo` incluye "degradado" → priorizar fijadoras de N y pioneras

### C4. Restricción altitudinal (USDA Zone)
- `zona_usda_min <= zona_sitio <= zona_usda_max` para incluir la especie
- Equivalencia aproximada: Zona 10 = tropical húmedo; Zona 9 = subtropical; Zona 8 = templado-cálido; Zona 7 = templado

## D. Mapeo al Algoritmo Genético — 9 Categorías

| Categoría AG | Campo(s) en arboles.csv | Lógica de uso |
|---|---|---|
| 1. Identidad | `id`, `nombre_cientifico`, `nombre_comun`, `familia` | Cada gen del AG representa una especie identificada |
| 2. Aptitud climática | `clima`, `temp_min_c`, `temp_max_c`, `precip_min_mm`, `precip_max_mm`, `zona_usda_min`, `zona_usda_max` | Función de fitness: penalizar si el sitio cae fuera del rango |
| 3. Capacidad de sitio | `ph_min`, `ph_max`, `sistema_raiz`, `tolerancia_sequia` | Restricción dura vs. suelo/hidrología del sitio (arboles_sitios.csv) |
| 4. Estructura forestal | `estrato_dosel`, `altura_madura_m_min`, `altura_madura_m_max`, `diam_copa_m`, `estado_sucesional` | Distribución de estratos; modelo CARGA (sección C1); sucesión temporal |
| 5. Servicios ecosistémicos | `fija_nitrogeno`, `co2_kg_arbol_anio`, `valor_biodiversidad`, `uso` | Maximizar fijación N + secuestro C + biodiversidad simultáneamente |
| 6. Interacciones | `arboles_interacciones.csv` completo | Matriz de pares: sum(valor_ij × presencia_i × presencia_j) → penalizar antagonismos |
| 7. Factibilidad económica | `precio_plantula_usd`, `disponibilidad`, `densidad_arboles_ha` | Costo mínimo de establecimiento; filtrar por disponibilidad local |
| 8. Conservación | `estatus_iucn` | Bonificar EN/VU en programas de restauración; penalizar invasoras |
| 9. Compatibilidad temporal | `tasa_crecimiento`, `estado_sucesional`, `tolerancia_sombra` | Secuenciar etapas: pioneras → secundarias → clímax según fase del proyecto |

### D.1 Función de fitness sugerida para el AG
```
fitness = w1×(aptitud_climatica_score) 
        + w2×(score_servicios_ecosistemicos)
        + w3×(score_interacciones_netas)
        - w4×(penalizacion_solape_copa)
        - w5×(penalizacion_estres_hidrico)
        + w6×(bonus_iucn)
        - w7×(costo_plantacion_normalizado)

donde w1..w7 son pesos ajustables por el operador del AG.
```
