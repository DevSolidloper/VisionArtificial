# Dataset de alteraciones poscosecha en frutas

Imágenes de mango, banano y fresa organizadas por fruta y por clase. Combina fotografías propias del equipo con conjuntos de datos públicos.

Este dataset se generó con `scripts/organizar_dataset.py` a partir de las carpetas originales del Drive (*Patologias de Frutas en Postcocecha*), que se conservan sin cambios como respaldo.

## Estructura

```
dataset/
├── mango/
│   ├── sano/
│   ├── antracnosis/
│   ├── sarna/
│   └── pudricion_pedunculo/
├── banano/
│   ├── sano/
│   ├── antracnosis/
│   ├── dano_mecanico/
│   └── pecas/
├── fresa/
│   ├── sano/
│   ├── moho_gris/
│   └── antracnosis/
├── etiquetas.csv     # una fila por imagen del dataset
├── particiones.csv   # partición train / validation / test de cada imagen
├── caracteristicas.csv  # características medidas en cada imagen (las usa la app)
└── excluidas.csv     # imágenes que no entraron, con el motivo
```

Cada imagen se llama `<fruta>_<clase>_<NNNN>.jpg`, por ejemplo `banano_pecas_0042.jpg`. Dentro de cada clase la numeración empieza por las fotos propias (ordenadas por integrante y fecha) y sigue con las externas.

## Cantidad de imágenes

| Fruta | Clase | Propias | Externas | Total |
|---|---|---|---|---|
| Mango | Sano | 0 | 249 | 249 |
| | Antracnosis | 0 | 252 | 252 |
| | Sarna (roña) | 0 | 300 | 300 |
| | Pudrición del extremo del pedúnculo | 0 | 300 | 300 |
| | **Total mango** | **0** | **1.101** | **1.101** |
| Banano | Sano | 66 | 68 | 134 |
| | Antracnosis | 108 | 625 | 733 |
| | Daño mecánico | 40 | 79 | 119 |
| | Pecas de maduración | 100 | 15 | 115 |
| | **Total banano** | **314** | **787** | **1.101** |
| Fresa | Sano | 176 | 0 | 176 |
| | Moho gris | 149 | 0 | 149 |
| | Antracnosis | 0 | 110 | 110 |
| | **Total fresa** | **325** | **110** | **435** |
| **Total** | | **639** | **1.998** | **2.637** |

Las fotos propias son el 0 % del mango, el 28,5 % del banano, el 74,7 % de la fresa y el 24,2 % del total.

**Limitación de la fresa.** Cada clase proviene de una sola fuente: sano y moho gris, de fotos propias; antracnosis, de Roboflow. Un modelo podría aprender a distinguir la fuente y no la alteración, así que sus métricas deben reportarse por fuente.

## Fuentes

| Fuente | Fruta y clases | Imágenes |
|---|---|---|
| Fotos propias del equipo | Banano (todas las clases) y fresa (sano y moho gris) | 639 |
| MangoDHDS (Mendeley Data) | Mango (todas las clases) | 1.101 |
| Banana and Banana Leaf Dataset (Mendeley Data) | Banano: antracnosis, daño mecánico y sano | 759 |
| Roboflow | Fresa: antracnosis | 110 |
| Externa sin identificar, cámara OPPO (archivos `Day_`) | Banano: pecas | 15 |
| Externa sin identificar (640 × 480 y 390 × 520 px) | Banano: antracnosis (12) y daño mecánico (1) | 13 |

**Fotos propias.** Las frutas se compraron en la Plaza Minorista de Medellín y en la Central Mayorista de Antioquia, y cada integrante fotografió las suyas día a día con su celular o cámara, siguiendo el protocolo de captura del Avance #1 (`docs/`). Cada foto propia se identifica por la cámara registrada en sus metadatos:

| Integrante | Cámara | Banano | Fresa |
|---|---|---|---|
| Andrés Arbeláez | Motorola Edge 50 Pro | 112 | 141 |
| Diego Cifuentes | Samsung Galaxy A56 5G | 137 | 48 |
| Sara Suárez | Samsung Galaxy A52 (SM-A525M) | 0 | 103 |
| Sofía Giraldo | Panasonic DMC-FH25 | 65 | 33 |

**Atribución de las externas de banano.** Las 759 imágenes asignadas al *Banana and Banana Leaf Dataset* se identificaron por su tamaño (1000 × 750 px) y por el patrón de sus nombres. Las 28 externas sin identificar están pendientes de documentar.

Referencias:

- Barhate, P., Barhate, B., & Joshi, M. (2025). *MangoDHDS: A Dataset of Diseased and Healthy Mangoes of 1.5 K Images* (Version 1) [Dataset]. Mendeley Data. https://doi.org/10.17632/b4nrw5hyyc.1
- Das, U., Azam, S., & Al Kafi, M. A. (2025). *Banana and Banana Leaf Dataset for Classification and Disease Detection* (Version 2) [Dataset]. Mendeley Data. https://doi.org/10.17632/5nfjzntwd8.2

## Procesamiento

