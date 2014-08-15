from . import commands
from .document import Document, documentlist


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


def quit_all(document):
    """Close all documents."""
    for document in documentlist:
        quit_document(document)


def force_quit(document):
    """Quit all documents without warning if unsaved changes."""
    for document in documentlist:
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
