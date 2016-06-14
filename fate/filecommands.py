"""
This module contains commands for opening, closing, saving and loading files.
"""
import logging
from . import commands
from .operation import Operation
from . import document
from .commandtools import compose
from .selection import Selection, Interval
from .text import StringText
import selectors  # Depend on selectors to be loaded


def save(doc, filename=None):
    """Save document text to file."""
    filename = filename or doc.filename

    if filename:
        try:
            with open(filename, 'w') as fd:
                fd.write(doc.text)
        except (FileNotFoundError, PermissionError) as e:
            logging.error(str(e))
        else:
            doc.saved = True
            doc.OnWrite.fire(doc)
    else:
        logging.error('No filename')
commands.save = save


def load(doc, filename=None):
    """Load document text from file."""
    filename = filename or doc.filename

    if filename:
        try:
            with open(filename, 'r') as fd:
                newtext = StringText(fd.read())
        except (FileNotFoundError, PermissionError) as e:
            logging.error(str(e))
        else:
            commands.selectall(doc)
            operation = Operation(doc, newcontent=[newtext])
            operation(doc)
            doc.selection = Selection(Interval(0, 0))

            doc.saved = True
            doc.OnRead.fire(doc)
    else:
        logging.error('No filename')
commands.load = load


def ask_filename(doc):
    doc.modes.prompt.start(doc, 'Filename: ')


def open_file(doc):
    """Open a new document."""
    filename = doc.modes.prompt.inputstring
    document.Document(filename)
commands.open_file = compose(ask_filename, open_file)


# TODO: make pressing esc work
def quit_document(doc):
    """Close current document and ask user for permission if there are unsaved changes."""
    def check_answer(doc):
        answer = doc.modes.prompt.inputstring
        if answer == 'y':
            doc.quit()
        elif answer == 'n':
            return
        else:
            quit_document(doc)

    if not doc.saved:
        doc.modes.prompt.start(doc, promptstring='Unsaved changes! Really quit? (y/n/esc)',
                               callback=check_answer)
    else:
        doc.quit()
commands.quit_document = quit_document


def quit_all(doc=None):
    """Close all documents."""
    docs = list(document.documentlist)
    for doc in docs:
        quit_document(doc)
commands.quit_all = quit_all


def force_quit(doc=None):
    """Quit all documents without warning if unsaved changes."""
    docs = list(document.documentlist)
    for doc in docs:
        doc.quit()
commands.force_quit = force_quit
