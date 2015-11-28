"""A document represents the state of an editing document."""
from .selection import Selection, Interval
from .event import Event
from . import commands
from .userinterface import UserInterfaceAPI
from .navigation import center_around_selection, is_position_visible
from .selecting import SelectModes
from .mode import Mode

from logging import error, info, debug

documentlist = []
activedocument = None


class Namespace:
    """
    Allow easy namespacing within attributes of an object.
    """
    pass


class Document:

    """Contains all objects of one file editing document"""
    OnDocumentInit = Event('OnDocumentInit')
    OnModeInit = Event('OnModeInit')
    create_userinterface = None

    _text = ''
    _mode = None

    expandtab = False
    tabwidth = 4
    autoindent = True

    locked_selection = None
    saved = True

    def __init__(self, filename=''):
        documentlist.append(self)
        self.OnTextChanged = Event('OnTextChanged')
        self.OnRead = Event('OnRead')
        self.OnWrite = Event('OnWrite')
        self.OnQuit = Event('OnQuit')
        self.OnActivate = Event('OnActivate')
        self.OnSelectionChange = Event('OnSelectionChange')

        self.filename = filename
        if filename:
            try:
                with open(filename, 'r') as fd:
                    self._text = fd.read()
            except (FileNotFoundError, PermissionError) as e:
                error(str(e))

        self._selection = Selection(Interval(0, 0))
        self.selectmode = SelectModes.normal

        if not self.create_userinterface:
            raise Exception('No function specified in Document.create_userinterface.')
        self.ui = self.create_userinterface(self)
        if not isinstance(self.ui, UserInterfaceAPI):
            raise Exception('document.ui not an instance of UserInterface.')

        self.modes = Namespace()
        self.OnModeInit.fire(self)
        self.mode = self.modes.normalmode
        self.OnDocumentInit.fire(self)

        self.OnRead.fire(self)
        self.OnTextChanged.fire(self)

    def quit(self):
        """Quit document."""
        info('Quitting document ' + str(self))
        self.OnQuit.fire(self)
        global activedocument
        index = documentlist.index(self)


        if len(documentlist) == 1:
            info('Closing the last document by setting activedocument to None')
            activedocument = None
            return

        if index < len(documentlist) - 1:
            nextdoc = documentlist[index + 1]
        else:
            nextdoc = documentlist[index - 1]

        nextdoc.activate()
        documentlist.remove(self)

    def activate(self):
        """Activate this document."""
        global activedocument
        activedocument = self
        self.OnActivate.fire(self)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if not isinstance(value, Mode):
            raise ValueError('Object {} is not an instance of Mode'.format(value))
        self._mode = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

        self.saved = False
        self.OnTextChanged.fire(self)

    @property
    def selection(self):
        return self._selection

    @selection.setter
    def selection(self, value):
        if not isinstance(value, Selection):
            raise ValueError('Object {} is not an instance of Selection'.format(value))
        value.validate(self)
        self._selection = value

        # Update the userinterface viewport to center around first interval
        if not is_position_visible(self, self._selection[-1][1]):
            center_around_selection(self)
        self.OnSelectionChange.fire(self)

    def processinput(self, userinput):
        """This method is called when this document receives userinput."""
        if userinput == 'ctrl-\\':
            raise KeyboardInterrupt
        debug('Mode:' + repr(self.mode))
        debug('Input: ' + repr(userinput))
        self.mode.processinput(self, userinput)


def next_document(doc):
    """Go to the next document."""
    index = documentlist.index(doc)
    ndoc = documentlist[(index + 1) % len(documentlist)]
    ndoc.activate()
commands.next_document = next_document


def previous_document(doc):
    """Go to the previous document."""
    index = documentlist.index(doc)
    ndoc = documentlist[(index - 1) % len(documentlist)]
    ndoc.activate()
commands.previous_document = previous_document


def goto_document(index):
    """Command constructor to go to the document at given index."""
    def wrapper(doc):
        documentlist[index].activate()
        return wrapper
