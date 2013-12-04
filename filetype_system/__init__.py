"""Detect and set filetype and fire the OnFileTypeLoaded event"""
from ..session import Session
from ..event import Event

extension_filetype = {'txt': 'txt', 'py': 'python', 'js': 'javascript', 'hs': 'haskell', 'cs': 'csharp'}


def detect_filetype(session):
    session.filetype = None
    for extension, filetype in extension_filetype.items():
        if session.filename.endswith('.' + extension):
            session.filetype = filetype
    session.OnFileTypeLoaded.fire()

Session.OnFileTypeLoaded = Event()
Session.OnSessionInit.add(detect_filetype)

import logging
logging.info('filetype system loaded')
