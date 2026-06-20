# Reglas del Algoritmo Genético — Base de Conocimiento Fauna Terrestre

## (a) Escala de Valor de Interacciones

| Valor | Categoria | Descripcion |
|-------|-----------|-------------|
| +2 | Sinergia fuerte | Beneficio mutuo documentado y cuantificado (ej. pastoreo mixto bovino-ovino reduce parasitos GI en ambas especies; patos fertilizan estanque de tilapia) |
| +1 | Sinergia moderada | Beneficio documentado pero unidireccional o de menor magnitud (ej. gallinas tras bovinos controlan moscas; abejas polinizan pastizal) |
| 0 | Neutral | Sin interaccion significativa documentada o interacciones que se compensan |
| -1 | Antagonismo leve | Competencia por recurso o riesgo sanitario moderado (ej. caballo compite con bovino por pasto de calidad) |
| -2 | Antagonismo fuerte | Riesgo sanitario severo o competencia irreconciliable (ej. cerdo + aves en contacto directo = riesgo influenza; mezcla de aves de distintos origenes = riesgo Newcastle/Marek) |

---

## (b) Heurísticas de Composición

### H1: Complementariedad de Estrato (sinergia por nicho diferenciado)
**Regla:** Si especie_A usa `estrato = pasto_bajo` Y especie_B usa `estrato = arbustivo_ramoneo`, entonces asignar `relacion = sinergia`, `valor >= +1`.

- Mecanismo: `complementariedad_estrato_pasto`
- Ejemplo: vaca_carne_cebu (pasto_bajo) + cabra_criolla (arbustivo_ramoneo) → valor +2
- Ejemplo: vaca_carne_cebu (pasto_bajo) + oveja_pelibuey (pasto_bajo) → sinergia +2 por parasiticidad cruzada, pero monitorear sobrecarga

**Advertencia de sobrecarga:** Si dos especies comparten el mismo estrato (`pasto_bajo`) Y la suma de UA supera la `capacidad_carga` del sitio → degradar valor a antagonismo (-1) por `competencia_pasto`.

### H2: Secuencia Temporal Aves–Rumiantes (sinergia sanitaria por rotacion)
**Regla:** Si especie_A tiene `grupo = rumiante` Y especie_B tiene `grupo = ave` Y especie_B tiene `nicho = forrajeo_suelo`, entonces en rotacion (B sigue a A con 3-4 dias de desfase) → `relacion = sinergia`, `valor = +2`.

- Mecanismo: `rotacion_aves_tras_ganado`
- Ejemplo: vaca_carne_cebu → (3-4 dias) → gallina_criolla → reduccion larvas de mosca y strongylidos en estiercol
- **Condicion:** La sinergia aplica en secuencia temporal, NO en copastura simultanea permanente. En copastura permanente el valor se degrada a +1.

### H3: Riesgo Sanitario por Contacto Cerdo-Aves
**Regla:** Si especie_A tiene `id = cerdo_tropical` Y especie_B tiene `grupo = ave`, entonces `relacion = antagonismo`.
- Si mismo corral/zona contigua: `valor = -2` (riesgo influenza A recombinante)
- Si distancia >50 m y sin contacto directo: `valor = -1`
- Mecanismo: `riesgo_sanitario_compartido`

### H4: Riesgo Sanitario Inter-Aves de Distinto Origen
**Regla:** Si especie_A y especie_B ambas tienen `grupo = ave` Y son de distinto `raza_tipo` (comercial vs criollo, o de distintas procedencias), entonces `relacion = antagonismo`, `valor = -1`.
- Mecanismo: `riesgo_sanitario_compartido`
- Justificacion: Newcastle, Marek, bronquitis infecciosa; mayor riesgo en mezcla de aves comerciales con aves locales sin vacunar

### H5: Polinizadores — Sinergia Generalizada con Floración
**Regla:** Si especie_A tiene `grupo = polinizador` Y la finca contiene cultivos con floración o praderas de leguminosas forrajeras → `relacion = sinergia`, `valor = +1` con cualquier otra especie de la finca (indirecto).
- Mecanismo: `polinizacion`
- La distancia optima de colmenas a cultivos: 0-2 km
- Densidad optima: 5-10 colmenas/ha en zonas de alta produccion floral

### H6: Reciclaje de Estiércol — Cierre del Ciclo
**Regla:** Si especie_A produce estiercol (`estiercol_kg_dia > 0`) Y especie_B tiene `aporte_principal` que incluye `reciclaje_residuos` (lombrices, tilapia via fertilizacion de estanque), entonces `relacion = sinergia`, `valor = +2`.
- Mecanismo: `reciclaje_estiercol`
- Ejemplo: cerdo_tropical → lombriz_eisenia (+2); gallina_ponedora → lombriz_eisenia (+1)

