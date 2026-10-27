"""Operaciones de imagen del proyecto, organizadas según las clases del curso.

Las usan la app de Streamlit (app/app.py) y el script que calcula las
características del dataset (scripts/calcular_caracteristicas.py).
Todas las imágenes se manejan como arreglos RGB de 8 bits (uint8).
"""
import cv2
import numpy as np
from PIL import Image, ImageOps

LADO_ANALISIS = 256      # lado mayor al que se reducen las imágenes para medir características
UMBRAL_OSCURO = 30       # L* (0 a 100) por debajo del cual un píxel de la fruta se considera lesión oscura


# ---------------------------------------------------------------------------
# Clase 2. Imagen digital y modelos de color
# ---------------------------------------------------------------------------
def leer(ruta, lado_max=None):
    """Lee una imagen como RGB uint8, enderezada según su EXIF y, si se pide, reducida."""
    with Image.open(ruta) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        if lado_max:
            im.thumbnail((lado_max, lado_max), Image.LANCZOS)
        return np.asarray(im)


def a_gris(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)


def a_hsv(rgb):
    """HSV de OpenCV: H de 0 a 179 (grados / 2), S y V de 0 a 255."""
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)


def a_lab(rgb):
    """CIE L*a*b* en escala estándar: L* de 0 a 100, a* y b* alrededor de 0."""
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    return np.dstack([lab[..., 0] * 100 / 255, lab[..., 1] - 128, lab[..., 2] - 128])


def histograma(canal, bins=256, rango=(0, 256), mascara=None):
    valores = canal[mascara] if mascara is not None else canal.ravel()
    h, _ = np.histogram(valores, bins=bins, range=rango)
    return h


def bytes_en_memoria(ancho, alto, canales=3, bits=8):
    """Espacio que ocupa la imagen sin comprimir: ancho × alto × canales × bits / 8."""
    return ancho * alto * canales * bits // 8


# ---------------------------------------------------------------------------
# Clase 3. Operaciones punto a punto
# ---------------------------------------------------------------------------
def expansion_lineal(rgb, p_bajo=2, p_alto=98):
    """Expansión del histograma: lleva los percentiles p_bajo y p_alto de cada canal a 0 y 255."""
    salida = np.empty_like(rgb)
    for c in range(3):
        lo, hi = np.percentile(rgb[..., c], [p_bajo, p_alto])
        salida[..., c] = np.clip((rgb[..., c].astype(np.float32) - lo) * 255 / max(hi - lo, 1), 0, 255)
    return salida


def ecualizar(rgb):
    """Ecualización del histograma sobre el canal V de HSV, para no alterar el tono."""
    hsv = a_hsv(rgb)
    hsv[..., 2] = cv2.equalizeHist(hsv[..., 2])
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)


def gamma(rgb, g):
    """Corrección gamma: salida = 255 · (entrada / 255) ** g. g < 1 aclara y g > 1 oscurece."""
    tabla = (np.linspace(0, 1, 256) ** g * 255).astype(np.uint8)
    return cv2.LUT(rgb, tabla)


def negativo(rgb):
    return 255 - rgb


# ---------------------------------------------------------------------------
# Clase 4. Convolución, filtros, ruido y transformaciones geométricas
# ---------------------------------------------------------------------------
def filtrar(rgb, tipo, k):
    """Filtro espacial de tamaño k × k: media, gaussiano o mediana."""
    k = int(k) | 1                                   # tamaño impar
    if tipo == "media":
        return cv2.blur(rgb, (k, k))
    if tipo == "gaussiano":
        return cv2.GaussianBlur(rgb, (k, k), 0)
    return cv2.medianBlur(rgb, k)


def agregar_ruido(rgb, tipo, nivel, semilla=0):
    """Ruido gaussiano (nivel = desviación) o sal y pimienta (nivel = % de píxeles)."""
    rng = np.random.default_rng(semilla)
    if tipo == "gaussiano":
        return np.clip(rgb + rng.normal(0, nivel, rgb.shape), 0, 255).astype(np.uint8)
    salida = rgb.copy()
    m = rng.random(rgb.shape[:2])
    p = nivel / 100
    salida[m < p / 2] = 0
    salida[m > 1 - p / 2] = 255
    return salida


def rotar(rgb, grados, escala=1.0):
    """Rotación alrededor del centro con interpolación bilineal (como un aumento de datos)."""
    h, w = rgb.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), grados, escala)
    return cv2.warpAffine(rgb, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def nitidez(gris):
    """Varianza del Laplaciano: valores bajos indican una imagen borrosa."""
    return float(cv2.Laplacian(gris, cv2.CV_64F).var())


def ruido_estimado(gris):
    """Desviación estimada del ruido con la máscara de Immerkær (1996)."""
    m = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], dtype=np.float64)
    conv = cv2.filter2D(gris.astype(np.float64), -1, m)[1:-1, 1:-1]
    h, w = gris.shape
    return float(np.sqrt(np.pi / 2) * np.abs(conv).sum() / (6 * (w - 2) * (h - 2)))


# ---------------------------------------------------------------------------
# Clase 5. Segmentación: umbralización, bordes y regiones
# ---------------------------------------------------------------------------
def umbral_fijo(gris, t):
    return (gris > t).astype(np.uint8) * 255


def umbral_otsu(gris):
    t, binaria = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binaria, float(t)


def umbral_adaptativo(gris, bloque=31, c=5):
    bloque = int(bloque) | 1
    return cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, bloque, c)


