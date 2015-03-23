from .mode import Mode, input_to_command
from .document import Document
from .keymap import default
from . import pointer

from copy import copy
import logging

class NormalMode(Mode):

    """Docstring for NormalMode. """

    keymap = copy(default)

    def processinput(self, doc, userinput):
        if isinstance(userinput, pointer.PointerInput):
            self.process_pointerinput(userinput)
        else:
            command = input_to_command(doc, userinput)
            if command:
                command(doc)

    def process_pointerinput(self, userinput):
        assert isinstance(userinput, pointer.PointerInput)

        if userinput.length:
            logging.debug('You sweeped from position {} till {}'
                          .format(userinput.pos, userinput.pos + userinput.length))
        else:
            logging.debug('You clicked at position ' + str(userinput.pos))

def add_normalmode(doc):
    doc.normalmode = NormalMode(doc)
    doc.mode = doc.normalmode

Document.OnDocumentInit.add(add_normalmode)
