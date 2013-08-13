from .selection import Selection
from ..session import Session

__dependencies__ = ['filetype_system']

def init(session):
    session.selection = Selection(session)

def main():
    Session.OnInit.add(init)