def bordes(gris, metodo, t1=50, t2=150):
    """Magnitud del gradiente con Sobel o Prewitt, o mapa binario de Canny."""
    if metodo == "Canny":
        return cv2.Canny(gris, t1, t2)
    if metodo == "Sobel":
        gx = cv2.Sobel(gris, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(gris, cv2.CV_64F, 0, 1, ksize=3)
    else:
        kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float64)
        gx = cv2.filter2D(gris.astype(np.float64), -1, kx)
        gy = cv2.filter2D(gris.astype(np.float64), -1, kx.T)
    mag = np.hypot(gx, gy)
    return (255 * mag / max(mag.max(), 1)).astype(np.uint8)


def mascara_fruta(rgb):
    """Separa la fruta del fondo.

    1. Umbral de Otsu sobre la saturación (S de HSV): los fondos blancos, grises
       y negros tienen poca saturación; la fruta, mucha.
    2. El umbral nunca baja de 50, para no tomar fondos grises algo coloreados,
       y se descartan los píxeles muy oscuros (V < 40), típicos del fondo negro.
    3. Cierre y apertura morfológicos para limpiar la máscara, y relleno de huecos
       para incluir las lesiones oscuras que quedan dentro de la fruta.
    4. Se conservan las regiones de más del 1 % de la imagen.
    """
    hsv = a_hsv(rgb)
    s, v = hsv[..., 1], hsv[..., 2]
    t, _ = cv2.threshold(s, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    m = ((s > max(t, 50)) & (v > 40)).astype(np.uint8) * 255
    elipse = lambda k: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, elipse(7))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, elipse(5))
    h, w = m.shape
    relleno = cv2.copyMakeBorder(m, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)   # borde para que el relleno parta del fondo
    cv2.floodFill(relleno, np.zeros((h + 4, w + 4), np.uint8), (0, 0), 255)
    m = m | cv2.bitwise_not(relleno[1:-1, 1:-1])
    n, etiquetas, stats, _ = cv2.connectedComponentsWithStats(m)
    grandes = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > 0.01 * h * w]
    return np.isin(etiquetas, grandes)


def regiones_oscuras(rgb, mascara, umbral=UMBRAL_OSCURO, area_min=20):
    """Regiones de la fruta con L* bajo y sus descriptores de forma del atlas de lesiones.

    Devuelve la máscara de las regiones y una lista con área, perímetro,
    circularidad (4πA/P²), solidez (A / área convexa) y relación de aspecto.
    """
    # Se erosiona la máscara para no contar sombras ni fondo pegados al contorno de la fruta
    interior = cv2.erode(mascara.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))) > 0
    oscuro = ((a_lab(rgb)[..., 0] < umbral) & interior).astype(np.uint8)
    contornos, _ = cv2.findContours(oscuro, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    filas, salida = [], np.zeros_like(oscuro)
    for c in contornos:
        area = cv2.contourArea(c)
        if area < area_min:
            continue
        perimetro = cv2.arcLength(c, True)
        casco = cv2.contourArea(cv2.convexHull(c))
        (_, _), (a, b), _ = cv2.minAreaRect(c)
        filas.append({
            "area_px": int(area),
            "perimetro_px": round(perimetro, 1),
            "circularidad": round(4 * np.pi * area / perimetro ** 2, 3) if perimetro else 0.0,
            "solidez": round(area / casco, 3) if casco else 0.0,
            "relacion_aspecto": round(max(a, b) / max(min(a, b), 1), 2),
        })
        cv2.drawContours(salida, [c], -1, 1, thickness=-1)
    return salida.astype(bool), filas


# ---------------------------------------------------------------------------
# Características por imagen (para el análisis del dataset)
# ---------------------------------------------------------------------------
def caracteristicas(rgb):
    """Mide, sobre la imagen reducida a LADO_ANALISIS px, las características del análisis."""
    gris = a_gris(rgb)
    hsv = a_hsv(rgb)
    lab = a_lab(rgb)
    h, w = gris.shape
    b = max(1, int(0.05 * min(h, w)))
    borde = np.concatenate([gris[:b].ravel(), gris[-b:].ravel(), gris[:, :b].ravel(), gris[:, -b:].ravel()])
    m = mascara_fruta(rgb)
    if m.sum() == 0:                        # si la segmentación falla, se usa toda la imagen
        m = np.ones_like(gris, dtype=bool)
    canny = cv2.Canny(gris, 50, 150) > 0
    fila = {
        "brillo": float(gris.mean()),
        "contraste": float(gris.std()),
        "rojo": float(rgb[..., 0].mean()),
        "verde": float(rgb[..., 1].mean()),
        "azul": float(rgb[..., 2].mean()),
        "brillo_fondo": float(borde.mean()),
        "nitidez": nitidez(gris),
        "ruido": ruido_estimado(gris),
        "fraccion_fruta": float(m.mean()),
        "L_fruta": float(lab[..., 0][m].mean()),
        "a_fruta": float(lab[..., 1][m].mean()),
        "b_fruta": float(lab[..., 2][m].mean()),
        "saturacion_fruta": float(hsv[..., 1][m].mean()),
        "densidad_bordes": float(canny[m].mean()),
    }
    # Histograma de tono de los píxeles saturados de la fruta, en 36 intervalos de 10°
    sat = m & (hsv[..., 1] > 64) & (hsv[..., 2] > 50)
    ht = histograma(hsv[..., 0].astype(np.float32) * 2, bins=36, rango=(0, 360), mascara=sat).astype(float)
    ht /= max(ht.sum(), 1)
    fila.update({f"tono_{10 * i:03d}": float(v) for i, v in enumerate(ht)})
    return fila
