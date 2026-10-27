# VisionArtificial

Proyecto del curso Visión Artificial (Universidad Nacional de Colombia, sede Medellín, 2026-2S): clasificación de alteraciones poscosecha en frutas con imágenes.

## Contenido

| Ruta | Qué hay |
|---|---|
| `dataset/` | Imágenes de mango, banano y fresa organizadas por fruta y clase, con sus tablas de etiquetas. Ver `dataset/README.md`. |
| `docs/` | Atlas de lesiones del banano y de la fresa, Avance #1, bitácora del proyecto y anotaciones de las fotos propias de fresa. |
| `docs/mosaicos_revision/` | Mosaicos de las fotos propias que se usaron para clasificarlas, por fruta e integrante. Los IDs corresponden al inventario de la sección 6 del notebook, con los nombres de archivo originales. |
| `figuras/` | Gráficos y mosaico de muestra generados en la sección 8 del notebook. |
| `app/` | App de Streamlit para presentar el análisis del dataset (`app.py`) y operaciones de imagen organizadas por clase del curso (`vision.py`). |
| `scripts/organizar_dataset.py` | Script que arma `dataset/` a partir de las carpetas originales del Drive. |
| `scripts/calcular_caracteristicas.py` | Script que mide las características de cada imagen y escribe `dataset/caracteristicas.csv`, que usa la app. |
| `va_analisis.ipynb` | Notebook del proyecto. La sección 8 carga el dataset, cuenta las imágenes por carpeta, fruta y clase, y analiza su origen, tamaño, color y fondo. |

## App de Streamlit

La app presenta el análisis del dataset en nueve secciones: inicio, composición del dataset, explorador de imágenes, imagen digital y color, procesamiento, segmentación, separabilidad, partición, y hallazgos y limitaciones. Las secciones de imagen digital, procesamiento y segmentación siguen las clases 2 a 5 del curso y permiten aplicar cada operación a cualquier imagen del dataset.

Para ejecutarla, desde la raíz del repositorio:

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

Si cambia el dataset, primero hay que volver a calcular las características con `python3 scripts/calcular_caracteristicas.py`.

Para publicarla en Streamlit Community Cloud: entrar con la cuenta de GitHub dueña del repositorio, crear una app nueva con este repositorio, la rama `main` y el archivo `app/app.py`.

