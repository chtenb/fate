This project is in an experimental state. No individuals affiliated with this project can be
held responsible for any kind of damage caused by usage of this software.

[![Build Status](https://travis-ci.org/Chiel92/fate.svg?branch=action-machinery-rewrite)](https://travis-ci.org/Chiel92/fate)

Fate
====
F.A.T.E. is a highly programmable text editor, mainly intended for programming purposes.

How to install
--------------
Available [here][fate-tui]

What you should know
--------------------
What originally started out as a rewrite of Vim in python, ended up as an entirely new text
editor.
Vim is a great text editor.
However, there are several issues I felt that needed to be adressed.
De code base is old and getting messy and is therefore hard to maintain.
It is not very extensible, even though vim has its own scripting language.
VimLanguage is neither easy, readable nor fast.
The architecture needs to be revised, for instance, it should not be restricted to a
single thread.
Another bad thing is that vim tries to be backward compatible too much (even with vi!).
This results in all kinds of quirks that only exist for historical reasons.
We don't want that. Once in a while, backward compatibility needs to be broken due to new
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
- performance critical parts can easily be implemented as a C or C++ extension

Vim has several user interfaces, due to the many platforms and user preferences.  To
anticipate on this, we will separate the user interface from the underlying machinery.

While writing a text editor from scratch anyway, we have the opportunity to rethink the
way vim works.
There is room for improvement.

Vim's visual mode removed the need for marks (kind of).
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
- Make sure the view updates fast enough to be in sync with userinterface.viewportoffset and
  viewportsize.
- Implement repeat
  - Record input of user
  - next_document should also be recorded: this just makes repeat more powerful
  - Be able to save these macros, and be able to construct macros via literal input.
    This makes it easy to record a macro and use it for bulk editing
- Allow fate to be used for bulk file editing according to some given script
  - Things like completion need to be disabled for this to speed up starting fate

MIDDLE TERM
- Different forms of wrapping left/right + word/character?
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
- Incorporate testing with multiple documents
- Unittests for pattern select machinery
- Think about how to decorate classes easily, without disabling subclassing
  - Can't decorate classes by functions: this turns them into functions
  - This means that they can't be used as parentclass
  - and that they can't be checked by issubclass
- Think about possibility to add remap support (i.e. map keys forall modes)
  - This is a generalization of the cancelkey feature
- Drag text operation
- Persistent document (using a context manager?)
- Switch to alternative regex engine?
- Focus on non-atomic operations
- Idea: jumplist of lines of changes
- Some sort of semantic snippet recognition, e.g. two identifiers that always need to be the same.
  If one changes, the other changes with it.
- Binary search for selections?

[docs]: http://chiel92.github.io/fate/
[fate-tui]: http://github.com/Chiel92/fate-tui

