"""A selector takes a selection and returns another derived selection"""
from .selection import Selection
from . import current
import re


def selector(function):
    """Makes the text parameter optional by defaulting to current.session.text"""
    def wrapper(selection, text=None):
        if not text:
            text = current.session.text
        return function(selection, text)
    return wrapper


@selector
def single_character(selection, text):
    return Selection(intervals=[(selection[0][0], selection[0][0])])


@selector
def complement(selection, text):
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
def next_line(interval, text):
    """Return line beneath interval"""
    beg, end = interval
    eol = text.find('\n', end + 1)
    if eol == -1:
        eol = len(text) - 1
    bol = text.rfind('\n', 0, eol) + 1
    return (bol, eol + 1)


@interval_selector
def previous_line(interval, text):
    """Return line above interval"""
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
def next_word(interval, text):
    """Return next word"""
    beg, end = interval
    next_space = text.find(' ', end + 1)
    if next_space == -1:
        next_space = len(text)
    prev_space = text.rfind(' ', 0, next_space - 1)
    return (prev_space + 1, next_space)


@interval_selector
def previous_word(interval, text):
    """Returns previous word"""
    beg, end = interval
    prev_space = text.rfind(' ', 0, max(beg - 1, 0))
    next_space = text.find(' ', prev_space + 1)
    if next_space == -1:
        next_space = len(text)
    return (prev_space + 1, next_space)


@interval_selector
def next_group(interval, text):
    """Return next group"""
    # regex = re.compile(r'\w+|\s+|[^\w\s]+')
    regex = re.compile(r'\b\w+\b')
    match = regex.search(text, interval[1])
    return (match.start(), match.end())
