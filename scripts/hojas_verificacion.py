"""Genera hojas para verificar a simple vista las imágenes excluidas del dataset.

- docs/verificacion/duplicados_<fruta>.jpg: cada duplicado excluido junto a la
  imagen original que sí quedó, con sus nombres originales y una comprobación
  de que sus píxeles son idénticos.
- docs/verificacion/banano_sano_stock.jpg: las fotos de stock de banano sano
  excluidas, rotadas o volteadas y sin su imagen original.
- docs/verificacion/fresas_excluidas.jpg: las fotos propias de fresa que no
  entraron, agrupadas por motivo y con sus etiquetas.

Lee las imágenes de las carpetas originales del Drive (no las del dataset).
Uso:
  python3 scripts/hojas_verificacion.py --origen "<carpeta 1>" "<carpeta 2>" "<carpeta 3>"
"""
import argparse
import os
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "docs" / "verificacion"
LADO = 150
PREFIJO = "Patologias de Frutas en Postcocecha/"


def fuente(t):
    for f in ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(f):
            return ImageFont.truetype(f, t)
    return ImageFont.load_default()


F_TXT, F_TIT = fuente(12), fuente(20)


def ubicar(origenes, ruta_original):
    """Encuentra el archivo original en alguna de las carpetas descargadas del Drive."""
    rel = unicodedata.normalize("NFC", ruta_original[len(PREFIJO):])
    for o in origenes:
        for forma in ("NFC", "NFD"):
            p = Path(o) / unicodedata.normalize(forma, rel)
            if p.exists():
                return p
    raise FileNotFoundError(ruta_original)


