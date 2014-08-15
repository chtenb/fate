"""
This module contains several base classes and decorators for creating commands.
"""
from logging import debug


def execute(command, document):
    """Call obj as an command recursively while callable."""
    while callable(command):
        command = command(document)
    return command


class Undoable:

    """
    For some commands, we want to be able to undo them.
    Let us define the class Undoable for that.

    Note that, all commands can be made trivially undoable,
    by storing the document before and after applying the command.
    This is however not desirable for reasons of space.
    Therefore we leave the specific implementation
    of the undo method to the concrete subclasses.
    """

    def __call__(self, document):
        """Add command to the undotree and execute it."""
        document.undotree.add(self)
        self.do(document)

    def undo(self, document):
        """Undo command."""
        raise NotImplementedError("An abstract method is not callable.")

    def do(self, document):
        """
        Execute command without it being added to the undotree again,
        e.g. for performing a redo.
        """
        raise NotImplementedError("An abstract method is not callable.")


# There is a complication with implementing composed commands.
# Suppose we want to create a compound selection which involves a the mode
# of the document to change to extend mode at some point.
# Then extend mode must be executed at creation time,
# in order to create the intended selection.
# However, this violates the principle that the document must not be
# touched while only creating an command.
# The solution is that compositions don't return an command and thus cannot be inspected
# If this functionality is required nonetheless, the composition must be defined in an
# command body

class Compose:

    """
    In order to be able to conveniently chain commands, we provide a
    function that composes a sequence of commands into a single command.
    The undoable subcommands should be undoable as a whole.
    """

    def __init__(self, *subcommands, name='', docs=''):
        self.subcommands = subcommands
        self.__name__ = name
        self.__docs__ = docs

    def __call__(self, document):
        # Execute subcommands
        document.undotree.start_sequence()
        for command in self.subcommands:
            while 1:
                debug(command)
                result = command(document)
                if not callable(result):
                    break
                command = result
        document.undotree.end_sequence()
