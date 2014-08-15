"""
An operator is a special type of command, that applies an operation to a
document. Strictly speaking, an operator is a function that is decorated
by operator, either directly or indirectly.
"""
from . import commands
from .operation import Operation


def uppercase(document, selection=None):
    """Delete content."""
    selection = selection or document.selection
    new_content = [s.upper() for s in selection.content(document)]
    operation = Operation(document, new_content, selection)
    operation(document)
commands.uppercase = uppercase


def lowercase(document, selection=None):
    """Lowercase content."""
    selection = selection or document.selection
    new_content = [s.lower() for s in selection.content(document)]
    operation = Operation(document, new_content, selection)
    operation(document)
commands.lowercase = lowercase


def delete(document, selection=None):
    """Delete content."""
    selection = selection or document.selection
    new_content = ['' for _ in selection]
    operation = Operation(document, new_content, selection)
    operation(document)
commands.delete = delete


# The classes Append and Insert are command constructors


class Append:

    """Append to content."""

    def __init__(self, string):
        self.string = string

    def __call__(self, document, selection=None):
        selection = selection or document.selection
        new_content = [content + self.string for content in selection.content(document)]
        operation = Operation(document, new_content, selection)
        operation(document)


class Insert:

    """Insert before content."""

    def __init__(self, string):
        self.string = string

    def __call__(self, document, selection=None):
        selection = selection or document.selection
        new_content = [self.string + content for content in selection.content(document)]
        operation = Operation(document, new_content, selection)
        operation(document)


class Change:

    """Insert in place of content."""

    def __init__(self, string):
        self.string = string

    def __call__(self, document, selection=None):
        selection = selection or document.selection
        new_content = [self.string for content in selection.content(document)]
        operation = Operation(document, new_content, selection)
        operation(document)

