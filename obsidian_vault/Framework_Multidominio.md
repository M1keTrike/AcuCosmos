---
type: arquitectura
status: activo
tags: [patrones, refactor, framework]
---
# Framework Multidominio

AcuCosmos evolucionó de un optimizador de acuarios a un framework genérico para **ensamblajes biológicos**.

## Patrones de Diseño
Utiliza el patrón **Strategy + Registry** (inspirado en DEAP y GoF) aislando la lógica del [[Motor_Algoritmo_Genetico]] de la capa de dominio. 

## Componentes
- src/esquema.py: Validación y carga del [[Configuracion_Dominio]].
- src/metricas.py y src/agregacion.py: Abstracción descrita en [[Metricas_y_Evaluacion]].
- src/heuristicas.py: Manejo de reglas y compatibilidades dispersas/densas.

Se encarga de procesar los [[Dominios_Biologicos]] inyectando el comportamiento correcto en tiempo de ejecución.

**Relaciones**
- [[_Inicio_MOC]]
- [[Motor_Algoritmo_Genetico]]
- [[Configuracion_Dominio]]
- [[Metricas_y_Evaluacion]]
- [[Dominios_Biologicos]]
