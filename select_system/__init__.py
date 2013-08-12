from protexted.select_system.selection import Selection
from protexted.session import Session

def init(session):
    session.selection = Selection(session)

Session.OnInit.add(init)
