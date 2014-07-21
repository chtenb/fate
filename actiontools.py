"""
This module contains several base classes and decorators for creating actions.
"""
from functools import wraps
from collections import deque
from logging import debug


class Undoable:

    """
    For some actions, we want to be able to undo them.
    Let us define the class Undoable for that.

    Note that, all actions can be made trivially undoable,
    by storing the session before and after applying the action.
    This is however not desirable for reasons of space.
    Therefore we leave the specific implementation
    of the undo method to the concrete subclasses.
    """

    def __call__(self, session):
        """Add action to the undotree and execute it."""
        session.undotree.add(self)
        self.do(session)

    def undo(self, session):
        """Undo action."""
        raise NotImplementedError("An abstract method is not callable.")

    def do(self, session):
        """
        Execute action without it being added to the undotree again,
        e.g. for performing a redo.
        """
        raise NotImplementedError("An abstract method is not callable.")


# There is a complication with implementing composed actions.
# Suppose we want to create a compound selection which involves a the mode
# of the session to change to extend mode at some point.
# Then extend mode must be executed at creation time, in order to create the intended selection.
# However, this violates the principle that the session must not be
# touched while only creating an action.
# The solution is that compositions don't return an action and thus cannot be inspected
# If this functionality is required nonetheless, the composition must be defined in an
# action body

class Compose:
    """
    In order to be able to conveniently chain actions, we provide a
    function that composes a sequence of actions into a single action.
    The undoable subactions should be undoable as a whole.
    """
    def __init__(self, *subactions, name='', docs=''):
        self.subactions = subactions
        self.__name__ = name
        self.__docs__ = docs

    def __call__(self, session):
        # Execute subactions
        session.undotree.start_sequence()
        for action in self.subactions:
            while 1:
                debug(action)
                result = action(session)
                if not callable(result):
                    break
                action = result
        session.undotree.end_sequence()

