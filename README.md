NOTE: Still very experimental and not ready for use.

FATE
====
Fate is a highly programmable text editor, mainly intended for programming purposes.

VIM
---
How is fate related to vim?
I'm a vim user myself.
Vim is a great text editor.
However, there are several issues that need to be adressed.
De code base is old and getting messy.
It is therefore hard to maintain.
It is not very extendible, even though vim has its own scripting language.
Vim language is neither easy, readable nor fast.
The architecture needs to be revised, for instance, it should not be restricted to a single thread.
Another bad thing is that vim tries to be backward compatible with vim.
This results in all kinds of quirks that only exist for historical reasons.
We don't want that. Once in a while, backwardscompatibility needs to be broken due to new developments or new insights.
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

Secondly, we like to generalize vim's modal approach.
We want the user to be able to add new modes easily.
This way things like snippet expansion can be implemented with a snippet mode.

Thirdly, we will not invent our own regex language, like vim did, but stick to python's regex language.
It is a good one, everybody knows it, and we get it for free.

Documentation
-------------
Available [here][docs].

User Interface
--------------
Available [here][fate-tui]


[docs]: http://chiel92.github.io/fate/
[fate-tui]: http://github.com/Chiel92/fate-tui

