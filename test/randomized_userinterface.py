from ..userinterface import UserInterface
import random
from re import escape

# All characters that can be entered by the user simulator
# Esc is included more often, to keep the insertions relatively small
character_space = list(
"""
1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM
`-=[]\\;',./~_+{}|:"<>?
!@#$%&*()
\n\t\b
"""
) + 10 * ['Esc'] + ['Up', 'Down', 'Left', 'Right']

class RandomizedUserSimulator(UserInterface):

    """UserInterface which simulates some random behaviour for testing purposes."""

    def __init__(self, session):
        UserInterface.__init__(self, session)

    def touch(self):
        pass

    def quit(self, session):
        assert session is self.session

    def activate(self):
        pass

    def getchar(self):
        return random.choice(character_space)

    def command_mode(self):
        pass

    def notify(self, message):
        pass

    def prompt(self, prompt_string='>'):
        length = random.randint(1, 10)
        # Generate random string
        randomstring = ''.join(self.getchar() for _ in range(length))
        # Escape string to ensure a valid regex
        return escape(randomstring)

