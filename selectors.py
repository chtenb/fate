"""A selector takes a selection and returns a second, derived selection"""
from .selection import Selection
import re
import logging

# TODO rewrite decorators to deal with selection modes

def selector(function):
    """Defaults to (0,0) when text or selection passed is empty.
    Returns original selection when result is empty or invalid."""
    def wrapper(session, selection=None):
        text = session.text
        if not selection:
            selection = session.selection

        if session.reduce_mode:
            result = function(selection.complement(), text)
            result = selection.reduce(result)
        elif session.extend_mode:
            result = function(selection, text)
            result = selection.extend(result)
        else:
            result = function(selection, text)

        # If the result isn't valid, we return the original selection
        for beg, end in result:
            if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                return selection

        if not result:
            # If the result is empty, we return the old selection
            return selection

        return result
    return wrapper


@selector
def single_character(selection, text):
    return Selection(selection.session, intervals=[(selection[0][0], selection[0][0] + 1)])


@selector
def complement(selection, text):
    return selection.complement()


def interval_selector(function):
    """An interval selector takes an interval to another interval.
    This induces a selector, by applying the interval
    selector to all intervals contained in a selection
    Keeps original interval when result is empty or invalid."""
    def wrapper(session, selection=None):
        text = session.text
        if not selection:
            selection = session.selection

        if session.reduce_mode:
            iterselection = selection.complement()
        else:
            iterselection = selection

        result = []
        for interval in iterselection:
            interval_result = function(interval, text)

            # If the result isn't valid, we take the original interval
            if not interval_result:
                interval_result = interval
            else:
                beg, end = interval_result
                if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                    interval_result = interval

            if session.reduce_mode or session.extend_mode:
                interval_result = min(interval[0], interval_result[0]), max(interval[1], interval_result[1])
            result.append(interval_result)

        result = Selection(session, result)
        if session.reduce_mode:
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


def pattern_selector(pattern, reverse=False):
    """Factory method for creating selectors based on a regular expression"""
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
