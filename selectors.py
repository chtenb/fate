"""
This module contains all kinds of actions and actors related to make selections.
We distinguish between functions that work selection-wise (global selectors)
and function that work interval-wise (local selectors).
Furthermore we have selectors that are based on regular expressions.

Selectors may return None, in which case the session should not be affected.
Selectors may also return a result which is identical to the previous selection.
The code that executes the action may want to check if this is the case, before applying.
"""
import re
from functools import partial

from . import actions
from .selection import Selection, Interval
from .modes import EXTEND_MODE, REDUCE_MODE


class SelectEverything(Selection):

    """Select the entire text."""

    def __init__(self, session, selection=None, selection_mode=None):
        Selection.__init__(self, Interval(0, len(session.text)))
actions.SelectEverything = SelectEverything


class SelectSingleInterval(Selection):

    """Reduce the selection to the single uppermost interval."""

    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        Selection.__init__(self, selection[0])
actions.SelectSingleInterval = SelectSingleInterval


class Empty(Selection):

    """Reduce the selection to a single uppermost empty interval."""

    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        beg = selection[0][0]
        Selection.__init__(self, Interval(beg, beg))
actions.Empty = Empty


class Join(Selection):

    """Join all intervals together."""

    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        Selection.__init__(self, Interval(selection[0][0], selection[-1][1]))
actions.Join = Join


class Complement(Selection):

    """Return the complement."""

    def __init__(self, session, selection=None, selection_mode=None):
        selection = selection or session.selection
        Selection.__init__(self, selection.complement(session))
actions.Complement = Complement


class EmptyBefore(Selection):

    """Return the empty interval before each interval."""

    def __init__(self, session, selection=None, selection_mode=None):
        Selection.__init__(self)
        selection = selection or session.selection
        for interval in selection:
            beg, _ = interval
            self.add(Interval(beg, beg))
actions.EmptyBefore = EmptyBefore


class EmptyAfter(Selection):

    """Return the empty interval after each interval."""

    def __init__(self, session, selection=None, selection_mode=None):
        Selection.__init__(self)
        selection = selection or session.selection
        for interval in selection:
            _, end = interval
            self.add(Interval(end, end))
actions.EmptyAfter = EmptyAfter


def find_matching_pair(string, pos, fst, snd):
    """Find matching pair of characters fst and snd around (inclusive) position pos."""
    assert 0 <= pos < len(string)
    level = 0
    i = pos
    beg = None
    while i >= 0:
        if string[i] == fst:
            if level > 0:
                level -= 1
            else:
                beg = i
        if string[i] == snd:
            level += 1
        i -= 1

    level = 0
    i = pos
    end = None
    while i < len(string):
        if string[i] == snd:
            if level > 0:
                level -= 1
            else:
                end = i + 1
        if string[i] == fst:
            level += 1
        i += 1

    if beg != None and end != None:
        return Interval(beg, end)


def interval_length(interval):
    return interval.end - interval.beg


def avg_interval_length(selection):
    return sum(end - beg for beg, end in selection) / len(selection)


def select_around_interval(string, beg, end, fst, snd):
    """Find matching pair of characters fst and snd around (inclusive) beg and end."""
    assert 0 <= beg <= end <= len(string)

    # These edge cases should not yield a result
    if beg == end == len(string) or beg == end == 0:
        return

    match1 = find_matching_pair(string, beg, fst, snd)
    match2 = find_matching_pair(string, max(0, end - 1), fst, snd)
    if match1 == None or match2 == None:
        return None
    nbeg, nend = max([match1, match2], key=interval_length)

    # If interval remains the same try selecting one level higher
    if (beg, end) == (nbeg, nend):
        if beg > 0:
            return select_around_interval(string, beg - 1, end, fst, snd)
        elif end < len(string):
            return select_around_interval(string, beg, end + 1, fst, snd)

    # Decide whether to select exclusive or remain inclusive
    if beg > nbeg + 1 or end < nend - 1:
        # Select exclusive
        nbeg += 1
        nend -= 1
    return Interval(nbeg, nend)


