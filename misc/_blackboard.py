"""
The goal of a text editor is to make modifications to a text.
More generally, the user should also be able to modify things other
than text, such as options or other meta stuff.
We store all relevant data for editing a text in a single object,
and call this object a document.

To make modifications to a document, we define actions.
An action is an abstract object that can make a modification to a
document. An action must therefore be executable (read: callable)
and accept a document as argument.
"""
from .. import modes
from ..document import Document
mydocument = Document()


"""
For instance, consider an action that changes the selection mode
of a document to EXTEND. This action could be implemented as follows.
"""


def set_extend_mode(document):
    document.selection_mode = modes.extend_mode


"""
Another equivalent way, using a class, would be:
"""


class SetExtendMode:

    def __call__(self, document):
        document.selection_mode = modes.extend_mode

set_extend_mode = SetExtendMode()  # create action
set_extend_mode(mydocument)  # execute the action on a document


"""
Actions like this can easily be composed, by putting them into a container action.
"""


def my_container_action(document):
    set_extend_mode(document)
    set_extend_mode(document)
    # etc


"""
For some actions, we want to be able to undo them.
Let us define the class Undoable for that.

Note that, all actions can be made trivially undoable,
by storing the document before and after applying the action.
This is however not desirable for reasons of space.
Therefore we leave the specific implementation
of the undo method to the concrete subclasses.
"""


class Undoable:

    def __call__(self, document):
        document.undotree.add(self)
        self._call(document)

    def undo(self, document):
        document.undotree.undo()
        self._undo(document)

    def _call(self, document):
        raise Exception("An abstract method is not callable.")

    def _undo(self, document):
        raise Exception("An abstract method is not callable.")


"""
Consider again the previous example. We will now make it undoable
by storing the relevant information in the action object and inherit
from Undoable.
"""


class UndoableSetExtendMode(Undoable):

    def _call(self, document):
        self.previous_mode = document.selection_mode
        document.selection_mode = modes.extend_mode

    def _undo(self, document):
        document.selection_mode = self.previous_mode

set_extend_mode = UndoableSetExtendMode()  # create action
set_extend_mode(mydocument)  # execute the action on a document
set_extend_mode.undo(mydocument)  # undo the action on a document


"""
We can turn a Selection also into an undoable action,
by specifying the following __call__ and undo methods.
"""


class Selection(Undoable):

    def __init__(self, intervals):
        # logic here
        pass

    def _call(self, document):
        self.previous_selection = document.selection
        document.selection = self

    def _undo(self, document):
        document.selection = self.previous_selection

my_selection = Selection(mydocument, [(0, 0)])  # create selection
my_selection(mydocument)  # execute the selection on a document
my_selection.undo(mydocument)  # undo the selection on a document


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

    def _call(self, document):
        # logic here
        pass

    def _undo(self, document):
        # logic here
        pass


"""
Can we also create actions that perform differently depending
on the context? Let us try to implement a 'select everything'.
"""


def select_everything(document):
    interval = (0, len(document.text))
    document.selection = Selection(document, [interval])


"""
Instead of the above, we may want to have it return an action,
such that we can split the creation of the selection (by __init__)
and the execution of the selection (by __call__).
This way we can create selections, and inspect them, without
having to actually apply them to the document.
If we wouldn't care about that, we might as well use the above.

Two alternatives. Looks like there are usecases for both of them,
so we might want to leave this choice open.

Conclusion: an actor is any class, function or callable object that takes a document and returns an action.

Observation: maybe we should not disinguish between actors and actions.
Just talk about actions and higher order actions. That makes several things easier.
Higher order actions may return a lower order actions if explicitly asked,
instead of just being executed.
"""


def SelectEverything(document, selection=None, selection_mode=None):
    """
        Good: - short and clear
        Bad: - cannot derive from Interactive etc
    """
    selection = selection or document.selection
    selection_mode = selection_mode or document.selection_mode
    interval = (0, len(document.text))
    return Selection([interval])


class SelectEverything2(Selection):

    """
        Good: - in case of updateable actions, we may need to be stored as
            a whole, in order to be able to undo and redo ourselves only
        Bad: - needs more knowledge of Selection's inner working
             - compound actors that are only partly undoable are stored completely
    """

    def __init__(self, document, selection=None, selection_mode=None):
        selection = selection or document.selection
        selection_mode = selection_mode or document.selection_mode
        interval = (0, len(document.text))
        Selection.__init__(self, [interval])

my_select_everything = SelectEverything2(mydocument)  # create selection
my_select_everything(mydocument)  # execute the selection on a document
my_select_everything.undo(mydocument)  # undo the selection on a document


"""
Can we also create selections that are based on more input than
only the document, like for instance regex patterns?
"""


class SelectPattern(Selection):

    def __init__(self, pattern, document, selection=None, selection_mode=None, reverse=False, group=0):
        selection = selection or document.selection
        selection_mode = selection_mode or document.selection_mode
        # do pattern logic here

# make sure we only have to pass a document at runtime
from functools import partial
SelectIndent = partial(SelectPattern, r'(?m)^([ \t]*)', reverse=True, group=1)

my_indent = SelectIndent(mydocument)  # create selection
my_indent(mydocument)  # execute the selection on a document
my_indent.undo(mydocument)  # undo the selection on a document


