"""Backend FastAPI que envuelve el motor multi-dominio (sin modificarlo).

Reutiliza `src/esquema.py`, `src/metricas.py` y `src/ga_acucosmos.py` para servir
metadatos por REST y transmitir el AG generacion a generacion por SSE. Correr desde
la raiz del repo:  ``uvicorn api.app:app --reload``.
"""
