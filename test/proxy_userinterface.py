from ..userinterface import UserInterface
from collections import deque


class ProxyUserInterface(UserInterface):

    """UserInterface which simulates some random behaviour for testing purposes."""

    def __init__(self, document):
        UserInterface.__init__(self, document)
        self.key_queue = deque()

    def feed(self, string):
        """
        Queue a sequence of characters which will be returned by the getkey function,
        when called.
        """
        for key in string:
            self.key_queue.appendleft(key)

    def touch(self):
        pass

    def quit(self, document):
        assert document is self.document

    def activate(self):
        pass

    def getinput(self):
        """
        Pop first key from the key_queue.
        When no more characters are available, return Esc.
        """
        if self.key_queue:
            return self.key_queue.pop()
        else:
            return 'Cancel'

    def peekinput(self):
        """
        Return first key from the key_queue.
        When no more characters are available, return Esc.
        """
        if self.key_queue:
            return self.key_queue[-1]
        else:
            return 'Cancel'

    def command_mode(self):
        pass

    def notify(self, message):
        pass

    def prompt(self, prompt_string='>'):
        pass
