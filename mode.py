"""
Mode are persistent commands, i.e. commands that take more than one keypress
to complete, and that may be interrupted by other commands (such as switching
to another document) without being cancelled.
This module provides several instruments to make creating new modes easier.
"""


class Mode:

    """Abstract class to make creating new modes more convenient."""

    def __init__(self, document):
        self.keymap = {}
        self.allowedcommands = []

    def start(self, document):
        """Must be called to start the mode."""
        document.mode.push(self)

    def stop(self, document):
        """Must be called to stop the mode."""
        document.mode.pop()
        if document.mode:
            document.mode.peek().proceed(document)

    def stop(self, document):
        document.mode = None

    def __str__(self):
        try:
            return self.__name__
        except AttributeError:
            return self.__class__.__name__

    def processinput(self, document, userinput):
        raise NotImplementedError('An abstract method is not callable.')

    def proceed(self, document):
        """
        This method gets called when a mode has submodes and a submode has finished.
        """
        raise NotImplementedError('This mode doesn\'t have submodes.')


class ModeStack:

    """
    This class is a container for the mode stack.
    Its purpose is to provide a more convenient interface than a plain list.
    """

    def __init__(self):
        self.stack = []

    def __bool__(self):
        return bool(self.stack)

    def __str__(self):
        if self.stack:
            return ' -> '.join(str(mode) for mode in self.stack)
        else:
            return 'Normal'

    def __getitem__(self, index):
        return self.stack[index]

    def push(self, mode):
        assert isinstance(mode, Mode)
        self.stack.append(mode)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]


def input_to_command(document, userinput, keymap=None):
    """
    Convert given userinput to a command.
    If keymap is not given, document.keymap is used.
    Returns None if userinput is a key but is not in keymap.
    """
    keymap = keymap or document.keymap
    if type(userinput) == str:
        key = userinput
        if key in keymap:
            command = keymap[key]
        else:
            command = None
    else:
        command = userinput

    return command


def normalmode(document, userinput):
    """Process input as if we were in normal mode."""
    command = input_to_command(document, userinput)
    command(document)
