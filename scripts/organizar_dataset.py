"""Organiza el dataset limpio del proyecto a partir de las carpetas originales del Drive.

Lee las imágenes de "Patologias de Frutas en Postcocecha" (puede venir partida en
varias carpetas al descargarla del Drive), decide cuáles entran al dataset, las
renombra por fruta y clase, reduce las fotos grandes y escribe dos tablas:

  dataset/etiquetas.csv  -> una fila por imagen incluida
  dataset/excluidas.csv  -> una fila por imagen que no entró, con el motivo

Uso:
  python3 scripts/organizar_dataset.py \
      --origen "~/Downloads/Patologias de Frutas en Postcocecha" \
               "~/Downloads/Patologias de Frutas en Postcocecha 2" \
               "~/Downloads/Patologias de Frutas en Postcocecha 3" \
      --origen-extra "~/Downloads/drive-download-20261125T172554Z-1-001" \
                     "~/Downloads/drive-download-20261125T174856Z-1-001" \
      --etiquetas-fresa docs/etiquetas_fresa_grupo.csv \
      --salida dataset

--origen-extra recibe descargas posteriores de carpetas sueltas de Dataset/train/
(una carpeta por clase, sin el resto del Drive). De ellas solo se toman las
imágenes que no estaban ya en las carpetas de --origen.

Requiere Pillow. Las carpetas de origen no se modifican.
"""
import argparse
import collections
import csv
import hashlib
import os
import shutil
import unicodedata

from PIL import Image, ImageOps

LADO_MAXIMO = 1024      # px del lado mayor para las fotos que se reducen
CALIDAD_JPEG = 90
EXTENSIONES = ('.jpg', '.jpeg', '.png', '.webp', '.avif')

# Carpetas de train del Drive -> (fruta, clase) del dataset limpio.
# banano_corona no aparece porque la clase se descartó.
CLASES = {
    'mango_sano': ('mango', 'sano'),
    'mango_antracnosis': ('mango', 'antracnosis'),
    'mango_sarna': ('mango', 'sarna'),
    'mango_pudricionextremo': ('mango', 'pudricion_pedunculo'),
    'banano_sano': ('banano', 'sano'),
    'banano_antracnosis': ('banano', 'antracnosis'),
    'banano_danomec': ('banano', 'dano_mecanico'),
    'banano_pecas': ('banano', 'pecas'),
    'fresa_antracnosis': ('fresa', 'antracnosis'),
    'fresa_moho_gris': ('fresa', 'moho_gris'),
    'fresa_sano': ('fresa', 'sano'),
}
# Si una misma imagen está guardada en dos clases, queda en la más grave.
GRAVEDAD = ['antracnosis', 'moho_gris', 'sarna', 'pudricion_pedunculo', 'dano_mecanico', 'pecas', 'sano']
PREFIJO_AUMENTO = 'aug_'    # aumentos (rotaciones) que subió el equipo; solo se usan en train
CLASES_DESCARTADAS = {'banano_corona': 'Clase descartada: pudrición de corona'}

# Cada integrante tomó sus fotos con un celular o cámara distinto.
# El modelo de la cámara (metadatos EXIF) identifica las fotos propias.
CAMARAS = {
    'motorola edge 50 pro': 'Andrés Arbeláez',
    'Galaxy A56 5G': 'Diego Cifuentes',
    'SM-A525M': 'Sara Suárez',
    'DMC-FH25': 'Sofía Giraldo',
}
INTEGRANTES = set(CAMARAS.values())

# Columnas de etiquetas del CSV de anotaciones de fresa.
ETIQUETAS_FRESA = ['sana', 'moho_gris_temprano', 'moho_gris_avanzado', 'pudricion_blanda',
                   'antracnosis', 'magulladura', 'deshidratacion', 'inmadura', 'dudoso']


def nfc(texto):
    """macOS guarda los nombres con tildes en forma descompuesta; se normalizan para comparar."""
    return unicodedata.normalize('NFC', texto)


