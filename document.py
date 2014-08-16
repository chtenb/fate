"""A document represents the state of an editing document."""
from .event import Event
from .selection import Selection, Interval
from . import modes, commands
from .userinterface import UserInterface
from collections import deque

import logging

documentlist = []
activedocument = None


class Document():

    """Contains all objects of one file editing document"""
    OnDocumentInit = Event()
    create_userinterface = None
    _text = ''
    saved = True
    mode = modes.SELECT
    persistentcommand = None  # TODO: Replace self.mode by this

    expandtab = False
    tabwidth = 4
    autoindent = True

    locked_selection = None

    def __init__(self, filename=""):
        documentlist.append(self)
        self.OnTextChanged = Event()
        self.OnRead = Event()
        self.OnWrite = Event()
        self.OnQuit = Event()
        self.OnUserInput = Event()

        self.filename = filename
        self.selection = Selection(Interval(0, 0))
        self.input_food = deque()

        if not self.create_userinterface:
            raise Exception('No function specified in Document.create_userinterface.')
        self.ui = self.create_userinterface(self)
        if not isinstance(self.ui, UserInterface):
            raise Exception('document.ui not an instance of UserInterface.')
        self.OnQuit.add(self.ui.quit)

        # Load the default key map
        from .keymap import default
        self.keymap = {}
        self.keymap.update(default)

        self.OnDocumentInit.fire(self)

        if filename:
            self.read()

    def getkey(self):
        if self.input_food:
            key = self.input_food.popleft()
        else:
            key = self.ui.getkey()
        self.OnUserInput.fire(self, key)
        return key

    def feed_input(self, keys):
        self.input_food.extend(keys)

    def quit(self):
        """Quit document."""
        logging.info('Quitting document ' + str(self))
        self.OnQuit.fire(self)
        documentlist.remove(self)

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, value):
        # Make sure only valid selections are applied
        assert isinstance(value, Selection) and value.isvalid(self)
        self._selection = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.saved = False
        self.OnTextChanged.fire(self)

    def read(self, filename=None):
        """Read text from file."""
        filename = filename or self.filename

        if filename:
            try:
                with open(filename, 'r') as fd:
                    self.text = fd.read()
                self.saved = True
                self.OnRead.fire(self)
            except (FileNotFoundError, PermissionError) as e:
                logging.error(str(e))
        else:
            logging.error('No filename')

    def write(self, filename=None):
        """Write current text to file."""
        filename = filename or self.filename

        if filename:
            try:
                with open(filename, 'w') as fd:
                    fd.write(self.text)
                self.saved = True
                self.OnWrite.fire(self)
            except (FileNotFoundError, PermissionError) as e:
                logging.error(str(e))
        else:
            logging.error('No filename')


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

def goto_document(index):
    """Command constructor to go to the document at given index."""
    def wrapper(document):
        documentlist[index].activate()
    return wrapper

