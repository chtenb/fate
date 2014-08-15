"""A document represents the state of an editing document."""
from .event import Event
from .selection import Selection, Interval
from . import modes
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

    expandtab = False
    tabwidth = 4
    autoindent = True

    search_pattern = ''
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
