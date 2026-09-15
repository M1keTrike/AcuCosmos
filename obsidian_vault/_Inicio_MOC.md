---
type: moc
status: activo
tags: [acucosmos, arquitectura, moc]
---
# AcuCosmos - Map of Content (MOC)

Bienvenido al Grafo de Conocimiento de AcuCosmos, un sistema de optimización multiobjetivo mediante Algoritmos Genéticos para el diseño de acuarios y otros ecosistemas biológicos.

## 🏗️ Arquitectura Principal
- [[Motor_Algoritmo_Genetico]]: El núcleo del sistema, implementado desde cero en Python.
- [[Framework_Multidominio]]: La extensión que convierte el sistema en una plataforma genérica mediante patrón Strategy y Registry.
- [[Backend_FastAPI]]: Interfaz REST y Streaming (SSE) para comunicación en tiempo real.
- [[Frontend_NextJS]]: Interfaz de usuario web interactiva.

## 🧬 Modelos de Datos y Lógica
- [[Cromosoma_y_Aptitud]]: Representación de individuos y cálculo escalar de aptitud (versión original).
- [[Metricas_y_Evaluacion]]: Sistema de evaluación genérica y agregación de objetivos (NSGA-II, Borda).
- [[Configuracion_Dominio]]: Esquema YAML que define las reglas de cada dominio.

## 🌍 Dominios y Conocimiento
- [[Dominios_Biologicos]]: Los cinco dominios soportados (Peces, Plantas, Árboles, Acuícola, Terrestre).

**Relaciones**
- [[Motor_Algoritmo_Genetico]]
- [[Framework_Multidominio]]
- [[Backend_FastAPI]]
- [[Frontend_NextJS]]
- [[Cromosoma_y_Aptitud]]
- [[Metricas_y_Evaluacion]]
- [[Configuracion_Dominio]]
- [[Dominios_Biologicos]]
