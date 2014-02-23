"""
An operator is a special type of action, that applies an operation to a
session. Strictly speaking, an operator is a function that is decorated
by operator, either directly or indirectly.
"""
from .operation import Operation, InsertOperation
from .selection import Selection
from .selectors import select_indent, previous_full_line
from .action import actor
import logging


def operator(function):
    """
    A decorator that turns a function taking a list of strings to an
    operator.
    """
    @actor
    def wrapper(session):
        new_content = function(session.selection.content)
        return Operation(session.selection, new_content)
    return wrapper


def local_operator(function):
    """A local operator operates interval wise."""
    @operator
    def wrapper(old_content):
        new_content = []
        for string in old_content:
            new_content.append(function(string))
        return new_content
    return wrapper


@local_operator
def delete(content):
    """Delete content."""
    return ''

# The following functions are operator constructors


def append(string):
    """Append to content."""
    @local_operator
    def wrapper(content):
        return content + string
    return wrapper


def insert(string):
    """Insert before content."""
    @local_operator
    def wrapper(content):
        return string + content
    return wrapper


# The following operators need to maintain state while being
# constructed, and therefore are classes

# TODO: Why is not every operator just a subclass of Operation?
class ChangeBefore(InsertOperation):
    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        return [self.insertions[i]
                + self.old_content[i][self.deletions[i]:]
                for i in range(len(self.old_content))]


def change_before(session):
    """Operator constructor which deletes `deletions`
    and adds `insertions` at the head of each interval."""
    session.insertoperation = ChangeBefore(session)


class ChangeAfter(InsertOperation):
    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        return [self.old_content[i][self.deletions[i]:]
                + self.insertions[i]
                for i in range(len(self.old_content))]


def change_after(session):
    """Operator constructor which deletes `deletions`
    and adds `insertions` at the head of each interval."""
    logging.debug(session.selection)
    session.insertoperation = ChangeAfter(session)


class ChangeInPlace(InsertOperation):
    def __init__(self, session):
        InsertOperation.__init__(self, session)

    @property
    def new_content(self):
        return [self.insertions[i] for i in range(len(self.old_content))]


def change_in_place(session):
    """Operator constructor which deletes `deletions`
    and adds `insertions` at the head of each interval."""
    session.insertoperation = ChangeInPlace(session)


class ChangeAround(InsertOperation):
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
            result.append(first_string
                          + self.old_content[i][self.deletions[i]:-self.deletions[i] or None]
                          + second_string)
        return result


def change_around(session):
    """Operator constructor which deletes `deletions`
    and adds `insertions` at the head of each interval."""
    session.insertoperation = ChangeAround(session)
