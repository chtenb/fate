"""
The goal of a text editor is to make modifications to a text.
More generally, the user should also be able to modify things other
than text, such as options or other meta stuff.
We store all relevant data for editing a text in a single object,
and call this object a document.

To make modifications to a document, we define commands.
An command is an abstract object that can make a modification to a
document. An command must therefore be executable (read: callable)
and accept a document as argument.
"""
from .. import modes
from ..document import Document
mydocument = Document()


"""
For instance, consider an command that changes the selection mode
of a document to EXTEND. This command could be implemented as follows.
"""


def set_extend_mode(document):
    document.selection_mode = modes.extend_mode


"""
Another equivalent way, using a class, would be:
"""


class SetExtendMode:

    def __call__(self, document):
        document.selection_mode = modes.extend_mode

set_extend_mode = SetExtendMode()  # create command
set_extend_mode(mydocument)  # execute the command on a document


"""
Actions like this can easily be composed, by putting them into a container command.
"""


def my_container_command(document):
    set_extend_mode(document)
    set_extend_mode(document)
    # etc


"""
For some commands, we want to be able to undo them.
Let us define the class Undoable for that.

Note that, all commands can be made trivially undoable,
by storing the document before and after applying the command.
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
by storing the relevant information in the command object and inherit
from Undoable.
"""


class UndoableSetExtendMode(Undoable):

    def _call(self, document):
        self.previous_mode = document.selection_mode
        document.selection_mode = modes.extend_mode

    def _undo(self, document):
        document.selection_mode = self.previous_mode

set_extend_mode = UndoableSetExtendMode()  # create command
set_extend_mode(mydocument)  # execute the command on a document
set_extend_mode.undo(mydocument)  # undo the command on a document


"""
We can turn a Selection also into an undoable command,
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
We will model Operations on text as commands as well.
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
Can we also create commands that perform differently depending
on the context? Let us try to implement a 'select everything'.
"""


def select_everything(document):
    interval = (0, len(document.text))
    document.selection = Selection(document, [interval])


"""
Instead of the above, we may want to have it return an command,
such that we can split the creation of the selection (by __init__)
and the execution of the selection (by __call__).
This way we can create selections, and inspect them, without
having to actually apply them to the document.
If we wouldn't care about that, we might as well use the above.

Two alternatives. Looks like there are usecases for both of them,
so we might want to leave this choice open.

Conclusion: an actor is any class, function or callable object that takes a document and returns an command.

Observation: maybe we should not disinguish between actors and commands.
Just talk about commands and higher order commands. That makes several things easier.
Higher order commands may return a lower order commands if explicitly asked,
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
        Good: - in case of updateable commands, we may need to be stored as
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
command an 'actor'. So in the above, select_somepattern is an actor,
which resulted from partially applying SelectPattern.
Note that Selection and Operation are not actors.

To improve selection/interval arithmetic, we should override basic operators
for the classes Selection and Interval.
(a,b)+(c,d)=(min(a,b),max(c,d))
s+t=s.extend(t)
Note that interval selector behaviour follows from these definitions.
"""


"""
Can we also make commands which are incrementally constructed by the
user while getting feedback, like an insertion operation?
We will introduce the class Updateable for this.
We can update an updateable command by calling the update method on it
with custom arguments.


More generally speaking, we want to interact with a general object/command
(that is not necessarily undoable).
So we need to think about how to implement intercommand in the most general way.
We can introduce an intercommand stack, such that we can nest intercommands.
If we then finish an intercommand, we can pop it from the stack and be dropped
into the parent intercommand.


The finished flag is used to indicate that we finished updating the command.
This is needed for a possible container command to know which subcommand the
update information should currectly be redirected to.
"""


class Interactive:
    finished = False

    def __call__(self, document):
        document.intercommand_stack.push(self)
        self._call(document)

    def finish(self, document):
        # TODO maybe add optional callback function for after the intercommand
        self.finished = True
        document.intercommand_stack.pop()

    def _call(self, document):
        raise Exception("An abstract method is not callable.")


class Updateable(Undoable, Interactive):

    """Updateable command."""

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
Do we want to make it a single command, or do we want to have an command for each placeholder?
In the first case we have to make it a CompoundAction.
In the second case we can either store the commands in advance (annoying to implement)
or store a snippet object in the document which is updateable and subsequently stores
placeholder commands in the undotree.
This requires a seperate field for updateable commands.
Updateable commands are then no longer determined from the last command in the history,
but have a separate field.

Generally speaking, we want to interact with a general object/command (that is not necessarily undoable).
In this case, a snippet object.
While interacting with the snippet object, we get multiple other intercommands with ChangeInPlace operations.

So we need to think about how to implement intercommand in the most general way.
We can introduce an intercommand stack, such that we can nest intercommands.
If we then finish an intercommand, we are dropped into the previous intercommand.
By default we must interact through characters that are typed by the user.
This is not very configurable, so for some interactive commands we must use other intercommand data.
In those cases, support by the user interface is needed, to translate the users insertions to the data of choice.
An alternative is to move this part to the fate core, but that kind of denies the design statement of splitting the user interface from the core.
To generalize ui support for the intercommands, we maybe could have dictionaries for the different types of intercommands.

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
To be able to do sequences of commands as a whole, we introduce the Compound class.
All its subcommands must be Undoable, and may be Updateable.

When an intercommand is composed into an undoable sequence, we want the tail of the sequence to wait until an earlier intercommand has finished.

