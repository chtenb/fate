from ..session import Session
from ..event import Event

def detect_filetype(session):
    session.filetype = None
    if session.filename.endswith('.txt'):
        session.filetype = 'txt'
    session.OnFileTypeLoaded.fire()

Session.OnFileTypeLoaded = Event()
Session.OnSessionInit.add(detect_filetype)
