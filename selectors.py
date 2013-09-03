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
            selection.add((0, 0))
        result = function(selection, text)
        return result if result else selection
    return wrapper


@selector
def single_character(selection, text):
    return Selection(intervals=[(selection[0][0], selection[0][0])])


@selector
def complement(selection, text):
    return selection.complement(text)


def interval_selector(function):
    """An interval selector takes an interval to another interval.
    This induces a selector, by applying the interval
    selector to all intervals contained in a selection"""
    @selector
    def wrapper(selection, text):
        result = Selection()
        for interval in selection:
            interval_result = function(interval, text)
            if interval_result:
                result.add(interval_result)
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


def find_next(interval, text, pattern, reverse=False, *flags):
    beg, end = interval
    regex = re.compile(pattern, *flags)
    matches = regex.finditer(text)
    if matches:
        if reverse:
            matches = reversed(list(matches))
            for match in matches:
                if match.start() < beg:
                    return match.start(), match.end()
        else:
            for match in matches:
                if end < match.end():
                    return match.start(), match.end()


@interval_selector
def next_word(interval, text):
    """Return next word"""
    return find_next(interval, text, r'\b\w+\b')


@interval_selector
def previous_word(interval, text):
    """Return previous word"""
    return find_next(interval, text, r'\b\w+\b', reverse=True)


@interval_selector
def next_paragraph(interval, text):
    """Return next paragraph"""
    return find_next(interval, text, r'(?s)((?:[^\n][\n]?)+)')


@interval_selector
def previous_paragraph(interval, text):
    """Return previous paragraph"""
    return find_next(interval, text, r'(?s)((?:[^\n][\n]?)+)', reverse=True)
