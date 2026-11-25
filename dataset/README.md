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

Cada imagen se llama `<fruta>_<clase>_<NNNN>.jpg`, por ejemplo `banano_pecas_0042.jpg`. Dentro de cada clase la numeración empieza por las fotos propias (ordenadas por integrante y fecha) sigue con las externas y termina con los aumentos.

## Cantidad de imágenes

| Fruta | Clase | Propias | Externas | Total |
|---|---|---|---|---|
| Mango | Sano | 0 | 249 | 249 |
| | Antracnosis | 0 | 252 | 252 |
| | Sarna (roña) | 0 | 300 | 300 |
| | Pudrición del extremo del pedúnculo | 0 | 300 | 300 |
| | **Total mango** | **0** | **1.101** | **1.101** |
| Banano | Sano | 66 | 68 | 134 |
| | Antracnosis | 108 | 628 | 736 |
| | Daño mecánico | 40 | 198 | 238 |
| | Pecas de maduración | 100 | 162 | 262 |
| | **Total banano** | **314** | **1.056** | **1.370** |
| Fresa | Sano | 230 | 263 | 493 |
| | Moho gris | 154 | 230 | 384 |
| | Antracnosis | 0 | 195 | 195 |
| | **Total fresa** | **384** | **688** | **1.072** |
| **Total** | | **698** | **2.845** | **3.543** |

Las fotos propias son el 0 % del mango, el 22,9 % del banano, el 35,8 % de la fresa y el 19,7 % del total.

**Aumentos.** Además de las 3.543 imágenes reales, en `fresa/antracnosis/` hay 373 aumentos (rotaciones de fotos de antracnosis de Roboflow, archivos originales `aug_`) que subió el equipo. Tienen `aumento = 1` en `etiquetas.csv`, no se cuentan en las tablas y solo se usan en train: 259 entran a `particiones.csv` y 114 no se usan porque su foto original quedó en validation o test.

**Limitaciones.**

- **Banano desbalanceado:** antracnosis tiene 736 imágenes y sano 134 (razón 5,49).
- **Antracnosis de fresa:** no tiene fotos propias; todas son de Roboflow.
- **Fresa sana y moho gris:** las externas son fotos de cultivo y las propias son de poscosecha sobre mesa, así que las métricas deben reportarse por fuente.
- **Imágenes ya aumentadas de origen:** las de Roboflow de banano (daño mecánico y pecas) repiten pocas frutas con rotaciones y cambios de color. En pecas se agrupan por el nombre de la foto original; en daño mecánico los nombres no lo permiten, así que versiones de una misma fruta pueden haber quedado en particiones distintas.

## Fuentes

| Fuente | Fruta y clases | Imágenes |
|---|---|---|
| Fotos propias del equipo | Banano (todas las clases) y fresa (sano y moho gris) | 698 |
| MangoDHDS (Mendeley Data) | Mango (todas las clases) | 1.101 |
| Banana and Banana Leaf Dataset (Mendeley Data) | Banano: antracnosis (616), daño mecánico (79) y sano (68) | 763 |
| Roboflow | Fresa: antracnosis (195) y moho gris (230). Banano: daño mecánico (118) y pecas (99) | 642 |
| Externa sin identificar (archivos `fresa_NNN`, fresas en cultivo) | Fresa: sano | 263 |
| Internet (fotos de stock y páginas web) | Banano: pecas | 48 |
| Externa sin identificar, cámara OPPO (archivos `Day_`) | Banano: pecas | 15 |
| Externa sin identificar (640 × 480 y 390 × 520 px) | Banano: antracnosis (12) y daño mecánico (1) | 13 |

**Imágenes agregadas después del 27 de octubre.** El equipo subió al Drive 952 imágenes de fresa (230 de moho gris, 263 sanas, 85 de antracnosis y 374 aumentos de antracnosis, uno de ellos dañado) y 266 de banano (119 de daño mecánico y 147 de pecas), todas externas. Las de Roboflow de daño mecánico vienen de un dataset de madurez de banano (los nombres dicen *ripe*, *unripe* y *rotten*). Diez de las de pecas venían en formato webp o avif y se convirtieron a `.jpg`.

**Fotos propias.** Las frutas se compraron en la Plaza Minorista de Medellín y en la Central Mayorista de Antioquia, y cada integrante fotografió las suyas día a día con su celular o cámara, siguiendo el protocolo de captura del Avance #1 (`docs/`). Cada foto propia se identifica por la cámara registrada en sus metadatos:

