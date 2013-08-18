from ..session import Session
from ..event import Event

def main():
    Session.OnFileTypeLoaded = Event()
    Session.OnSessionInit.add(detect_filetype)

def detect_filetype(session):
    session.filetype = None
    session.OnFileTypeLoaded.fire()
