"""
This module contains functions which act on the user interface.
We shall call them ui actors.
"""
from fate import selectors
from .session import Session, session_list
import re

# The following actions have to be converted to interactive actions or something else


def open_session(session):
    """Open a new session."""
    filename = session.ui.prompt('Filename: ')
    Session(filename)


def quit_session(session):
    """Close current session."""
    if not session.saved:
        session.ui.status_win.draw_status('Unsaved changes! Really quit? (y/n)')
        while 1:
            char = session.ui.getchar()
            if char == 'y':
                session.quit()
            if char == 'n':
                break
    else:
        session.quit()


def next_session(session):
    """Go to the next session."""
    index = session_list.index(session)
    nsession = session_list[(index + 1) % len(session_list)]
    session.ui.deactivate()
    nsession.ui.activate()


def previous_session(session):
    """Go to the previous session."""
    index = session_list.index(session)
    nsession = session_list[(index - 1) % len(session_list)]
    session.ui.deactivate()
    nsession.ui.activate()


def local_find(session):
    char = session.ui.getchar()
    selectors.SelectLocalPattern(re.escape(char), session)(session)


def local_find_backwards(session):
    char = session.ui.getchar()
    selectors.SelectLocalPattern(re.escape(char), session, reverse=True)(session)


def search(session):
    session.search_pattern = session.ui.prompt('/')
    try:
        selectors.SelectPattern(session.search_pattern, session)(session)
    except re.error as e:
        session.ui.status_win.set_status(str(e))
        session.ui.getchar()
        session.ui.status_win.set_default_status()


def search_current_content(session):
    session.search_pattern = re.escape(session.content(session.selection)[-1])
    selectors.SelectPattern(session.search_pattern, session)(session)


def search_next(session):
    if session.search_pattern:
        selectors.SelectPattern(session.search_pattern, session)(session)


def search_previous(session):
    if session.search_pattern:
        selectors.SelectPattern(session.search_pattern, session, reverse=True)(session)
