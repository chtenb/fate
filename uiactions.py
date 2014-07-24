"""
This module contains functions which act on the user interface.
We shall call them ui actors.
"""
import re

from .session import Session, sessionlist
from . import actions
from .selectors import SelectPattern, SelectLocalPattern


def open_session(session):
    """Open a new session."""
    filename = session.ui.prompt('Filename: ')
    Session(filename)
actions.open_session = open_session


def quit_session(session):
    """Close current session."""
    if not session.saved:
        while 1:
            answer = session.ui.prompt('Unsaved changes! Really quit? (y/n)')
            if answer == 'y':
                session.quit()
            if answer == 'n':
                break
    else:
        session.quit()
actions.quit_session = quit_session


def next_session(session):
    """Go to the next session."""
    index = sessionlist.index(session)
    nsession = sessionlist[(index + 1) % len(sessionlist)]
    nsession.ui.activate()
actions.next_session = next_session


def previous_session(session):
    """Go to the previous session."""
    index = sessionlist.index(session)
    nsession = sessionlist[(index - 1) % len(sessionlist)]
    nsession.ui.activate()
actions.previous_session = previous_session


def local_find(session):
    char = session.ui.getchar()
    SelectLocalPattern(re.escape(char), session)(session)
actions.local_find = local_find


def local_find_backwards(session):
    char = session.ui.getchar()
    SelectLocalPattern(re.escape(char), session, reverse=True)(session)
actions.local_find_backwards = local_find_backwards


def search(session):
    session.search_pattern = session.ui.prompt('/')
    if session.search_pattern:
        try:
            SelectPattern(session.search_pattern, session)(session)
        except re.error as e:
            session.ui.notify(str(e))
actions.search = search


def search_current_content(session):
    session.search_pattern = re.escape(session.selection.content(session)[-1])
    SelectPattern(session.search_pattern, session)(session)
actions.search_current_content = search_current_content


def search_next(session):
    if session.search_pattern:
        SelectPattern(session.search_pattern, session)(session)
actions.search_next = search_next


def search_previous(session):
    if session.search_pattern:
        SelectPattern(session.search_pattern, session, reverse=True)(session)
actions.search_previous = search_previous


def command_mode(session):
    session.ui.command_mode()
actions.command_mode = command_mode

