"""An operator takes a selection (and optional additional arguments) and returns an operation"""
from .operation import Operation


def operator(function):
    def wrapper(selection, session):
        old_content = session.content(selection)
        return function(selection, old_content, session)
    return wrapper


@operator
def delete(selection, old_content, session):
    new_content = []
    for s in old_content:
        new_content.append('')
    return Operation(session, selection, new_content)


def change_after(session, selection, insertions, deletions):
    """Changes text after each interval in the selection.

    :insertions: string; text to be inserted
    :deletions: int >= 0; number of chars to be deleted
    """
    old_content = session.content(selection)
    new_content = []
    for s in old_content:
        new_string = s[:-deletions or None] + insertions
        new_content.append(new_string)
    return Operation(session, selection, new_content)


def change_before(session, selection, insertions, deletions):
    """Changes text before each interval in the selection.

    :insertions: string; text to be inserted
    :deletions: int >= 0; number of chars to be deleted
    """
    old_content = session.content(selection)
    new_content = []
    for s in old_content:
        new_string = insertions + s[deletions:]
        new_content.append(new_string)
    return Operation(session, selection, new_content)


def change_in_place(session, selection, insertions, deletions):
    """Changes text in place of each interval in the selection.

    :insertions: string; text to be inserted
    :deletions: is not used
    """
    old_content = session.content(selection)
    new_content = []
    for s in old_content:
        new_content.append(insertions)
    return Operation(session, selection, new_content)


def change_around(session, selection, insertions, deletions):
    """Changes text before each interval in the selection.

    :insertions: string; text to be inserted
    :deletions: int >= 0; number of chars to be deleted
    """
    old_content = session.content(selection)
    new_content = []
    character_pairs = [('{', '}'), ('[', ']'), ('(', ')')]
    first_string = insertions[::-1]
    second_string = insertions
    for first, second in character_pairs:
        first_string = first_string.replace(second, first)
        second_string = second_string.replace(first, second)

    for s in old_content:
        new_content.append(first_string + s[deletions:-deletions or None] + second_string)
    return Operation(session, selection, new_content)
