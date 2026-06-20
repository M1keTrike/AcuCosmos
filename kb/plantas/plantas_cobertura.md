# Cobertura de la Base de Conocimiento — Informe de Calidad

## Conteos Generales

| Indicador | Valor |
|-----------|-------|
| Total de especies en plantas.csv | 40 |
| Total de pares documentados en plantas_pares_documentados.csv | 31 |
| Total de sitios en plantas_sitios.csv | 9 |
| Archivos generados | 6 |

---

## Desglose por Verificación (columna `verificacion` en plantas.csv)

| Código | Significado | Especies | % |
|--------|-------------|----------|---|
| V | Verificado en ≥2 fuentes clave | 38 | 95% |
| P | Solo 1 fuente primaria | 1 | 2.5% |
| E | Estimado/derivado por analogía | 1 | 2.5% |

**Especies marcadas P (1 fuente)**:
- `ayote` (Cucurbita moschata): FAO e INTA Costa Rica consultados; datos de temperatura por analogía con C. pepo pero con ajuste a mayor tolerancia al calor húmedo.
- (`culantro` se reclasificó a V tras contrastar ECHO Community con literatura del Caribe.)

**Especies marcadas E (estimado)**:
- `quelites` (Amaranthus hybridus): datos de tolerancia por analogía con otros Amaranthus spp.; la especie exacta cultivada varía regionalmente en México/Guatemala.
- Precios de semilla (`precio_semilla_usd`): todos son estimados de mercado regional; columna es orientativa, no de catálogo.

---

## Desglose por Tipo de Planta

| Tipo | Cantidad de Especies |
|------|---------------------|
| hortaliza_fruto | 8 |
| hortaliza_hoja | 6 |
| raiz_tuberculo | 7 |
| leguminosa | 7 |
| graminea | 1 |
| aromatica | 7 |
| flor | 4 |
| abono_verde | 3 |

---

## Pares Documentados por Tipo de Relación

| Relación | Cantidad | % del total |
|----------|----------|-------------|
| sinergia | 23 | 74% |
| antagonismo | 8 | 26% |

**Pares con valor +2 (sinergia fuerte)**: 12 pares
**Pares con valor -2 (antagonismo fuerte)**: 1 par (girasol-frijol)

---

## Vacíos e Incertidumbres Conocidos

### Datos con Mayor Incertidumbre

1. **Precios de semilla**: Los valores en `precio_semilla_usd` son aproximaciones de mercado regional (Latinoamérica tropical). Los precios varían significativamente según país, temporada y proveedor. Se recomienda actualizar con catálogos locales antes de usar en función de costo.

2. **Zona USDA min/max**: Las zonas USDA son en origen para regiones templadas de Norteamérica. Para el trópico (zonas 10-13), los límites se basan en temperatura mínima pero no capturan la importancia de la temperatura MÁXIMA ni la humedad. Usar con cautela como criterio de filtro.

3. **`rendimiento_rel`**: Escala relativa 0-3 dentro de la base (no comparación a rendimiento agrícola comercial). Es una estimación cualitativa del potencial productivo para el huerto familiar.

4. **Alelopatía del epazote**: La inhibición por ascaridole está documentada pero la distancia exacta de efecto (>30 cm como umbral) es empírica; la concentración varía con temperatura y tipo de suelo.

5. **Efectividad nematicida de Tagetes y Caléndula**: Ambos requieren condiciones específicas (cultivo denso por ≥2 meses en el mismo suelo). En companion planting intercalado simultáneo la efectividad es significativamente menor. Los valores de compatibilidad en la base reflejan condiciones óptimas.

### Familias Botánicas No Cubiertas

- **Brassicaceae** (brócoli, col, coliflor): solo cubierta por rábano. Falta brócoli y repollo si el alcance se expande.
- **Allium** (cebolla, ajo, puerro): no incluidas en esta versión; el par clásico zanahoria-cebolla está omitido porque cebolla no está en la base.
- **Cucurbitaceae**: cubierta (calabaza, ayote, pepino) pero falta melón y sandía.

### Pares No Investigados (a Derivar por Heurísticas)

Con 40 especies hay 780 pares posibles. Los 31 documentados son los más relevantes y citados en la literatura. Los 749 pares restantes deben derivarse con las heurísticas H1-H5 de `plantas_reglas.md`. Los pares más críticos pendientes de investigación más profunda:

- Chaya + leguminosas (datos muy escasos)
- Malanga + otras plantas en sistemas de huerta (poco estudiado fuera de policultura caribeña)
- Quelites como alelopático o benéfico (literatura principalmente en español/mesoamericana no digitalizada)
- Culantro (E. foetidum) en companion planting vs. cilantro (C. sativum)

### Limitaciones del Diseño de Datos

- La columna `ciclo_dias` para perennes (chaya, gandul, romero, hierbabuena) refleja el tiempo a primera cosecha, no la duración del ciclo de vida.
- El campo `espaciado_cm` es una distancia simple (radio del círculo de influencia); para plantas de forma irregular (calabaza rastrera, mucuna trepadora) el espacio real requerido puede ser 2-3× mayor.
- Las columnas `valor_polinizador`, `valor_estetico` y `rendimiento_rel` son índices cualitativos (0-3) asignados por criterio del investigador con base en literatura; no deben usarse para comparaciones cuantitativas absolutas.

---

## Ultima Actualizacion

Fecha de compilación: 2026-06-19
Investigador: Agente de datos horticultura / Base de Conocimiento Companion Planting AG
Estado: Versión 1.0 — apta para alimentar el Algoritmo Genético de ensamblaje
