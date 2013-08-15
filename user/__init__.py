__dependencies__ = ['filetype_system']

from ..session import Session

def main():
    Session.OnSessionInit.add(session_init)

def session_init(session):
    session.OnFileTypeLoaded.add(custom_filetypes)

def custom_filetypes(session):
    if session.filename == "TODO":
        session.filetype = "todo"
