"""
This is a singleton which should contain all actions that are available to the user.
A completion engine can use this to compute completions.

The goal of a text editor is to make modifications to a text.
More generally, the user should also be able to modify things other
than text, such as options or other meta stuff.
We store all relevant data for editing a text in a single object,
and call this object a session.

To make modifications to a session, we define actions.
An action is an abstract object that can make a modification to a session.
An action must therefore be callable and accept a session as argument.

In many cases it is useful to create actions on the fly.
Callable objects that create and return actions are called 'action constructors'.

A special type of action constructors are those that require a session as argument.
Let us call these 'actors'.
"""

# TODO: decide upon naming convention for actions
# Action constructors: CamelCase
# Actions: camelcase or camel_case


def undo(session):
    """Undo last action."""
    session.undotree.undo()


def redo(session):
    """Redo last undo."""
    session.undotree.redo()

