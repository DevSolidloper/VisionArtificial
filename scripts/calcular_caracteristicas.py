"""Calcula las características de cada imagen del dataset para el análisis y la app.

Para cada imagen de dataset/etiquetas.csv mide, sobre una versión reducida a
256 px en su lado mayor: brillo y contraste, promedio de cada canal RGB,
brillo del fondo, nitidez, ruido, fracción de la imagen ocupada por la fruta,
color de la fruta en CIE L*a*b*, saturación, densidad de bordes e
histograma de tono. Las funciones están en app/vision.py.

Uso, desde la raíz del repositorio:
  python3 scripts/calcular_caracteristicas.py
Escribe dataset/caracteristicas.csv.
"""
import sys
import time
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))
import vision  # noqa: E402

DATASET = RAIZ / "dataset"


def main():
    etiquetas = pd.read_csv(DATASET / "etiquetas.csv")
    inicio = time.time()
    filas = []
    for i, archivo in enumerate(etiquetas["archivo"], 1):
        rgb = vision.leer(DATASET / archivo, vision.LADO_ANALISIS)
        filas.append({"archivo": archivo, **vision.caracteristicas(rgb)})
        if i % 500 == 0:
            print(f"{i} imágenes ({time.time() - inicio:.0f} s)")
    tabla = pd.DataFrame(filas).round(5)
    tabla.to_csv(DATASET / "caracteristicas.csv", index=False)
    print(f"Listo: {len(tabla)} imágenes y {tabla.shape[1] - 1} características en "
          f"{DATASET / 'caracteristicas.csv'} ({time.time() - inicio:.0f} s)")


if __name__ == "__main__":
    main()
