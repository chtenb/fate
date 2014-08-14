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
        """
        raise NotImplementedError("An abstract method is not callable.")

    def notify(self, message):
        """
        Notify the user with the given message.
        """
        raise NotImplementedError("An abstract method is not callable.")

    def activate(self):
        raise NotImplementedError("An abstract method is not callable.")

    def getinput(self):
        raise NotImplementedError("An abstract method is not callable.")

    def peekinput(self):
        raise NotImplementedError("An abstract method is not callable.")

    def getchar(self):
        """
        Get character typed by user.
        Returns Cancel if interrupted by command.
        """
        userinput = self.peekinput()
        if type(userinput) == str:
            return self.getinput()
        else:
            return 'Cancel'

    def prompt(self, prompt_string='>'):
        raise NotImplementedError("An abstract method is not callable.")
