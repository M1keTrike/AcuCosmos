---
type: modulo
status: estable
tags: [algoritmo-genetico, core, python]
---
# Motor Algoritmo Genético

El Motor de Algoritmo Genético es el corazón de AcuCosmos (src/ga_acucosmos.py y src/operadores.py). Se encarga de la evolución de la población buscando soluciones óptimas o el Frente de Pareto.

## Componentes y Flujo
- **Inicialización**: Utiliza distribución de Dirichlet.
- **Selección**: Selección por torneo.
- **Cruzamiento**: Cruza uniforme.
- **Mutación**: Cuatro tipos de operadores de mutación.
- **Elitismo**: Modelo (μ+λ) con Hall of Fame.
- **Anti-estancamiento**: Reinicio parcial tras cierto número de generaciones sin mejora.

El motor fue diseñado inicialmente para acuarios pero abstraído posteriormente en el [[Framework_Multidominio]].
Interactúa directamente con [[Cromosoma_y_Aptitud]] y [[Metricas_y_Evaluacion]].

**Relaciones**
- [[_Inicio_MOC]]
- [[Framework_Multidominio]]
- [[Cromosoma_y_Aptitud]]
- [[Metricas_y_Evaluacion]]
