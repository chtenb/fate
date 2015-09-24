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


def select_enclosing_char(doc, interval, char=None, backward=False):
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
        match_beg = doc.text.find(beg_delim, beg)
        if match_beg == -1:
            return
        match_end = doc.text.find(end_delim, match_beg + 1) + 1
        if match_end == -1:
            return

        if beg == match_beg and end == match_end:
            # Exclude delimiters
            return Interval(match_beg + 1, match_end - 1)
        else:
            # Include delimiters
            return Interval(match_beg, match_end)
    else:
        match_beg = doc.text.rfind(beg_delim, 0, beg)
        if match_beg == -1:
            return
        match_end = doc.text.find(end_delim, match_beg + 1) + 1
        if match_end == -1:
            return

        if beg == match_beg + 1 and end == match_end - 1:
            # Include delimiters
            return Interval(match_beg, match_end)
        else:
            # Exclude delimiters
            return Interval(match_beg + 1, match_end - 1)

select_enclosing_char_helper = intervalselector_withmode(select_enclosing_char)


def select_next_enclosing_char(doc):
    char = doc.ui.getkey()
    if char == doc.cancelkey:
        return
    return select_enclosing_char_helper(doc, char=char, backward=False)
commands.select_next_enclosing_char = select_next_enclosing_char


def select_previous_enclosing_char(doc):
    char = doc.ui.getkey()
    if char == doc.cancelkey:
        return
    return select_enclosing_char_helper(doc, char=char, backward=True)
commands.select_previous_enclosing_char = select_previous_enclosing_char


def select_enclosing(doc, interval, backward=False):
    """Select around common surrounding character pair."""
    default_chars = ['{', '[', '(', '<', '\'', '"']
    candidates = []

    for char in default_chars:
        candidate = select_enclosing_char(doc, interval, char=char, backward=backward)
        if candidate != None:
            candidates.append(candidate)
    if candidates:
        # Select candidate with nearest starting delimiter
        return min(candidates, key=lambda candidate: abs(interval[0] - candidate[0]))


@intervalselector_withmode
def select_next_enclosing(doc, interval):
    return select_enclosing(doc, interval, backward=False)
commands.select_next_enclosing = select_next_enclosing


@intervalselector_withmode
def select_previous_enclosing(doc, interval):
    return select_enclosing(doc, interval, backward=True)
commands.select_previous_enclosing = select_previous_enclosing
