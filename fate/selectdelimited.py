"""
This module contains commands for selecting around and inside nested structures.

The idea is that we identify an enclosing structure by its starting delimiter.
We can then simply move back and forth over these starting delimiters, selecting the
corresponding enclosing structures.
We must allow both inclusive and exclusive selections, unless they coincide with existing
selections.
"""

from .selection import Interval
from .selectors import intervalselector_withmode
from . import commands


def select_delimiting_char(doc, interval, char=None, backward=False):
    """
    Select around given character.
    Return None if not all intervals are surrounded.
    """
    beg, end = interval

    # Check if we should check for a matching pair
    character_pairs = [('{', '}'), ('[', ']'), ('(', ')'), ('<', '>')]
    beg_delim, end_delim = char, char
    for fst, snd in character_pairs:
        if char == fst or char == snd:
            beg_delim, end_delim = fst, snd
            break

    # For each interval find the smallest surrounding pair
    if not backward:
        try:
            match_beg = doc.text.index(beg_delim, beg)
            match_end = doc.text.index(end_delim, match_beg + 1) + 1
        except ValueError:
            return

        if beg == match_beg and end == match_end:
            # Exclude delimiters
            return Interval(match_beg + 1, match_end - 1)
        else:
            # Include delimiters
            return Interval(match_beg, match_end)
    else:
        try:
            match_beg = doc.text.rindex(beg_delim, 0, beg)
            match_end = doc.text.index(end_delim, match_beg + 1) + 1
        except ValueError:
            return

        if beg == match_beg + 1 and end == match_end - 1:
            # Include delimiters
            return Interval(match_beg, match_end)
        else:
            # Exclude delimiters
            return Interval(match_beg + 1, match_end - 1)

select_delimiting_char_helper = intervalselector_withmode(select_delimiting_char)


def select_next_delimiting_char(doc, char=None):
    char = char or doc.ui.getkey()
    if char == doc.cancelkey:
        return
    return select_delimiting_char_helper(doc, char=char, backward=False)
commands.select_next_delimiting_char = select_next_delimiting_char


def select_previous_delimiting_char(doc, char=None):
    char = char or doc.ui.getkey()
    if char == doc.cancelkey:
        return
    return select_delimiting_char_helper(doc, char=char, backward=True)
commands.select_previous_delimiting_char = select_previous_delimiting_char


def select_delimiting(doc, interval, backward=False):
    """Select around common surrounding character pair."""
    default_chars = ['{', '[', '(', '<', '\'', '"']
    candidates = []

    for char in default_chars:
        candidate = select_delimiting_char(doc, interval, char=char, backward=backward)
        if candidate != None:
            candidates.append(candidate)
    if candidates:
        # Select candidate with nearest starting delimiter
        return min(candidates, key=lambda candidate: abs(interval[0] - candidate[0]))


@intervalselector_withmode
def select_next_delimiting(doc, interval):
    return select_delimiting(doc, interval, backward=False)
commands.select_next_delimiting = select_next_delimiting


@intervalselector_withmode
def select_previous_delimiting(doc, interval):
    return select_delimiting(doc, interval, backward=True)
commands.select_previous_delimiting = select_previous_delimiting
