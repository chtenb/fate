"""An operator takes a selection (and optional additional arguments) and returns an operation"""
from .operation import Operation, reverse


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


def insert_after(session, selection, string):
    old_content = session.content(selection)
    new_content = []
    for s in old_content:
        new_content.append(s + string)
    return Operation(session, selection, new_content)


def insert_before(session, selection, string):
    old_content = session.content(selection)
    new_content = []
    for s in old_content:
        new_content.append(string + s)
    return Operation(session, selection, new_content)


def insert_in_place(session, selection, string):
    old_content = session.content(selection)
    new_content = []
    for s in old_content:
        new_content.append(string)
    return Operation(session, selection, new_content)


def insert_around(session, selection, string):
    old_content = session.content(selection)
    new_content = []
    character_pairs = [('{', '}'), ('[', ']'), ('(', ')')]
    first_string = reverse(string)
    second_string = string
    for first, second in character_pairs:
        first_string = first_string.replace(second, first)
        second_string = second_string.replace(first, second)

    for s in old_content:
        new_content.append(first_string + s + second_string)
    return Operation(session, selection, new_content)
