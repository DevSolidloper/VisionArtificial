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
| Fresa | Sano | 116 | 0 | 116 |
| | Moho gris | 53 | 0 | 53 |
| | Antracnosis | 0 | 110 | 110 |
| | **Total fresa** | **169** | **110** | **279** |
| **Total** | | **483** | **1.998** | **2.481** |

Las fotos propias son el 0 % del mango, el 28,5 % del banano, el 60,6 % de la fresa y el 19,5 % del total.

**Limitación de la fresa.** Cada clase proviene de una sola fuente: sano y moho gris, de fotos propias; antracnosis, de Roboflow. Un modelo podría aprender a distinguir la fuente y no la alteración, así que sus métricas deben reportarse por fuente.

## Fuentes

| Fuente | Fruta y clases | Imágenes |
|---|---|---|
| Fotos propias del equipo | Banano (todas las clases) y fresa (sano y moho gris) | 483 |
| MangoDHDS (Mendeley Data) | Mango (todas las clases) | 1.101 |
| Banana and Banana Leaf Dataset (Mendeley Data) | Banano: antracnosis, daño mecánico y sano | 759 |
| Roboflow | Fresa: antracnosis | 110 |
| Externa sin identificar, cámara OPPO (archivos `Day_`) | Banano: pecas | 15 |
| Externa sin identificar (640 × 480 y 390 × 520 px) | Banano: antracnosis (12) y daño mecánico (1) | 13 |

**Fotos propias.** Las frutas se compraron en la Plaza Minorista de Medellín y en la Central Mayorista de Antioquia, y cada integrante fotografió las suyas día a día con su celular o cámara, siguiendo el protocolo de captura del Avance #1 (`docs/`). Cada foto propia se identifica por la cámara registrada en sus metadatos:

| Integrante | Cámara | Banano | Fresa |
|---|---|---|---|
| Andrés Arbeláez | Motorola Edge 50 Pro | 112 | 57 |
| Diego Cifuentes | Samsung Galaxy A56 5G | 137 | 17 |
| Sara Suárez | Samsung Galaxy A52 (SM-A525M) | 0 | 68 |
| Sofía Giraldo | Panasonic DMC-FH25 | 65 | 27 |

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

Las fotos propias de fresa se clasificaron con las anotaciones de `docs/etiquetas_fresa_grupo.csv`, que registran todas las alteraciones visibles en cada foto. Una foto entra a una clase solo si esa es su única etiqueta:

- **sano:** solo *sana*, o *sana* con *inmadura*.
- **moho_gris:** solo *moho gris temprano*, *moho gris avanzado* o ambas.
- **antracnosis:** solo *antracnosis*.

Las fotos con deshidratación, magulladura, pudrición blanda, *dudoso* o con más de una clase quedan fuera.

## Imágenes excluidas

Hay 648 imágenes que no entraron. Todas siguen en el Drive y aparecen en `excluidas.csv` con su ruta original y el motivo. En los duplicados, las columnas `duplicado_de_original` y `duplicado_de_archivo` dicen cuál es la imagen que sí quedó, con su nombre original y con su nombre en el dataset. Por ejemplo, `He163.jpg` es una copia de `He10.jpg`, que quedó como `mango/sano/mango_sano_0002.jpg`.

Para revisarlas a simple vista, `docs/verificacion/` tiene una hoja por fruta con cada duplicado junto a la imagen original que quedó (`duplicados_mango.jpg`, `duplicados_banano.jpg` y `duplicados_fresa.jpg`; en los 169 pares los píxeles son idénticos) y una hoja con las 274 fotos propias de fresa excluidas, agrupadas por motivo y con sus etiquetas (`fresas_excluidas.jpg`). Se generan con `scripts/hojas_verificacion.py` a partir de las carpetas originales del Drive.

| Motivo | Imágenes |
|---|---|
| Fotos propias de fresa con varias etiquetas o fuera de las tres clases | 274 |
| Duplicados exactos: se conservó una sola copia (99 de mango, que ya venían repetidas en MangoDHDS; 40 de fresa y 30 de banano) | 169 |
| Fotos de stock de banano sano, aumentadas (rotadas o volteadas) y sin la imagen original | 163 |
| Clase descartada: pudrición de corona del banano | 36 |
| Misma imagen guardada en dos clases de banano (3 pares) | 6 |
| **Total** | **648** |

## Columnas de `etiquetas.csv`

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

## Partición en train, validation y test

La partición está en `particiones.csv`, con una fila por imagen, y se genera en la sección 7 de `va_analisis.ipynb`. Incluye las tres frutas.

Las fotos propias son series diarias de las mismas frutas, así que no se reparten al azar: las de Sofía Giraldo van todas a test, y las de los demás integrantes se reparten entre train y validation por sesión (fruta, integrante y día). Las externas se reparten al azar, 70/15/15 dentro de cada clase, manteniendo juntas las imágenes casi idénticas. El resultado es 1.718 imágenes en train, 368 en validation y 395 en test.

## Cómo regenerarlo

Con las carpetas del Drive descargadas en `~/Downloads`:

```bash
python3 scripts/organizar_dataset.py \
    --origen "$HOME/Downloads/Patologias de Frutas en Postcocecha" \
             "$HOME/Downloads/Patologias de Frutas en Postcocecha 2" \
             "$HOME/Downloads/Patologias de Frutas en Postcocecha 3" \
    --etiquetas-fresa docs/etiquetas_fresa_grupo.csv \
    --salida dataset
```

El script solo lee las carpetas de origen y vuelve a crear las carpetas de imágenes, `etiquetas.csv` y `excluidas.csv`. Después hay que volver a ejecutar la sección 7 del notebook para regenerar `particiones.csv`.
