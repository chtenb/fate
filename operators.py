"""
An operator is a special type of action, that applies an operation to a
session. Strictly speaking, an operator is a function that is decorated
by operator, either directly or indirectly.
"""
from . import actions
from .operation import Operation, InsertOperation


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


class Append:

    """Append to content."""

    def __init__(self, string):
        self.string = string

    def __call__(self, session, selection=None):
        selection = selection or session.selection
        new_content = [content + self.string for content in selection.content(session)]
        operation = Operation(session, new_content, selection)
        operation(session)
actions.Append = Append


class Insert:

    """Insert before content."""

    def __init__(self, string):
        self.string = string

    def __call__(self, session, selection=None):
        selection = selection or session.selection
        new_content = [self.string + content for content in selection.content(session)]
        operation = Operation(session, new_content, selection)
        operation(session)
actions.Insert = Insert


class ChangeInPlace(InsertOperation):

    """
    Interactive Operation which adds `insertions` in place of each interval.
    """

    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        return [self.insertions[i] for i in range(len(self.old_content))]
actions.ChangeInPlace = ChangeInPlace


class ChangeBefore(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        return [self.insertions[i]
                + self.old_content[i][self.deletions[i]:]
                for i in range(len(self.old_content))]
actions.ChangeBefore = ChangeBefore


class ChangeAfter(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        return [self.old_content[i][:-self.deletions[i] or None]
                + self.insertions[i]
                for i in range(len(self.old_content))]
actions.ChangeAfter = ChangeAfter


class ChangeAround(InsertOperation):

    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """

    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        character_pairs = [('{', '}'), ('[', ']'), ('(', ')'), ('<', '>')]
        result = []
        for i in range(len(self.old_content)):
            first_string = self.insertions[i][::-1]
            second_string = self.insertions[i]
            for first, second in character_pairs:
                first_string = first_string.replace(second, first)
                second_string = second_string.replace(first, second)
            beg, end = self.deletions[i], -self.deletions[i] or None
            result.append(first_string
                          + self.old_content[i][beg:end]
                          + second_string)
        return result
actions.ChangeAround = ChangeAround