def miniatura(ruta):
    with Image.open(ruta) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((LADO, LADO))
    fondo = Image.new("RGB", (LADO, LADO), "white")
    fondo.paste(im, ((LADO - im.width) // 2, (LADO - im.height) // 2))
    return fondo


def pixeles_iguales(a, b):
    with Image.open(a) as x, Image.open(b) as y:
        return np.array_equal(np.asarray(x.convert("RGB")), np.asarray(y.convert("RGB")))


def hoja_duplicados(excluidas, origenes, fruta):
    d = excluidas[(excluidas["fruta"] == fruta) & excluidas["motivo"].str.startswith("Duplicado exacto")]
    if d.empty:
        return None
    cols, ancho_celda, alto_celda = 3, 2 * LADO + 60, LADO + 66
    filas = (len(d) + cols - 1) // cols
    hoja = Image.new("RGB", (cols * ancho_celda, 60 + filas * alto_celda), "white")
    dib = ImageDraw.Draw(hoja)
    dib.text((10, 10), f"{fruta.capitalize()}: {len(d)} duplicados exactos. Izquierda: la excluida. "
                       f"Derecha: la original que quedó.", fill="black", font=F_TIT)
    iguales = 0
    for i, r in enumerate(d.sort_values("ruta_original").itertuples()):
        x, y = (i % cols) * ancho_celda + 5, 60 + (i // cols) * alto_celda
        a, b = ubicar(origenes, r.ruta_original), ubicar(origenes, r.duplicado_de_original)
        ok = pixeles_iguales(a, b)
        iguales += ok
        hoja.paste(miniatura(a), (x, y))
        hoja.paste(miniatura(b), (x + LADO + 5, y))
        dib.text((x, y + LADO + 2), f"Excluida: {a.name}"[:48], fill="#b00020", font=F_TXT)
        dib.text((x, y + LADO + 16), f"Quedó: {b.name}"[:48], fill="#1b5e20", font=F_TXT)
        dib.text((x, y + LADO + 30), f"   en el dataset: {Path(r.duplicado_de_archivo).name}"[:48], fill="#1b5e20", font=F_TXT)
        dib.text((x, y + LADO + 44), "píxeles idénticos" if ok else "PÍXELES DISTINTOS", fill="black" if ok else "red", font=F_TXT)
    SALIDA.mkdir(parents=True, exist_ok=True)
    hoja.save(SALIDA / f"duplicados_{fruta}.jpg", quality=85)
    return len(d), iguales


ABREV = {"sana": "S", "inmadura": "I", "moho_gris_temprano": "MGt", "moho_gris_avanzado": "MGa",
         "deshidratacion": "D", "magulladura": "Mg", "pudricion_blanda": "PB", "antracnosis": "A", "dudoso": "?"}
def hoja_fresas(excluidas, origenes):
    d = excluidas[(excluidas["fruta"] == "fresa") & (excluidas["origen"] == "propia")].copy()
    d["motivo_fresa"] = d["motivo"].str.split(":").str[0].str.replace("Fresa ", "", regex=False).str.capitalize()
    cols, alto_celda = 8, LADO + 36
    conteo = d["motivo_fresa"].value_counts()
    alto = 90 + sum(34 + ((n + cols - 1) // cols) * alto_celda for n in conteo)
    hoja = Image.new("RGB", (cols * (LADO + 10) + 10, alto), "white")
    dib = ImageDraw.Draw(hoja)
    dib.text((10, 10), f"Fresas propias excluidas: {len(d)}. Etiquetas de docs/etiquetas_fresa_grupo.csv", fill="black", font=F_TIT)
    dib.text((10, 40), "S sana · I inmadura · MGt moho gris temprano · MGa moho gris avanzado · D deshidratación · "
                       "Mg magulladura · PB pudrición blanda · A antracnosis · ? dudoso", fill="#333333", font=F_TXT)
    y = 90
    for m in conteo.index:
        g = d[d["motivo_fresa"] == m].sort_values("ruta_original")
        if g.empty:
            continue
        dib.text((10, y + 6), f"{m} ({len(g)} fotos)", fill="#0d47a1", font=F_TIT)
        y += 34
        for i, r in enumerate(g.itertuples()):
            x, yy = 10 + (i % cols) * (LADO + 10), y + (i // cols) * alto_celda
            hoja.paste(miniatura(ubicar(origenes, r.ruta_original)), (x, yy))
            dib.text((x, yy + LADO + 2), Path(r.ruta_original).name[:21], fill="black", font=F_TXT)
            dib.text((x, yy + LADO + 16), " ".join(ABREV.get(e, e) for e in str(r.etiquetas_fresa).split("+")),
                     fill="#b00020", font=F_TXT)
        y += ((len(g) + cols - 1) // cols) * alto_celda
    hoja.save(SALIDA / "fresas_excluidas.jpg", quality=80)
    return conteo


def hoja_stock(excluidas, origenes):
    """Las fotos de stock de banano sano excluidas: capturas de pantalla rotadas o volteadas."""
    d = excluidas[excluidas["motivo"].str.startswith("Foto de stock")].copy()
    d["nombre"] = d["ruta_original"].map(lambda r: Path(r).name)
    d["captura"] = d["nombre"].str.replace(r"^(rotated_by_15_|vertical_flip_)", "", regex=True)
    d = d.sort_values(["captura", "nombre"])
    cols, alto_celda = 8, LADO + 36
    filas = (len(d) + cols - 1) // cols
    hoja = Image.new("RGB", (cols * (LADO + 10) + 10, 90 + filas * alto_celda), "white")
    dib = ImageDraw.Draw(hoja)
    dib.text((10, 10), f"Banano sano: {len(d)} fotos de stock excluidas, de {d['captura'].nunique()} capturas de pantalla distintas",
             fill="black", font=F_TIT)
    dib.text((10, 40), "Cada archivo es una captura de 2018 rotada 15° (rotated_by_15_) o volteada (vertical_flip_). "
                       "La imagen original sin transformar no está en el Drive.", fill="#333333", font=F_TXT)
    for i, r in enumerate(d.itertuples()):
        x, y = 10 + (i % cols) * (LADO + 10), 90 + (i // cols) * alto_celda
        hoja.paste(miniatura(ubicar(origenes, r.ruta_original)), (x, y))
        tipo = "rotada 15°" if r.nombre.startswith("rotated") else "volteada"
        hora = r.captura.replace("Screen Shot ", "").replace(".png", "")
        dib.text((x, y + LADO + 2), tipo, fill="#b00020", font=F_TXT)
        dib.text((x, y + LADO + 16), hora[:24], fill="black", font=F_TXT)
    hoja.save(SALIDA / "banano_sano_stock.jpg", quality=80)
    return len(d), d["captura"].nunique()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--origen", nargs="+", required=True)
    a = p.parse_args()
    origenes = [os.path.expanduser(o) for o in a.origen]
    excluidas = pd.read_csv(RAIZ / "dataset" / "excluidas.csv")
    for fruta in ["mango", "banano", "fresa"]:
        r = hoja_duplicados(excluidas, origenes, fruta)
        if r:
            print(f"duplicados_{fruta}.jpg: {r[0]} pares, {r[1]} con píxeles idénticos")
    n, capturas = hoja_stock(excluidas, origenes)
    print(f"banano_sano_stock.jpg: {n} fotos de {capturas} capturas distintas")
    conteo = hoja_fresas(excluidas, origenes)
    print(f"fresas_excluidas.jpg: {conteo.sum()} fotos")
    print(conteo.to_string())


if __name__ == "__main__":
    main()
