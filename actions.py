"""
The goal of a text editor is to make modifications to a text.
More generally, the user should also be able to modify things other
than text, such as options or other meta stuff.
We store all relevant data for editing a text in a single object,
and call this object a session.

To make modifications to a session, we define actions.
An action is an abstract object that can make a modification to a session.
An action must therefore be callable and accept a session as argument.

In many cases it is useful to create actions on the fly.
Callable objects that create and return actions are called 'action constructors'.

A special type of action constructors are those that require a session as argument.
Let us call these 'actors'.
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


class Interactive:

    """
    Can we also make actions which are incrementally constructed by the
    user while getting feedback, like an insertion operation?
    We introduce the class Interactive for this.
    We can interact with an interactive action by
    calling the interact method on it.
    Thus, essentially an interaction is somewhat like a Vim mode.

    More generally speaking, we want to be able to interact with
    a general action, that is not necessarily undoable.
    So we need to think about how to implement interaction in the most general way.
    To know which action are currently wating for interaction, we introduce
    an interaction stack with the top action being the current active one.
    This way we can nest interactions.

    If we then finish an interaction, we can pop it from the stack and be dropped
    into the parent interaction.
    The finished flag is used to indicate that we finished updating the action.
    This is needed for a possible container action to know which subaction the
    update information should currectly be redirected to.
    """
    # TODO: think about how interactions can have their own keymap

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


class Compound(Interactive):

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
        Interactive.__call__(self, session)
        # TODO: allow nested compositions

        # We call start and end methods of the undotree, indicating the
        # start and end of a sequence of undoables.
        session.undotree.start_sequence()
        self.proceed(session)

    def proceed(self, session):
        while self.todo:
            # We allow actions as well as actors to be composed
            subaction = self.todo.popleft()
            while 1:
                result = subaction(session)
                if not callable(result):
                    break
                subaction = result

            if isinstance(subaction, Interactive) and not subaction.finished:
                # Stop here, this subaction needs interaction
                return
        session.undotree.end_sequence()
        Interactive.proceed(self, session)


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

