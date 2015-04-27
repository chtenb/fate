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
        self.OnUserInput = Event()

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
        Returns Cancel if interrupted by a command.
        """
        userinput = self.peekinput()
        if type(userinput) == str:
            return self.getinput()
        else:
            return 'Cancel'

    def feedinput(self, userinput):
        self.inputqueue.appendleft(userinput)

