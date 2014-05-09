"""
This module contains functions which act on the user interface.
We shall call them ui actors.
"""
from fate import selectors
from .session import Session, session_list
from . import actions
import re


def open_session(session):
    """Open a new session."""
    filename = session.ui.prompt('Filename: ')
    Session(filename)
actions.open_session = open_session


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
actions.quit_session = quit_session


def next_session(session):
    """Go to the next session."""
    index = session_list.index(session)
    nsession = session_list[(index + 1) % len(session_list)]
    session.ui.deactivate()
    nsession.ui.activate()
actions.next_session = next_session


def previous_session(session):
    """Go to the previous session."""
    index = session_list.index(session)
    nsession = session_list[(index - 1) % len(session_list)]
    session.ui.deactivate()
    nsession.ui.activate()
actions.previous_session = previous_session


def local_find(session):
    char = session.ui.getchar()
    selectors.SelectLocalPattern(re.escape(char), session)(session)
actions.local_find = local_find


def local_find_backwards(session):
    char = session.ui.getchar()
    selectors.SelectLocalPattern(re.escape(char), session, reverse=True)(session)
actions.local_find_backwards = local_find_backwards


def search(session):
    session.search_pattern = session.ui.prompt('/')
    try:
        selectors.SelectPattern(session.search_pattern, session)(session)
    except re.error as e:
        session.ui.status_win.set_status(str(e))
        session.ui.getchar()
        session.ui.status_win.set_default_status()
actions.search = search


def search_current_content(session):
    session.search_pattern = re.escape(session.content(session.selection)[-1])
    selectors.SelectPattern(session.search_pattern, session)(session)
actions.search_current_content = search_current_content


def search_next(session):
    if session.search_pattern:
        selectors.SelectPattern(session.search_pattern, session)(session)
actions.search_next = search_next


def search_previous(session):
    if session.search_pattern:
        selectors.SelectPattern(session.search_pattern, session, reverse=True)(session)
actions.search_previous = search_previous


def command_mode(session):
    session.ui.command_win.prompt()
actions.command_mode = command_mode
