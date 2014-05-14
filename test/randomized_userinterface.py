from ..userinterface import UserInterface
from ..session import Session
import random
import string

class RandomizedUserInterface(UserInterface):

    """Docstring for TestUserInterface. """

    def __init__(self, session):
        UserInterface.__init__(self, session)

    def quit(self):
        pass

    def activate(self):
        pass

    def getchar(self):
        return random.choice(string.printable)

    def command_mode(self):
        pass

    def notify(self, message):
        pass

    def prompt(self, prompt_string='>'):
        length = random.randint(1, 5)
        return ''.join(self.getchar() for i in range(length))

Session.OnSessionInit.add(RandomizedUserInterface)
