"""
The goal of a text editor is to make modifications to a text.
More generally, the user should also be able to modify things other
than text, such as options or other meta stuff.
We store all relevant data for editing a text in a single object,
and call this object a session.

To make modifications to a session, we define actions.
An action is an abstract object that can make a modification to a
session. An action must therefore be callable and accept a session
as argument.
"""
from . import modes
from .session import Session
mysession = Session()


"""
For instance, consider an action that changes the selection mode
of a session to EXTEND. This action could be implemented as follows.
"""


def set_extend_mode(session):
    session.selection_mode = modes.extend_mode


"""
Another equivalent way, using a class, would be:
"""


class SetExtendMode:
    def __call__(self, session):
        session.selection_mode = modes.extend_mode

set_extend_mode = SetExtendMode()  # create action
set_extend_mode(mysession)  # execute the action on a session


"""
Actions like this can easily be composed, by putting them into a container action.
"""


def my_container_action(session):
    set_extend_mode(session)
    set_extend_mode(session)
    # etc


"""
For some actions, we want to be able to undo them.
Let us define the class Undoable for that.

Note that, all actions can be made trivially undoable,
by storing the session before and after applying the action.
This is however not desirable for reasons of space.
Therefore we leave the specific implementation
of the undo method to the concrete subclasses.
"""


class Undoable:
    def __call__(self, session):
        session.actiontree.add(self)
        self._call(session)

    def undo(self, session):
        session.actiontree.undo()
        self._undo(session)

    def _call(self, session):
        raise Exception("An abstract method is not callable.")

    def _undo(self, session):
        raise Exception("An abstract method is not callable.")


"""
Consider again the previous example. We will now make it undoable
by storing the relevant information in the action object and inherit
from Undoable.
"""


class UndoableSetExtendMode(Undoable):
    def _call(self, session):
        self.previous_mode = session.selection_mode
        session.selection_mode = modes.extend_mode

    def _undo(self, session):
        session.selection_mode = self.previous_mode

set_extend_mode = UndoableSetExtendMode()  # create action
set_extend_mode(mysession)  # execute the action on a session
set_extend_mode.undo(mysession)  # undo the action on a session


"""
We can turn a Selection also into an undoable action,
by specifying the following __call__ and undo methods.
"""


class Selection(Undoable):
    def __init__(self, intervals):
        # logic here
        pass

    def _call(self, session):
        self.previous_selection = session.selection
        session.selection = self

    def _undo(self, session):
        session.selection = self.previous_selection

my_selection = Selection(mysession, [(0, 0)])  # create selection
my_selection(mysession)  # execute the selection on a session
my_selection.undo(mysession)  # undo the selection on a session


"""
We will model Operations on text as actions as well.
"""


class Operation(Undoable):
    def __init__(self, selection, new_content):
        # logic here
        self.old_content = selection.content
        self.old_selection = selection
        self.new_content = new_content

    @property
    def new_selection(self):
        """The selection containing the potential result of the operation."""
        pass

    def _call(self, session):
        # logic here
        pass

    def _undo(self, session):
        # logic here
        pass


"""
Can we also create actions that perform differently depending
on the context? Let us try to implement a 'select everything'.
"""


def select_everything(session):
    interval = (0, len(session.text))
    session.selection = Selection(session, [interval])


"""
Instead of the above, we may want to subclass from Selection,
such that we can split the creation of the selection (by __init__)
and the execution of the selection (by __call__).
This way we can create selections, and inspect them, without
having to actually apply them to the session.
If we wouldn't care about that, we might as well use the above.
"""

#TODO: we also want to be able to accept a selection in the __init__.
#That way we can chain several selectors and inspect the result afterwards,
#without affecting a session.


class SelectEverything(Selection):
    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        selection_mode = selection_mode or session.selection_mode
        interval = (0, len(session.text))
        Selection.__init__(self, [interval])

my_select_everything = SelectEverything(mysession)  # create selection
my_select_everything(mysession)  # execute the selection on a session
my_select_everything.undo(mysession)  # undo the selection on a session


"""
Can we also create selections that are based on more input than
only the session, like for instance regex patterns?
"""


class SelectPattern(Selection):
    def __init__(self, pattern, session, selection=None, selection_mode=None, reverse=False, group=0):
        selection = selection or session.selection
        selection_mode = selection_mode or session.selection_mode
        # do pattern logic here

# make sure we only have to pass a session at runtime
from functools import partial
SelectIndent = partial(SelectPattern, r'(?m)^([ \t]*)', reverse=True, group=1)

