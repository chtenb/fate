from ..session import Session
from .. import filetype_system
from .. import undo_system
from .. import labeling_system


def session_init(session):
    session.OnFileTypeLoaded.add(custom_filetypes)

Session.OnSessionInit.add(session_init)

def custom_filetypes(session):
    if session.filename == "TODO":
        session.filetype = "todo"
