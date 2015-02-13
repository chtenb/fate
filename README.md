NOTE: Still very experimental and not ready for use.

[![Build Status](https://travis-ci.org/Chiel92/fate.svg?branch=action-machinery-rewrite)](https://travis-ci.org/Chiel92/fate)

Fate
====
Fate is a highly programmable text editor, mainly intended for programming purposes.

Documentation
-------------
Available [here][docs].

User Interface
--------------
Available [here][fate-tui]

Vim
---
How is fate related to vim?
I'm a vim user myself.
Vim is a great text editor.
However, there are several issues that need to be adressed.
De code base is old and getting messy and is therefore hard to maintain.
It is not very extensible, even though vim has its own scripting language.
Vim language is neither easy, readable nor fast.
The architecture needs to be revised, for instance, it should not be restricted to a single thread.
Another bad thing is that vim tries to be backward compatible too much (even with vi!).
This results in all kinds of quirks that only exist for historical reasons.
We don't want that. Once in a while, backward compatibility needs to be broken due to new developments or new insights.
Python's transition to version 3 is a good example of this.
Neovim tries to fix some of these problems, which is a good thing in my opinion, but it is not drastically enough.
So we are not trying to be compatible with vim, let alone vi.

Given these things, the best option is to write a new text editor from scratch.
We would like to have a powerful, yet small, extendible and pluggable code base.
The language of choice is Python, because

- it is easy, which is not only a good thing in itself, but also makes doing contributions easier
- allows to write relatively short and elegant code
- naturally the scripting language will be python as well, such that we get the scripting machinery almost for free
- because there are several python implementations, this even potentially allows fate to be run in-browser

Vim has several user interfaces, due to the many platforms and user preferences.
To anticipate on this, we will separate the user interface from the underlying machinery.

While writing a text editor from scratch anyway, we have the opportunity to rethink the way vim works.
There is room for improvement.

Vim's visual mode removed the need for marks (kind of).
Why don't we take this one step further?
Let's make all motions visual, such that we can select a word by pressing `w`, and then change it by pressing `c`.
In vim we would have to press `cw`, not getting feedback on what we selected.
From an architectural point of view, the new approach is also appealing, as it removes the need for a distinction between visual mode and normal mode.
The syntax diagram will be easier, there is no need for a change mode, which accepts motions,
but instead we can just select something and apply an operator.
Note that we remove the concept of a cursor.
We always work with entire selections instead.

Secondly, we like to generalize vim's modal approach.
We want the user to be able to add new modes easily.
This way things like snippet expansion can be implemented with a snippet mode.

Thirdly, we will not invent our own regex language like vim did, but stick to python's regex language.
It is a good, well documented, well known engine, and we get it for free.

Design
======
Here we state some important design decisions that were made.

Performance
-----------
To be able to efficiently do operations on the text while keeping the possibility to execute regex queries, we need a C data structure that acts as a string (implementing python's buffer protocol) but which is a different tree structure underneath.
TODO: is the text lazily loaded from the harddisk?

There are two categories of syntactic constructs that we want to match in a text:
- those that require the entire text to be parsed (e.g. constructs with ambiguous delimiters such as strings)
- those that don't (e.g. keywords, matching parenthesis)

The first category need the entire text, and can thus only be performed if the textsize is small enough or if its not used frequently or automatically (syntax highlighting) and the user is willing to wait that long.
The second category can be parsed by only looking in a window.

Syntaxhighlighting should be disabled for the first category, while global search should not.


Todo
----
SHORT TERM
- Change extend/reduce selections to change back/forth.
    don't pass selectmode to selectors, but treat everything the same
- Selectaround
- Gui integration communication (windowsize)
- Different forms of wrapping left/right + word/character
- Ready for use
- Errorchecking
- Fix unnecessary pylint complains
- Reimplement repeat, since classes can't be decorated
    Problem: how to handle next_document etc? We don't want those to be recorded.
- Implement commandmode as a persistent command, similar to undomode
- Select around/inside (not finished yet)
- Improve syntax highlighting, for instance by disregarding quotes inside comments and strings
    select around should maybe also disregard brackets etc in comments and strings
- Enhance selector set
- Think about how to decorate classes easily, without disabling subclassing
    Can't decorate classes by functions: this turns them into functions
    this means that they can't be used as parentclass
    and that they can't be checked by issubclass
- Think about possibility to add remap support (i.e. map keys forall modes)
    This is a generalization of the cancelkey feature
- Incorporate testing with multiple sessions
- Unittests for pattern select machinery

LONG TERM
- Drag text operation
- Make labeling generation asynchronous
- Persistent session (using a context manager?)
- Contextual completion
    For completion it is also needed that the full text can be constructed including the pending operation. (No it isn't!! Only filtering is done based on the input, the context is not changed)
- Switch to alternative regex engine?
- Focus on non-atomic operations
- Idea: jumplist of lines of changes
- Conceal
- Easier file opening
- Some sort of semantic snippet recognition, e.g. two identifiers that always need to be the same. If one changes, the other changes with it.

RESEARCH
- Optimal configurable datastructure for text editing
    optimize it for linenumber queries as well, not only for char numbers
- Optimal configurable datastructure for labeling/syntax highlighting
- Store additional metadata such as the number of line breaks in a certain range
- Executing regex over the whole text should be fast, so is this case we want lookup to be constant time (amortized)

[docs]: http://chiel92.github.io/fate/
[fate-tui]: http://github.com/Chiel92/fate-tui