# ---------------------------------------------------------------------------
# 1. Inventario de las carpetas de origen
# ---------------------------------------------------------------------------
def leer_exif(ruta):
    """Devuelve (marca, modelo, fecha AAAA-MM-DD, ancho, alto) de una imagen."""
    with Image.open(ruta) as im:
        ancho, alto = im.size
        exif = im.getexif()
        marca = str(exif.get(271, '')).strip('\x00 ')
        modelo = str(exif.get(272, '')).strip('\x00 ')
        fecha = str(exif.get(306, '') or '')
        try:
            fecha = str(exif.get_ifd(0x8769).get(36867, '') or fecha)
        except Exception:
            pass
    return marca, modelo, fecha[:10].replace(':', '-'), ancho, alto


def registro(ruta, relativa, nombre, carpeta_clase, en_carpeta_integrante=None):
    """Lee una imagen candidata y devuelve su registro."""
    with open(ruta, 'rb') as fh:
        md5 = hashlib.md5(fh.read()).hexdigest()
    r = {'ruta': ruta, 'ruta_original': relativa, 'nombre': nfc(nombre), 'carpeta': carpeta_clase,
         'md5': md5, 'ancho': 0, 'alto': 0, 'marca': '', 'integrante': '', 'camara': '', 'fecha': '',
         'aumento': nombre.startswith(PREFIJO_AUMENTO), 'danado': False}
    try:
        marca, modelo, fecha, ancho, alto = leer_exif(ruta)
    except Exception:
        r['danado'] = True           # archivo vacío o que no se puede abrir
        return r
    integrante = next((v for k, v in CAMARAS.items() if k in modelo), '')
    if en_carpeta_integrante:
        assert integrante == en_carpeta_integrante, f'Cámara no coincide con la carpeta: {relativa}'
    camara = modelo if modelo.lower().startswith(marca.lower()) else f'{marca} {modelo}'
    r.update({'ancho': ancho, 'alto': alto, 'marca': marca, 'integrante': integrante,
              'camara': camara.strip() if integrante else '', 'fecha': fecha if integrante else ''})
    return r


def inventariar(origenes, extras=()):
    """Recorre las carpetas del Drive y devuelve un registro por imagen candidata.

    Candidatas: las imágenes de Dataset/train/<clase>/ y las fotos propias de
    fresa que siguen en Dataset/<integrante>/. Los mosaicos de revisión no entran.

    Las carpetas extra son descargas posteriores de carpetas de clase sueltas
    (<clase>/<imagen>). Como repiten lo que ya estaba en el Drive, de ellas solo
    se toman las imágenes cuyo contenido no estaba ya en la misma clase.
    """
    registros = []
    for origen in origenes:
        for carpeta, _, archivos in os.walk(origen):
            for nombre in sorted(archivos):
                if not nombre.lower().endswith(EXTENSIONES):
                    continue
                ruta = os.path.join(carpeta, nombre)
                relativa = nfc(os.path.relpath(ruta, origen))
                partes = relativa.split('/')
                if len(partes) < 3 or partes[0] != 'Dataset':
                    continue
                if partes[1] == 'train':
                    registros.append(registro(ruta, relativa, nombre, partes[2]))
                elif partes[1] in INTEGRANTES:
                    registros.append(registro(ruta, relativa, nombre, 'fresa_propia', partes[1]))
    for origen in extras:
        ya_estaban = {(r['carpeta'], r['md5']) for r in registros}
        for carpeta, _, archivos in os.walk(origen):
            for nombre in sorted(archivos):
                if not nombre.lower().endswith(EXTENSIONES):
                    continue
                ruta = os.path.join(carpeta, nombre)
                partes = nfc(os.path.relpath(ruta, origen)).split('/')
                if len(partes) != 2 or partes[0] not in set(CLASES) | set(CLASES_DESCARTADAS):
                    continue
                r = registro(ruta, 'Dataset/train/' + '/'.join(partes), nombre, partes[0])
                if (r['carpeta'], r['md5']) not in ya_estaban:
                    registros.append(r)
    return registros