- Las imágenes con el lado mayor por encima de 1024 px se redujeron a 1024 px, conservando la proporción (JPEG, calidad 90).
- Las fotos propias se enderezaron según la orientación del celular y se guardaron sin metadatos EXIF, que pueden incluir la ubicación.
- Las imágenes externas pequeñas se copiaron sin cambios.
- Todas las imágenes quedaron en RGB y en formato `.jpg`.

## Clasificación de las fotos propias de fresa

Las fotos propias de fresa se clasificaron con las anotaciones de `docs/etiquetas_fresa_grupo.csv`, que registran todas las alteraciones visibles en cada foto. Cada foto va a la clase de la alteración más grave que tenga:

- **moho_gris:** tiene *moho gris* (temprano o avanzado), aunque también tenga fresas sanas, deshidratadas o magulladas. 90 de las 149 son fotos de grupo, donde el moho puede estar en una sola fresa entre varias sanas.
- **antracnosis:** tiene *antracnosis*.
- **sano:** no tiene enfermedades y tiene *sana*, *deshidratación* o *inmadura*. La deshidratación no es una enfermedad, así que la clase sano significa "sin moho gris ni antracnosis"; 60 de las 176 fotos sanas tienen deshidratación.

Quedan fuera las fotos marcadas como *dudoso*, las que tienen dos enfermedades a la vez, las de *pudrición blanda* (no es una de las tres clases), las de *magulladura* sin enfermedad y las que no tienen etiqueta.

## Imágenes excluidas

Hay 492 imágenes que no entraron. Ninguna se borró: todas siguen en el Drive y aparecen en `excluidas.csv` con su ruta original y el motivo.

| Motivo | Imágenes |
|---|---|
| Duplicados exactos: se conservó una sola copia | 169 |
| Fotos de stock de banano sano, aumentadas y sin la imagen original | 163 |
| Fotos propias de fresa que no cumplen la regla de clasificación | 118 |
| Clase descartada: pudrición de corona del banano | 36 |
| Misma imagen guardada en dos clases de banano (3 pares) | 6 |
| **Total** | **492** |

**Duplicados exactos (169).** Son archivos idénticos byte a byte a otro que sí quedó: 99 de mango, 40 de fresa y 30 de banano. La comparación se hizo entre los archivos originales, antes de renombrar. En mango las copias ya venían dentro de los archivos de MangoDHDS, con nombres distintos (por ejemplo, `He163.jpg` es igual a `He10.jpg`). En banano y fresa la copia conserva el nombre original con un sufijo que agrega el sistema al copiar: ` - Copy` (Windows), ` copy` o ` 2` (Mac). En `excluidas.csv`, las columnas `duplicado_de_original` y `duplicado_de_archivo` dicen cuál es la imagen que quedó, con su nombre original y con su nombre en el dataset.

**Fotos de stock de banano sano (163).** Son capturas de pantalla de fotos de stock de 2018, rotadas 15° (107, prefijo `rotated_by_15_`) o volteadas (56, prefijo `vertical_flip_`), y la imagen sin transformar no está en el Drive. Corresponden a 135 capturas distintas: de 28 hay las dos versiones. Incluyen bananos pelados, en rodajas y sobre fondos de colores, que no son fotos de poscosecha; un modelo podría asociar el estilo de foto de stock con la clase sano, y las dos versiones de una misma captura podrían quedar en particiones distintas.

**Fotos propias de fresa (118).** Son las que la regla de la sección anterior deja fuera:

| Motivo de exclusión | Fotos |
|---|---|
| Marcadas como *dudoso* | 56 |
| Con magulladura y sin enfermedad | 54 |
| Con dos enfermedades a la vez (moho gris y pudrición blanda) | 5 |
| Sin etiqueta | 3 |

**Hojas de verificación.** En `docs/verificacion/` están las imágenes excluidas a simple vista, tomadas de las carpetas originales del Drive:

- `duplicados_mango.jpg`, `duplicados_banano.jpg` y `duplicados_fresa.jpg`: cada duplicado junto a la imagen que quedó; en los 169 pares los píxeles son idénticos.
- `banano_sano_stock.jpg`: las 163 fotos de stock de banano sano.
- `fresas_excluidas.jpg`: las 118 fotos propias de fresa excluidas, agrupadas por motivo y con sus etiquetas.

**Imágenes casi idénticas.** Además de los duplicados exactos, hay 90 pares de imágenes que son la misma foto guardada con otra compresión: 55 en la antracnosis de fresa, 32 en mango y 3 en banano. No se excluyeron, pero la partición las mantiene siempre juntas (sección 7.1 del notebook).

## Tablas

### `etiquetas.csv`

Una fila por imagen del dataset.

