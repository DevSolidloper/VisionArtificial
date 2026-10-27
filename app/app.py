"""App de Streamlit: análisis del dataset de alteraciones poscosecha en frutas.

Ejecutar desde la raíz del repositorio:
    streamlit run app/app.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vision as V  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DATASET = RAIZ / "dataset"
ORDEN = {
    "mango": ["sano", "antracnosis", "sarna", "pudricion_pedunculo"],
    "banano": ["sano", "antracnosis", "dano_mecanico", "pecas"],
    "fresa": ["sano", "moho_gris", "antracnosis"],
}
FRUTAS = list(ORDEN)
PARTICIONES = ["train", "validation", "test"]
COLOR_ORIGEN = {"propia": "#2a9d8f", "externa": "#e9c46a"}
COLOR_PARTICION = {"train": "#264653", "validation": "#e9c46a", "test": "#e76f51"}
CARACTERISTICAS = {
    "brillo": "Brillo (media de gris)",
    "contraste": "Contraste (desviación de gris)",
    "brillo_fondo": "Brillo del fondo",
    "nitidez": "Nitidez (varianza del Laplaciano)",
    "ruido": "Ruido estimado (Immerkær)",
    "fraccion_fruta": "Fracción del cuadro ocupada por la fruta",
    "L_fruta": "L* de la fruta",
    "a_fruta": "a* de la fruta (verde − / rojo +)",
    "b_fruta": "b* de la fruta (azul − / amarillo +)",
    "saturacion_fruta": "Saturación de la fruta",
    "densidad_bordes": "Densidad de bordes (Canny) en la fruta",
}

st.set_page_config(page_title="Dataset poscosecha · Visión Artificial", page_icon="🍌", layout="wide")


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    e = pd.read_csv(DATASET / "etiquetas.csv")
    p = pd.read_csv(DATASET / "particiones.csv")[["archivo", "grupo", "particion"]]
    c = pd.read_csv(DATASET / "caracteristicas.csv")
    d = e.merge(p, on="archivo").merge(c, on="archivo")
    d["clase_completa"] = d["fruta"] + " · " + d["clase"]
    d["fuente_corta"] = d["fuente"].str.replace(r" \(Mendeley Data\)", "", regex=True)
    d["lado_mayor"] = d[["ancho", "alto"]].max(axis=1)
    d["bytes_disco"] = [(DATASET / a).stat().st_size for a in d["archivo"]]
    return d


@st.cache_data
def cargar_excluidas():
    x = pd.read_csv(DATASET / "excluidas.csv")
    x["motivo_corto"] = (x["motivo"].str.replace(r"^Duplicado exacto de .*", "Duplicado exacto", regex=True)
                         .str.replace(r"^Misma imagen en dos clases: .*", "Misma imagen en dos clases", regex=True))
    return x


@st.cache_data(max_entries=300)
def imagen(archivo, lado=None):
    return V.leer(DATASET / archivo, lado)


def orden_clases(fruta=None):
    if fruta:
        return ORDEN[fruta]
    return [f"{f} · {c}" for f in FRUTAS for c in ORDEN[f]]


def pct(a, b):
    return f"{100 * a / b:.1f} %".replace(".", ",")


def miles(n):
    return f"{n:,}".replace(",", ".")


def num(x, d=1):
    """Número con coma decimal."""
    return f"{x:.{d}f}".replace(".", ",")


def grafico(fig, alto=None):
    if alto:
        fig.update_layout(height=alto)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)


def selector_imagen(datos, clave, fruta_defecto="banano"):
    """Controles para elegir una imagen del dataset. Devuelve la fila elegida."""
    c1, c2, c3, c4 = st.columns([1, 1.3, 1, 1.2])
    fruta = c1.selectbox("Fruta", FRUTAS, index=FRUTAS.index(fruta_defecto), key=f"{clave}_fruta")
    clase = c2.selectbox("Clase", ORDEN[fruta], key=f"{clave}_clase")
    opciones = datos[(datos["fruta"] == fruta) & (datos["clase"] == clase)]
    origenes = ["todas"] + sorted(opciones["origen"].unique())
    origen = c3.selectbox("Origen", origenes, key=f"{clave}_origen")
    if origen != "todas":
        opciones = opciones[opciones["origen"] == origen]
    n = c4.number_input(f"Imagen (1 a {len(opciones)})", 1, len(opciones), 1, key=f"{clave}_n")
    return opciones.iloc[int(n) - 1]


def mostrar_pares(original, resultado, titulo_resultado, ancho=None):
    c1, c2 = st.columns(2)
    c1.image(original, caption="Original", width="stretch")
    c2.image(resultado, caption=titulo_resultado, width="stretch", clamp=True)


def histograma_gris(imgs, nombres):
    filas = []
    for img, nombre in zip(imgs, nombres):
        g = V.a_gris(img) if img.ndim == 3 else img
        h = V.histograma(g)
        filas += [{"nivel": i, "píxeles": v, "imagen": nombre} for i, v in enumerate(h)]
    fig = px.line(pd.DataFrame(filas), x="nivel", y="píxeles", color="imagen",
                  title="Histograma de niveles de gris")
    grafico(fig, 300)


datos = cargar_datos()
excluidas = cargar_excluidas()


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------
def pagina_inicio():
    st.title("Alteraciones poscosecha en frutas: análisis del dataset")
    st.caption("Visión Artificial · Facultad de Minas, Universidad Nacional de Colombia, sede Medellín · 2026-2S")
    st.markdown(
        "Dataset para clasificar alteraciones visibles en **mango, banano y fresa**. Combina fotos propias del "
        "equipo, tomadas a frutas compradas en la Plaza Minorista y la Central Mayorista, con conjuntos de datos públicos."
    )
    n = len(datos)
    propias = int((datos["origen"] == "propia").sum())
    c = st.columns(5)
    c[0].metric("Imágenes", miles(n))
    c[1].metric("Fotos propias", miles(propias), pct(propias, n), delta_color="off")
    c[2].metric("Frutas", len(FRUTAS))
    c[3].metric("Clases", sum(len(v) for v in ORDEN.values()))
    c[4].metric("Imágenes excluidas", miles(len(excluidas)))

    cols = st.columns(3)
    for col, fruta in zip(cols, FRUTAS):
        d = datos[datos["fruta"] == fruta]
        with col:
            st.subheader(fruta.capitalize())
            tabla = (d.groupby("clase")["origen"].value_counts().unstack(fill_value=0)
                     .reindex(index=ORDEN[fruta], columns=["propia", "externa"], fill_value=0))
            tabla["total"] = tabla.sum(axis=1)
            st.dataframe(tabla, width="stretch")
            st.caption(f"{miles(len(d))} imágenes · {pct((d['origen'] == 'propia').sum(), len(d))} propias")

    st.subheader("Cómo se relaciona cada sección con el curso")
    st.table(pd.DataFrame([
        ["Composición del dataset", "Clase 1: adquisición y repositorios de datos", "Cantidad, distribución por clase, fuentes, integrantes y exclusiones"],
        ["Explorador de imágenes", "Clase 1: adquisición", "Muestras de cada clase y fuente, con sus metadatos"],
        ["Imagen digital y color", "Clase 2: imagen digital, histograma y modelos de color", "Resolución, espacio en memoria, histogramas RGB, HSV y CIE L*a*b*"],
        ["Procesamiento", "Clases 3 y 4: operaciones punto a punto, convolución, filtros, ruido y transformaciones geométricas", "Expansión, ecualización, gamma, filtros, ruido y rotación; nitidez y ruido por fuente"],
        ["Segmentación", "Clase 5: umbralización, bordes y regiones", "Otsu, umbral adaptativo, Sobel, Prewitt, Canny y descriptores de forma del atlas de lesiones"],
        ["Separabilidad", "Próximas clases: extracción de características y reconocimiento", "Qué tanto se separan las clases, y las fuentes, con características simples"],
        ["Partición", "Evaluación de desempeño", "Train, validation y test sin fuga de información"],
    ], columns=["Sección", "Tema del curso", "Qué muestra"]))


def pagina_composicion():
    st.header("Composición del dataset")
    st.markdown("Cantidad de imágenes por fruta y clase, de dónde vienen y qué se dejó fuera.")

    conteo = datos.groupby(["fruta", "clase", "origen"]).size().reset_index(name="imágenes")
    fig = px.bar(conteo, x="clase", y="imágenes", color="origen", facet_col="fruta", text_auto=True,
                 color_discrete_map=COLOR_ORIGEN, category_orders={"fruta": FRUTAS, "origen": ["propia", "externa"]},
                 title="Imágenes por clase y origen")
    fig.update_xaxes(matches=None)
    for i, f in enumerate(FRUTAS, 1):
        fig.update_xaxes(categoryorder="array", categoryarray=ORDEN[f], col=i)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
    grafico(fig, 420)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Balance de clases")
        tot = datos.groupby(["fruta", "clase"]).size()
        bal = pd.DataFrame({"clase menor": tot.groupby(level=0).min(), "clase mayor": tot.groupby(level=0).max()}).loc[FRUTAS]
        bal["razón mayor / menor"] = (bal["clase mayor"] / bal["clase menor"]).round(2)
        st.dataframe(bal, width="stretch")
        st.caption("Una razón de 1 indica clases del mismo tamaño.")
        st.subheader("Fotos propias por integrante")
        prop = datos[datos["origen"] == "propia"]
        st.dataframe(pd.crosstab(prop["integrante"], prop["fruta"], margins=True, margins_name="total"),
                     width="stretch")
    with c2:
        st.subheader("Fuentes")
        st.dataframe(pd.crosstab(datos["fuente"], datos["fruta"], margins=True, margins_name="total")
                     [FRUTAS + ["total"]], width="stretch")
        st.subheader("Imágenes excluidas")
        st.dataframe(pd.crosstab(excluidas["motivo_corto"], excluidas["fruta"], margins=True, margins_name="total"),
                     width="stretch")

    prop = datos[datos["origen"] == "propia"]
    por_dia = prop.groupby(["fecha_captura", "fruta"]).size().reset_index(name="fotos")
    fig = px.bar(por_dia, x="fecha_captura", y="fotos", color="fruta", title="Fotos propias por día de captura (según la cámara)",
                 color_discrete_map={"banano": "#e9c46a", "fresa": "#e76f51"})
    grafico(fig, 320)


def pagina_explorador():
    st.header("Explorador de imágenes")
    c1, c2, c3, c4, c5 = st.columns(5)
    fruta = c1.selectbox("Fruta", ["todas"] + FRUTAS)
    clases = ["todas"] + (ORDEN[fruta] if fruta != "todas" else sorted(datos["clase"].unique()))
    clase = c2.selectbox("Clase", clases)
    origen = c3.selectbox("Origen", ["todas", "propia", "externa"])
    particion = c4.selectbox("Partición", ["todas"] + PARTICIONES)
    n = c5.slider("Imágenes", 6, 48, 18, step=6)
    d = datos
    for col, val in [("fruta", fruta), ("clase", clase), ("origen", origen), ("particion", particion)]:
        if val != "todas":
            d = d[d[col] == val]
    st.caption(f"{miles(len(d))} imágenes cumplen el filtro.")
    if d.empty:
        return
    if st.button("Otra muestra"):
        st.session_state["semilla_explorador"] = st.session_state.get("semilla_explorador", 0) + 1
    muestra = d.sample(min(n, len(d)), random_state=st.session_state.get("semilla_explorador", 0))
    cols = st.columns(6)
    for i, fila in enumerate(muestra.itertuples()):
        with cols[i % 6]:
            st.image(imagen(fila.archivo, 300), width="stretch")
            st.caption(f"{fila.fruta} · {fila.clase}  \n{fila.origen} · {fila.particion}")
    with st.expander("Metadatos de la muestra"):
        st.dataframe(muestra[["archivo", "fruta", "clase", "origen", "fuente", "integrante", "fecha_captura",
                              "ancho", "alto", "particion"]], width="stretch", hide_index=True)


def pagina_imagen_digital():
    st.header("Imagen digital y color")
    st.markdown("Clase 2: resolución, espacio que ocupa una imagen, histograma y modelos de color.")

    st.subheader("Resolución y espacio por fuente")
    res = (datos.groupby(["fruta", "fuente_corta"])
           .agg(imágenes=("archivo", "size"),
                tamaño_más_común=("ancho", lambda s: (s.astype(str) + " × " + datos.loc[s.index, "alto"].astype(str)).mode()[0]),
                lado_mayor=("lado_mayor", "median"),
                kB_en_disco=("bytes_disco", lambda s: round(s.mean() / 1024, 1)))
           .reset_index())
    res["kB_sin_comprimir"] = [round(V.bytes_en_memoria(*map(int, t.split(" × "))) / 1024, 1) for t in res["tamaño_más_común"]]
    res["compresión"] = (res["kB_sin_comprimir"] / res["kB_en_disco"]).round(1).astype(str) + " : 1"
    st.dataframe(res, width="stretch", hide_index=True)
    st.caption("Todas las imágenes son RGB de 8 bits por canal (24 bits por píxel). "
               "Sin comprimir ocupan ancho × alto × 3 bytes; en disco están en JPEG.")

    st.subheader("Histograma y modelos de color de una imagen")
    fila = selector_imagen(datos, "color")
    rgb = imagen(fila["archivo"], 512)
    c1, c2 = st.columns([1, 2])
    c1.image(rgb, caption=f"{fila['archivo']} · {fila['fuente']}", width="stretch")
    with c2:
        canales = pd.concat([pd.DataFrame({"nivel": range(256), "píxeles": V.histograma(rgb[..., i]), "canal": n})
                             for i, n in enumerate(["R", "G", "B"])])
        grafico(px.line(canales, x="nivel", y="píxeles", color="canal", title="Histograma por canal RGB",
                        color_discrete_map={"R": "red", "G": "green", "B": "blue"}), 260)
        hsv = V.a_hsv(rgb)
        m = V.mascara_fruta(rgb)
        sat = m & (hsv[..., 1] > 64) & (hsv[..., 2] > 50)
        tono = V.histograma(hsv[..., 0].astype(np.float32) * 2, bins=36, rango=(0, 360), mascara=sat)
        grafico(px.bar(x=np.arange(5, 360, 10), y=tono, labels={"x": "tono H (grados)", "y": "píxeles"},
                       title="Histograma de tono (HSV) en los píxeles saturados de la fruta"), 240)
    lab = V.a_lab(rgb)
    v = st.columns(4)
    v[0].metric("L* fruta", f"{lab[..., 0][m].mean():.1f}" if m.any() else "–")
    v[1].metric("a* fruta", f"{lab[..., 1][m].mean():.1f}" if m.any() else "–")
    v[2].metric("b* fruta", f"{lab[..., 2][m].mean():.1f}" if m.any() else "–")
    v[3].metric("Fracción de fruta", f"{m.mean():.2f}")

    st.subheader("Color de la fruta por clase")
    st.markdown("Medido sobre la fruta segmentada (sección Segmentación). En CIE L*a*b*, **a*** va de verde (−) a rojo (+) "
                "y **b*** de azul (−) a amarillo (+). El atlas de la fresa propone a* para seguir el moho gris.")
    var = st.selectbox("Variable", ["a_fruta", "b_fruta", "L_fruta", "saturacion_fruta"], format_func=CARACTERISTICAS.get)
    grafico(px.box(datos, x="clase_completa", y=var, color="fruta", points=False,
                   category_orders={"clase_completa": orden_clases()},
                   labels={"clase_completa": "", var: CARACTERISTICAS[var]}), 380)

    tonos = [c for c in datos.columns if c.startswith("tono_")]
    medio = datos.groupby(["fruta", "clase"])[tonos].mean().reset_index().melt(["fruta", "clase"], var_name="t", value_name="fracción")
    medio["tono"] = medio["t"].str[5:].astype(int) + 5
    fig = px.line(medio, x="tono", y="fracción", color="clase", facet_col="fruta", category_orders={"fruta": FRUTAS},
                  title="Histograma promedio de tono por clase", labels={"tono": "tono H (grados)"})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
    grafico(fig, 340)

    st.subheader("Brillo y contraste por fuente")
    var = st.radio("Variable", ["brillo", "contraste"], horizontal=True, format_func=CARACTERISTICAS.get)
    grafico(px.box(datos, x="fuente_corta", y=var, color="origen", color_discrete_map=COLOR_ORIGEN, points=False,
                   labels={"fuente_corta": "", var: CARACTERISTICAS[var]}), 360)


def pagina_procesamiento():
    st.header("Procesamiento")
    st.markdown("Clases 3 y 4: operaciones punto a punto, convolución, filtros, ruido y transformaciones geométricas. "
                "Sirven para decidir el preprocesamiento: las fuentes tienen exposición, nitidez y ruido distintos.")
    fila = selector_imagen(datos, "proc", fruta_defecto="mango")
    rgb = imagen(fila["archivo"], 512)
    op = st.radio("Operación", ["Expansión del histograma", "Ecualización", "Corrección gamma", "Negativo",
                                "Filtro de suavizado", "Ruido y su filtrado", "Rotación"], horizontal=True)
    if op == "Expansión del histograma":
        p = st.slider("Percentiles que se llevan a 0 y 255", 0, 20, 2)
        res, titulo = V.expansion_lineal(rgb, p, 100 - p), f"Expansión lineal (percentiles {p} y {100 - p})"
    elif op == "Ecualización":
        res, titulo = V.ecualizar(rgb), "Ecualización del canal V (HSV)"
    elif op == "Corrección gamma":
        g = st.slider("γ", 0.2, 3.0, 0.6, 0.1)
        res, titulo = V.gamma(rgb, g), f"Corrección gamma, γ = {g:.1f}"
    elif op == "Negativo":
        res, titulo = V.negativo(rgb), "Negativo"
    elif op == "Filtro de suavizado":
        c1, c2 = st.columns(2)
        tipo = c1.selectbox("Filtro", ["media", "gaussiano", "mediana"])
        k = c2.slider("Tamaño de la máscara (k × k)", 3, 31, 9, 2)
        res, titulo = V.filtrar(rgb, tipo, k), f"Filtro {tipo} {k} × {k}"
    elif op == "Ruido y su filtrado":
        c1, c2, c3 = st.columns(3)
        tipo = c1.selectbox("Ruido", ["gaussiano", "sal y pimienta"])
        nivel = c2.slider("Nivel (desviación o % de píxeles)", 1, 50, 15)
        filtro = c3.selectbox("Filtro para limpiarlo", ["ninguno", "media", "gaussiano", "mediana"])
        ruidosa = V.agregar_ruido(rgb, tipo, nivel)
        res = ruidosa if filtro == "ninguno" else V.filtrar(ruidosa, filtro, 5)
        titulo = f"Ruido {tipo} ({nivel})" + ("" if filtro == "ninguno" else f" y filtro {filtro} 5 × 5")
    else:
        c1, c2 = st.columns(2)
        grados = c1.slider("Ángulo (grados)", -180, 180, 30, 5)
        escala = c2.slider("Escala", 0.5, 1.5, 1.0, 0.05)
        res, titulo = V.rotar(rgb, grados, escala), f"Rotación de {grados}° y escala {escala:.2f}"
    mostrar_pares(rgb, res, titulo)
    histograma_gris([rgb, res], ["original", "resultado"])
    m = st.columns(4)
    g0, g1 = V.a_gris(rgb), V.a_gris(res)
    m[0].metric("Nitidez original", f"{V.nitidez(g0):.0f}")
    m[1].metric("Nitidez resultado", f"{V.nitidez(g1):.0f}")
    m[2].metric("Ruido original", f"{V.ruido_estimado(g0):.2f}")
    m[3].metric("Ruido resultado", f"{V.ruido_estimado(g1):.2f}")

    st.subheader("Nitidez y ruido por fuente")
    st.markdown("Medidos sobre todas las imágenes reducidas a 256 px. La **nitidez** es la varianza del Laplaciano "
                "(un filtro de segunda derivada): baja en imágenes borrosas. El **ruido** se estima con la máscara de "
                "Immerkær, que anula las zonas suaves y deja pasar las variaciones finas.")
    var = st.radio("Variable", ["nitidez", "ruido"], horizontal=True, format_func=CARACTERISTICAS.get, key="nr")
    fig = px.box(datos, x="fuente_corta", y=var, color="origen", color_discrete_map=COLOR_ORIGEN, points=False,
                 log_y=(var == "nitidez"), labels={"fuente_corta": "", var: CARACTERISTICAS[var]})
    grafico(fig, 380)
    med = datos.groupby("fuente_corta")[["nitidez", "ruido"]].median().round(2)
    st.dataframe(med.rename(columns={"nitidez": "nitidez (mediana)", "ruido": "ruido (mediana)"}), width="stretch")


def pagina_segmentacion():
    st.header("Segmentación")
    st.markdown("Clase 5: umbralización, detección de bordes y regiones. La segmentación separa la fruta del fondo, "
                "que cambia mucho entre fuentes, y permite medir las lesiones con los descriptores del atlas.")
    fila = selector_imagen(datos, "seg")
    rgb = imagen(fila["archivo"], 512)
    gris = V.a_gris(rgb)
    metodo = st.radio("Método", ["Umbral fijo", "Otsu", "Umbral adaptativo", "Bordes", "Fruta y lesiones oscuras"],
                      horizontal=True)
    if metodo == "Umbral fijo":
        t = st.slider("Umbral sobre el nivel de gris", 0, 255, 128)
        mostrar_pares(rgb, V.umbral_fijo(gris, t), f"Píxeles con gris > {t}")
    elif metodo == "Otsu":
        binaria, t = V.umbral_otsu(gris)
        mostrar_pares(rgb, binaria, f"Otsu: umbral automático = {t:.0f}")
        st.caption("Otsu elige el umbral que mejor separa los dos grupos del histograma de gris "
                   "(máxima varianza entre clases).")
    elif metodo == "Umbral adaptativo":
        c1, c2 = st.columns(2)
        b = c1.slider("Tamaño del vecindario", 3, 151, 51, 2)
        c = c2.slider("Constante C", -20, 30, 5)
        mostrar_pares(rgb, V.umbral_adaptativo(gris, b, c), f"Umbral gaussiano local ({b} × {b}, C = {c})")
    elif metodo == "Bordes":
        c1, c2, c3 = st.columns(3)
        op = c1.selectbox("Operador", ["Sobel", "Prewitt", "Canny"])
        t1 = c2.slider("Canny: umbral bajo", 0, 255, 50, disabled=op != "Canny")
        t2 = c3.slider("Canny: umbral alto", 0, 255, 150, disabled=op != "Canny")
        mostrar_pares(rgb, V.bordes(gris, op, t1, t2), f"Bordes con {op}")
    else:
        u = st.slider("Umbral de L* para considerar un píxel oscuro", 10, 60, V.UMBRAL_OSCURO)
        m = V.mascara_fruta(rgb)
        osc, regiones = V.regiones_oscuras(rgb, m, umbral=u)
        vis = rgb.copy()
        vis[~m] = (vis[~m] * 0.25).astype(np.uint8)
        vis[osc] = [255, 0, 255]
        mostrar_pares(rgb, vis, "Fruta (Otsu sobre la saturación) y regiones oscuras en magenta")
        c = st.columns(3)
        c[0].metric("Fracción de la imagen ocupada por la fruta", f"{m.mean():.2f}")
        c[1].metric("Área oscura sobre la fruta", f"{osc.sum() / max(m.sum(), 1):.1%}".replace(".", ","))
        c[2].metric("Regiones oscuras", len(regiones))
        if regiones:
            st.markdown("Descriptores de forma de cada región, los mismos que propone el atlas de lesiones: "
                        "circularidad 4πA/P² (1 = círculo), solidez A / área convexa y relación de aspecto.")
            st.dataframe(pd.DataFrame(regiones).sort_values("area_px", ascending=False), width="stretch",
                         hide_index=True)
        st.caption("La máscara es aproximada: falla con fondos grises o con frutas poco saturadas, y entre fresas "
                   "agrupadas puede incluir el fondo. Sirve para ilustrar el método, no como medida definitiva.")

    st.subheader("El fondo según la fuente")
    st.markdown("Brillo medio de una franja del 5 % junto a los bordes de cada imagen, donde casi siempre está el fondo.")
    grafico(px.box(datos, x="fuente_corta", y="brillo_fondo", color="origen", color_discrete_map=COLOR_ORIGEN,
                   points=False, labels={"fuente_corta": "", "brillo_fondo": "brillo del fondo (0 = negro)"}), 360)
    fondo = (datos.assign(fondo_oscuro=datos["brillo_fondo"] < 50)
             .groupby(["fruta", "clase"])
             .agg(imágenes=("archivo", "size"),
                  propias=("origen", lambda s: pct((s == "propia").sum(), len(s))),
                  fondo_oscuro=("fondo_oscuro", lambda s: pct(s.sum(), len(s))))
             .reindex([(f, c) for f in FRUTAS for c in ORDEN[f]]))
    st.dataframe(fondo, width="stretch")
    st.caption("En banano, el fondo oscuro casi coincide con la clase: un modelo podría aprender el fondo en vez de "
               "la lesión. Segmentar la fruta antes de clasificar reduce ese riesgo.")

    c1, c2 = st.columns(2)
    with c1:
        grafico(px.box(datos, x="fuente_corta", y="fraccion_fruta", color="fruta", points=False,
                       title="Fracción del cuadro ocupada por la fruta",
                       labels={"fuente_corta": "", "fraccion_fruta": "fracción"}), 380)
    with c2:
        grafico(px.box(datos, x="clase_completa", y="densidad_bordes", color="fruta", points=False,
                       category_orders={"clase_completa": orden_clases()}, title="Densidad de bordes (Canny) en la fruta",
                       labels={"clase_completa": "", "densidad_bordes": "fracción de píxeles de borde"}), 380)


def centroide_mas_cercano(entreno, prueba, columnas, objetivo):
    """Clasificador de centroide más cercano sobre características estandarizadas con los datos de entrenamiento."""
    mu = entreno[columnas].mean()
    sd = entreno[columnas].std().replace(0, 1)
    xe = ((entreno[columnas] - mu) / sd).to_numpy()
    xp = ((prueba[columnas] - mu) / sd).to_numpy()
    etiquetas = sorted(entreno[objetivo].unique())
    centros = np.stack([xe[(entreno[objetivo] == e).to_numpy()].mean(axis=0) for e in etiquetas])
    pred = np.array(etiquetas)[((xp[:, None, :] - centros[None]) ** 2).sum(-1).argmin(1)]
    return pred


def pagina_separabilidad():
    st.header("Separabilidad con características simples")
    st.markdown("Anticipa las próximas clases (extracción de características y reconocimiento). Con las características "
                "medidas en las secciones anteriores se proyectan las imágenes en dos dimensiones con **análisis de "
                "componentes principales (PCA)** y se prueba un clasificador de **centroide más cercano**. No es el "
                "modelo del proyecto: es un diagnóstico de qué información separa las clases y cuál separa las fuentes.")
    c1, c2 = st.columns([1, 3])
    fruta = c1.selectbox("Fruta", FRUTAS, index=1, key="sep_fruta")
    feats = c2.multiselect("Características", list(CARACTERISTICAS), default=list(CARACTERISTICAS),
                           format_func=CARACTERISTICAS.get)
    tono = st.checkbox("Agregar el histograma de tono (36 valores)", value=False)
    columnas = feats + ([c for c in datos.columns if c.startswith("tono_")] if tono else [])
    if len(columnas) < 2:
        st.info("Elige al menos dos características.")
        return
    d = datos[datos["fruta"] == fruta].copy()
    x = d[columnas].to_numpy(float)
    x = (x - x.mean(0)) / np.where(x.std(0) == 0, 1, x.std(0))
    _, s, vt = np.linalg.svd(x, full_matrices=False)
    comp = x @ vt[:2].T
    d["CP1"], d["CP2"] = comp[:, 0], comp[:, 1]
    var = s ** 2 / (s ** 2).sum()
    color = st.radio("Colorear por", ["clase", "origen", "fuente_corta", "particion"], horizontal=True,
                     format_func=lambda c: {"fuente_corta": "fuente", "particion": "partición"}.get(c, c))
    fig = px.scatter(d, x="CP1", y="CP2", color=color, opacity=0.7, hover_data=["archivo", "clase", "fuente"],
                     category_orders={"clase": ORDEN[fruta]},
                     labels={"CP1": f"CP1 ({var[0]:.0%} de la varianza)", "CP2": f"CP2 ({var[1]:.0%} de la varianza)"})
    grafico(fig, 480)

    st.subheader("Centroide más cercano: entrena con train y se evalúa en test")
    entreno, prueba = d[d["particion"] == "train"], d[d["particion"] == "test"]
    filas = []
    objetivos = ["clase"] + (["origen"] if d["origen"].nunique() > 1 else [])
    for obj in objetivos:
        pred = centroide_mas_cercano(entreno, prueba, columnas, obj)
        acierto = pred == prueba[obj].to_numpy()
        filas.append({"qué se predice": obj, "exactitud en test": pct(acierto.sum(), len(acierto)),
                      "si se dijera siempre la más frecuente": pct(prueba[obj].value_counts().iloc[0], len(prueba))})
        if obj == "clase" and d["origen"].nunique() > 1:
            for o in ["propia", "externa"]:
                sel = (prueba["origen"] == o).to_numpy()
                filas.append({"qué se predice": f"clase, solo imágenes {o}s",
                              "exactitud en test": pct(acierto[sel].sum(), sel.sum()),
                              "si se dijera siempre la más frecuente": pct(prueba[sel]["clase"].value_counts().iloc[0], sel.sum())})
    st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)
    st.caption("Si la fuente se predice casi sin error, las características llevan la firma de la fuente "
               "(fondo, nitidez, encuadre). Por eso conviene reportar las métricas por separado para fotos propias y externas.")


def pagina_particion():
    st.header("Partición: train, validation y test")
    st.markdown(
        "- **Externas:** al azar, 70/15/15 dentro de cada clase. Quedan juntas las ráfagas de una misma fruta, "
        "las versiones de una misma foto de Roboflow y las imágenes casi idénticas.\n"
        "- **Propias de Sofía Giraldo:** todas en test, porque son frutas, cámara y fondo que el modelo no ve al entrenar.\n"
        "- **Propias de los demás integrantes:** entre train y validation, por sesión (fruta, integrante y día), porque "
        "las fotos siguen las mismas frutas durante varios días.\n\n"
        "Se genera en la sección 7 del notebook y se guarda en `dataset/particiones.csv`."
    )
    t = pd.crosstab(datos["fruta"], datos["particion"], margins=True, margins_name="total")[PARTICIONES + ["total"]]
    t = t.loc[FRUTAS + ["total"]]
    for p in PARTICIONES:
        t[f"% {p}"] = (100 * t[p] / t["total"]).round(1)
    st.dataframe(t, width="stretch")
    conteo = datos.groupby(["fruta", "clase", "particion"]).size().reset_index(name="imágenes")
    fig = px.bar(conteo, x="clase", y="imágenes", color="particion", facet_col="fruta", barmode="stack",
                 color_discrete_map=COLOR_PARTICION, category_orders={"fruta": FRUTAS, "particion": PARTICIONES},
                 title="Imágenes por clase y partición")
    fig.update_xaxes(matches=None)
    for i, f in enumerate(FRUTAS, 1):
        fig.update_xaxes(categoryorder="array", categoryarray=ORDEN[f], col=i)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1].capitalize()))
    grafico(fig, 400)
    st.subheader("Origen en cada partición")
    st.dataframe(pd.crosstab([datos["fruta"], datos["origen"]], datos["particion"])[PARTICIONES].loc[FRUTAS],
                 width="stretch")
    grupos = datos.groupby("grupo")["particion"].nunique()
    st.success(f"Comprobación: {miles(len(grupos))} grupos y ninguno quedó repartido entre dos particiones."
               if (grupos == 1).all() else "Hay grupos repartidos entre particiones.")


def pagina_hallazgos():
    st.header("Hallazgos y limitaciones")
    d = datos
    n = len(d)
    b = d[d["fruta"] == "banano"]
    tot_b = b.groupby("clase").size()
    prop_b = b.groupby("clase")["origen"].apply(lambda s: (s == "propia").mean())
    oscuro_b = b.groupby("clase")["brillo_fondo"].apply(lambda s: (s < 50).mean())
    med = d.groupby("fuente_corta")[["fraccion_fruta"]].median()
    med_b = b.groupby("fuente_corta")[["nitidez", "ruido"]].median()
    a_fresa = d[d["fruta"] == "fresa"].groupby("clase")["a_fruta"].median()
    bordes_m = d[d["fruta"] == "mango"].groupby("clase")["densidad_bordes"].median()
    f = lambda x: f"{100 * x:.0f} %"
    columnas = list(CARACTERISTICAS)
    pred = centroide_mas_cercano(b[b.particion == "train"], b[b.particion == "test"], columnas, "clase")
    prueba = b[b.particion == "test"]
    acierto = pd.Series(pred == prueba["clase"].to_numpy(), index=prueba.index).groupby(prueba["origen"]).mean()
    st.markdown(f"""