def SelectAroundChar(session, char=None, selection=None):
    """
    Select around given character. If no character given, get it from user.
    Return None if not all intervals are surrounded.
    """
    selection = selection or session.selection
    char = char or session.ui.getchar()
    result = Selection()

    # Check if we should check for a matching pair
    character_pairs = [('{', '}'), ('[', ']'), ('(', ')'), ('<', '>')]
    for fst, snd in character_pairs:
        if char == fst or char == snd:
            # For each interval find the smallest surrounding pair
            for beg, end in selection:
                match = select_around_interval(session.text, beg, end, fst, snd)
                if match == None:
                    return
                result.add(match)
            return result

    # If not, we simple find the first surrounding occurances
    for beg, end in selection:
        nend = session.text.find(char, end)
        nbeg = session.text.rfind(char, 0, beg)
        if nend != -1 and nbeg != -1:
            result.add(Interval(nbeg, nend + 1))
        else:
            return None
    return result
actions.SelectAroundChar = SelectAroundChar


def SelectAround(session, selection=None):
    """Select around common surrounding character pair."""
    selection = selection or session.selection
    default_chars = ['{', '[', '(', '<', '\'', '"']
    candidates = []
    for char in default_chars:
        candidate = SelectAroundChar(session, char, selection)
        if candidate != None:
            candidates.append(candidate)
    if candidates:
        # Select smallest enclosing candidate
        return min(candidates, key=avg_interval_length)
actions.SelectAround = SelectAround


def find_pattern(text, pattern, reverse=False, group=0):
    """Find intervals that match given pattern."""
    matches = re.finditer(pattern, text)
    if reverse:
        matches = reversed(list(matches))
    return [Interval(match.start(group), match.end(group))
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
            new_selection = Selection(Interval(mbeg, mend))
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

            # If the result invalid, return original selection
            if not new_interval:
                self._intervals = selection._intervals
                return

            self.add(new_interval)

SelectIndent = partial(SelectLocalPattern, r'(?m)^([ \t]*)', reverse=True, group=1)
actions.SelectIndent = SelectIndent


def pattern_pair(pattern, **kwargs):
    """
    Return two local pattern selectors for given pattern,
    one matching forward and one matching backward.
    """
    return (partial(SelectLocalPattern, pattern, **kwargs),
            partial(SelectLocalPattern, pattern, reverse=True, **kwargs))

NextChar, PreviousChar = pattern_pair(r'(?s).')
actions.NextChar = NextChar
actions.PreviousChar = PreviousChar
NextWord, PreviousWord = pattern_pair(r'\b\w+\b')
actions.NextWord = NextWord
actions.PreviousWord = PreviousWord
NextLine, PreviousLine = pattern_pair(r'\s*([^\n]*)', group=1)
actions.NextLine = NextLine
actions.PreviousLine = PreviousLine
NextFullLine, PreviousFullLine = pattern_pair(r'[^\n]*\n?')
actions.NextFullLine = NextFullLine
actions.PreviousFullLine = PreviousFullLine
NextParagraph, PreviousParagraph = pattern_pair(r'(?s)((?:[^\n][\n]?)+)')
actions.NextParagraph = NextParagraph
actions.PreviousParagraph = PreviousParagraph
NextWhiteSpace, PreviousWhiteSpace = pattern_pair(r'\s')
actions.NextWhiteSpace = NextWhiteSpace
actions.PreviousWhiteSpace = PreviousWhiteSpace


def lock_selection(session):
    """Lock current selection."""
    if session.locked_selection == None:
        session.locked_selection = Selection()
    session.locked_selection += session.selection
    assert not session.locked_selection.isempty
actions.lock = lock_selection


def unlock_selection(session):
    """Remove current selection from locked selection."""
    locked = session.locked_selection
    if locked != None:
        nselection = locked - session.selection
        if not nselection.isempty:
            session.locked_selection = nselection
actions.unlock = unlock_selection


def release_locked_selection(session):
    """Release locked selection."""
    if session.locked_selection != None:
        # The text length may be changed after the locked selection was first created
        # So we must bound it to the current text length
        newselection = session.locked_selection.bound(0, len(session.text))
        if not newselection.isempty:
            session.selection = newselection
        session.locked_selection = None
actions.release = release_locked_selection
