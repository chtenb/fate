"""A selector takes a selection and returns another derived selection"""
from .selection import Selection
import re


def selector(function):
    """Defaults to (0,0) when selection passed is empty.
    Returns original selection when result is empty."""
    def wrapper(selection, text):
        if not selection:
            selection.add((0, 0))
        result = function(selection, text)
        return result if result else selection
    return wrapper


@selector
def single_character(selection, text):
    return Selection(selection.session, intervals=[(selection[0][0], selection[0][0])])


@selector
def complement(selection, text):
    return selection.complement()


def interval_selector(function):
    """An interval selector takes an interval to another interval.
    This induces a selector, by applying the interval
    selector to all intervals contained in a selection"""
    @selector
    def wrapper(selection, text):
        result = Selection(selection.session)
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


def pattern_selector(pattern, reverse=False):
    @interval_selector
    def wrapper(interval, text):
        beg, end = interval
        regex = re.compile(pattern)
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
    return wrapper

# Predefined pattern selectors
next_word = pattern_selector(r'\b\w+\b')
previous_word = pattern_selector(r'\b\w+\b', reverse=True)
next_paragraph = pattern_selector(r'(?s)((?:[^\n][\n]?)+)')
previous_paragraph = pattern_selector(r'(?s)((?:[^\n][\n]?)+)', reverse=True)
