"""A selector takes a selection and returns another derived selection"""
from .selection import Selection
from . import current
import re


def selector(function):
    """Makes the text parameter optional by defaulting to current.session.text"""
    def wrapper(selection, text=None):
        if not text:
            text = current.session.text
        if not selection:
            selection.add((0,0))
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
    eol = text.find('\n', end)
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
    regex = re.compile(r'\b\w+\b')
    match = regex.search(text, interval[1])
    if match:
        return (match.start(), match.end())
    return interval


@interval_selector
def previous_word(interval, text):
    """Return previous word"""
    regex = re.compile(r'\b\w+\b')
    matches = list(regex.finditer(text, 0, interval[0]))
    if matches:
        match = next(reversed(matches))
        return (match.start(), match.end())
    return interval
