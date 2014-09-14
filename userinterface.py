"""
This module contains the abstract base class for userinterfaces.
A userinterface should subclass this.
"""


class UserInterface:

    """Abstract base class for userinteraces. """

    def __init__(self, document):
        self.document = document

    def touch(self):
        """
        Must be an atomic operation which forces a redraw of the screen.
        E.g. it should set a boolean somewhere such that the drawing thread notices
        that a redraw is required.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def activate(self):
        """
        When this userinterface must become active (e.g. if the user switches to
        our document), this function gets called.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def notify(self, message):
        """
        Notify the user with the given message.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def getinput(self):
        """
        Get the next input from the user.
        This can either be a key (in string representation) or a command.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def peekinput(self):
        """
        Same as getinput, but don't actually consume the input.
        """
        raise NotImplementedError("An abstract method is not callable.")

    #def prompt(self, prompt_string='>'):
        #"""
        #Prompt the user for an input string.
        #"""
        #raise NotImplementedError("An abstract method is not callable.")

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
