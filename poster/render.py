"""Renderiza el poster BioNexo a PDF (60x90 cm, vectorial) + PNG de previsualizacion."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
HTML = (HERE / "bionexo_poster.html").as_uri()
PDF = HERE / "BioNexo_poster_60x90.pdf"
PNG = HERE / "BioNexo_poster_preview.png"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 2268, "height": 3402}, device_scale_factor=1)
    pg.goto(HTML, wait_until="networkidle")
    pg.evaluate("() => document.fonts.ready")
    pg.wait_for_timeout(500)
    # PDF vectorial a tamano fisico exacto (CSS @page = 600mm x 900mm)
    pg.pdf(path=str(PDF), prefer_css_page_size=True, print_background=True)
    # PNG de previsualizacion (raster 1:1 a 96dpi)
    pg.screenshot(path=str(PNG), full_page=True)
    b.close()

print("PDF:", PDF, PDF.stat().st_size // 1024, "KB")
print("PNG:", PNG, PNG.stat().st_size // 1024, "KB")
