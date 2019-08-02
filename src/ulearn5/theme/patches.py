# -*- coding: utf-8 -*-
from plone.memoize.view import memoize

import os

ICONS_DIR = os.path.join(os.path.dirname(__file__), 'theme/assets/icons')
PREFIX = '++theme++ulearn5/assets/icons/'

AUDIO = ['mp3', 'flac', 'mid', 'midi', 'wav', 'wma', 'cda', 'ogm', 'aac', 'ac3', 'aym', 'm4a', 'oga']

VIDEO = ['avi', 'mp4', 'mpeg', 'asl', 'lsf', 'asx', 'bik', 'smk', 'div', 'divx', 'dvd', 'wob', 'mgw',
         'ivf', 'm1v', 'mp2v', 'mpa', 'mpe', 'mpg', 'mpv2', 'mox', 'qt', 'qtl', 'rpm', 'wm', 'wmv',
         '3gp', 'flv', 'm4v', 'mkv', 'mov', 'ogv', 'webm', 'f4v', 'ogg', 'swf', 'rm']

IMAGEN = ['png', 'jpg', 'jpeg', 'svg', 'gif', 'bmp', 'psd', 'ico', 'ai', 'cdr', 'dwg', 'raw', 'nef']

TEXTO = ['txt', 'rst', 'rtf', 'text']

LECTURA = ['pdf', 'epub', 'azw', 'ibook', 'kf8']

DOCUMENTACION = ['doc', 'docx', 'odt', 'sxg', 'sxw']

HOJA_CALCULO = ['xls', 'xlsx', 'ods', 'csv', 'sxc']

PRESENTACION = ['ppt', 'pptx', 'odp', 'sxi']

IMAGEN_DISCO = ['iso', 'mds']

CODIGO = ['c', 'c++', 'java', 'py', 'php', 'html', 'css', 'less', 'scss']

COMPRIMIDO = ['zip', 'rar', 'tar', 'gz', 'gzip', 'tgz', '7z']

FUENTE = ['ttf', 'ttc']

FIRMA = ['cades', 'xades', 'pades', 'ooxml', 'odf']


@memoize
def getMimeTypeIcon(self, content_file):
    filetype = content_file.filename.split('.')[1].lower()
    if filetype in AUDIO:
        mimetype = 'file-audio-ulearn'
    elif filetype in VIDEO:
        mimetype = 'file-video-ulearn'
    elif filetype in IMAGEN:
        mimetype = 'file-image-ulearn'
    elif filetype in TEXTO:
        mimetype = 'file-alt-ulearn'
    elif filetype in LECTURA:
        mimetype = 'file-pdf-ulearn'
    elif filetype in DOCUMENTACION:
        mimetype = 'file-word-ulearn'
    elif filetype in HOJA_CALCULO:
        mimetype = 'file-excel-ulearn'
    elif filetype in PRESENTACION:
        mimetype = 'file-powerpoint-ulearn'
    elif filetype in IMAGEN_DISCO:
        mimetype = 'compact-disc-ulearn'
    elif filetype in CODIGO:
        mimetype = 'file-code-ulearn'
    elif filetype in COMPRIMIDO:
        mimetype = 'file-archive-ulearn'
    elif filetype in FUENTE:
        mimetype = 'font-ulearn'
    elif filetype in FIRMA:
        mimetype = 'file-signature-ulearn'
    else:
        mimetype = filetype

    icon_path = '%s.svg' % mimetype
    if os.path.exists(os.path.join(ICONS_DIR, icon_path)):
        return PREFIX + icon_path
    else:
        icon_path = '%s.png' % mimetype
        if os.path.exists(os.path.join(ICONS_DIR, icon_path)):
            return PREFIX + icon_path
    return PREFIX + 'file-ulearn.svg'


def MimeTypeIcon(self):
    return getMimeTypeIcon(self, self.file)
