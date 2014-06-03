"""
This module contains several base classes and decorators for creating actions.
"""
from functools import wraps
from collections import deque


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

    def call(self, session):
        """Do action."""
        session.undotree.add(self)

    def undo(self, session):
        """Undo action."""
        raise NotImplementedError("An abstract method is not callable.")

    def do(self, session):
        """Redo action."""
        raise NotImplementedError("An abstract method is not callable.")


class Compound:

    """
    This class can be used to compose multiple possibly interactive or undoable
    actions into a single action.
    When an the composed action sequence contains interactive action,
    we want the tail of the sequence to wait until an earlier interaction has finished.
    """
    # There is a complication with implementing CompoundUndoable.
    # Suppose we want to create a compound selection which involves a the mode
    # of the session to change to extend mode at some point.
    # Then extend mode must be executed at creation time,
    # in order to create the intended selection.
    # However, this violates the principle that the session must not be
    # touched while only creating an action.
    #
    # The solution must be to state that extend mode only affects selectors
    # that are done live by the user.
    # For other situations, extend mode must be passed explicitly.

    def __init__(self, *subactions):
        self.todo = deque(subactions)

    def __call__(self, session):
        """
        Execute subactions, gathering undoable actions into a CompoundUndoable
        action, until first non finished subaction is encountered.
        """
        # TODO: allow nested compositions

        # We call start and end methods of the undotree, indicating the
        # start and end of a sequence of undoables.
        session.undotree.start_sequence()

        while self.todo:
            # We allow actions as well as actors to be composed
            subaction = self.todo.popleft()
            while 1:
                result = subaction(session)
                if not callable(result):
                    break
                subaction = result

        session.undotree.end_sequence()


def Compose(*subactions, name='', docs=''):
    """
    In order to be able to conveniently chain actions or actors, we provide a
    function that composes a sequence of actions/actors into a single undoable actor.
    """
    def wrapper(session):
        compound = Compound(*subactions)
        compound.__name__ = name
        compound.__docs__ = docs
        return compound
    return wrapper


def previewable(function):
    # TODO: not sure if this one is needed
    """Utility function that could be used for higher order actions."""
    @wraps(function)
    def wrapper(session, *args, preview=False, **kwargs):
        result = function(session, *args, **kwargs)
        if preview:
            return result
        else:
            result(session)
    return wrapper
