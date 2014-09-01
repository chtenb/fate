"""
This module contains functionality for user prompting.
"""

from .mode import Mode
from . import commands
from .userinterface import UserInterface

UserInterface.promptinput = ''
class Prompt(Mode):
    def __init__(self):
        Mode.__init__(self)
        self.keymap.update({
            'Ctrl-u' : self.clear,
            'Ctrl-w' : self.delete_word
            })

    def processinput(self, document, userinput):
        if callable(userinput):
            return

        if type(userinput) == str:
            if len(userinput) > 1:
                return
            if userinput == '\b':
                document.ui.promptinput = document.ui.promptinput[:-1]
            else:
                document.ui.promptinput += userinput

    def clear(self, document):
        document.ui.promptinput = ''

    def delete_word(self, document):
        pass
commands.Prompt = Prompt