| Integrante | Cámara | Banano | Fresa |
|---|---|---|---|
| Andrés Arbeláez | Motorola Edge 50 Pro | 112 | 143 |
| Diego Cifuentes | Samsung Galaxy A56 5G | 137 | 48 |
| Sara Suárez | Samsung Galaxy A52 (SM-A525M) | 0 | 159 |
| Sofía Giraldo | Panasonic DMC-FH25 | 65 | 34 |

**Atribución de las externas de banano.** Las 763 imágenes asignadas al *Banana and Banana Leaf Dataset* se identificaron por su tamaño (1000 × 750 px) y por el patrón de sus nombres. Las de Roboflow se reconocen por el sufijo `.rf.` de sus nombres.

Referencias:

- Barhate, P., Barhate, B., & Joshi, M. (2025). *MangoDHDS: A Dataset of Diseased and Healthy Mangoes of 1.5 K Images* (Version 1) [Dataset]. Mendeley Data. https://doi.org/10.17632/b4nrw5hyyc.1
- Das, U., Azam, S., & Al Kafi, M. A. (2025). *Banana and Banana Leaf Dataset for Classification and Disease Detection* (Version 2) [Dataset]. Mendeley Data. https://doi.org/10.17632/5nfjzntwd8.2

## Procesamiento

- Las imágenes con el lado mayor por encima de 1024 px se redujeron a 1024 px, conservando la proporción (JPEG, calidad 90).
- Las fotos propias se enderezaron según la orientación del celular y se guardaron sin metadatos EXIF, que pueden incluir la ubicación.
- Las imágenes externas pequeñas se copiaron sin cambios.
- Todas las imágenes quedaron en RGB y en formato `.jpg`.

## Clasificación de las fotos propias de fresa

Las fotos propias de fresa se clasificaron con las anotaciones de `docs/etiquetas_fresa_grupo.csv`, que registran todas las alteraciones visibles en cada foto. Ninguna foto se excluye por tener varias alteraciones: cada una va a la clase de la alteración más grave que tenga.

- **moho_gris:** tiene *moho gris* (temprano o avanzado), aunque también tenga pudrición blanda, magulladura, deshidratación o fresas sanas. En 83 de las 154 fotos también hay fresas sanas, así que el moho puede estar en una sola fresa entre varias.
- **antracnosis:** tiene *antracnosis* y no tiene moho gris. Ninguna foto propia quedó en esta clase.
- **sano:** no tiene enfermedades y tiene *sana*, *deshidratación*, *inmadura* o *magulladura*. Ni la deshidratación ni la magulladura son enfermedades, así que la clase sano significa "sin moho gris ni antracnosis"; 72 de las 230 fotos sanas tienen deshidratación y 54 tienen magulladura.

Quedan fuera las fotos marcadas como *dudoso*, las que solo tienen *pudrición blanda* (no es una de las tres clases) y las que no tienen etiqueta.

La misma regla se aplica a una imagen guardada en dos carpetas de clase del Drive: queda una sola vez, en la clase más grave. Pasa con tres imágenes de banano, que quedaron en antracnosis.

## Imágenes excluidas

Hay 458 imágenes que no entraron. Ninguna se borró: todas siguen en el Drive y aparecen en `excluidas.csv` con su ruta original y el motivo.

| Motivo | Imágenes |
|---|---|
| Duplicados exactos: se conservó una sola copia | 196 |
| Fotos de stock de banano sano, aumentadas y sin la imagen original | 163 |
| Fotos propias de fresa marcadas como *dudoso* | 56 |
| Clase descartada: pudrición de corona del banano | 36 |
| Copia de una imagen guardada en dos clases de banano (quedó la de antracnosis) | 3 |
| Fotos propias de fresa sin etiqueta | 3 |
| Archivo dañado (0 bytes): un aumento de antracnosis de fresa | 1 |
| **Total** | **458** |

**Duplicados exactos (196).** Son archivos idénticos byte a byte a otro que sí quedó: 99 de mango, 57 de banano y 40 de fresa. La comparación se hizo entre los archivos originales, antes de renombrar. En mango las copias ya venían dentro de los archivos de MangoDHDS, con nombres distintos (por ejemplo, `He163.jpg` es igual a `He10.jpg`). En banano y fresa la copia conserva el nombre original con un sufijo que agrega el sistema al copiar: ` - Copy` (Windows), ` copy`, ` 2` (Mac) o `(1)`. En `excluidas.csv`, las columnas `duplicado_de_original` y `duplicado_de_archivo` dicen cuál es la imagen que quedó, con su nombre original y con su nombre en el dataset.

