"""
This module contains the abstract base class for userinterfaces.
A userinterface should subclass this.
"""


class UserInterface:

    """Abstract base class for userinteraces. """

    def __init__(self, session):
        self.session = session
        self.session.ui = self
        self.session.OnQuit.add(self.quit)

    def quit(self):
        raise NotImplementedError("An abstract method is not callable.")

    def activate(self):
        raise NotImplementedError("An abstract method is not callable.")

    def getchar(self):
        raise NotImplementedError("An abstract method is not callable.")

    def prompt(self, prompt_string='>'):
        raise NotImplementedError("An abstract method is not callable.")