1. **Cantidad.** {miles(n)} imágenes: {miles((d.fruta == 'mango').sum())} de mango, {miles((d.fruta == 'banano').sum())} de banano y {miles((d.fruta == 'fresa').sum())} de fresa. Las fotos propias son el {pct((d.origen == 'propia').sum(), n)} del total.
2. **Balance.** En banano, antracnosis tiene {miles(tot_b['antracnosis'])} imágenes, {num(tot_b['antracnosis'] / tot_b.min())} veces la clase más pequeña ({miles(tot_b.min())}). El mango está casi balanceado.
3. **Origen por clase.** En banano, la proporción de fotos propias va de {f(prop_b.min())} ({prop_b.idxmin()}) a {f(prop_b.max())} ({prop_b.idxmax()}).
4. **Fondo.** El porcentaje de imágenes con fondo oscuro en banano va de {f(oscuro_b.min())} ({oscuro_b.idxmin()}) a {f(oscuro_b.max())} ({oscuro_b.idxmax()}), porque las externas tienen fondo negro. Un modelo podría aprender el fondo en vez de la lesión.
5. **Nitidez y ruido.** En banano, las imágenes del dataset de Mendeley tienen una nitidez mediana de {num(med_b.loc['Banana and Banana Leaf Dataset', 'nitidez'], 0)} y las propias de {num(med_b.loc['Propia', 'nitidez'], 0)}; el ruido estimado es {num(med_b.loc['Banana and Banana Leaf Dataset', 'ruido'], 2)} frente a {num(med_b.loc['Propia', 'ruido'], 2)}. Es otra huella de la fuente que el preprocesamiento debe tener en cuenta.
6. **Encuadre.** La fruta ocupa, en mediana, el {f(med.loc['MangoDHDS', 'fraccion_fruta'])} del cuadro en MangoDHDS y el {f(med.loc['Roboflow', 'fraccion_fruta'])} en Roboflow, pero solo el {f(med.loc['Propia', 'fraccion_fruta'])} en las fotos propias, donde suelen aparecer varias frutas, y el {f(med.loc['Banana and Banana Leaf Dataset', 'fraccion_fruta'])} en el dataset de banano de Mendeley. Todas las imágenes deberán llevarse a un mismo tamaño y encuadre de entrada.
7. **Color.** En la fresa, el canal a* (rojo) baja de {num(a_fresa['sano'])} en sana a {num(a_fresa['moho_gris'])} en moho gris, como anticipa el atlas. En el banano, la clase sana es la única con a* negativo (más verde); en el mango lo son la sana y la sarna.
8. **Textura.** La densidad de bordes separa las clases del mango: {num(bordes_m['sano'], 2)} en sano frente a {num(bordes_m['sarna'], 2)} en sarna y {num(bordes_m['antracnosis'], 2)} en antracnosis.
9. **Fresa.** Cada clase proviene de una sola fuente: sana y moho gris, de fotos propias; antracnosis, de Roboflow. Sus métricas deben reportarse por fuente.
10. **Imágenes casi idénticas.** El notebook (sección 7.1) encontró 90 pares de imágenes casi idénticas: 55 en la antracnosis de fresa, 32 en mango y 3 en banano. Quedan siempre en la misma partición.
11. **Transferencia a las fotos propias.** Un clasificador simple de centroide más cercano, entrenado con train sobre las características de esta app, acierta la clase del {f(acierto['externa'])} de las imágenes externas de banano en test, pero solo del {f(acierto['propia'])} de las fotos propias (las de Sofía Giraldo). Lo que se aprende de las externas no se transfiere bien a las propias (ver Separabilidad).
""")
    st.subheader("Limitaciones")
    st.markdown("""