def fuente(r):
    """Origen de cada imagen. Las propias se reconocen por la cámara de cada integrante."""
    if r['integrante']:
        return 'Propia'
    if r['carpeta'].startswith('mango_'):
        return 'MangoDHDS (Mendeley Data)'
    if r['carpeta'] == 'fresa_antracnosis' or '.rf.' in r['nombre']:
        return 'Roboflow'
    if 'Screen Shot' in r['nombre']:
        return 'Kaggle (fotos de stock aumentadas)'
    if r['marca'] == 'OPPO':
        return 'Externa sin identificar (cámara OPPO)'
    if r['carpeta'].startswith('banano_') and {r['ancho'], r['alto']} == {1000, 750}:
        return 'Banana and Banana Leaf Dataset (Mendeley Data)'
    if r['carpeta'] == 'banano_pecas':
        return 'Internet (fotos de stock y páginas web)'
    return 'Externa sin identificar'


# ---------------------------------------------------------------------------
# 2. Qué entra al dataset y qué se excluye
# ---------------------------------------------------------------------------
def clase_fresa_propia(fila):
    """Clase de una foto propia de fresa según el CSV de anotaciones.

    Ninguna foto se excluye por tener varias alteraciones: cada una va a la
    clase de la alteración más grave que tenga.
    - Con moho gris (temprano o avanzado) es moho_gris, aunque también tenga
      pudrición blanda, magulladura, deshidratación o fresas sanas.
    - Con antracnosis (y sin moho gris) es antracnosis.
    - Sin enfermedades, con sana, deshidratación, inmadura o magulladura, es
      sano: ni la deshidratación ni la magulladura son enfermedades.
    Quedan fuera las fotos marcadas como dudosas, las que solo tienen pudrición
    blanda (no es una de las tres clases) y las que no tienen etiqueta.

    Devuelve (clase, None) si la foto entra, o (None, motivo) si no.
    """
    tiene = lambda k: fila[k] == '1'
    if tiene('dudoso'):
        return None, 'Fresa marcada como dudosa'
    if tiene('moho_gris_temprano') or tiene('moho_gris_avanzado'):
        return 'moho_gris', None
    if tiene('antracnosis'):
        return 'antracnosis', None
    if tiene('pudricion_blanda'):
        return None, 'Fresa con pudrición blanda, que no es una de las tres clases'
    if tiene('sana') or tiene('deshidratacion') or tiene('inmadura') or tiene('magulladura'):
        return 'sano', None
    return None, 'Fresa sin etiqueta'


def decidir(registros, etiquetas_fresa):
    """Separa los registros en incluidos y excluidos, con el motivo de cada exclusión."""
    anotaciones = {}
    with open(etiquetas_fresa, encoding='utf-8-sig') as fh:
        for fila in csv.DictReader(fh):
            anotaciones[nfc(fila['archivo'])] = fila

    # Una misma imagen (mismo md5) guardada en dos clases queda una sola vez, en la más grave.
    por_md5 = collections.defaultdict(set)
    for r in registros:
        if r['carpeta'] in CLASES:
            por_md5[r['md5']].add(r['carpeta'])
    mas_grave = lambda carpetas: min(carpetas, key=lambda c: GRAVEDAD.index(CLASES[c][1]))

    incluidos, excluidos, vistos = [], [], {}
    # Se ordena para que, entre duplicados, se conserve el archivo que no dice "copy".
    for r in sorted(registros, key=lambda x: ('copy' in x['nombre'].lower(), x['carpeta'], x['nombre'])):
        r['fuente'] = fuente(r)
        r['etiquetas_fresa'] = ''
        if r['danado']:
            r['motivo'] = 'Archivo dañado: no se puede abrir'
            excluidos.append(r)
            continue
        if r['carpeta'] in CLASES_DESCARTADAS:
            r['motivo'] = CLASES_DESCARTADAS[r['carpeta']]
            excluidos.append(r)
            continue
        if r['carpeta'] == 'fresa_propia':
            fila = anotaciones[r['nombre']]
            r['etiquetas_fresa'] = '+'.join(k for k in ETIQUETAS_FRESA if fila[k] == '1')
            clase, motivo = clase_fresa_propia(fila)
            if clase is None:
                r['motivo'] = motivo
                excluidos.append(r)
                continue
            r['fruta'], r['clase'] = 'fresa', clase
            incluidos.append(r)
            continue
        r['fruta'], r['clase'] = CLASES[r['carpeta']]
        if len(por_md5[r['md5']]) > 1 and r['carpeta'] != mas_grave(por_md5[r['md5']]):
            r['motivo'] = ('Copia de una imagen guardada en dos clases (' + ' y '.join(sorted(por_md5[r['md5']]))
                           + '): quedó en ' + mas_grave(por_md5[r['md5']]))
            excluidos.append(r)
        elif r['fuente'].startswith('Kaggle'):
            r['motivo'] = 'Foto de stock aumentada, sin la imagen original'
            excluidos.append(r)
        elif r['md5'] in vistos:
            r['duplicado_de'] = vistos[r['md5']]
            r['motivo'] = 'Duplicado exacto'
            excluidos.append(r)
        else:
            vistos[r['md5']] = r
            incluidos.append(r)
    return incluidos, excluidos


