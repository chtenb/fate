"""
An operator is a special type of action, that applies an operation to a
session. Strictly speaking, an operator is a function that is decorated
by operator, either directly or indirectly.
"""
from . import actions
from .operation import Operation


def uppercase(session, selection=None):
    """Delete content."""
    selection = selection or session.selection
    new_content = [s.upper() for s in selection.content(session)]
    operation = Operation(session, new_content, selection)
    operation(session)
actions.uppercase = uppercase


def lowercase(session, selection=None):
    """Lowercase content."""
    selection = selection or session.selection
    new_content = [s.lower() for s in selection.content(session)]
    operation = Operation(session, new_content, selection)
    operation(session)
actions.lowercase = lowercase


def delete(session, selection=None):
    """Delete content."""
    selection = selection or session.selection
    new_content = ['' for _ in selection]
    operation = Operation(session, new_content, selection)
    operation(session)
actions.delete = delete


# The classes Append and Insert are action constructors


class Append:

    """Append to content."""

    def __init__(self, string):
        self.string = string

    def __call__(self, session, selection=None):
        selection = selection or session.selection
        new_content = [content + self.string for content in selection.content(session)]
        operation = Operation(session, new_content, selection)
        operation(session)


class Insert:

    """Insert before content."""

    def __init__(self, string):
        self.string = string

    def __call__(self, session, selection=None):
        selection = selection or session.selection
        new_content = [self.string + content for content in selection.content(session)]
        operation = Operation(session, new_content, selection)
        operation(session)


class Change:

    """Insert in place of content."""

    def __init__(self, string):
        self.string = string

    def __call__(self, session, selection=None):
        selection = selection or session.selection
        new_content = [self.string for content in selection.content(session)]
        operation = Operation(session, new_content, selection)
        operation(session)