"""
Now we can call any function that takes a document and returns an
action an 'actor'. So in the above, select_somepattern is an actor,
which resulted from partially applying SelectPattern.
Note that Selection and Operation are not actors.

To improve selection/interval arithmetic, we should override basic operators
for the classes Selection and Interval.
(a,b)+(c,d)=(min(a,b),max(c,d))
s+t=s.extend(t)
Note that interval selector behaviour follows from these definitions.
"""


"""
Can we also make actions which are incrementally constructed by the
user while getting feedback, like an insertion operation?
We will introduce the class Updateable for this.
We can update an updateable action by calling the update method on it
with custom arguments.


More generally speaking, we want to interact with a general object/action
(that is not necessarily undoable).
So we need to think about how to implement interaction in the most general way.
We can introduce an interaction stack, such that we can nest interactions.
If we then finish an interaction, we can pop it from the stack and be dropped
into the parent interaction.


The finished flag is used to indicate that we finished updating the action.
This is needed for a possible container action to know which subaction the
update information should currectly be redirected to.
"""


class Interactive:
    finished = False

    def __call__(self, document):
        document.interaction_stack.push(self)
        self._call(document)

    def finish(self, document):
        # TODO maybe add optional callback function for after the interaction
        self.finished = True
        document.interaction_stack.pop()

    def _call(self, document):
        raise Exception("An abstract method is not callable.")


class Updateable(Undoable, Interactive):

    """Updateable action."""

    def update(self, document):
        """
        Makes sure to apply the update to the document.
        """
        document.undotree.hard_undo()
        self(document)


class InsertOperation(Operation, Updateable):

    """Abstract class for operations dealing with insertion of text."""

    def __init__(self, selection):
        Operation.__init__(self, selection, None)
        self.insertions = ['' for _ in selection]
        self.deletions = [0 for _ in selection]

    def insert(self, document, string):
        """
        Insert a string (typically a char) in the operation.
        By only autoindenting on a single \n, we potentially allow proper pasting.
        """
        indent = SelectIndent(document, self.new_selection)
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

        self.update(document)


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
                          + self.old_content[i][
                              self.deletions[i]:-self.deletions[i] or None
                          ]
                          + second_string)
        return result


"""
Eventually we also want to have completion, so we should see if we
can fit that into our current design.
Let us introduce a subclass of InsertOperation named Completeable.
"""


class Completeable(InsertOperation):

    """Abstract class for insert operations that can be completed."""

    def complete(self, document):
        if document.completer.current_completion:
            self.insertions = document.completer.current_completion
            self.update(document)

    def insert(self, document, string):
        super().insert(document, string)
        # Notify the completer that the insertions have changed
        document.completer.need_refresh = True


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
or store a snippet object in the document which is updateable and subsequently stores
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

    def _call(self, document):
        selection = document.selection
        snippet_insertions = [self.snippet_text for _ in selection]
        insert_snippet = Operation(selection, snippet_insertions)
        insert_snippet(document)

    def next_placeholder(self, document):
        # TODO update selectionlist after previous modifications
        # Selection needs method to compute itself after an Operation
        if self.current_selection < len(self.selection_list):
            self.current_selection += 1
            document.selection = self.selection_list[self.current_selection]
            fill_placeholder = ChangeInPlace(document)
            fill_placeholder(document)
        else:
            self.finish(document)


"""
To be able to do sequences of actions as a whole, we introduce the Compound class.
All its subactions must be Undoable, and may be Updateable.

When an interaction is composed into an undoable sequence, we want the tail of the sequence to wait until an earlier interaction has finished.

A compound action should be transparent to classes such as Completeable, Interactive, Undoable, etc such that arbitrary actions can be composed together.
If a new action class is written that needs explicit support from Compound
to be able to be composed, you have to subclass Compound, modify it to
your needs, and use that subclass for your stuff.
"""
# TODO: Problem
# How can we let the compound actions know that a child has been finished?
# Option 1: give the child a callback function
# Option 2: make all updates go through parents


class Compound(Updateable):

    def __init__(self, *args):
        self.subactions = args
        for subaction in self.subactions:
            if not isinstance(subaction, Undoable):
                raise Exception('Not all my subactions are undoable.')

    def _call(self, document):
        for subaction in self.subactions:
            subaction._call(document)
            if isinstance(subaction, Updateable) and not subaction.finished:
                return

    # def _update(self, document, *args):
        #"""Update the next updateable subaction."""
        # for subaction in self.subactions:
            # if isinstance(subaction, Updateable) and not subaction.finished:
                #subaction._update(document, *args)
                # return

    # def finish(self):
        #"""Finish the next updateable subaction."""
        # for subaction in self.subactions:
            # if isinstance(subaction, Updateable) and not subaction.finished:
                # subaction.finish()
                # return

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
    def compoundactor(document):
        subactions = [subactor(document) for subactor in args]
        return Compound(*subactions)
    return compoundactor
my_chained_actor = compose(SelectEverything,  # create the compound actor
                           SelectIndent,
                           set_extend_mode)
my_chained_action = my_chained_actor(mydocument)  # create compound action
my_chained_action(mydocument)  # execute the compound action on a document
my_chained_action.undo(mydocument)  # undo the compound action on a document