indent = SelectIndent(mysession)  # create selection
indent(mysession)  # execute the selection on a session
indent.undo(mysession)  # undo the selection on a session


"""
Now we can call any function that takes a session and returns an
action an 'actor'. So in the above, select_somepattern is an actor,
which resulted from partially applying SelectPattern.
Note that Selection and Operation are not actors.
"""


"""
Can we also make actions which are incrementally constructed by the
user while getting feedback, like an insertion operation?
We will introduce the class Updateable for this.
We can update an updateable action by calling the update method on it
with custom arguments.
The finished flag is used to indicate that we finished updating the action.
This is needed for a possible container action to know which subaction the
update information should currectly be redirected to.

The UserInterface can know that we are in insert mode by checking if the
last operation is an unfinished updateable operation.
"""


class Updateable(Undoable):
    finished = False

    def update(self, session, *args):
        self._update(session, *args)
        session.actiontree.hard_undo()
        self(session)

    def _update(self, session, *args):
        raise Exception('An abstract method is not callable.')

    def finish(self):
        self.finished = True


#class Completeable(Operation, Updateable):
    #def __init__(self, selection):
        #Operation.__init__(self, selection, None)
        #self.insertions = ['' for _ in selection]
        #self.deletions = [0 for _ in selection]

    #def _update(self, session, string, complete):
        #if complete:
            #if session.completer.current_completion:
                #self.insertions = session.completer.current_completion
        #elif string:
            #self.insertions += string

    #def update(self, session, string='', complete=False):
        #Updateable.update(session, string, complete)
        #if string:
            #session.completer.update_completions()


class ChangeAfter(Operation, Updateable):
    def __init__(self, selection):
        Operation.__init__(self, selection, None)
        self.insertions = ['' for _ in selection]
        self.deletions = [0 for _ in selection]

    def _update(self, session, string, complete):
        if complete:
            if session.completer.current_completion:
                self.insertions = session.completer.current_completion
        elif string:
            self.insert(session, string)

    def insert(self, session, string):
        """Insert a string (typically a char) in the operation."""
        indent = SelectIndent(session, self.new_selection)
        for i in range(len(self.new_selection)):
            for char in string:
                if char == '\b':
                    # remove char
                    if self.insertions[i]:
                        self.insertions[i] = self.insertions[i][:-1]
                    else:
                        self.deletions[i] += 1
                elif char == '\n':
                    # add indent after \n
                    self.insertions[i] += char + indent.content[i]
                else:
                    # add char
                    self.insertions[i] += char

    def update(self, session, string='', complete=False):
        Updateable.update(session, string, complete)
        if string:
            session.completer.update_completions()

    @property
    def new_content(self):
        return [self.old_content[i][self.deletions[i]:]
                + self.insertions[i]
                for i in range(len(self.old_content))]


"""
To be able to compose undoable actions together, we define the class
Compound.
A sequence of actions is undoable iff all sub actions are undoable.
Note that the class CompoundAction is not an actor.
A compound action may also contain updatable actions.
"""


class CompoundAction(Updateable):
    def __init__(self, *args):
        self.subactions = args
        for subaction in self.subactions:
            if not isinstance(subaction, Undoable):
                raise Exception('Not all my subactions are undoable.')

    def _call(self, session):
        for subaction in self.subactions:
            subaction._call(session)

    def _undo(self, session):
        for subaction in self.subactions:
            subaction._undo(session)

    def _update(self, session, *args):
        for subaction in self.subactions:
            if isinstance(subaction, Updateable) and not subaction.finished:
                subaction.update(session, *args)
                return

    def finish(self):
        """Finish the next updateable subaction."""
        for subaction in self.subactions:
            if isinstance(subaction, Updateable) and not subaction.finished:
                subaction.finish()
                return

    @property
    def finished(self):
        """We are finished if all our subactions are finished."""
        for subaction in self.subactions:
            if isinstance(subaction, Updateable) and not subaction.finished:
                return True
        return False


"""
In order to be able to conveniently chain actors, we provide a
function that composes a sequence of actors into a single actor.
"""


def compose(*args):
    def compoundactor(session):
        subactions = [subactor(session) for subactor in args]
        return CompoundAction(*subactions)
    return compoundactor
my_chained_actor = compose(SelectEverything,  # create the compound actor
                           select_somepattern,
                           set_extend_mode)
my_chained_action = my_chained_actor(mysession)  # create compound action
my_chained_action(mysession)  # execute the compound action on a session
my_chained_action.undo(mysession)  # undo the compound action on a session
