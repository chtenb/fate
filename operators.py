"""An operator is a special type of action, that applies an operation to a
session. Strictly speaking, an operator is a function that is decorated
by operator, either directly or indirectly.
"""
from .operation import Operation
from .action import actor


def operator(function):
    """A decorator that turns a function taking a list of strings to an
    operator. The resulting operator will have the following arguments.

    :param session: The session on which the operator will act.
    """
    @actor
    def wrapper(session):
        operation = Operation(session.selection)
        operation.new_content = function(operation.new_content)
        return operation
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
def change_after(insertions, deletions):
    """Operator constructor which deletes `deletions`
    and adds `insertions` at the tail of each interval content."""
    @local_operator
    def wrapper(content):
        return content[:-deletions or None] + insertions
    return wrapper


def change_before(insertions, deletions):
    """Operator constructor which deletes `deletions`
    and adds `insertions` at the head of each interval content."""
    @local_operator
    def wrapper(content):
        return insertions + content[deletions:]
    return wrapper


def change_in_place(insertions, deletions):
    """Operator constructor which puts `insertions` in place of each
    interval content. The deletions argument is not used."""
    @local_operator
    def wrapper(content):
        return insertions
    return wrapper


def change_around(insertions, deletions):
    """Operator constructor which deletes `deletions` and adds
    `insertions` both at the tail and at the head of each interval
    content."""
    @local_operator
    def wrapper(content):
        character_pairs = [('{', '}'), ('[', ']'), ('(', ')')]
        first_string = insertions[::-1]
        second_string = insertions
        for first, second in character_pairs:
            first_string = first_string.replace(second, first)
            second_string = second_string.replace(first, second)
        return first_string + content[deletions:-deletions or None] + second_string
    return wrapper
