"""An operator takes a selection (and optional additional arguments) and returns an operation"""
from .operation import Operation
from .selection import Selection
import logging

def to_operation(obj):
    if obj.__class__ == Selection:
        return Operation(obj)
    elif obj.__class__ == Operation:
        return obj
    else:
        raise Exception('Only Selections and Operations can be applied')

def operator(function):
    """A decorator for things that need to be done in every atomic operator"""
    def wrapper(obj, *args):
        operation = to_operation(obj)
        operation.new_content = function(operation.new_content, *args)
        return operation
    return wrapper


def interval_operator(function):
    def wrapper(obj, *args):
        operation = to_operation(obj)
        for i in range(len(operation.new_content)):
            operation.new_content[i] = function(operation.new_content[i], *args)
        return operation
    return wrapper


@operator
def delete(content):
    return ['' for s in content]


@interval_operator
def change_after(content, insertions, deletions):
    return content[:-deletions or None] + insertions


@interval_operator
def change_before(content, insertions, deletions):
    return insertions + content[deletions:]


@interval_operator
def change_in_place(content, insertions, deletions):
    return insertions


@interval_operator
def change_around(content, insertions, deletions):
    character_pairs = [('{', '}'), ('[', ']'), ('(', ')')]
    first_string = insertions[::-1]
    second_string = insertions
    for first, second in character_pairs:
        first_string = first_string.replace(second, first)
        second_string = second_string.replace(first, second)
    return first_string + content[deletions:-deletions or None] + second_string
