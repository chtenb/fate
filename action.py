"""
This module exposes the basic action machinery.

An action is an abstract object that can make a modification to a
session. An action must therefore be callable and accept a session
as argument.

For instance, consider an action that changes the selection mode
of a session to EXTEND. This action could be implemented like
def set_extend_mode(session):
    session.selection_mode = mode.extend_mode

Another equivalent way, using a class, would be
class SetExtendMode:
    def __call__(self, session):
        session.selection_mode = mode.extend_mode
set_extend_mode = SetExtendMode()

Some actions are undoable, which means that they posess an
undo method. An action is previewable iff it is undoable.
Consider again the previous example. We will now make it undoable
by storing the relevant information in the action object.
class SetExtendMode:
    def __call__(self, session):
        self.previous_mode = session.selection_mode
        session.selection_mode = mode.extend_mode
    def undo(self, session):
        session.selection_mode = self.previous_mode
set_extend_mode = SetExtendMode()


We can turn a Selection also into an action, by specifying the
following __call__ method.
class Selection:
    def __call__(self, session):
        self.previous_selection = session.selection
        session.selection = self


Can we also create actions that perform differently depending
on the context? Let us try to implement a 'select everything'.
def select_everything(session):
    interval = (0, len(session.text))
    session.selection = Selection(session, [interval])

We may want to subclass from Selection, such that we can split
the creation of the selection and the execution of the selection.
class SelectEverything(Selection):
    def __init__(self, session):
        interval = (0, len(session.text))
        Selection.__init__(self, [interval])


Actions can be composed into a CompoundAction.
A CompoundAction is undoable iff all sub actions are undoable.

All actions can be made trivially undoable, by storing the session
before and after applying the action. This is however not
desirable for reasons of space.

"""


class Action:
    """Base class for actions."""

    def __init__(self, session, *args):
        """Every object in args must have an undo and a do function."""
        self.session = session

    def _do(self):
        """Do implemented by subclass."""
        pass

    def _undo(self):
        """Undo implemented by subclass."""
        pass

    def undo(self):
        """Undo action."""
        self._undo()
        self.check_text_changed()

    # TODO: maybe this should be transformed into __call__
    def do(self, redo=False):
        """Do action."""
        self._do()

        if not redo:
            self.session.actiontree.add(self)
        self.check_text_changed()

    def check_text_changed(self):
        """Check for changes in text."""
        if self.session.text_changed:
            self.session.saved = False
            self.session.OnTextChanged.fire(self.session)
            self.session.text_changed = False

    def redo(self):
        """Redo action."""
        self.do(redo=True)


# TODO: make sure CompoundActions can deal with InsertOperations
class CompoundAction(Action):
    """
    This class can be used to compose multiple actions into a single
    action.
    """
    def __init__(self, session, *args):
        """Every object in args must be an Action."""
        Action.__init__(self, session)
        self.sub_actions = tuple(a for a in args if a)

    def __str__(self):
        result = []
        for sub_action in self:
            result.append(str(sub_action))
        return '(' + ', '.join(result) + ')'

    def _undo(self):
        """Undo action."""
        for sub_action in self:
            sub_action._undo()

    def _do(self):
        """Do action."""
        for sub_action in self.sub_actions:
            sub_action._do()

    def __iter__(self):
        """Iterate linearly through all atomic subactions."""
        for sub_action in self.sub_actions:
            if sub_action.__class__ == CompoundAction:
                for sub_sub_action in sub_action:
                    if sub_sub_action != None:
                        yield sub_sub_action
            else:
                if sub_action != None:
                    yield sub_action

    def contains_class(self, cls):
        """
        Check if an atomic subaction of class _class is contained
        in self.
        """
        for sub_action in self:
            if sub_action.__class__ == cls:
                return True
        return False


def actor(function):
    """Base function for actors."""
    def wrapper(session, preview=False, **kwargs):
        action = function(session, **kwargs)
        if action and not preview:
            action.do()
        else:
            return action

    wrapper.is_actor = True
    return wrapper


def compose(*args):
    """
    This function returns the compositional actor from the
    argument actors, and does the resulting actions upon execution.
    """
    @actor
    def wrapper(session):
        actionlist = [f(session, preview=True)
                      if hasattr(f, 'is_actor') else f(session) for f in args]
        actionlist = [x for x in actionlist if x]
        if not actionlist:
            return
        return CompoundAction(session, *actionlist)
    return wrapper
