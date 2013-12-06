"""An operator is a function that is decorated by `selector`, either directly or indirectly. An operator is a special type of action, that
is used to modify the text of the session."""
from .operation import Operation


def operator(function):
    """A decorator for things that need to be done in every atomic operator"""
    def wrapper(session, preview=False):
        operation = Operation(session.selection)
        operation.new_content = function(operation.new_content)

        if preview:
            return operation
        else:
            operation.apply()

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
    """Operator constructor which deletes `deletions` and adds `insertions` at the tail of each interval content."""
    @local_operator
    def wrapper(content):
        return content[:-deletions or None] + insertions
    return wrapper


def change_before(insertions, deletions):
    """Operator constructor which deletes `deletions` and adds `insertions` at the head of each interval content."""
    @local_operator
    def wrapper(content):
        return insertions + content[deletions:]
    return wrapper


def change_in_place(insertions, deletions):
    """Operator constructor which puts `insertions` in place of each interval content. The deletions argument is not used."""
    @local_operator
    def wrapper(content):
        return insertions
    return wrapper


def change_around(insertions, deletions):
    """Operator constructor which deletes `deletions` and adds `insertions` both at the tail and at the head of each interval content."""
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
