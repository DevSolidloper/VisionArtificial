# VisionArtificial

Proyecto del curso Visión Artificial (Universidad Nacional de Colombia, sede Medellín, 2026-2S): clasificación de alteraciones poscosecha en frutas con imágenes.

## Contenido

| Ruta | Qué hay |
|---|---|
| `dataset/` | Imágenes de mango, banano y fresa organizadas por fruta y clase, con sus tablas de etiquetas. Ver `dataset/README.md`. |
| `docs/` | Atlas de lesiones del banano y de la fresa, Avance #1, bitácora del proyecto y anotaciones de las fotos propias de fresa. |
| `docs/mosaicos_revision/` | Mosaicos de las fotos propias que se usaron para clasificarlas, por fruta e integrante. Los IDs corresponden al inventario de la sección 6 del notebook, con los nombres de archivo originales. |
| `figuras/` | Gráficos y mosaico de muestra generados en la sección 8 del notebook. |
| `scripts/organizar_dataset.py` | Script que arma `dataset/` a partir de las carpetas originales del Drive. |
| `va_analisis.ipynb` | Notebook del proyecto. La sección 8 carga el dataset, cuenta las imágenes por carpeta, fruta y clase, y analiza su origen, tamaño, color y fondo. |
