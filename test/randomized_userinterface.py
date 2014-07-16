from ..userinterface import UserInterface
from ..session import Session
import random
import string
from re import escape

character_space = list(
"""
1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM
`-=[]\\;',./~_+{}|:"<>?
!@#$%&*()
\n\t\b
"""
) + 4 * ['Esc']

class RandomizedUserInterface(UserInterface):

    """Docstring for TestUserInterface. """

    def __init__(self, session):
        UserInterface.__init__(self, session)

    def touch(self):
        pass

    def quit(self):
        pass

    def activate(self):
        pass

    def getchar(self):
        return random.choice(character_space)

    def command_mode(self):
        pass

    def notify(self, message):
        pass

    def prompt(self, prompt_string='>'):
        length = random.randint(1, 5)
        return escape(''.join(self.getchar() for _ in range(length)))

Session.OnSessionInit.add(RandomizedUserInterface)
