from ..userinterface import UserInterface
import random
from re import escape

# All keys that can be entered by the user simulator
# Esc is included more often, to keep the insertions relatively small
key_space = list(
    """
    1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM
    `-=[]\\;',./~_+{}|:"<>?
    !@#$%&*()
    \n\t\b
    """
) + 10 * ['Esc'] + ['Up', 'Down', 'Left', 'Right']


class RandomizedUserSimulator(UserInterface):

    """UserInterface which simulates some random behaviour for testing purposes."""

    def __init__(self, document):
        UserInterface.__init__(self, document)
        self.nextkey = random.choice(key_space)

    def touch(self):
        pass

    def quit(self, document):
        assert document is self.document

    def activate(self):
        pass

    def getinput(self):
        nextkey = self.nextkey
        self.nextkey = random.choice(key_space)
        return nextkey

    def peekinput(self):
        return self.nextkey

    def command_mode(self):
        pass

    def notify(self, message):
        pass

    def prompt(self, prompt_string='>'):
        length = random.randint(1, 10)
        # Generate random string
        randomstring = ''.join(self.getkey() for _ in range(length))
        # Escape string to ensure a valid regex
        return escape(randomstring)
