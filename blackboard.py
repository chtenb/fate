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
        session.undotree.add(self)
        self._call(session)

    def undo(self, session):
        session.undotree.undo()
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

my_indent = SelectIndent(mysession)  # create selection
my_indent(mysession)  # execute the selection on a session
my_indent.undo(mysession)  # undo the selection on a session


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


class Interactive:
    finished = False

    def __call__(self, session):
        session.interaction_stack.push(self)
        self._call(session)

    def finish(self, session):
        # TODO maybe add optional callback function for after the interaction
        self.finished = True
        session.interaction_stack.pop()

    def _call(self, session):
        raise Exception("An abstract method is not callable.")


class Updateable(Undoable, Interactive):
    """Updateable action."""

    def update(self, session):
        """
        Makes sure to apply the update to the session.
        """
        session.undotree.hard_undo()
        self(session)


class InsertOperation(Operation, Updateable):
    """Abstract class for operations dealing with insertion of text."""
    def __init__(self, selection):
        Operation.__init__(self, selection, None)
        self.insertions = ['' for _ in selection]
        self.deletions = [0 for _ in selection]

    def insert(self, session, string):
        """
        Insert a string (typically a char) in the operation.
        By only autoindenting on a single \n, we potentially allow proper pasting.
        """
        indent = SelectIndent(session, self.new_selection)
        for i in range(len(self.new_selection)):
            if string == '\b':
                # remove string
                if self.insertions[i]:
                    self.insertions[i] = self.insertions[i][:-1]
                else:
                    self.deletions[i] += 1
            elif string == '\n':
                # add indent after \n
                self.insertions[i] += string + indent.content[i]
            else:
                # add string
                self.insertions[i] += string

        self.update(session)


class ChangeAround(InsertOperation):
    @property
    def new_content(self):
        character_pairs = [('{', '}'), ('[', ']'), ('(', ')')]
        result = []
        for i in range(len(self.old_content)):
            first_string = self.insertions[i][::-1]
            second_string = self.insertions[i]
            for first, second in character_pairs:
                first_string = first_string.replace(second, first)
                second_string = second_string.replace(first, second)
            result.append(first_string
                          + self.old_content[i][self.deletions[i]:-self.deletions[i] or None]
                          + second_string)
        return result


"""
Eventually we also want to have completion, so we should see if we
can fit that into our current design.
Let us introduce a subclass of InsertOperation named Completeable.
"""


class Completeable(InsertOperation):
    """Abstract class for insert operations that can be completed."""
    def complete(self, session):
        if session.completer.current_completion:
            self.insertions = session.completer.current_completion
            self.update(session)

    def insert(self, session, string):
        super().insert(session, string)
        # Notify the completer that the insertions have changed
        session.completer.need_refresh = True


class ChangeAfter(Completeable):
    @property
    def new_content(self):
        return [self.old_content[i][self.deletions[i]:]
                + self.insertions[i]
                for i in range(len(self.old_content))]


class ChangeInPlace(Completeable):
    @property
    def new_content(self):
        return [self.insertions[i] for i in range(len(self.old_content))]

"""
Snippet expansion should be trivial due to our abstract machinery.
There are several possibilities.
Do we want to make it a single action, or do we want to have an action for each placeholder?
In the first case we have to make it a CompoundAction.
In the second case we can either store the actions in advance (annoying to implement)
or store a snippet object in the session which is updateable and subsequently stores
placeholder actions in the undotree.
This requires a seperate field for updateable actions.
Updateable actions are then no longer determined from the last action in the history,
but have a separate field.

Generally speaking, we want to interact with a general object/action (that is not necessarily undoable).
In this case, a snippet object.
While interacting with the snippet object, we get multiple other interactions with ChangeInPlace operations.

So we need to think about how to implement interaction in the most general way.
We can introduce an interaction stack, such that we can nest interactions.
If we then finish an interaction, we are dropped into the previous interaction.
By default we must interact through characters that are typed by the user.
This is not very configurable, so for some interactive actions we must use other interaction data.
In those cases, support by the user interface is needed, to translate the users insertions to the data of choice.
An alternative is to move this part to the fate core, but that kind of denies the design statement of splitting the user interface from the core.
To generalize ui support for the interactions, we maybe could have dictionaries for the different types of interactions.

SOLUTION:
The UI must have knowledge about subclasses of Interactive, like InsertOperation, en have interpretation functions for them. That can be a
dict: key -> func, but also a function that translates keys to characters and passes them to the insert method of InsertOperation
"""


class Snippet(Interactive):
    def __init__(self, snippet_text, selection_list):
        self.snippet_text = snippet_text
        self.selection_list = selection_list
        self.current_selection = 0

    def _call(self, session):
        selection = session.selection
        snippet_insertions = [self.snippet_text for _ in selection]
        insert_snippet = Operation(selection, snippet_insertions)
        insert_snippet(session)

    def next_placeholder(self, session):
        # TODO update selectionlist after previous modifications
        # Selection needs method to compute itself after an Operation
        if self.current_selection < len(self.selection_list):
            self.current_selection += 1
            session.selection = self.selection_list[self.current_selection]
            fill_placeholder = ChangeInPlace(session)
            fill_placeholder(session)
        else:
            self.finish(session)


"""
To be able to compose actions together, we define the class Compound.
A sequence of actions is undoable iff all sub actions are undoable.
A sequence of actions is interactive iff some sub actions are interactive.
Note that the class CompoundUndoable is not an actor.
A compound action should be transparent to classes such as Completeable,
such that arbitrary actions can be composed together.
"""


class Compound(Interactive, Undoable):
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

    def update(self, session, *args):
        """Update the next updateable subaction."""
        for subaction in self.subactions:
            if isinstance(subaction, Updateable) and not subaction.finished:
                subaction._update(session, *args)
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
In order to be able to conveniently chain undoable actors, we provide a
function that composes a sequence of undoable actors into a single undoable actor.
"""


def compose(*args):
    def compoundactor(session):
        subactions = [subactor(session) for subactor in args]
        return Compound(*subactions)
    return compoundactor
my_chained_actor = compose(SelectEverything,  # create the compound actor
                           SelectIndent,
                           set_extend_mode)
my_chained_action = my_chained_actor(mysession)  # create compound action
my_chained_action(mysession)  # execute the compound action on a session
my_chained_action.undo(mysession)  # undo the compound action on a session
