from .document import Document
from logging import debug


class PointerInput:

    def __init__(self, pos, length):
        self.pos = pos
        self.length = length


def process_pointerinput(self, userinput):
    assert isinstance(userinput, PointerInput)

    if userinput.length:
        debug('You sweeped from position {} till {}'
              .format(userinput.pos, userinput.pos + userinput.length))
    else:
        debug('You clicked at position ' + str(userinput.pos))

Document.process_pointerinput = process_pointerinput
