"""Detect and set filetype and fire the OnFileTypeLoaded event"""
from ..document import Document
from ..event import Event

extension_filetype = {'txt': 'txt', 'py': 'python', 'js': 'javascript', 'hs': 'haskell', 'cs': 'csharp'}


def detect_filetype(document):
    document.filetype = None
    for extension, filetype in extension_filetype.items():
        if document.filename.endswith('.' + extension):
            document.filetype = filetype
    document.OnFileTypeLoaded.fire(document)

Document.OnFileTypeLoaded = Event()
Document.OnDocumentInit.add(detect_filetype)

import logging
logging.info('filetype system loaded')
