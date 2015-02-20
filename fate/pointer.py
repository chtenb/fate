"""
This module contains support for userinput by pointer like devices.
"""

class PointerInput:

    """
    Base class for various pointer input types.
    """

    def __init__(self, pos, length):
        self.pos = pos
        self.length = length


class PointerClick(PointerInput):

    def __init__(self, pos):
        PointerInput.__init__(self, pos, 0)


class PointerDoubleClick(PointerClick):

    def __init__(self, pos):
        PointerClick.__init__(self, pos)


class PointerTripleClick(PointerClick):

    def __init__(self, pos):
        PointerClick.__init__(self, pos)
