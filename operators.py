"""
An operator is a special type of action, that applies an operation to a
session. Strictly speaking, an operator is a function that is decorated
by operator, either directly or indirectly.
"""
from .operation import Operation, InsertOperation


class Delete(Operation):
    """Delete content."""
    def __init__(self, session, selection=None):
        selection = selection or session.selection
        new_content = ['' for _ in selection]
        Operation.__init__(self, selection, new_content)


class Append(Operation):
    """Append to content."""
    def __init__(self, string, session, selection=None):
        selection = selection or session.selection
        new_content = [content + string for content in selection.content]
        Operation.__init__(self, selection, new_content)


class Insert(Operation):
    """Insert before content."""
    def __init__(self, string, session, selection=None):
        selection = selection or session.selection
        new_content = [string + content for content in selection.content]
        Operation.__init__(self, selection, new_content)


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


class ChangeInPlace(InsertOperation):
    """
    Interactive Operation which adds `insertions` in place of each interval.
    """
    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        return [self.insertions[i] for i in range(len(self.old_content))]


class ChangeAround(InsertOperation):
    """
    Interactive Operation which deletes `deletions`
    and adds `insertions` at the head of each interval.
    """
    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        character_pairs = [('{', '}'), ('[', ']'), ('(', ')')]
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
