from ..session import Session
from ..event import Event

def detect_filetype(session):
    session.filetype = None
    session.OnFileTypeLoaded.fire()

Session.OnFileTypeLoaded = Event()
Session.OnSessionInit.add(detect_filetype)
