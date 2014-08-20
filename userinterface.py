"""
This module contains the abstract base class for userinterfaces.
A userinterface should subclass this.
"""
from collections import deque
from .event import Event
from .document import activedocument

class UserInterface:

    """Abstract base class for userinteraces. """

    def __init__(self, document):
        self.document = document
        self.inputqueue = deque()
        self.OnUserInput = Event()

    def touch(self):
        """
        Must be an atomic operation which forces a redraw of the screen.
        E.g. it should set a boolean somewhere such that the drawing thread notices
        that a redraw is required.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def _activate(self):
        """
        When this userinterface must become active (e.g. if the user switches to
        our document), this function gets called.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def activate(self):
        """
        Manage activation of a new document.
        """
        global activedocument
        activedocument = self
        self._activate()

    def notify(self, message):
        """
        Notify the user with the given message.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def prompt(self, prompt_string='>'):
        """
        Prompt the user for an input string.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def _getuserinput(self):
        """
        Get the next input from the user.
        This can either be a key (in string representation) or a command.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def getinput(self):
        """
        Pop and return the first object from the input queue.
        """
        if not self.inputqueue:
            self.inputqueue.appendleft(self._getuserinput())
        result = self.inputqueue.pop()
        self.OnUserInput.fire(self, result)
        return result

    def peekinput(self):
        """
        Return the first object from the input queue.
        """
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

