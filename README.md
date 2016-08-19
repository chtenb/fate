This project is in an experimental state. No individuals affiliated with this project can be
held responsible for any kind of damage caused by usage of this software.

[![Build Status](https://travis-ci.org/Chiel92/fate.svg?branch=action-machinery-rewrite)](https://travis-ci.org/Chiel92/fate)

Fate
====
F.A.T.E. is a highly programmable text editor, mainly intended for programming purposes.

Purpose
-------
The most important values for fate are the following.
1. Fate must be a convenient text editor to work with.
2. Fate must be able to act as a text processing language.
3. Fate must be highly programmable.

Combining these targets in one application has several advantages.
If you use fate as your text editor that makes it easy to write text processing scripts as you
very well know its concepts and commands. You don't need to learn a new language and google
around to find the commands you need, as may be the case with tools like awk, sed etcetera.
Conversely, having an interactive mode in your text processing language allows you to test your
programs interactively and even record your programs as macros.
The programmability is needed, if not required, by both values 1 and 2.
It namely gives the resulting text processing language arbitrary power. And looking at other
editors, it is readily observed that a text editor must be easily extendable in order to be
successful.


What you should know
--------------------
What originally started out as a rewrite of Vim in python, ended up as an entirely new text
editor.
Vim is a great text editor.
However, there are several issues I felt that needed to be adressed.
De code base is old and getting messy and is therefore hard to maintain.
It is not very extensible, even though vim has its own scripting language.
VimLanguage is neither easy to master, readable nor fast.
The architecture needs to be revised, for instance, it should not be restricted to a
single thread.
Another bad thing is that vim tries to be backward compatible too much (even with vi!).
This results in all kinds of artifacts that only exist for historical reasons.
I don't want that. Once in a while, backward compatibility needs to be broken due to new
developments or new insights.
Python's transition to version 3 is a good example of this.
Neovim tries to fix some of these problems, which is a good thing in my opinion, but it is
not drastically enough.
So we are not trying to be compatible with vim, let alone vi.

Given these things, the best option is to write a new text editor from scratch.
We would like to have a powerful, yet small, extendible and pluggable code base.
The language of choice is Python, because

- it is easy, which is not only a good thing in itself, but also makes doing contributions easier
- allows to write relatively short and elegant code
- naturally the scripting language will be python as well, such that we get the scripting
  machinery almost for free
- because there are several python implementations, this even potentially allows fate to
  be run in-browser
- performance critical parts can easily be implemented as a C or C++ extension, or using
  Cython, when the need arises

Vim has several user interfaces, due to the many platforms and user preferences.  To
anticipate on this, we will separate the user interface from the underlying machinery.

While writing a text editor from scratch anyway, we have the opportunity to rethink the
way vim works.
There is room for improvement.

Vim's visual mode removed the need for marks (at least for using them as motions).
Why don't we take this one step further?
Let's make all motions visual, such that we can select a word by pressing `w`, and then
change it by pressing `c`.
In vim we would have to press `cw`, not getting feedback on what we selected.
From an architectural point of view, the new approach is also appealing, as it removes the
need for a distinction between visual mode and normal mode.
The syntax diagram will be easier, there is no need for a change mode, which accepts motions,
but instead we can just select something and apply an operator.
Note that we remove the concept of a cursor.
We always work with entire selections instead.

Secondly, we like to generalize vim's modal approach.
We want the user to be able to add new modes easily.
This way things like snippet expansion can be implemented with a snippet mode.

Thirdly, we will not invent our own regex language or scripting language like vim did, but
stick to python and it's regex language.
It is a good, well documented, well known engine, and we get it for free.

Fourthly, since we can never always anticipate in what environments people want to use a text
editor (terminal, gui, in-browser, visual studio plugin, etc) we leave the userinterface out of
the project.
This potentially also allows to use fate as a text editing library.
If we pull this off really well, fate might even be used as glue for many editor agnostic
feature implementations, such as completers, snippet expanders, syntax highlighters, error
checkers, code formatters, etc.


How to install
--------------
Available [here][fate-tui]

Documentation
-------------
Available [here][docs].

Design
======
Here we state some important design decisions that were made.

Performance of text modifications
---------------------------------
To be able to efficiently do operations on the text while keeping the possibility to
execute regex queries, we need a C/C++ data structure that acts as a string (implementing
python's buffer protocol) but which is a different tree structure underneath.
Question: is the text lazily loaded from the harddisk?

Text display augmenting features (a.k.a. syntax highlighting and text concealment)
----------------------------------------------------------------------------------
There are two categories of syntactic constructs that we may want to match and augment in a text:
- those that require the entire text to be parsed (e.g. constructs with ambiguous
  delimiters such as strings)
- those that don't (e.g. keywords, matching parenthesis)

The first category needs the entire text, and can thus only be performed if the textsize is
small enough or if its not used frequently or automatically (syntax highlighting) and the
user is willing to wait that long.
The second category can be parsed by only looking in a small window of the text.

A text display augmenting feature can be implemented by a map from positions to objects,
e.g. an array with an offset or a dictionary. Mapping from intervals instead of positions
will only decrease space requirements with a constant, while increasing the time
requirements with a constant.
How can we represent non-injective relationships?

Todo
====
SHORT TERM
- Integrate TextTransformation
  - Make Operation a subclass of TextTransformation and Undoable.
  - Implement insert mode preview as concealments.
  - Distinguish between concealment inside and outside selections. The epsilon that replaces
    empty intervals in tfate should be defined as a concealment. This changes how often and
    when the concealment is computed. I.e. it is not possible to insert characters now, ony
    substitutions are supported.
  - Make textview a container of pre mapped stuff, like selection view.
  - Make selection accept adjacent intervals. If this is not preferable for user selections
    introduce a class UserSelection with the restriction.
- Add CLI interface for batch processing. Only allowing key input here is fine for now.
  - Things like completion need to be disabled for this to speed up starting fate
- Fix interval mapping.
- Add textview creation to randomized userinterface.
- Clipboard should be shared among documents to make it possible to copy paste across.
- Implement repeat
  - Record input of user
  - next_document should also be recorded: this just makes repeat more powerful
  - Be able to save these macros, and be able to construct macros via literal input.
    This makes it easy to record a macro and use it for bulk editing

MIDDLE TERM
- Create a check_types precondition.
- Navigation mode.
- Make it easily possible to integrate fate into other text editors.
- Make fate save a recovery file on crash to prevent dataloss.
- Create an options namespace.
  - To separate variables that can be arbitrarily configured by the user from variables that
    are simply part of the document state and should not be corrupted.
  - To allow for automated testing with arbitrary configurations.
- Make sphinx documentation up to date.
- Tests for selectors.
- Make labeling generation asynchronous
- Fix unnecessary pylint complains
- Enhance selector set
- Text datastructure that is optimized for text editing
  - For small to normal texts: plain string
  - As soon as the text gets too big, split up into (not too small) blocks of a fixed size.
    Use a binary search tree to find the right block fast.
    Functionality that need the entire text as plain string must be disabled in this mode.
    Substring search must be implemented manually, regex search is only possible on a local
    scale.
  - Switching between these modes should be done automatically, but it should be possible to
    override manually.
- Implement commandmode as a persistent command, similar to undomode
- Improve syntax highlighting, for instance by disregarding quotes inside comments and strings
  - select around should maybe also disregard brackets etc in comments and strings
  - Maybe it helps to only match regex per line in some cases
- Snippet technology
  - Expand and surround/refactoring
- Easier file opening

LONG TERM
- Different forms of wrapping left/right + word/character?
- Use a tool that computes unit test coverage.
- Create something that computes the internal crash probability (per input unit) based on the randomized tests? Not sure if this is feasible, since once crashes they should be fixed right away.
- Think about to what extent we can have static type checking.
- Incorporate testing with multiple documents
- Think about how to decorate classes easily, without disabling subclassing
  - Can't decorate classes by functions: this turns them into functions
  - This means that they can't be used as parentclass
  - and that they can't be checked by issubclass
- Think about possibility to add remap support (i.e. map keys forall modes)
  - This is a generalization of the cancelkey feature
- Drag text operation, i.e. visual cut & paste or swapping text
- Persistent document (does this relate to recovery file?)
- Switch to alternative regex engine?
- Idea: jumplist of lines of changes
- Some sort of semantic snippet recognition, e.g. two identifiers that always need to be the same.
  If one changes, the other changes with it.
- Binary search for selections? Easymotion?











API Philosophy
--------------
This is a brief introduction in how the extensibility of fate is designed by explaining some of
the core constructions. For the actual implementations you're gonna have to dig into the code,
which shouldn't be too hard, since the codebase is relatively small.

The goal of a text editor is to make modifications to a text.  More generally, the user should
also be able to modify things other than text, such as options or other meta stuff.  We store
all relevant data for editing a text in a single object, and call this object a document.

To make modifications to a document, we define commands.  An command is an abstract object that
can make a modification to a document. An command must therefore be executable (read: callable)
and accept a document as argument.  For instance, consider an command that changes the
selection mode of a document to EXTEND. This command could be implemented as follows.

For instance, consider a very simple implementation of a command that
saves the text of the document to a file.

```python
def save(document):
    Save document text to file.
    if document.filename:
        try:
            with open(filename, 'w') as fd:
                fd.write(document.text)
        except (FileNotFoundError, PermissionError) as e:
            logging.error(str(e))
    else:
        logging.error('No filename')
```

Can we also make commands which are incrementally constructed by the
user while getting feedback, like an insertion operation?

```python
def set_tail_mode(document):
    document.selection_mode = selecting.tail_mode
```

Another equivalent way, using a class, would be:

```python
class SetExtendMode:

    def __call__(self, document):
        document.selection_mode = selecting.tail_mode

set_tail_mode = SetExtendMode()  # create command
set_tail_mode(mydocument)  # execute the command on a document
```

Commands like this can easily be composed, by putting them into a container command.

```python
def my_container_command(document):
    set_tail_mode(document)
    set_tail_mode(document)
    # etc
```

Let us take a simple example command which lets the user set the filename.
One way to do this would be as follows.
Suppose that we can get a character from the user by calling document.ui.getkey().

```python
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
```

One good thing about this definition is that it's easy to write and understand.
But there are several major drawbacks.

Most importantly it blocks the entire thread and as such doesn't allow the user
to do something else, like switching to another document, until this command is finished.
A possible solution to this would be to give each document its own command thread.
But this is complicated, likely to give lots of crossthreading bugs, and removes
the possibility to write commands that operate on multiple documents.
An example of such a command could be a search/replace command over all documents.

Another approach to implemented these kind of commands is by making them stateful.
Such a stateful command is then stored somewhere in the document object,
and is somehow called when there is input to process.
Let us call a stateful commands a 'mode' and assume it is stored in document.mode.
Assume that a mode needs to have a method 'processinput'
which is called with the userinput.

```python
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
```

This command is truly stateful as it can be interrupted anytime without being corrupted.

Anything that a user can do is captured by a command.
Doing a Selection, performing a text Operation, etcetera.

For some commands, we want to be able to undo them.
Let us define the class Undoable for that.

Note that, all commands can be made trivially undoable,
by storing the document before and after applying the command.
This is however not desirable for reasons of space.
Therefore we leave the specific implementation
of the undo method to the concrete subclasses.

```python
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
```

Consider again the previous example. We will now make it undoable
by storing the relevant information in the command object and inherit
from Undoable.

```python
class UndoableSetExtendMode(Undoable):

    def _call(self, document):
        self.previous_mode = document.selection_mode
        document.selection_mode = selecting.tail_mode

    def _undo(self, document):
        document.selection_mode = self.previous_mode

set_tail_mode = UndoableSetExtendMode()  # create command
set_tail_mode(mydocument)  # execute the command on a document
set_tail_mode.undo(mydocument)  # undo the command on a document
```

Can we also create commands that perform differently depending
on the context? Let us try to implement a 'select everything'.

```python
def select_everything(document):
    interval = (0, len(document.text))
    document.selection = Selection([interval])
```

Instead of the above, we may want to have it return a command,
such that we can split the creation of the selection (by __init__)
and the execution of the selection (by __call__).
This way we can create selections, and inspect them, without
having to actually apply them to the document.
If we wouldn't care about that, we might as well use the above.

Two alternatives. Looks like there are usecases for both of them,
so we might want to leave this choice open.
Generalizing this a bit further, we can have commands that return other commands, which we
call higher order commands.

```python
def SelectEverything(document, selection=None, selection_mode=None):

        Good: - short and clear
        Bad: - cannot derive from Interactive etc

    selection = selection or document.selection
    selection_mode = selection_mode or document.selection_mode
    interval = (0, len(document.text))
    return Selection([interval])

class SelectEverything2(Selection):

        Good: - in case of updateable commands, we may need to be stored as
            a whole, in order to be able to undo and redo ourselves only
        Bad: - needs more knowledge of Selection's inner working
             - compound actors that are only partly undoable are stored completely

    def __init__(self, document, selection=None, selection_mode=None):
        selection = selection or document.selection
        selection_mode = selection_mode or document.selection_mode
        interval = (0, len(document.text))
        Selection.__init__(self, [interval])

my_select_everything = SelectEverything2(mydocument)  # create selection
my_select_everything(mydocument)  # execute the selection on a document
my_select_everything.undo(mydocument)  # undo the selection on a document
```

Can we also create selections that are based on more input than
only the document, like for instance regex patterns?

```python
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
```

Now we can call any function that takes a document and returns an
command an 'actor'. So in the above, select_somepattern is an actor,
which resulted from partially applying SelectPattern.
Note that Selection and Operation are not actors.

To improve selection/interval arithmetic, we should override basic operators
for the classes Selection and Interval.
(a,b)+(c,d)=(min(a,b),max(c,d))
s+t=s.tail(t)
Note that interval selector behaviour follows from these definitions.

Can we also make commands which are incrementally constructed by the
user while getting feedback, like an insertion operation?

- Nested modes or not?

Snippet expansion should be trivial due to our modal command machinery.
There are several possibilities.
Do we want to make it a single command, or do we want to have an command for each placeholder?
In the first case we have to make it a CompoundCommand.
In the second case we can either store the commands in advance (annoying to implement)
or store a snippet object in the document which is updateable and subsequently stores
placeholder commands in the undotree.
This requires a seperate field for updateable commands.
Updateable commands are then no longer determined from the last command in the history,
but have a separate field.

Generally speaking, we want to interact with a general object/command.
In this case, a snippet object.
While interacting with the snippet object, we get multiple other interactions with ChangeInPlace operations.

So we need to think about how to implement interaction in the most general way.
We can introduce an interaction stack, such that we can nest interactions.
If we then finish an interaction, we are dropped into the previous interaction.



[docs]: http://chiel92.github.io/fate/
[fate-tui]: http://github.com/Chiel92/fate-tui

