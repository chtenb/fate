"""Detect and set filetype and fire the OnFileTypeLoaded event"""
from ..document import Document
from ..event import Event
from logging import debug

extension_filetype = {
    'txt': 'txt',
    'py': 'python',
    'js': 'javascript',
    'hs': 'haskell',
    'cs': 'csharp'
}


def detect_filetype(doc):
    doc.filetype = None
    for extension, filetype in extension_filetype.items():
        if doc.filename.endswith('.' + extension):
            debug('Filetype detected')
            doc.filetype = filetype
    doc.OnDocumentInit.add_for_once(doc.OnFileTypeLoaded.fire)

Document.OnFileTypeLoaded = Event('OnFileTypeLoaded')
Document.OnDocumentInit.add(detect_filetype)

import logging
logging.info('filetype system loaded')
