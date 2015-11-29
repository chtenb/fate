"""
This module contains several base classes and decorators for creating commands.
"""
from logging import debug
from collections import deque
from inspect import isclass
from .mode import Mode

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

    def __call__(self, doc):
        """Add command to the undotree and execute it."""
        doc.undotree.add(self)
        self.do(doc)

    def undo(self, doc):
        """Undo command."""
        raise NotImplementedError("An abstract method is not callable.")

    def do(self, doc):
        """
        Execute command without it being added to the undotree again,
        e.g. for performing a redo.
        """
        raise NotImplementedError("An abstract method is not callable.")


# PROBLEM:
# Suppose we want to create a compound selection which involves a the mode
# of the document to change to extend mode at some point.
# Then extend mode must be executed at creation time,
# in order to create the intended selection.
# However, this violates the principle that the document must not be
# touched while only creating a command.
# The solution is that compositions don't return an command and thus
# cannot be inspected
# If this functionality is required nonetheless,
# the composition must be defined in a command body

# PROBLEM:
# how do you know whether to wait or to proceed after executing a mode
# solution: always wait, if you need a mode to change behaviour of further commands
# you should do it differently. Modes are meant to change the way that userinput is
# processed. If you need to switch between behaviours of certain commands (like head/tail
# selection) you should toggle a bool somewhere.

def compose(*subcommands, docs=''):
    """
    In order to be able to conveniently chain commands, we provide a
    function that composes a sequence of commands into a single command.
    The undoable subcommands will be undoable as a whole.
    """
    # We need to define a new class for each composition
    # This is because compounds have state, so each execution is in fact a creation of a
    # new object.
    class Compound:

        def __init__(self, doc, callback=None):
            self.subcommands = subcommands
            self.callback = callback

            self.todo = deque(self.subcommands[:])
            doc.undotree.start_sequence()
            self.proceed(doc)

        def proceed(self, doc):
            """
            This function gets called when a submode finishes,
            as it is passed as a callback function to submodes.
            """
            while self.todo:
                command = self.todo.popleft()
                while 1:
                    debug('Subcommand: {}'.format(command))
                    # Pass ourselves as callback when executing a mode
                    if isinstance(command, Mode):
                        command(doc, callback=self.proceed)
                        return

                    # Also pass ourselves as callback when executing a Compound,
                    # since this compound may contain a mode
                    if isclass(command) and issubclass(command, Compound):
                        command(doc, callback=self.proceed)
                        return

                    result = command(doc)
                    if not callable(result):
                        break
                    command = result

            # Now we are completely finished
            doc.undotree.end_sequence()

            if self.callback:
                self.callback(doc)

    Compound.__docs__ = docs
    return Compound
