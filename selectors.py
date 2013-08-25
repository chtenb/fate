"""A selector takes a selection and returns another derived selection"""
from .selection import Selection
from . import current


def selector(function):
    def wrapper(selection, text=None):
        if not text:
            text = current.session.text
        return function(selection, text)
    return wrapper


@selector
def single_character(selection, text):
    return Selection(intervals=[(selection[0][0], selection[0][0])])


@selector
def invert(selection, text):
    return selection.complement(text)


def interval_selector(function):
    """An interval selector takes an interval to another interval.
    This induces a selection, by applying the interval
    selector to all intervals contained in a selection"""
    @selector
    def wrapper(selection, text):
        result = Selection()
        for interval in selection:
            result.add(function(interval, text))
        return result
    return wrapper


@interval_selector
def move_to_next_line(interval, text):
    """Move all intervals one line forwards"""
    beg, end = interval
    eol = text.find('\n', beg)
    if eol == -1:
        return interval
    bol = text.rfind('\n', 0, beg)
    return (eol + beg - bol, eol + end - bol)


@interval_selector
def move_to_previous_line(interval, text):
    """Move all intervals one line backwards"""
    beg, end = interval
    bol = text.rfind('\n', 0, beg)
    if bol == -1:
        return interval
    bol2 = text.rfind('\n', 0, bol)
    return (bol2 + beg - bol, bol2 + end - bol)


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
def next_word(interval, text):
    beg, end = interval
    next_space = text.find(' ', end + 1)
    if next_space == -1:
        next_space = len(text)
    prev_space = text.rfind(' ', 0, next_space - 1)
    return (prev_space + 1, next_space)


@interval_selector
def previous_word(interval, text):
    beg, end = interval
    prev_space = text.rfind(' ', 0, max(beg - 1, 0))
    next_space = text.find(' ', prev_space + 1)
    if next_space == -1:
        next_space = len(text)
    return (prev_space + 1, next_space)
