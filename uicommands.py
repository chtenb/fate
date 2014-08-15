"""
This module contains functions which act on the user interface.
We shall call them ui actors.
"""
import re

from .document import Document, documentlist
from . import commands
from .selectors import SelectPattern, SelectLocalPattern


def open_document(document):
    """Open a new document."""
    filename = document.ui.prompt('Filename: ')
    Document(filename)
commands.open_document = open_document


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
commands.quit_document = quit_document


def force_quit(document):
    document.quit()
commands.force_quit = force_quit


def next_document(document):
    """Go to the next document."""
    index = documentlist.index(document)
    ndocument = documentlist[(index + 1) % len(documentlist)]
    ndocument.ui.activate()
commands.next_document = next_document


def previous_document(document):
    """Go to the previous document."""
    index = documentlist.index(document)
    ndocument = documentlist[(index - 1) % len(documentlist)]
    ndocument.ui.activate()
commands.previous_document = previous_document


def local_find(document):
    key = document.ui.getkey()
    SelectLocalPattern(re.escape(key), document)(document)
commands.local_find = local_find


def local_find_backwards(document):
    key = document.ui.getkey()
    SelectLocalPattern(re.escape(key), document, reverse=True)(document)
commands.local_find_backwards = local_find_backwards


def search(document):
    document.search_pattern = document.ui.prompt('/')
    if document.search_pattern:
        try:
            SelectPattern(document.search_pattern, document)(document)
        except re.error as e:
            document.ui.notify(str(e))
commands.search = search


def search_current_content(document):
    document.search_pattern = re.escape(document.selection.content(document)[-1])
    SelectPattern(document.search_pattern, document)(document)
commands.search_current_content = search_current_content


def search_next(document):
    if document.search_pattern:
        SelectPattern(document.search_pattern, document)(document)
commands.search_next = search_next


def search_previous(document):
    if document.search_pattern:
        SelectPattern(document.search_pattern, document, reverse=True)(document)
commands.search_previous = search_previous


def command_mode(document):
    document.ui.command_mode()
commands.command_mode = command_mode
