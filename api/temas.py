"""Metadatos de TEMA por dominio (presentacion) + mapeo categoria -> color/forma.

La logica de "que icono/color le toca a cada especie" vive aqui (una sola vez); el
frontend solo renderiza lo que el backend ya resolvio. Espejo ligero en
`web/lib/themes.ts` (solo lo puramente visual: gradientes de escena).
"""
from __future__ import annotations

# Paleta categorica estable (se reparte por orden de aparicion del grupo).
PALETA = [
    "#ef4444", "#f59e0b", "#eab308", "#84cc16", "#22c55e", "#14b8a6",
    "#06b6d4", "#3b82f6", "#8b5cf6", "#d946ef", "#ec4899", "#f43f5e",
    "#fb923c", "#a3e635", "#2dd4bf", "#60a5fa",
]

# Un tema por dominio. `forma` = silueta que dibuja el canvas para sus criaturas.
TEMAS = {
    "peces_ornamental": {
        "etiqueta": "Acuario ornamental",
        "emoji": "\U0001F420",                # 🐠
        "descripcion": "Disena un acuario comunitario estetico y saludable.",
        "acento": "#38bdf8", "acento2": "#22d3ee",
        "fondo": "#04293f", "fondo2": "#0a3a5a",
        "forma": "pez",
        "grupo_col": "grupo_cromatico",
        "grupo_etiqueta_col": "grupo_cromatico_nombre",
        "tamano_col": "tamano_max_cm",
        "estrato_etiquetas": {"1": "Fondo", "2": "Medio", "3": "Superficie"},
        # color semantico por nombre del grupo cromatico (el pez se ve como su nombre).
        "colores_etiqueta": {
            "Azules/Púrpuras": "#6366f1",
            "Rojos/Naranjas": "#ef4444",
            "Negros/Oscuros": "#475569",
            "Multicolor/Iridiscentes": "#e879f9",
            "Plateados/Grises": "#cbd5e1",
            "Amarillos/Dorados": "#facc15",
            "Blancos/Albinos": "#f1f5f9",
            "Rayados/Barrados": "#fb923c",
            "Verdes": "#22c55e",
        },
    },
    "fauna_acuicola": {
        "etiqueta": "Policultivo acuicola",
        "emoji": "\U0001F41F",                # 🐟
        "descripcion": "Optimiza un policultivo de agua dulce productivo.",
        "acento": "#2dd4bf", "acento2": "#34d399",
        "fondo": "#053b34", "fondo2": "#0a5048",
        "forma": "pez",
        "grupo_col": "grupo",
        "tamano_col": "peso_cosecha_g",
        "estrato_etiquetas": {"toda_la_columna": "Toda la columna"},
    },
    "plantas_jardin": {
        "etiqueta": "Huerto / policultivo",
        "emoji": "\U0001F331",                # 🌱
        "descripcion": "Compon un huerto con sinergias de companion planting.",
        "acento": "#84cc16", "acento2": "#fbbf24",
        "fondo": "#1a2e05", "fondo2": "#2c4a0a",
        "forma": "planta",
        "grupo_col": "tipo",
        "tamano_col": "altura_cm_max",
        "estrato_etiquetas": {},
    },
    "arboles_bosque": {
        "etiqueta": "Bosque / agroforesteria",
        "emoji": "\U0001F333",                # 🌳
        "descripcion": "Reforesta maximizando CO2 y biodiversidad.",
        "acento": "#22c55e", "acento2": "#65a30d",
        "fondo": "#052e16", "fondo2": "#0a3d20",
        "forma": "arbol",
        "grupo_col": "uso",
        "grupo_split": ";",
        "tamano_col": "altura_madura_m_max",
        "estrato_etiquetas": {},
    },
    "fauna_terrestre": {
        "etiqueta": "Granja integrada",
        "emoji": "\U0001F404",                # 🐄
        "descripcion": "Integra animales de granja por gremios complementarios.",
        "acento": "#f59e0b", "acento2": "#fb923c",
        "fondo": "#3a2206", "fondo2": "#52310a",
        "forma": "animal",
        "grupo_col": "grupo",
        "tamano_col": "espacio_min_m2",
        "estrato_etiquetas": {},
    },
}


def tema(dom: str) -> dict:
    if dom not in TEMAS:
        # tema neutro por si aparece un dominio nuevo sin entrada explicita
        return {
            "etiqueta": dom, "emoji": "\U0001F9EC", "descripcion": "",
            "acento": "#38bdf8", "acento2": "#22d3ee",
            "fondo": "#0f172a", "fondo2": "#1e293b",
            "forma": "pez", "grupo_col": None, "tamano_col": None,
            "estrato_etiquetas": {},
        }
    return TEMAS[dom]


def valor_grupo(t: dict, valor) -> str:
    """Normaliza el valor de la columna de grupo (toma primer token si hay split)."""
    s = "" if valor is None else str(valor).strip()
    sep = t.get("grupo_split")
    if sep and sep in s:
        s = s.split(sep)[0].strip()
    return s


def asignar_colores(valores_unicos):
    """valor_de_grupo -> color, estable por orden de aparicion."""
    return {v: PALETA[i % len(PALETA)] for i, v in enumerate(valores_unicos)}


def asignar_colores_tema(t: dict, valores_unicos, etiquetas: dict):
    """Como asignar_colores, pero si el tema declara `colores_etiqueta` usa el color
    semantico por etiqueta (p.ej. peces: el pez se ve como su grupo cromatico)."""
    semantico = t.get("colores_etiqueta")
    if not semantico:
        return asignar_colores(valores_unicos)
    out = {}
    for i, v in enumerate(valores_unicos):
        out[v] = semantico.get(etiquetas.get(v, ""), PALETA[i % len(PALETA)])
    return out