| Columna | Contenido |
|---|---|
| `archivo` | Ruta de la imagen dentro de `dataset/` |
| `fruta`, `clase` | Etiqueta de la imagen |
| `origen` | `propia` o `externa` |
| `fuente` | Conjunto de datos de origen, o `Propia` |
| `integrante`, `camara` | Quién tomó la foto y con qué (solo propias) |
| `fecha_captura` | Fecha registrada por la cámara (solo propias) |
| `ancho`, `alto` | Tamaño final en píxeles |
| `ruta_original` | Ruta de la imagen en el Drive |
| `md5_original` | Huella del archivo original, para rastrearlo |
| `etiquetas_fresa` | Anotaciones de la foto en `docs/etiquetas_fresa_grupo.csv` (solo fresas propias) |

### `excluidas.csv`

Una fila por imagen que no entró al dataset.

| Columna | Contenido |
|---|---|
| `ruta_original` | Ruta de la imagen en el Drive |
| `fruta`, `carpeta_original` | Fruta y carpeta del Drive donde estaba |
| `origen`, `fuente`, `integrante`, `fecha_captura` | Igual que en `etiquetas.csv` |
| `motivo` | Por qué se excluyó |
| `duplicado_de_original` | En los duplicados, ruta original de la imagen que quedó |
| `duplicado_de_archivo` | En los duplicados, nombre de la imagen que quedó dentro de `dataset/` |
| `md5_original` | Huella del archivo original |
| `etiquetas_fresa` | Anotaciones de la foto (solo fresas propias) |

### `particiones.csv`

Una fila por imagen del dataset, con las columnas `archivo`, `fruta`, `clase`, `origen`, `grupo` y `particion` (`train`, `validation` o `test`). Las imágenes del mismo `grupo` van siempre a la misma partición.

### `caracteristicas.csv`

Una fila por imagen, medida sobre una versión reducida a 256 px en su lado mayor. La genera `scripts/calcular_caracteristicas.py` y la usa la app de Streamlit.

| Columna | Contenido |
|---|---|
| `brillo`, `contraste` | Media y desviación estándar del nivel de gris |
| `rojo`, `verde`, `azul` | Media de cada canal RGB |
| `brillo_fondo` | Media de gris en una franja del 5 % junto a los bordes |
| `nitidez` | Varianza del Laplaciano |
| `ruido` | Desviación estimada del ruido (máscara de Immerkær) |
| `fraccion_fruta` | Fracción de la imagen ocupada por la fruta, con una segmentación aproximada (Otsu sobre la saturación) |
| `L_fruta`, `a_fruta`, `b_fruta` | Color medio de la fruta en CIE L*a*b* |
| `saturacion_fruta` | Saturación media de la fruta (HSV) |
| `densidad_bordes` | Fracción de píxeles de borde (Canny) dentro de la fruta |
| `tono_000` a `tono_350` | Histograma de tono (HSV) de la fruta, en 36 intervalos de 10° |

## Partición en train, validation y test

La partición se genera en la sección 7 de `va_analisis.ipynb` e incluye las tres frutas. Las fotos propias son series diarias de las mismas frutas, así que no se reparten al azar:

- **Fotos propias de Sofía Giraldo:** todas en test, porque son frutas, cámara y fondo que el modelo no ve al entrenar.
- **Fotos propias de los demás integrantes:** entre train y validation, por sesión (fruta, integrante y día).
- **Externas:** al azar, 70/15/15 dentro de cada clase, manteniendo juntas las tomas en ráfaga, las versiones de una misma foto de Roboflow y las imágenes casi idénticas.

| Fruta | Train | Validation | Test | Total |
|---|---|---|---|---|
| Mango | 768 | 167 | 166 | 1.101 |
| Banano | 757 | 159 | 185 | 1.101 |
| Fresa | 317 | 68 | 50 | 435 |
| **Total** | **1.842** | **394** | **401** | **2.637** |

En la fresa, el test tiene solo las 33 fotos propias de Sofía (26 sanas y 7 con moho gris) y las 17 de antracnosis de Roboflow, así que sus métricas por clase serán poco estables.

## Cómo regenerarlo

Con las carpetas del Drive descargadas en `~/Downloads`, desde la raíz del repositorio:

```bash
ORIGEN=("$HOME/Downloads/Patologias de Frutas en Postcocecha" \
        "$HOME/Downloads/Patologias de Frutas en Postcocecha 2" \
        "$HOME/Downloads/Patologias de Frutas en Postcocecha 3")

# 1. Imágenes, etiquetas.csv y excluidas.csv
python3 scripts/organizar_dataset.py --origen "${ORIGEN[@]}" \
    --etiquetas-fresa docs/etiquetas_fresa_grupo.csv --salida dataset

# 2. particiones.csv: ejecutar la sección 7 de va_analisis.ipynb

# 3. caracteristicas.csv, para la app
python3 scripts/calcular_caracteristicas.py

# 4. Hojas de docs/verificacion/
python3 scripts/hojas_verificacion.py --origen "${ORIGEN[@]}"
```

Los scripts solo leen las carpetas de origen; nunca las modifican.

## Pendientes

- Nombre y enlace del dataset de Roboflow de la antracnosis de fresa.
- Fuente de las 28 imágenes externas de banano sin identificar.
- Confirmar si las imágenes del *Banana and Banana Leaf Dataset* vienen de su carpeta *Raw Data* o de *Augmented Data*.
