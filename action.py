from logging import debug
from functools import wraps
from collections import deque


class Undoable:

    def call(self, session):
        """Do action."""
        session.undotree.add(self)

    def undo(self, session):
        """Undo action."""
        raise NotImplementedError("An abstract method is not callable.")

    def do(self, session):
        """Redo action."""
        raise NotImplementedError("An abstract method is not callable.")


class Interactive:
    finished = False

    def __call__(self, session):
        """Push ourselves on the interactionstack."""
        session.interactionstack.push(self)

    def interact(self, session, string):
        """Interact with this action."""
        raise NotImplementedError("An abstract method is not callable.")

    def proceed(self, session):
        """Proceed by finishing ourselves."""
        self.finished = True
        parent = session.interactionstack.backtrack()
        if parent:
            parent.proceed(session)


class Compound(Interactive):  # Updatable(CompoundUndoable):

    """
    This class can be used to compose multiple possibly interactive or undoable
    actions into a single action.
    """

    def __init__(self, *subactions):
        self.todo = deque(subactions)

    def __call__(self, session):
        """
        Execute subactions, gathering undoable actions into a CompoundUndoable
        action, until first non finished subaction is encountered.
        """
        Interactive.__call__(self, session)
        # TODO: allow nested compositions
        session.undotree.start_sequence()
        self.proceed(session)

    def proceed(self, session):
        while self.todo:
            # Problem: Delete is not Undoable, but its result is
            # So either we have to require that higher order actions always return lower
            # order actions (bad) and solve that here with a hacky execution loop (bad)
            # or we simply call start and end methods of the undotree, indicating the
            # start and end of a sequence of undoables.
            #
            # So lets do the latter

            # Let us not only allow actions to be composed, but also action constructors
            # that only take a session.
            # ChangeAfter is a constructor that needs this.
            subaction = self.todo.popleft()
            while 1:
                result = subaction(session)
                if not callable(result):
                    break
                subaction = result

            #while isinstance(subaction, type):
                #debug(subaction)
                #subaction = subaction(session)

            #debug(subaction)
            #subaction(session)

            if isinstance(subaction, Interactive) and not subaction.finished:
                # Stop here, this subaction needs interaction
                return
        session.undotree.end_sequence()
        Interactive.proceed(self, session)


def Compose(*subactions, name='', docs=''):
    """
    Function that composes several actions or constructors into a single constructor.
    """
    def wrapper(session):
        compound = Compound(*subactions)
        compound.__name__ = name
        compound.__docs__ = docs
        return compound
    return wrapper


def previewable(function):
    """Utility function that could be used for higher order actions."""
    @wraps(function)
    def wrapper(session, *args, preview=False, **kwargs):
        result = function(session, *args, **kwargs)
        if preview:
            return result
        else:
            result(session)
    return wrapper

# OLD ------------------

# TODO: How to make sure that we get updated if a child gets updated?
# Maybe we don't want to get updated, since only the child changed
# But then we need to be able to replace the child in the undotree
# I.e. we must undo the old child, do the new child and place the new child in the undotree

# Or we must not deepcopy undoable actions into the undotree
    # But then we cannot easily update at all, since we have changed, and thus the undo method has been corrupted
    # I think the latter is the way to go
    # Because removing code solves the problem here :)
    #
    # Done that. Now we don't need to be Updateable anymore.
    # def update(self, session):
    #"""
    # Make sure we are up to date with possible (interactive) modifications to us.
    #"""
    # session.undotree.hard_undo()
    # Backtrack twice, for the pending subaction and for ourselves
    # session.interactionstack.backtrack()
    # session.interactionstack.backtrack()
    # self(session)


# def compose(*args):
    #"""Utility function that can be used to compose several actors into one."""
    # def wrapper(session):
    # return Compose(session, *args)
    # return wrapper

"""
There is a complication with implementing CompoundUndoable.
Suppose we want to create a compound selection which involves a change to extend mode at some point.
Then extend mode must be executed at creation time, in order to create the intended selection.
However, this violates the principle that the session must not be touched while only creating an action.

The solution must be to state that extend mode only affects selectors that are done live by the user.
For other situations, extend mode must be passed explicitly.
To make things simpler, we require all subactions to be undoable.
"""

# class CompoundUndoable(Undoable):
#
#     """
#     This class can be used to compose multiple undoable actions
#     into a single undoable action.
#     """
#
#     def __init__(self, session, *subactions):
#         """Every subaction must be undoable."""
#         for subaction in subactions:
#             if not isinstance(subaction, Undoable):
#                 raise TypeError('Subaction {} is not an instance of Undoable.'
#                                 .format(repr(subaction)))
#         self.subactions = subactions
#
#     def __str__(self):
#         result = []
#         for subaction in self:
#             result.append(str(subaction))
#         return '(' + ', '.join(result) + ')'
#
#     def _undo(self):
#         """Undo action."""
#         for subaction in reversed(self):
#             subaction._undo()
#
#     def _call(self):
#         """Do action."""
#         for subaction in self.subactions:
#             subaction._call()
