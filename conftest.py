import os
import sys

# Asegura que la raíz del repo esté en sys.path para `import src...` / `import tests...`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Backend no interactivo para las pruebas (headless-safe).
import matplotlib  # noqa: E402
matplotlib.use("Agg")
