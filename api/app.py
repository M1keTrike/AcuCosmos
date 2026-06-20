"""App FastAPI: REST de metadatos + SSE para correr el AG en vivo.

Correr desde la raiz del repo:  ``uvicorn api.app:app --reload``  (puerto 8000).
El frontend Next.js (puerto 3000) lo consume por HTTP + EventSource.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from api import servicio, streaming

app = FastAPI(title="AcuCosmos — API multi-dominio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # dev local; restringir en produccion
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/salud")
def salud():
    return {"ok": True, "dominios": servicio.lista_ids()}


@app.get("/api/dominios")
def get_dominios():
    return servicio.dominios()


def _verifica(dom: str):
    if dom not in servicio.lista_ids():
        raise HTTPException(status_code=404, detail=f"dominio desconocido: {dom}")


@app.get("/api/dominios/{dom}/escenarios")
def get_escenarios(dom: str):
    _verifica(dom)
    return servicio.escenarios(dom)


@app.get("/api/dominios/{dom}/catalogo")
def get_catalogo(dom: str):
    _verifica(dom)
    return servicio.catalogo(dom)


@app.get("/api/dominios/{dom}/kappa")
def get_kappa(dom: str):
    _verifica(dom)
    return servicio.kappa(dom)


@app.get("/api/run")
async def get_run(
    dom: str = Query(...),
    escenario: str | None = Query(None),
    seed: int | None = Query(None),
    generaciones: int = Query(120, ge=10, le=400),
    poblacion: int = Query(60, ge=20, le=200),
):
    _verifica(dom)
    return EventSourceResponse(
        streaming.stream_run(dom, escenario, seed, generaciones, poblacion)
    )
