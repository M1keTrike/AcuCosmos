---
type: modulo
status: activo
tags: [backend, api, sse, fastapi]
---
# Backend FastAPI

El backend expone el [[Motor_Algoritmo_Genetico]] mediante una API RESTful (pi/app.py).

## Características principales
- **Streaming (SSE)**: Permite enviar eventos Server-Sent Events (/api/run) para visualizar las generaciones en tiempo real sin bloquear el proceso principal.
- **Metadatos**: Endpoints para proveer catálogos, compatibilidades y detalles definidos en la [[Configuracion_Dominio]].

Es consumido principalmente por el [[Frontend_NextJS]].

**Relaciones**
- [[_Inicio_MOC]]
- [[Frontend_NextJS]]
- [[Motor_Algoritmo_Genetico]]
- [[Configuracion_Dominio]]
