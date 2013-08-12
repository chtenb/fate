from protexted.select_system.selection import Selection

def init(session):
    session.selection = Selection(session)
