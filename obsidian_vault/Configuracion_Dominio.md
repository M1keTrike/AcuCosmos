---
type: configuracion
status: activo
tags: [yaml, configuracion, multidominio]
---
# Configuración de Dominio

La capa de definición de reglas del [[Framework_Multidominio]] reside en archivos YAML (config/*.yaml).

## Estructura YAML
- 
utas: Paths de los CSVs de conocimiento.
- 
asgos: Mapeo de variables genéticas a columnas de datos.
- estratos y ejes_ambientales: Definición del entorno físico y rangos.
- metricas: Referencias al registro definido en [[Metricas_y_Evaluacion]].
- 
estricciones y penalizaciones: Control de factibilidad (mortal, graduada, dinámica).
- gregacion: Método de optimización (NSGA-II, suma, Borda).

Aplica a todos los [[Dominios_Biologicos]].

**Relaciones**
- [[_Inicio_MOC]]
- [[Framework_Multidominio]]
- [[Metricas_y_Evaluacion]]
- [[Dominios_Biologicos]]
