"""
This is a singleton which should contain all commands that are available to the user.
A completion engine can use this to compute completions.

The goal of a text editor is to make modifications to a text.
More generally, the user should also be able to modify things other
than text, such as options or other meta stuff.
We store all relevant data for editing a text in a single object,
and call this object a document.

To make modifications to a document, we define commands.
An command is an abstract object that can make a modification to a document.
An command must therefore be callable and accept a document as argument.

In many cases it is useful to create commands on the fly.
Callable objects that create and return commands are called 'command constructors'.

A special type of command constructors are those that require a document as argument.
Let us call these 'actors'.
"""

# TODO: decide upon naming convention for commands
# Action constructors: CamelCase
# Actions: camelcase or camel_case

