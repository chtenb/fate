"""A selector takes a selection and returns a second, derived selection. We distinguish between functions that work selection-wise
(selectors) and function that work interval-wise (interval selectors)."""
from .selection import Selection
from .operation import Operation
from .session import select_mode, extend_mode, reduce_mode
import re
import logging

# TODO rename decorators to global and local selector, and make selector
# a decorator used by both


def to_selection(obj):
    if obj.__class__ == Operation:
        obj.session.apply(obj)
        return obj.new_selection
    elif obj.__class__ == Selection:
        return obj
    else:
        raise Exception('Only Selections and Operations can be applied')


def selector(function):
    """Defaults to (0,0) when text or selection passed is empty.
    Returns original selection when result is empty or invalid."""
    def wrapper(obj):
        selection = to_selection(obj)
        session = selection.session
        text = session.text

        if session.selection_mode == reduce_mode:
            result = function(selection.complement(), text)
            if result:  # result can be None
                result = selection.reduce(result)
        elif session.selection_mode == extend_mode:
            result = function(selection, text)
            if result:  # result can be None
                result = selection.extend(result)
        else:
            result = function(selection, text)

        if not result:
            # If the result is empty, we return the old selection
            return selection

        # If the result isnt valid, we return the original selection
        for beg, end in result:
            if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                return selection

        return result
    return wrapper


@selector
def single_character(selection, text):
    return Selection(selection.session, intervals=[(selection[0][0], selection[0][0] + 1)])


@selector
def empty(selection, text):
    x = selection[0][0]
    return Selection(selection.session, intervals=[(x, x)])


@selector
def complement(selection, text):
    return selection.complement()


@selector
def join(selection, text):
    return Selection(selection.session, intervals=[(selection[0][0], selection[-1][1])])


def interval_selector(function):
    """An interval selector takes an interval to another interval.
    This induces a selector, by applying the interval
    selector to all intervals contained in a selection
    Keeps original interval when result is empty or invalid."""
    def wrapper(obj):
        selection = to_selection(obj)
        session = selection.session
        text = session.text

        if session.selection_mode == reduce_mode:
            iterselection = selection.complement()
        else:
            iterselection = selection

        result = []
        for interval in iterselection:
            interval_result = function(interval, text)

            # If the result isnt valid, we take the original interval
            if not interval_result:
                interval_result = interval
            else:
                beg, end = interval_result
                if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                    interval_result = interval

            if session.selection_mode == reduce_mode or session.selection_mode == extend_mode:
                interval_result = min(interval[0], interval_result[0]), max(interval[1], interval_result[1])
            result.append(interval_result)

        result = Selection(session, result)
        if session.selection_mode == reduce_mode:
            result = selection.reduce(result)
            if result:
                return result
            return selection
        return result
    return wrapper


@interval_selector
def next_line(interval, text):
    """Return line beneath interval"""
    beg, end = interval
    eol = text.find('\n', end + 1)
    if eol == -1:
        eol = len(text) - 1
    bol = text.rfind('\n', 0, eol) + 1
    return (bol, eol)


@interval_selector
def previous_line(interval, text):
    """Return line above interval"""
    beg, end = interval
    bol = text.rfind('\n', 0, max(0, beg - 1)) + 1
    eol = text.find('\n', bol)
    if eol == -1:
        eol = len(text) - 1
    return (bol, eol)


@interval_selector
def next_full_line(interval, text):
    """Return line beneath interval including newline char"""
    beg, end = interval
    eol = text.find('\n', end)
    if eol == -1:
        eol = len(text) - 1
    bol = text.rfind('\n', 0, eol) + 1
    return (bol, eol + 1)


@interval_selector
def previous_full_line(interval, text):
    """Return line above interval including newline char"""
    beg, end = interval
    bol = text.rfind('\n', 0, max(0, beg - 1)) + 1
    eol = text.find('\n', bol)
    if eol == -1:
        eol = len(text) - 1
    return (bol, eol + 1)


@interval_selector
def previous_char(interval, text):
    """Return previous char"""
    beg, end = interval
    nbeg = max(0, beg - 1)
    return (nbeg, nbeg + 1)


@interval_selector
def next_char(interval, text):
    """Return next char"""
    beg, end = interval
    nend = min(len(text), end + 1)
    return (nend - 1, nend)


@interval_selector
def move_to_previous_line(interval, text):
    """Move all intervals one line backwards"""
    beg, end = interval
    bol = text.rfind('\n', 0, beg)
    if bol == -1:
        return interval
    bol2 = text.rfind('\n', 0, bol)
    return (min(bol, bol2 + beg - bol), min(bol, bol2 + end - bol))


@interval_selector
def move_to_next_line(interval, text):
    """Move all intervals one line forwards"""
    beg, end = interval
    eol = text.find('\n', beg)
    if eol == -1:
        return interval
    bol = text.rfind('\n', 0, beg)
    return (max(eol, eol + beg - bol), max(eol, eol + end - bol))


# reverse and all should be a single flag
# a selection should be passed, indicating the bounds of the search space
def find_pattern(pattern, position, text, reverse=False, all=False):
    regex = re.compile(pattern)

    matches = regex.finditer(text)

    if matches:
        if all:
            return [(match.start(), match.end()) for match in matches]
        elif reverse:
            matches = reversed(list(matches))
            for match in matches:
                if match.start() < position:
                    return match.start(), match.end()
        else:
            for match in matches:
                if position < match.end():
                    return match.start(), match.end()


def pattern_selector(pattern, reverse=False):
    """Factory method for creating selectors based on a regular expression"""
    @selector
    def wrapper(selection, text):
        if reverse:
            position = selection[0][0]
        else:
            position = selection[-1][1]

        result = find_pattern(pattern, position, text, reverse=reverse, all=selection.session.forall)
        if not all and result:
            result = [result]
        if result:
            return Selection(selection.session, intervals=result)
    return wrapper


def pattern_interval_selector(pattern, reverse=False):
    """Factory method for creating interval selectors based on a regular expression"""
    @interval_selector
    def wrapper(interval, text):
        if reverse:
            position = interval[0]
        else:
            position = interval[1]
        return find_pattern(pattern, position, text, reverse=reverse)
    return wrapper


# Predefined pattern selectors
next_word = pattern_interval_selector(r'\b\w+\b')
previous_word = pattern_interval_selector(r'\b\w+\b', reverse=True)
next_paragraph = pattern_interval_selector(r'(?s)((?:[^\n][\n]?)+)')
previous_paragraph = pattern_interval_selector(r'(?s)((?:[^\n][\n]?)+)', reverse=True)
