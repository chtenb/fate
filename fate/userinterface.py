"""
This module contains the abstract base class for userinterfaces.
A userinterface should subclass this.
"""
from collections import deque
from .event import Event
from abc import ABC, abstractmethod, abstractproperty

class UserInterfaceAPI(ABC):

    """Abstract base class for userinterace APIs."""

    def __init__(self, doc):
        self.doc = doc
        self.inputqueue = deque()
        self.OnUserInput = Event('OnUserInput')
        self._textview = None
        # TODO: update textview as needed
        # self.doc.OnTextChange

    @property
    def textview(self):
        """
        Get the textview corresponding to the viewport offset/size.
        This is used by commands like move page up/down to compute how much the offset has to move.
        Note that this doesn't mean that the UI can't create another textview e.g. to use as a buffer
        to allow for smooth scrolling.
        """
        return self._textview

    @textview.setter
    def textview(self, value):
        self._textvalue = value

    @abstractproperty
    def viewport_size(self):
        """
        Get viewport size as a tuple (width, height).
        Must both be positive.
        """
        pass

    @abstractproperty
    def viewport_offset(self):
        """
        Get and set viewport offset as a single text position.
        Must be positive.
        """
        pass

    @abstractmethod
    def touch(self):
        """
        Must be an atomic operation which forces a redraw of the screen.
        E.g. it should set a boolean somewhere such that the drawing thread notices
        that a redraw is required.
        """
        pass

    @abstractmethod
    def notify(self, message):
        """Notify the user with the given message. """
        pass

    @abstractmethod
    def _getuserinput(self):
        """
        Get the next input from the user.
        This can either be a key (in string representation) or a command.
        """
        pass

    def getinput(self):
        """Pop and return the first object from the input queue. """
        if not self.inputqueue:
            self.inputqueue.appendleft(self._getuserinput())
        result = self.inputqueue.pop()

        if result == 'ctrl-\\':
            raise KeyboardInterrupt

        self.OnUserInput.fire(self, result)
        return result

    #def prompt(self, prompt_string='>'):
        #"""
        #Prompt the user for an input string.
        #"""
        #raise NotImplementedError("An abstract method is not callable.")

    def peekinput(self):
        """Return the first object from the input queue. """
        if not self.inputqueue:
            self.inputqueue.appendleft(self._getuserinput())
        return self.inputqueue[-1]

    def getkey(self):
        """
        Get character typed by user.
        Returns cancelkey if interrupted by a command.
        """
        userinput = self.peekinput()
        if type(userinput) == str:
            return self.getinput()
        else:
            return self.doc.cancelkey

    def feedinput(self, userinput):
        self.inputqueue.appendleft(userinput)

