from ..userinterface import UserInterface
from queue import Queue

from logging import debug


class ProxyUserInterface(UserInterface):

    """UserInterface which simulates some random behaviour for testing purposes."""

    def __init__(self, document):
        UserInterface.__init__(self, document)
        self.char_queue = Queue()

    def feed(self, string):
        """
        Queue a sequence of characters which will be returned by the getchar function,
        when called.
        """
        for char in string:
            self.char_queue.put(char)

    def touch(self):
        pass

    def quit(self, document):
        assert document is self.document

    def activate(self):
        pass

    def getchar(self):
        """
        Return characters from the char_queue.
        When no more characters are available, return Esc.
        """
        debug(1)
        if not self.char_queue.empty():
            return self.char_queue.get()
        else:
            return 'Esc'

    def command_mode(self):
        pass

    def notify(self, message):
        pass

    def prompt(self, prompt_string='>'):
        pass
