NOTE: Still very experimental and not ready for use.

FATE
====
Barely Awesome Text Editor

VIM
---
How is fate related to vim?
I'm a vim user myself.
Vim is a great text editor.
However, there are several issues that need to be adressed.
De code base is old and getting messy.
It is therefore hard to maintain.
It is not very extendible, even though vim has its own scripting language.
Vim language is neither an easy, readable nor a fast scripting language.
The architecture needs to be revised, for instance, it should not be restricted to a single thread.

Neovim tries to fix some of these problems, which is a good thing in my opinion, but it is not drastically enough.
Given these things, the best option is to write a new text editor from scratch.
We would like to have a powerful, yet small, extendible and pluggable code base.
The language of choice is Python, because

- it is easy, which is not only a good thing in itself, but also makes doing contributions easier
- allows to write relatively short and elegant code
- naturally the scripting language will be python as well, such that we get the scripting machinery almost for free

Vim has several user interface, due to the many platforms and user preferences.
To anticipate on this, we will separate the user interface from the underlying machinery.

While writing a text editor from scratch anyway, we have the opportunity to rethink the way vim works.
There is room for improvement.

Vim's visual mode removed the need for marks (kind of).
Why don't we take this one step further?
Let's make all motions visual, such that we can select a word by pressing `w`, and then change it by pressing `c`.
In vim we would have to press `cw`, not getting feedback on what we selected.
From an architectural point of view, the new approach is also appealing, as it removes the need for a distinction between visual mode and normal mode.


Documentation
-------------
Available [here][docs].

User Interface
--------------
Available [here][fate-tui]


[docs]: http://chiel92.github.io/fate/
[fate-tui]: http://github.com/Chiel92/fate-tui