# ---------------------------------------------------------------------------
# 3. Renombrar, copiar y documentar
# ---------------------------------------------------------------------------
def escribir_imagen(r, destino):
    """Copia la imagen tal cual o la reduce a LADO_MAXIMO px.

    Las fotos propias siempre se vuelven a guardar: se endereza la orientación
    del celular y se quitan los metadatos EXIF (que pueden incluir ubicación).
    Las externas pequeñas se copian sin cambios.
    """
    grande = max(r['ancho'], r['alto']) > LADO_MAXIMO
    if not grande and not r['marca'] and r['nombre'].lower().endswith(('.jpg', '.jpeg')):
        shutil.copyfile(r['ruta'], destino)
        return r['ancho'], r['alto']
    with Image.open(r['ruta']) as original:
        im = ImageOps.exif_transpose(original)
        if im.mode in ('P', 'LA', 'RGBA', 'PA'):          # las transparencias se rellenan de blanco
            im = im.convert('RGBA')
            fondo = Image.new('RGBA', im.size, 'white')
            im = Image.alpha_composite(fondo, im)
        im = im.convert('RGB')
    im.thumbnail((LADO_MAXIMO, LADO_MAXIMO), Image.LANCZOS)
    im.save(destino, 'JPEG', quality=CALIDAD_JPEG, optimize=True)
    return im.size


def numerar_y_copiar(incluidos, salida):
    """Nombra cada imagen como <fruta>_<clase>_<NNNN>.jpg: propias, externas y, al final, aumentos."""
    por_clase = collections.defaultdict(list)
    for r in incluidos:
        por_clase[(r['fruta'], r['clase'])].append(r)
    for (fruta, clase), grupo in sorted(por_clase.items()):
        os.makedirs(os.path.join(salida, fruta, clase), exist_ok=True)
        grupo.sort(key=lambda x: (x['fuente'] != 'Propia', x['aumento'], x['integrante'], x['fecha'], x['fuente'], x['nombre']))
        for i, r in enumerate(grupo, 1):
            r['archivo'] = f'{fruta}/{clase}/{fruta}_{clase}_{i:04d}.jpg'
            r['ancho_final'], r['alto_final'] = escribir_imagen(r, os.path.join(salida, r['archivo']))