**Fotos de stock de banano sano (163).** Son capturas de pantalla de fotos de stock de 2018, rotadas 15° (107, prefijo `rotated_by_15_`) o volteadas (56, prefijo `vertical_flip_`), y la imagen sin transformar no está en el Drive. Corresponden a 135 capturas distintas: de 28 hay las dos versiones. Incluyen bananos pelados, en rodajas y sobre fondos de colores, que no son fotos de poscosecha; un modelo podría asociar el estilo de foto de stock con la clase sano, y las dos versiones de una misma captura podrían quedar en particiones distintas.

**Fotos propias de fresa (59).** Las 56 marcadas como *dudoso* y las 3 sin etiqueta. Las 54 con magulladura y sin enfermedad y las 5 con moho gris y pudrición blanda, que antes se excluían, ahora entran a sano y a moho gris.

**Hojas de verificación.** En `docs/verificacion/` están las imágenes excluidas a simple vista, tomadas de las carpetas originales del Drive:

- `duplicados_mango.jpg`, `duplicados_banano.jpg` y `duplicados_fresa.jpg`: cada duplicado junto a la imagen que quedó; en los 196 pares los píxeles son idénticos.
- `banano_sano_stock.jpg`: las 163 fotos de stock de banano sano.
- `fresas_excluidas.jpg`: las 59 fotos propias de fresa excluidas, agrupadas por motivo y con sus etiquetas.

**Imágenes casi idénticas.** Además de los duplicados exactos, hay 150 pares de imágenes que son la misma foto guardada con otra compresión: 68 en la antracnosis de fresa, 1 en el moho gris de fresa, 46 en las pecas de banano, 3 en la antracnosis de banano y 32 en mango. No se excluyeron, pero la partición las mantiene siempre juntas (sección 7.1 del notebook).

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
| `aumento` | 1 si la imagen es un aumento (rotación) de otra foto; 0 si es una imagen real |

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

Una fila por imagen usada para entrenar o evaluar (las imágenes reales y los aumentos que entran a train), con las columnas `archivo`, `fruta`, `clase`, `origen`, `grupo`, `particion` (`train`, `validation` o `test`) y `aumento`. Las imágenes del mismo `grupo` van siempre a la misma partición.

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
- **Aumentos:** solo en train, y solo si su foto original también quedó en train (o no está en el dataset).

| Fruta | Train | Validation | Test | Total |
|---|---|---|---|---|
| Mango | 770 | 165 | 166 | 1.101 |
| Banano | 946 | 198 | 226 | 1.370 |
| Fresa | 782 | 150 | 140 | 1.072 |
| **Total** | **2.498** | **513** | **532** | **3.543** |

Con los 259 aumentos de antracnosis de fresa, train tiene 2.757 imágenes y `particiones.csv` 3.802 filas. En train la fresa queda con 354 sanas, 292 de moho gris y 395 de antracnosis (136 reales y 259 aumentos).

En la fresa, el test tiene 140 imágenes: 67 sanas, 42 de moho gris y 31 de antracnosis. De ellas, 34 son las fotos propias de Sofía (27 sanas y 7 con moho gris).

## Cómo regenerarlo

Con las carpetas del Drive descargadas en `~/Downloads`, desde la raíz del repositorio:

```bash
ORIGEN=("$HOME/Downloads/Patologias de Frutas en Postcocecha" \
        "$HOME/Downloads/Patologias de Frutas en Postcocecha 2" \
        "$HOME/Downloads/Patologias de Frutas en Postcocecha 3")
# Descargas posteriores de carpetas de clase sueltas de Dataset/train/ (fresa y mango; banano)
EXTRA=("$HOME/Downloads/drive-download-20261125T172554Z-1-001" \
       "$HOME/Downloads/drive-download-20261125T174856Z-1-001")

# 1. Imágenes, etiquetas.csv y excluidas.csv
python3 scripts/organizar_dataset.py --origen "${ORIGEN[@]}" --origen-extra "${EXTRA[@]}" \
    --etiquetas-fresa docs/etiquetas_fresa_grupo.csv --salida dataset

# 2. particiones.csv: ejecutar la sección 7 de va_analisis.ipynb

# 3. caracteristicas.csv, para la app
python3 scripts/calcular_caracteristicas.py

# 4. Hojas de docs/verificacion/
python3 scripts/hojas_verificacion.py --origen "${ORIGEN[@]}" "${EXTRA[@]}"
```

De las carpetas de `--origen-extra` solo se toman las imágenes que no estaban ya en las de `--origen`. Los scripts solo leen las carpetas de origen; nunca las modifican.
