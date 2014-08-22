"""
This module contains several base classes and decorators for creating commands.
"""
from logging import debug
from collections import deque
from inspect import isclass
from .mode import Mode


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

class Compound(Mode):

    """
    In order to be able to conveniently chain commands, we provide a
    function that composes a sequence of commands into a single command.
    The undoable subcommands should be undoable as a whole.
    """

    def __init__(self, document, *subcommands, name='', docs=''):
        Mode.__init__(self, document)
        self.__name__ = name
        self.__docs__ = docs
        self.subcommands = subcommands

        self.todo = deque(self.subcommands[:])
        document.undotree.start_sequence()
        self.start(document)
        self.proceed(document)

    def __str__(self):
        return self.__name__

    def proceed(self, document):
        """This function gets called when a submode finishes."""
        while self.todo:
            command = self.todo.popleft()
            while 1:
                if isclass(command) and issubclass(command, Mode):
                    command(document)
                    return

                result = command(document)
                if not callable(result):
                    break
                command = result

        # Now we are completely finished
        document.undotree.end_sequence()
        self.stop(document)

    def processinput(self, document, userinput):
        print(document.mode)
        print(self.subcommands)
        print(self.todo)
        raise Exception('Can\'t process input')

def Compose(*subcommands, name='', docs=''):
    def inner(document):
        compound = Compound(document, *subcommands, name=name, docs=docs)
        return compound
    return inner
