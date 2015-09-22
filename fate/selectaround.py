"""
This module contains commands for selecting around and inside nested structures.

Lemma. If selected a complete nested structure with multiple toplevel groups,
on either side, the first surround character that exceeds the toplevel is the result.

Proposed steps:
    - compute properties of selected interval
    - expand interval to be a valid nested structure
    - if multiple toplevel groups: expand interval to increase the level


Lemma. 
"""

from .selection import Selection, Interval
from . import commands

def find_nesting_levels(string, beg, end, fst, snd):
    """Find the nesting level of beg and end."""
    beg_level = 0
    end_level = 0

    for i in range(beg, end):
        if string[i] == fst:
            end_level += 1
        if string[i] == snd:
            if end_level > 0:
                end_level -= 1
            else:
                beg_level += 1

    return beg_level, end_level

def find_matching_snd(string, pos, fst, snd):
    """Given the position pos of the fst character, find the matching snd."""
    assert 0 <= pos <= len(string)
    assert string[pos] == fst

    level = 1
    i = pos

    while i < len(string):
        if string[i] == snd:
            if level > 0:
                level -= 1
            else:
                return i
        elif string[i] == fst:
            level += 1
        i += 1

def expand_to_valid_structure(string, beg, end, fst, snd):
    """
    Find first matching pair of characters fst and snd around the interval beg, end.
    """
    assert 0 <= beg <= end <= len(string)

    beg_level, end_level = find_nesting_levels(string, beg, end, fst, snd)

    # First find nbeg
    i = beg - 1
    if beg_level == 0:
        nbeg = beg
    else:
        nbeg = None
        while i >= 0:
            if string[i] == fst:
                if beg_level > 0:
                    beg_level -= 1
                else:
                    nbeg = i
                    break
            elif string[i] == snd:
                beg_level += 1
            i -= 1

    # Then find nend
    i = end
    if end_level == 0:
        nend = end
    else:
        nend = None
        while i < len(string):
            if string[i] == snd:
                if end_level > 0:
                    end_level -= 1
                else:
                    nend = i + 1
                    break
            elif string[i] == fst:
                end_level += 1
            i += 1

    if nbeg != None and nend != None:
        return Interval(nbeg, nend)


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

    match = expand_to_valid_structure(string, beg, end, fst, snd)
    if match == None:
        return None
    nbeg, nend = match
    #match1 = find_matching_pair(string, beg, end, fst, snd)
    #match2 = find_matching_pair(string, max(0, end - 1), fst, snd)
    #if match1 == None or match2 == None:
        #return None
    #nbeg, nend = max([match1, match2], key=interval_length)

    # If interval remains the same try selecting one level higher
    # TODO: fix infinite recursion
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


def selectaround_char(document, char=None, selection=None):
    """
    Select around given character. If no character given, get it from user.
    Return None if not all intervals are surrounded.
    """
    selection = selection or document.selection
    char = char or document.ui.getkey()
    if char == 'Cancel':
        return
    result = Selection()

    # Check if we should check for a matching pair
    character_pairs = [('{', '}'), ('[', ']'), ('(', ')'), ('<', '>')]
    for fst, snd in character_pairs:
        if char == fst or char == snd:
            # For each interval find the smallest surrounding pair
            for beg, end in selection:
                match = select_around_interval(document.text, beg, end, fst, snd)
                if match == None:
                    return
                result.add(match)
            return result

    # If not, we simple find the first surrounding occurances
    for beg, end in selection:
        nend = document.text.find(char, end)
        nbeg = document.text.rfind(char, 0, beg)
        if nend != -1 and nbeg != -1:
            result.add(Interval(nbeg, nend + 1))
        else:
            return
    return result
commands.selectaround_char = selectaround_char


def selectaround(document, selection=None):
    """Select around common surrounding character pair."""
    selection = selection or document.selection
    default_chars = ['{', '[', '(', '<', '\'', '"']
    candidates = []
    for char in default_chars:
        candidate = selectaround_char(document, char, selection)
        if candidate != None:
            candidates.append(candidate)
    if candidates:
        # Select smallest enclosing candidate
        return min(candidates, key=avg_interval_length)
commands.selectaround = selectaround
