"""
Mode are persistent commands, i.e. commands that take more than one keypress
to complete, and that may be interrupted by other commands (such as switching
to another document) without being cancelled.
This module provides several instruments to make creating new modes easier.
"""
class Mode:

    """Abstract class to make creating new modes more convenient."""

    def __init__(self):
        self.keymap = {}
        self.allowedcommands = []

    def __call__(self, document):
        document.mode = self

    def __str__(self):
        raise NotImplementedError('An abstract method is not callable.')

    def input_to_command(self, document, userinput, keymap=None):
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

    def normalmode(self, document, userinput):
        """Process input as if we were in normal mode."""
        command = self.input_to_command(document, userinput)
        command(document)

    def processinput(self, document, userinput):
        raise NotImplementedError('An abstract method is not callable.')

def cancel(document):
    """Go back to normalmode."""
    if document.mode != None:
        document.mode.processinput(document, 'Cancel')