A compound command should be transparent to classes such as Completeable, Interactive, Undoable, etc such that arbitrary commands can be composed together.
If a new command class is written that needs explicit support from Compound
to be able to be composed, you have to subclass Compound, modify it to
your needs, and use that subclass for your stuff.
"""
# TODO: Problem
# How can we let the compound commands know that a child has been finished?
# Option 1: give the child a callback function
# Option 2: make all updates go through parents


class Compound(Updateable):

    def __init__(self, *args):
        self.subcommands = args
        for subcommand in self.subcommands:
            if not isinstance(subcommand, Undoable):
                raise Exception('Not all my subcommands are undoable.')

    def _call(self, document):
        for subcommand in self.subcommands:
            subcommand._call(document)
            if isinstance(subcommand, Updateable) and not subcommand.finished:
                return

    # def _update(self, document, *args):
        #"""Update the next updateable subcommand."""
        # for subcommand in self.subcommands:
            # if isinstance(subcommand, Updateable) and not subcommand.finished:
                #subcommand._update(document, *args)
                # return

    # def finish(self):
        #"""Finish the next updateable subcommand."""
        # for subcommand in self.subcommands:
            # if isinstance(subcommand, Updateable) and not subcommand.finished:
                # subcommand.finish()
                # return

    @property
    def finished(self):
        """We are finished if all our subcommands are finished."""
        for subcommand in self.subcommands:
            if isinstance(subcommand, Updateable) and not subcommand.finished:
                return True
        return False


"""
In order to be able to conveniently chain undoable actors, we provide a
function that composes a sequence of undoable actors into a single undoable actor.
"""


def compose(*args):
    def compoundactor(document):
        subcommands = [subactor(document) for subactor in args]
        return Compound(*subcommands)
    return compoundactor
my_chained_actor = compose(SelectEverything,  # create the compound actor
                           SelectIndent,
                           set_extend_mode)
my_chained_command = my_chained_actor(mydocument)  # create compound command
my_chained_command(mydocument)  # execute the compound command on a document
my_chained_command.undo(mydocument)  # undo the compound command on a document

#--------------------------------------


"""
Things to explain:
    definition command

    definition mode (=stateful command)

    why using modes as opposed to using while loop inside command

    how commands can be decorated

    why stateful commands have to be classes or some function that
    creates objects, because we want them to be able to be used
    across documents at the same time


To be decided upon:
    Why we can have commands as input instead of characters
    What to do with mouse input etc
        Allow any type of userinput, e.g. mouse event objects?
        Then let the mode decide what to do with it
        For now...
        It's the most general/powerful approach

"""

#
# -------------------------------------------------------------------
#

import logging

"""
The goal of a text editor is to make modifications to a text.
More generally, the user should also be able to modify things other
than text, such as options or other meta stuff.
We store all relevant data for editing a text in a single object,
and call this object a document.

To make modifications to a document, we define commands.
A command is an abstract object that can make a modification to a
document. A command must therefore be executable (read: callable)
and accept a document as argument.
"""

"""
For instance, consider a very simple implementation of a command that
saves the text of the document to a file.
"""


def save(document):
    """Save document text to file."""
    if document.filename:
        try:
            with open(filename, 'w') as fd:
                fd.write(document.text)
        except (FileNotFoundError, PermissionError) as e:
            logging.error(str(e))
    else:
        logging.error('No filename')


"""
Can we also make commands which are incrementally constructed by the
user while getting feedback, like an insertion operation?
"""

"""
Let us take a simple example command which lets the user set the filename.
One way to do this would be as follows.
Suppose that we can get a character from the user by calling document.ui.getkey().
"""


def setfilename(document):
    filename = ''
    while 1:
        key = document.ui.getkey()
        if key == 'Esc':
            break
        elif key == '\n':
            document.filename = filename
            return
        elif key == '\b':
            filename = filename[:-1]
        else:
            filename += key


"""
One good thing about this definition is that it's easy to write and understand.
But there are several major drawbacks.

Most importantly it blocks the entire thread and as such doesn't allow the user
to do something else, like switching to another document, until this command is finished.
A possible solution to this would be to give each document its own command thread.
But this is complicated, likely to give lots of crossthreading bugs, and removes
the possibility to write commands that operate on multiple documents.
An example of such a command could be a search/replace command over all documents.

...
"""

"""
Another approach to implemented these kind of commands is by making them stateful.
Such a stateful command is then stored somewhere in the document object,
and is somehow called when there is input to process.
Let us call a stateful commands a 'mode' and assume it is stored in document.mode.
Assume that a mode needs to have a method 'processinput'
which is called with the userinput.
"""


class SetFileName:

    def __init__(self, document):
        self.doc = document
        document.mode = self
        self.filename = ''

    def processinput(self, userinput):
        if type(userinput) == str:
            # User input is a string
            # Maybe a single character
            key = userinput
            if key == 'Esc':
                return
            elif key == '\n':
                self.doc.filename = filename
                return
            elif key == '\b':
                filename = filename[:-1]
            else:
                filename += key
        if isinstance(userinput, MouseEvent):
            # The userinput appears to be a mouse event type
            # Cancel upon mouse click
            return
        else:
            # Userinput is maybe a command, like next_document or delete
            # Type not supported
            pass

"""
This command is truly stateful as it can be interrupted anytime without being corrupted.
"""

