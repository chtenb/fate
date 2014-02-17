"""
A selector is a special type of action that is used to modify the selection of a session.
Strictly speaking, a selector is a function that is decorated by `selector`,
either directly or indirectly.
We distinguish between functions that work selection-wise (global selectors)
and function that work interval-wise (local selectors).
Furthermore we have selectors that are based on regular expressions.
"""
from .selection import Selection
from .action import actor
from .modes import EXTEND_MODE, REDUCE_MODE
import re


def selector(function):
    """
    This is the function decorator for selectors.
    The passed function will be turned into a selector
    and will be passed a selection, text and selection mode
    and should return a Selection.
    If the resulting Selection is empty, invalid or the same as
    the original selection, return nothing.
    """
    @actor
    def wrapper(session):
        selection = session.selection
        text = session.text

        result = function(selection, text, session.selection_mode)
        assert result == None or result.__class__ == Selection

        # If the result is empty, invalid or the same, return None
        if not result or result == selection:
            return
        for beg, end in result:
            if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                return

        return result
    return wrapper


@selector
def single_interval(selection, text, mode):
    """Reduce the selection to the single uppermost interval."""
    return Selection(selection.session, intervals=selection[0])


@selector
def empty(selection, text, mode):
    """Reduce the selection to a single uppermost empty interval."""
    beg = selection[0][0]
    return Selection(selection.session, intervals=[(beg, beg)])


@selector
def everything(selection, text, mode):
    """Select the entire text."""
    return Selection(selection.session, intervals=[(0, len(text))])


@selector
def join(selection, text, mode):
    """Join all intervals together."""
    return Selection(selection.session, intervals=[(selection[0][0], selection[-1][1])])


@selector
def complement(selection, text, mode):
    """Return the complement."""
    return selection.complement()


def local_selector(function):
    """
    This is a function decorator to turn the given function into
    a local selector.
    The given function should take an interval to another interval.
    It is turned into a selector by applying the function
    to all intervals contained in a selection.
    Keeps original interval when resulting interval is invalid.
    """
    @selector
    def wrapper(selection, text, mode):
        if mode == REDUCE_MODE:
            iterselection = selection.complement()
        else:
            iterselection = selection

        result = []
        for interval in iterselection:
            interval_result = function(interval, text)
            nbeg, nend = interval_result
            assert nbeg <= nend

            # If the result invalid, we return None
            if not interval_result:
                return None
            else:
                beg, end = interval_result
                if not (0 <= beg < len(text) and 0 <= end <= len(text)):
                    interval_result = interval

            if mode == REDUCE_MODE or mode == EXTEND_MODE:
                interval_result = (min(interval[0], interval_result[0]),
                                   max(interval[1], interval_result[1]))
            result.append(interval_result)

        result = Selection(selection.session, result)
        if mode == REDUCE_MODE:
            result = selection.reduce(result)
        return result
    return wrapper


@local_selector
def empty_before(interval, text):
    """Return the empty interval before each interval."""
    beg, _ = interval
    return (beg, beg)


@local_selector
def empty_after(interval, text):
    """Return the empty interval after each interval."""
    _, end = interval
    return (end, end)


def find_pattern(text, pattern, reverse=False, group=0):
    """Find intervals that match given pattern."""
    matches = re.finditer(pattern, text)
    if reverse:
        matches = reversed(list(matches))
    return [(match.start(group), match.end(group))
            for match in matches]


def global_pattern_selector(pattern, reverse=False, group=0):
    """
    Factory method for creating a selector based on a regular expression.
    First try to select all occurences intersecting with selection.
    If that doesn't change the selection,
    start selecting one by one, outside selection.
    """
    @selector
    def wrapper(selection, text, mode):
        match_intervals = find_pattern(text, pattern, reverse, group)

        # First select all occurences intersecting with selection,
        # and process according to mode
        new_intervals = [interval for interval in match_intervals
                         if selection.intersects(interval)]

        if new_intervals:
            new_selection = Selection(selection.session, intervals=new_intervals)
            if mode == EXTEND_MODE:
                new_selection = selection.extend(new_selection)
            elif mode == REDUCE_MODE:
                new_selection = selection.reduce(new_selection)

            if new_selection and selection != new_selection:
                return new_selection

        # If that doesn't change the selection,
        # start selecting one by one, and process according to mode
        new_intervals = []
        if reverse:
            beg, end = selection[-1]
        else:
            beg, end = selection[0]

        for mbeg, mend in match_intervals:
            new_selection = Selection(selection.session, intervals=[(mbeg, mend)])
            # If match is in the right direction
            if not reverse and mend > beg or reverse and mbeg < end:
                if mode == EXTEND_MODE:
                    new_selection = selection.extend(new_selection)
                elif mode == REDUCE_MODE:
                    new_selection = selection.reduce(new_selection)

                if new_selection and selection != new_selection:
                    return new_selection

    return wrapper


def reduce_interval(self, interval):
    """Reduce first interval with second interval."""
    beg, end = self
    nbeg, nend = self
    mbeg, mend = interval
    if mbeg <= beg:
        nbeg = max(beg, mend)
    if mend >= end:
        nend = min(end, mbeg)

    if nbeg <= nend:
        return nbeg, nend


def local_pattern_selector(pattern, reverse=False, group=0):
    """
    Factory method for creating local selectors based on a regular expression.
    """
    @selector
    def wrapper(selection, text, mode):
        match_intervals = find_pattern(text, pattern, reverse, group)

        new_intervals = []
        for interval in selection:
            beg, end = interval
            new_interval = None

            for mbeg, mend in match_intervals:
                # If match is valid, i.e. overlaps
                # or is beyond current interval in right direction
                if (not reverse and mend > beg
                        or reverse and mbeg < end):
                    if mode == EXTEND_MODE:
                        new_interval = min(beg, mbeg), max(end, mend)
                    elif mode == REDUCE_MODE:
                        if reverse:
                            mend = max(end, mend)
                        else:
                            mbeg = min(beg, mbeg)
                        new_interval = reduce_interval(interval, (mbeg, mend))
                    else:
                        new_interval = mbeg, mend

                    if new_interval and new_interval != interval:
                        break

            # If the result invalid or the same as old interval, we return None
            if not new_interval or new_interval == interval:
                return None

            new_intervals.append(new_interval)

        return Selection(selection.session, intervals=new_intervals)
    return wrapper


def pattern_pair(pattern, **kwargs):
    """Return two local pattern selectors for given pattern,
    one matching forward and one matching backward."""
    return (local_pattern_selector(pattern, **kwargs),
            local_pattern_selector(pattern, reverse=True, **kwargs))


next_char, previous_char = pattern_pair(r'(?s).')
next_word, previous_word = pattern_pair(r'\b\w+\b')
next_line, previous_line = pattern_pair(r'\s*([^\n]*)', group=1)
next_full_line, previous_full_line = pattern_pair(r'[^\n]*\n?')
next_paragraph, previous_paragraph = pattern_pair(r'(?s)((?:[^\n][\n]?)+)')
next_white_space, previous_white_space = pattern_pair(r'\s')