def escribir_tablas(incluidos, excluidos, salida):
    prefijo = 'Patologias de Frutas en Postcocecha/'
    columnas = ['archivo', 'fruta', 'clase', 'origen', 'fuente', 'integrante', 'camara',
                'fecha_captura', 'ancho', 'alto', 'ruta_original', 'md5_original', 'etiquetas_fresa', 'aumento']
    with open(os.path.join(salida, 'etiquetas.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(columnas)
        for r in sorted(incluidos, key=lambda x: x['archivo']):
            w.writerow([r['archivo'], r['fruta'], r['clase'],
                        'propia' if r['fuente'] == 'Propia' else 'externa', r['fuente'],
                        r['integrante'], r['camara'], r['fecha'], r['ancho_final'], r['alto_final'],
                        prefijo + r['ruta_original'], r['md5'], r['etiquetas_fresa'],
                        int(r['aumento'])])
    columnas = ['ruta_original', 'fruta', 'carpeta_original', 'origen', 'fuente', 'integrante',
                'fecha_captura', 'motivo', 'duplicado_de_original', 'duplicado_de_archivo',
                'md5_original', 'etiquetas_fresa']
    with open(os.path.join(salida, 'excluidas.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(columnas)
        for r in sorted(excluidos, key=lambda x: (x['motivo'], x['ruta_original'])):
            motivo, original, nuevo = r['motivo'], '', ''
            if 'duplicado_de' in r:
                # Se nombra la imagen que quedó por su nombre original y por su nombre nuevo
                original = prefijo + r['duplicado_de']['ruta_original']
                nuevo = r['duplicado_de']['archivo']
                motivo = (f"Duplicado exacto de {r['duplicado_de']['nombre']} "
                          f"(en el dataset: {nuevo})")
            w.writerow([prefijo + r['ruta_original'], r['carpeta'].split('_')[0], r['carpeta'],
                        'propia' if r['fuente'] == 'Propia' else 'externa', r['fuente'],
                        r['integrante'], r['fecha'], motivo, original, nuevo, r['md5'], r['etiquetas_fresa']])


def resumen(incluidos, excluidos):
    """Imprime los conteos en Markdown, listos para el README y el notebook."""
    tabla = collections.defaultdict(lambda: [0, 0, 0])
    for r in incluidos:
        tabla[(r['fruta'], r['clase'])][2 if r['aumento'] else 0 if r['fuente'] == 'Propia' else 1] += 1
    print('| Fruta | Clase | Propias | Externas | Aumentos | Total |')
    print('|---|---|---|---|---|---|')
    total = [0, 0, 0]
    for fruta in ['mango', 'banano', 'fresa']:
        sub = [0, 0, 0]
        for (f, clase), fila in sorted(tabla.items()):
            if f == fruta:
                print(f'| {fruta} | {clase} | {fila[0]} | {fila[1]} | {fila[2]} | {sum(fila)} |')
                sub = [a + b for a, b in zip(sub, fila)]
        print(f'| **{fruta}** | **total** | **{sub[0]}** | **{sub[1]}** | **{sub[2]}** | **{sum(sub)}** |')
        total = [a + b for a, b in zip(total, sub)]
    print(f'| **Total** | | **{total[0]}** | **{total[1]}** | **{total[2]}** | **{sum(total)}** |')
    print()
    for motivo, n in collections.Counter(r['motivo'].split(':')[0].split(' (')[0] for r in excluidos).most_common():
        print(f'- {motivo}: {n}')
    print()
    for f, n in collections.Counter(r['fuente'] for r in incluidos).most_common():
        print(f'- {f}: {n}')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--origen', nargs='+', required=True, help='Carpetas descargadas del Drive')
    p.add_argument('--origen-extra', nargs='*', default=[],
                   help='Descargas posteriores de carpetas de clase sueltas de Dataset/train/')
    p.add_argument('--etiquetas-fresa', required=True, help='CSV de anotaciones de las fotos propias de fresa')
    p.add_argument('--salida', default='dataset', help='Carpeta del dataset limpio')
    a = p.parse_args()
    origenes = [os.path.expanduser(o) for o in a.origen]
    for fruta in ['mango', 'banano', 'fresa']:          # se reconstruye desde cero
        shutil.rmtree(os.path.join(a.salida, fruta), ignore_errors=True)
    registros = inventariar(origenes, [os.path.expanduser(o) for o in a.origen_extra])
    incluidos, excluidos = decidir(registros, os.path.expanduser(a.etiquetas_fresa))
    assert len(incluidos) + len(excluidos) == len(registros)
    numerar_y_copiar(incluidos, a.salida)
    escribir_tablas(incluidos, excluidos, a.salida)
    print(f'Imágenes revisadas: {len(registros)} | incluidas: {len(incluidos)} | excluidas: {len(excluidos)}\n')
    resumen(incluidos, excluidos)


if __name__ == '__main__':
    main()
