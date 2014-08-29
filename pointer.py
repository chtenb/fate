"""
This module contains support for userinput by pointer like devices.
"""
from .document import Document
from logging import debug


class PointerInput:

    """
    Base class for various pointer input types.
    """

    def __init__(self, pos, length):
        self.pos = pos
        self.length = length


class PointerClick(PointerInput):

    def __init__(self, pos):
        PointerInput.__init__(self, pos, 1)


class PointerDoubleClick(PointerClick):

    def __init__(self, pos):
        PointerClick.__init__(self, pos)


class PointerTripleClick(PointerClick):

    def __init__(self, pos):
        PointerClick.__init__(self, pos)


def process_pointerinput(self, userinput):
    assert isinstance(userinput, PointerInput)

    if userinput.length:
        debug('You sweeped from position {} till {}'
              .format(userinput.pos, userinput.pos + userinput.length))
    else:
        debug('You clicked at position ' + str(userinput.pos))

Document.process_pointerinput = process_pointerinput
