"""Genera el *golden output* de la Fase 0 (correr una vez; commitear los JSON).

Uso:  python -m tests.generar_golden
"""
from tests.golden_lib import ESCENARIOS, correr_escenario, guardar_golden, SEED


def main():
    print(f"Generando golden output (seed={SEED})...")
    for cfg in ESCENARIOS:
        print(f"  {cfg['nombre']} ...", end="", flush=True)
        data = correr_escenario(cfg)
        guardar_golden(cfg["nombre"], data)
        m = data["metricas"]
        print(f" F={data['f_final']:.4f}  n_sp={m['n_especies']}  "
              f"factible={m['factible']}")
    print("Listo: tests/golden/*.json")


if __name__ == "__main__":
    main()