- El mango no tiene fotos propias: todas sus imágenes vienen de MangoDHDS, con fondo blanco y 256 × 256 px.
- Las etiquetas son clasificaciones visuales de síntomas, no diagnósticos de laboratorio: *la cámara ve síntomas, no hongos*.
- Falta identificar la fuente de 28 imágenes externas de banano y confirmar si las del *Banana and Banana Leaf Dataset* son originales o aumentadas.
- Las fotos propias son series de las mismas frutas en varios días, por eso la partición se hace por integrante y sesión.
- La segmentación de la fruta es aproximada; sirve para describir el dataset, no como medida definitiva.
""")


PAGINAS = {
    "Inicio": pagina_inicio,
    "Composición del dataset": pagina_composicion,
    "Explorador de imágenes": pagina_explorador,
    "Imagen digital y color": pagina_imagen_digital,
    "Procesamiento": pagina_procesamiento,
    "Segmentación": pagina_segmentacion,
    "Separabilidad": pagina_separabilidad,
    "Partición": pagina_particion,
    "Hallazgos y limitaciones": pagina_hallazgos,
}
st.sidebar.title("Dataset poscosecha")
pagina = st.sidebar.radio("Sección", list(PAGINAS))
st.sidebar.caption(f"{miles(len(datos))} imágenes · mango, banano y fresa")
PAGINAS[pagina]()
