"""
A selector is a special type of action that is used to modify the selection of a session.
Strictly speaking, a selector is a function that is decorated by `selector`,
either directly or indirectly.
We distinguish between functions that work selection-wise (global selectors)
and function that work interval-wise (local selectors).
Furthermore we have selectors that are based on regular expressions.
"""
from .selection import Selection, Interval
from .modes import SELECT_MODE, EXTEND_MODE, REDUCE_MODE
import re
from functools import partial
import logging


class SelectEverything(Selection):
    """Select the entire text."""
    def __init__(self, session, selection=None, selection_mode=None):
        Selection.__init__(self, Interval(0, len(session.text)))


class SelectSingleInterval(Selection):
    """Reduce the selection to the single uppermost interval."""
    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        Selection.__init__(self, selection[0])


class Empty(Selection):
    """Reduce the selection to a single uppermost empty interval."""
    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        beg = selection[0][0]
        Selection.__init__(self, Interval(beg, beg))


class Join(Selection):
    """Join all intervals together."""
    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        Selection.__init__(self, Interval(selection[0][0], selection[-1][1]))


class Complement(Selection):
    """Return the complement."""
    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        Selection.__init__(self, selection.complement())


class EmptyBefore(Selection):
    """Return the empty interval before each interval."""
    def __init__(self, session, selection=None, selection_mode=None):
        Selection.__init__(self)
        selection = selection or session.selection
        for interval in selection:
            beg, _ = interval
            self.add(Interval(beg, beg))


class EmptyAfter(Selection):
    """Return the empty interval after each interval."""
    def __init__(self, session, selection=None, selection_mode=None):
        Selection.__init__(self)
        selection = selection or session.selection
        for interval in selection:
            _, end = interval
            self.add(Interval(end, end))


def find_pattern(text, pattern, reverse=False, group=0):
    """Find intervals that match given pattern."""
    matches = re.finditer(pattern, text)
    if reverse:
        matches = reversed(list(matches))
    return [(match.start(group), match.end(group))
            for match in matches]


class SelectPattern(Selection):
    def __init__(self, pattern, session, selection=None, selection_mode=None,
                 reverse=False, group=0):
        Selection.__init__(self)
        selection = selection or session.selection
        selection_mode = selection_mode or session.selection_mode

        match_intervals = find_pattern(session.text, pattern, reverse, group)

        # First select all occurences intersecting with selection,
        # and process according to mode
        new_intervals = [interval for interval in match_intervals
                         if selection.intersects(interval)]

        if new_intervals:
            new_selection = Selection(new_intervals)
            if selection_mode == EXTEND_MODE:
                new_selection.add(new_intervals)
            elif selection_mode == REDUCE_MODE:
                new_selection.substract(new_intervals)

            if new_selection and selection != new_selection:
                self.add(new_selection)
                return

        # If that doesn't change the selection,
        # start selecting one by one, and process according to mode
        new_intervals = []
        if reverse:
            beg, end = selection[-1]
        else:
            beg, end = selection[0]

        for mbeg, mend in match_intervals:
            new_selection = Selection([Interval(mbeg, mend)])
            # If match is in the right direction
            if not reverse and mend > beg or reverse and mbeg < end:
                if selection_mode == EXTEND_MODE:
                    new_selection = selection.add(new_selection)
                elif selection_mode == REDUCE_MODE:
                    new_selection = selection.substract(new_selection)

                if new_selection and selection != new_selection:
                    self.add(new_selection)
                    return


class SelectLocalPattern(Selection):
    def __init__(self, pattern, session, selection=None, selection_mode=None,
                 reverse=False, group=0, only_within=False):
        Selection.__init__(self)
        selection = selection or session.selection
        selection_mode = selection_mode or session.selection_mode

        match_intervals = find_pattern(session.text, pattern, reverse, group)

        for interval in selection:
            beg, end = interval
            new_interval = None

            for mbeg, mend in match_intervals:
                # If only_within is True,
                # match must be within current interval
                if only_within and not (beg <= mbeg and mend <= end):
                    continue

                # If match is valid, i.e. overlaps
                # or is beyond current interval in right direction
                if (not reverse and mend > beg
                        or reverse and mbeg < end):
                    if selection_mode == EXTEND_MODE:
                        new_interval = Interval(min(beg, mbeg), max(end, mend))
                    elif selection_mode == REDUCE_MODE:
                        if reverse:
                            mend = max(end, mend)
                        else:
                            mbeg = min(beg, mbeg)
                        new_interval = interval - Interval(mbeg, mend)
                    else:
                        new_interval = Interval(mbeg, mend)

                    if new_interval and new_interval != interval:
                        break

            # If the result invalid or the same as old interval, we return None
            if not new_interval or new_interval == interval:
                return None

            self.add(new_interval)

SelectIndent = partial(SelectLocalPattern, r'(?m)^([ \t]*)', reverse=True, group=1)


def pattern_pair(pattern, **kwargs):
    """
    Return two local pattern selectors for given pattern,
    one matching forward and one matching backward.
    """
    return (SelectLocalPattern(pattern, **kwargs),
            SelectLocalPattern(pattern, reverse=True, **kwargs))

NextChar, PreviousChar = pattern_pair(r'(?s).')
NextWord, PreviousWord = pattern_pair(r'\b\w+\b')
NextLine, PreviousLine = pattern_pair(r'\s*([^\n]*)', group=1)
NextFullLine, PreviousFullLine = pattern_pair(r'[^\n]*\n?')
NextParagraph, PreviousParagraph = pattern_pair(r'(?s)((?:[^\n][\n]?)+)')
NextWhiteSpace, PreviousWhiteSpace = pattern_pair(r'\s')

