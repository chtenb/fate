from collections import deque
from ..document import quit_document
from ..userinterface import UserInterface


class ProxyUserInterface(UserInterface):

    """UserInterface which simulates some random behaviour for testing purposes."""

    def __init__(self, document):
        UserInterface.__init__(self, document)

    def touch(self):
        pass

    def quit(self, document):
        assert document is self.document

    def activate(self):
        pass

    def _getuserinput(self):
        """
        Get input from user.
        Since we have no user, this raises an exception.
        """
        raise Exception('Inputqueue is empty.')

    def command_mode(self):
        pass

    def notify(self, message):
        pass

    def prompt(self, prompt_string='>'):
        pass
