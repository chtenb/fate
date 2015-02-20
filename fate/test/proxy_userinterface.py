from collections import deque
from ..filecommands import quit_document
from ..userinterface import UserInterface


class ProxyUserInterface(UserInterface):

    """UserInterface which simulates some random behaviour for testing purposes."""

    def __init__(self, document):
        UserInterface.__init__(self, document)
        self.offset = (0, 0)

    @property
    def viewport_size(self):
        """Get viewport size."""
        return (500, 500)

    @property
    def viewport_offset(self):
        """Get and set viewport offset."""
        return self.offset

    @viewport_offset.setter
    def viewport_offset(self, value):
        """Get and set viewport offset."""
        self.offset = value

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