### H7: Control de Plagas — Aves de Guinea y Patos en Pastizal con Ganado
**Regla:** Si especie_A tiene `aporte_principal` que incluye `control_plagas` Y especie_B tiene `grupo = rumiante`, entonces `relacion = sinergia`, `valor = +2`.
- Mecanismo: `control_parasitos_pastoreo_mixto`
- Pintadas consumen garrapatas en el cuerpo del ganado y en el suelo

---

## (c) Modelo de Carga vs Capacidad

### Unidad Animal (UA) — Tabla de Conversión

| Especie | Peso Referencia (kg) | Factor UA |
|---------|---------------------|-----------|
| Bovino adulto (referencia) | 450 | 1.00 |
| Búfalo de agua | 550 | 1.22 |
| Caballo | 500 | 1.11 |
| Burro | 250 | 0.56 |
| Oveja Pelibuey | 45 | 0.10 |
| Cabra criolla | 35 | 0.08 |
| Cerdo adulto | 80 | 0.18 |
| Gallina adulta | 2 | 0.004 |
| Pato adulto | 3 | 0.007 |
| Ganso adulto | 6 | 0.013 |
| Pavo adulto | 8 | 0.018 |
| Codorniz | 0.15 | 0.0003 |
| Cuy | 1.0 | 0.002 |
| Conejo adulto | 3.5 | 0.008 |

> Referencia base: 1 UA = bovino de 450 kg (NRCS-USDA; FAO Chapter 5 livestock systems)

### Regla de Carga Total en Potrero
```
Carga_total_UA = SUM(n_animales_i × factor_UA_i)
Ratio_carga = Carga_total_UA / (superficie_ha × capacidad_carga_UA_por_ha)

Si Ratio_carga <= 0.80 → VERDE (carga segura)
Si 0.80 < Ratio_carga <= 1.00 → AMARILLO (carga al limite, monitorear)
Si Ratio_carga > 1.00 → ROJO (sobrecarga; penalizar fitness del ensamblaje)
```

### Conversión Aves (densidad/m2 a UA/ha)
Para gallinero de 100 m2 con 700 gallinas:
- No aplica UA/ha de pastizal: usar densidad_carga en aves/m2
- Para integrar en balance de finca: peso vivo total / 450 = UA equivalente

### Capacidades de Referencia por Sitio
| Sitio | Capacidad de Carga |
|-------|-------------------|
| Potrero nativo tropical | 0.5–0.8 UA/ha |
| Potrero mejorado (Brachiaria/Panicum) | 1.0–2.5 UA/ha |
| Sistema silvopastoral intensivo | 2.0–6.0 UA/ha |
| Gallinero intensivo | 7–10 aves/m2 |
| Gallinero tropical (con calor) | 5–7 aves/m2 |
| Chiquero confinamiento | 1.5–2.5 m2/cerdo adulto |
| Conejera | 0.5–1.0 m2/reproductora |

---

## (d) Mapeo de Archivos a las 9 Categorías del AG

| Categoria AG | Archivo | Columnas Clave |
|-------------|---------|----------------|
| 1. Identidad de especie/raza | terrestre_especies.csv | id, nombre_cientifico, nombre_comun, grupo, raza_tipo |
| 2. Adaptacion climatica | terrestre_especies.csv | clima_tol, temp_min_c, temp_max_c |
| 3. Nicho y estrato | terrestre_especies.csv | nicho, estrato |
| 4. Densidad y carga animal | terrestre_especies.csv + terrestre_sitios.csv | densidad_carga, unidad_carga, capacidad_carga |
| 5. Consumo (alimento y agua) | terrestre_especies.csv | consumo_alimento_kg_dia, agua_l_dia |
| 6. Servicios ecosistemicos y aporte | terrestre_especies.csv | aporte_principal, estiercol_kg_dia |
| 7. Produccion y valor | terrestre_especies.csv | producto, rendimiento_rel, valor_mercado |
| 8. Interacciones entre especies | terrestre_interacciones.csv | especie_a, especie_b, relacion, valor, mecanismo |
| 9. Infraestructura y sitio | terrestre_sitios.csv | tipo, infraestructura, costo_usd |

### Función de Fitness Sugerida para el AG
```
Fitness(ensamblaje) =
  + SUM(rendimiento_rel_i × valor_mercado_i)   // produccion
  + SUM(valor_ij para cada par i,j)            // sinergia entre especies
  - penalizacion_sobrecarga                    // carga > capacidad
  - penalizacion_riesgo_sanitario              // pares con valor <= -2
  + bonus_servicios_ecosistemicos              // polinizacion, control plagas, reciclaje
  - costo_infraestructura / factor_escala      // viabilidad economica
```
