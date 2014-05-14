from ..session import Session
import random
import string

class RandomUserInterface:

    """Docstring for TestUserInterface. """

    def __init__(self):
        self.session = Session()
        self.session.ui = self
        self.session.OnQuit.add(self.quit)

    def quit(self):
        pass

    def getchar(self):
        return random.choice(string.printable)

    def prompt(self, prompt_string='>'):
        length = random.randint(1, 5)
        return ''.join(self.getchar() for i in range(length))
