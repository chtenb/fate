"""
This module contains functions which act on the user interface.
We shall call them ui actors.
"""
from fate import actors, selectors, operators
from .session import Session, session_list
import re

# The following actions have to be converted to interactive actions or something else


def open_session(session):
    """Open a new session."""
    filename = session.ui.prompt('Filename: ')
    new_session = Session(filename)


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
    next_session = session_list[(index + 1) % len(session_list)]
    next_session.activate()


def previous_session(session):
    """Go to the previous session."""
    index = session_list.index(session)
    next_session = session_list[(index - 1) % len(session_list)]
    next_session.activate()


def local_find(ui):
    char = chr(ui.stdscr.getch())
    selectors.SelectLocalPattern(re.escape(char), ui.session)(ui.session)


def local_find_backwards(ui):
    char = chr(ui.stdscr.getch())
    selectors.SelectLocalPattern(re.escape(char), ui.session, reverse=True)(ui.session)


def search(ui):
    s = ui.session
    s.search_pattern = ui.prompt('/')
    try:
        selectors.SelectPattern(s.search_pattern, s)(s)
    except Exception as e:
        ui.status_win.draw_status(str(e))
        ui.stdscr.getch()


def search_current_content(ui):
    s = ui.session
    s.search_pattern = re.escape(s.content(s.selection)[-1])
    selectors.SelectPattern(s.search_pattern, s)(s)


def search_next(ui):
    s = ui.session
    if s.search_pattern:
        selectors.SelectPattern(s.search_pattern, s)(s)


def search_previous(ui):
    s = ui.session
    if s.search_pattern:
        selectors.SelectPattern(s.search_pattern, s, reverse=True)(s)
