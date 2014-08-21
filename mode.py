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
        document.mode.append(self)

    def stop(self, document):
        """Must be called to stop the mode."""
        document.mode.pop()
        if document.mode:
            document.mode[-1].proceed(document)

    def __str__(self):
        raise NotImplementedError('An abstract method is not callable.')

    def processinput(self, document, userinput):
        raise NotImplementedError('An abstract method is not callable.')


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


def cancel(document):
    """Go back to normalmode."""
    if document.mode:
        document.mode.processinput(document, 'Cancel')
