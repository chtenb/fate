"""
This module contains functions which act on the user interface.
We shall call them ui actors.
"""
import re

from .document import Document, documentlist
from . import actions
from .selectors import SelectPattern, SelectLocalPattern


def open_document(document):
    """Open a new document."""
    filename = document.ui.prompt('Filename: ')
    Document(filename)
actions.open_document = open_document


def quit_document(document):
    """Close current document."""
    if not document.saved:
        while 1:
            answer = document.ui.prompt('Unsaved changes! Really quit? (y/n)')
            if answer == 'y':
                document.quit()
                break
            if answer == 'n':
                break
    else:
        document.quit()
actions.quit_document = quit_document


def force_quit(document):
    document.quit()
actions.force_quit = force_quit


def next_document(document):
    """Go to the next document."""
    index = documentlist.index(document)
    ndocument = documentlist[(index + 1) % len(documentlist)]
    ndocument.ui.activate()
actions.next_document = next_document


def previous_document(document):
    """Go to the previous document."""
    index = documentlist.index(document)
    ndocument = documentlist[(index - 1) % len(documentlist)]
    ndocument.ui.activate()
actions.previous_document = previous_document


def local_find(document):
    char = document.ui.getchar()
    SelectLocalPattern(re.escape(char), document)(document)
actions.local_find = local_find


def local_find_backwards(document):
    char = document.ui.getchar()
    SelectLocalPattern(re.escape(char), document, reverse=True)(document)
actions.local_find_backwards = local_find_backwards


def search(document):
    document.search_pattern = document.ui.prompt('/')
    if document.search_pattern:
        try:
            SelectPattern(document.search_pattern, document)(document)
        except re.error as e:
            document.ui.notify(str(e))
actions.search = search


def search_current_content(document):
    document.search_pattern = re.escape(document.selection.content(document)[-1])
    SelectPattern(document.search_pattern, document)(document)
actions.search_current_content = search_current_content


def search_next(document):
    if document.search_pattern:
        SelectPattern(document.search_pattern, document)(document)
actions.search_next = search_next


def search_previous(document):
    if document.search_pattern:
        SelectPattern(document.search_pattern, document, reverse=True)(document)
actions.search_previous = search_previous


def command_mode(document):
    document.ui.command_mode()
actions.command_mode = command_mode
