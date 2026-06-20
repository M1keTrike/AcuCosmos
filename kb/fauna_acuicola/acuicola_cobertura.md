# Reporte de cobertura — Dominio FAUNA ACUÍCOLA

## Resumen
- **40 especies** de policultivo de agua dulce (foco tropical/subtropical, con especies de uso global).
- **37 pares** de interacción documentados (19 investigados / 18 derivados por reglas).
- **9 sitios** (estanques de tierra, tanques revestidos/concreto/biofloc, jaula, raceway, RAS).

## Verificación de especies (campos clave: temp, pH, OD, densidad)
| nivel | nº | % | criterio |
|------|---:|---:|----------|
| V (≥2 fuentes) | 17 | 42.5% | parámetros contrastados en ≥2 fuentes (carpas chinas e indias núcleo, tilapia del Nilo, cachama negra/blanca, bocachico, Clarias, Pangasius, paiche, bagre de canal, camarón gigante) |
| P (1 fuente) | 22 | 55% | una fuente cuantitativa principal |
| E (estimado) | 1 | 2.5% | matrinxa (por analogía con yamú/Brycon) |

## Cobertura por grupo y nicho
- Grupos: carpa (12), nativo neotropical (8), bagre (5), tilapia (4), carácido (4), otro (4), crustáceo (3).
- Nichos tróficos representados: filtrador_plancton (3), herbívoro (3), detritívoro (5), iliófago (2), omnívoro (19), carnívoro (8) → cubre todos los gremios para que el AG arme ensamblajes complementarios.
- Estratos: fondo (17), columna (16), toda_la_columna (6), superficie (1) → permite repartir la columna de agua.
- Incluye especies con **respiración aérea** (Clarias, paiche, gurami, pejelagarto, pangasius) que relajan la restricción de oxígeno, y especies de **agua fría/altura** (trucha, pejerrey) para sitios subtropicales de altura.

## Metodología de compatibilidades
- Pares **investigados** (19): combinaciones documentadas en literatura (policultivo chino silver/bighead/grass/common; regla india 4:2:3:1 catla/rohu/mrigal; tilapia+camarón; tilapia+bocachico; cachama+bocachico; depredación paiche/tucunaré sobre tilapia; prawn+carpa).
- Pares **derivados** (18): aplicando H1–H5 de `acuicola_reglas.md` (mismo nicho→competencia; nichos distintos→complementariedad; carnívoro+presa→depredación; detritívoro/filtrador+balanceado→limpieza; rangos térmicos sin solape→incompatibilidad).
- Matriz **simétrica y sin contradicciones de signo** (validado: complementariedad>0, competencia/depredación<0; integridad referencial 100% de ids).

## Vacíos e incertidumbres conocidas
1. **Densidad** (`densidad_siembra_ind_m3`): valor representativo de cultivo semi-intensivo; varía mucho por sistema y fase. Tratar como referencia, no como óptimo cerrado.
2. **Precios** (`valor_mercado_usd_kg`): estimaciones de precio de granja en LatAm; no provienen de una serie de precios única. Usar como peso relativo, no como valor absoluto.
3. **FCA y peso de cosecha**: promedios típicos; dependen de dieta y manejo.
4. **Incompatibilidad térmica**: se modela mejor con las tolerancias (categoría 2) que con la matriz; sólo se incluyen 2 pares −2 como ilustración.
5. Sólo ~37 de los 780 pares posibles (C(40,2)) están en la tabla; el resto **debe derivarse** con las reglas en tiempo de ejecución del AG.
6. Especies marcadas `P` (p. ej. surubí, rhamdia, pejelagarto, lisa, pejerrey, matrinxa) tienen menor respaldo cuantitativo; verificar antes de uso productivo real.
