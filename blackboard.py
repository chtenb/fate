"""
The main object in fate is a session. The session stores all
relevant information for editing a single text.

An action is an abstract object that can make a modification to a
session. An action must therefore be callable and accept a session
as argument.
"""
from . import modes
from .session import Session
mysession = Session()

"""
For instance, consider an action that changes the selection mode
of a session to EXTEND. This action could be implemented like
"""
def set_extend_mode(session):
    session.selection_mode = modes.extend_mode

"""
Another equivalent way, using a class, would be
"""
class SetExtendMode:
    def __call__(self, session):
        session.selection_mode = modes.extend_mode
set_extend_mode = SetExtendMode() # create action
set_extend_mode(mysession) # execute the action on a session

"""
Some actions are undoable, which means that they possess an
undo method. An action is previewable iff it is undoable.
Consider again the previous example. We will now make it undoable
by storing the relevant information in the action object.
All actions can be made trivially undoable, by storing the session
before and after applying the action. This is however not
desirable for reasons of space.
NOTE: actions are really undoable if they inherit from Undoable.
"""
class UndoableSetExtendMode:
    def __call__(self, session):
        self.previous_mode = session.selection_mode
        session.selection_mode = modes.extend_mode
    def undo(self, session):
        session.selection_mode = self.previous_mode
set_extend_mode = UndoableSetExtendMode() # create action
set_extend_mode(mysession) # execute the action on a session
set_extend_mode.undo(mysession) # undo the action on a session

"""
We can turn a Selection also into an undoable action,
by specifying the following __call__ and undo methods.
"""
class Selection:
    def __init__(self, session, intervals):
        # init logic here
        pass
    def __call__(self, session):
        self.previous_selection = session.selection
        session.selection = self
    def undo(self, session):
        session.selection = self.previous_selection
my_selection = Selection(mysession, [(0,0)]) # create selection
my_selection(mysession) # execute the selection on a session
my_selection.undo(mysession) # undo the selection on a session



"""
Can we also create actions that perform differently depending
on the context? Let us try to implement a 'select everything'.
"""
def select_everything(session):
    interval = (0, len(session.text))
    session.selection = Selection(session, [interval])

"""
We may want to subclass from Selection, such that we can split
the creation of the selection (by __init__) and the execution of
the selection (by __call__).
This way we can create selections, and inspect them, without
having to actually apply them to the session.
If we wouldn't care about that, we might as well use the above.
"""
class SelectEverything(Selection):
    def __init__(self, session):
        interval = (0, len(session.text))
        Selection.__init__(self, session, [interval])
my_select_everything = SelectEverything(mysession) # create selection
my_select_everything(mysession) # execute the selection on a session
my_select_everything.undo(mysession) # undo the selection on a session



"""
Can we also create selections that are based on more input than
only the session, like for instance regex patterns?
"""
class SelectPattern(Selection):
    def __init__(self, pattern, session):
        # Do logic here
        pass
# make sure we only have to pass a session at runtime
from functools import partial
select_somepattern = partial(SelectPattern, 'somepattern')

my_select_somepattern = select_somepattern(mysession) # create selection
my_select_somepattern(mysession) # execute the selection on a session
my_select_somepattern.undo(mysession) # undo the selection on a session

"""
Now we can call any function that takes a session and returns an
action an 'actor'. So in the above, select_somepattern is an actor,
which resulted from partially applying SelectPattern.
"""

"""
Actions can be composed into a compound action.
Note that the class CompoundAction is not an actor.
A CompoundAction is undoable iff all sub actions are undoable.
"""
class CompoundAction:
    def __init__(self, *args):
        self.subactions = args
    def __call__(self, session):
        for subaction in self.subactions:
            subaction(session)
    def undo(self, session):
        for subaction in self.subactions:
            if not hasattr(subaction, 'undo'):
                raise Exception('Not all my subactions are undoable.')
        for subaction in self.subactions:
            subaction.undo(session)






