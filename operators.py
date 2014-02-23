"""
An operator is a special type of action, that applies an operation to a
session. Strictly speaking, an operator is a function that is decorated
by operator, either directly or indirectly.
"""
from .operation import Operation, InsertOperation
from .selection import Selection
from .selectors import select_indent, previous_full_line
import logging


def operator(function):
    """
    A decorator that turns a function taking a list of strings to an
    operator. The resulting operator will have the following arguments.
    """
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


# We should probably change the following functions to accept the string of inserted characters (including backspaces)
# That way we can make sure that indentation is right, even if the function is repeated in a different context

# def insertoperator(function):
    # def wrapper(operation):
        # session = operation.session
        # text = session.text
        # new_content = []
        # for interval in operation.new_selection:
            # interval_selection = Selection(session, intervals=[interval])
            # content = interval_selection.content[0]
            # content = function(content, interval_selection, text)
            # new_content.append(content)
        # session.actiontree.hard_undo()
        # operation.new_content = new_content
        # operation.do()
    # return wrapper


# def change_after(inputstring):
    #"""Operator constructor which deletes `deletions`
    # and adds `insertions` at the tail of each interval content."""
    #@insertoperator
    # def wrapper(content, interval_selection, text):
        # for char in inputstring:
            # if char == '\b':
                ## remove char
                # content = content[:-1]
            # elif char == '\n':
                ## get indent
                # indent = select_indent(interval_selection, text)
                # indent = indent.content[0]
                ## add indent after \n
                # content += char + indent
            # else:
                ## add char
                # content += char
        # return content
    # return wrapper

# def change_before(inputstring):
    #"""Operator constructor which deletes `deletions`
    # and adds `insertions` at the tail of each interval content."""
    #@insertoperator
    # def wrapper(content, interval_selection, text):
        # for char in inputstring:
            # if char == '\b':
                ## remove char
                # content = content[1:]
            # elif char == '\n':
                ## get indent
                # indent = select_indent(interval_selection, text)
                # logging.debug(str(indent))
                # indent = indent.content[0]
                # logging.debug(str(indent) + '$')
                ## add indent after \n
                # content = char + indent + content
            # else:
                ## add char
                # content = char + content
        # return content
    # return wrapper


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
