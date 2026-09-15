---
type: modulo
status: activo
tags: [evaluacion, algoritmos, pareto]
---
# Métricas y Evaluación

Subsistema (src/metricas.py y src/agregacion.py) que reemplaza y expande el antiguo cálculo de aptitud de [[Cromosoma_y_Aptitud]].

## Funcionalidades
- **Registro de Métricas**: Utiliza un decorador @metrica para inyectar cálculos dinámicamente según la [[Configuracion_Dominio]].
- **Agregación Multiobjetivo**:
  - Suma normalizada.
  - NSGA-II con dominancia con restricciones (Deb).
  - Borda count.
  - Esqueleto para NSGA-III.
- **Penalizaciones**: Soporta esquemas mortales, graduados y dinámicos para el manejo de individuos inviables sin destruir diversidad prematuramente.

Utilizado por el [[Motor_Algoritmo_Genetico]].

**Relaciones**
- [[_Inicio_MOC]]
- [[Cromosoma_y_Aptitud]]
- [[Configuracion_Dominio]]
- [[Motor_Algoritmo_Genetico]]
