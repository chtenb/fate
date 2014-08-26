"""
This module contains all kinds of commands and actors related to make selections.
We distinguish between functions that work selection-wise (global selectors)
and function that work interval-wise (local selectors).
Furthermore we have selectors that are based on regular expressions.

Selectors may return None, in which case the document should not be affected.
Selectors may also return a result which is identical to the previous selection.
The code that executes the command may want to check if this is the case, before applying.

Because it is often handy to use selectors as building blocks for other computations,
selectors return their result as a selection instead of executing them immediately.
Secondly, one can pass a selection which should be used as starting point
for the selector instead of the current selection of the document.
"""
import re
from functools import partial, wraps

from . import commands
from .selection import Selection, Interval
from .mode import Mode, normalmode

from logging import debug


def escape(document):
    if document.selectmode != '':
        normalselectmode(document)
    else:
        empty(document)
commands.escape = escape


def extendmode(document):
    document.selectmode = 'Extend'
commands.extendmode = extendmode


def reducemode(document):
    document.selectmode = 'Reduce'
commands.reducemode = reducemode


def normalselectmode(document):
    document.selectmode = ''
commands.normalselectmode = normalselectmode


def selector(command):
    """Decorator to make it more convenient to write selectors."""
    @wraps(command)
    def wrapper(document, selection=None, selectmode=None, preview=False):
        selection = selection or document.selection
        selectmode = selectmode or document.selectmode
        selection = command(document, selection, selectmode)
        if preview:
            return selection
        selection(document)
    return wrapper


@selector
def selectall(document, selection, selectmode):
    """Select the entire text."""
    return Selection(Interval(0, len(document.text)))
commands.selectall = selectall


@selector
def select_single_interval(document, selection, selectmode):
    """Reduce the selection to the single uppermost interval."""
    return Selection(selection[0])
commands.select_single_interval = select_single_interval


@selector
def empty(document, selection, selectmode):
    """Reduce the selection to a single uppermost empty interval."""
    beg = selection[0][0]
    return Selection(Interval(beg, beg))
commands.empty = empty


@selector
def join(document, selection, selectmode):
    """Join all intervals together."""
    return Selection(Interval(selection[0][0], selection[-1][1]))
commands.join = join


@selector
def complement(document, selection, selectmode):
    """Return the complement."""
    return Selection(selection.complement(document))
commands.complement = complement


@selector
def emptybefore(document, selection, selectmode):
    """Return the empty interval before each interval."""
    intervals = []
    for interval in selection:
        beg, _ = interval
        intervals.append(Interval(beg, beg))
    return Selection(intervals)
commands.emptybefore = emptybefore


@selector
def emptyafter(document, selection, selectmode):
    """Return the empty interval after each interval."""
    intervals = []
    for interval in selection:
        _, end = interval
        intervals.append(Interval(end, end))
    return Selection(intervals)
commands.emptyafter = emptyafter


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


def findpattern(text, pattern, reverse=False, group=0):
    """Find intervals that match given pattern."""
    matches = re.finditer(pattern, text)
    if reverse:
        matches = reversed(list(matches))
    return [Interval(match.start(group), match.end(group))
            for match in matches]


def selectpattern(pattern, document, selection=None, selectmode=None,
                  reverse=False, group=0):
    newselection = Selection()
    selection = selection or document.selection
    selectmode = selectmode or document.selectmode

    match_intervals = findpattern(document.text, pattern, reverse, group)

    # First select all occurences intersecting with selection,
    # and process according to mode
    new_intervals = [interval for interval in match_intervals
                     if selection.intersects(interval)]

    if new_intervals:
        new_selection = Selection(new_intervals)
        if selectmode == 'Extend':
            new_selection.add(new_intervals)
        elif selectmode == 'Reduce':
            new_selection.substract(new_intervals)

        if new_selection and selection != new_selection:
            newselection.add(new_selection)
            return newselection

    # If that doesnt change the selection,
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
            if selectmode == 'Extend':
                new_selection = selection.add(new_selection)
            elif selectmode == 'Reduce':
                new_selection = selection.substract(new_selection)

            if new_selection and selection != new_selection:
                newselection.add(new_selection)
                return newselection

    return newselection


def select_local_pattern(pattern, document, selection=None, selectmode=None, reverse=False,
                         group=0, only_within=False, allow_same_interval=False):
    newselection = Selection()
    selection = selection or document.selection
    selectmode = selectmode or document.selectmode

    match_intervals = findpattern(document.text, pattern, reverse, group)

    for interval in selection:
        beg, end = interval
        new_interval = None

        for mbeg, mend in match_intervals:
                # If only_within is True,
                # match must be within current interval
            if only_within and not (beg <= mbeg and mend <= end):
                continue

            # If allow_same_interval is True, allow same interval as original
            if allow_same_interval and (beg, end) == (mbeg, mend):
                new_interval = Interval(mbeg, mend)
                break

            # If match is valid, i.e. overlaps
            # or is beyond current interval in right direction
            # or is empty interval adjacent to current interval in right direction
            if (not reverse and mend > beg
                    or reverse and mbeg < end):
                if selectmode == 'Extend':
                    new_interval = Interval(min(beg, mbeg), max(end, mend))
                elif selectmode == 'Reduce':
                    if reverse:
                        mend = max(end, mend)
                    else:
                        mbeg = min(beg, mbeg)
                    new_interval = interval - Interval(mbeg, mend)
                else:
                    new_interval = Interval(mbeg, mend)

                if new_interval and new_interval != interval:
                    break

        # If no suitable result for this interval, return original selection
        if not new_interval:
            return selection

        newselection.add(new_interval)
    return newselection

selectindent = partial(select_local_pattern, r'(?m)^([ \t]*)', reverse=True, group=1,
                       allow_same_interval=True)
commands.selectindent = selectindent


def patternpair(pattern, **kwargs):
    """
    Return two local pattern selectors for given pattern,
    one matching forward and one matching backward.
    """
    return (partial(select_local_pattern, pattern, **kwargs),
            partial(select_local_pattern, pattern, reverse=True, **kwargs))

nextchar, previouschar = patternpair(r'(?s).')
commands.nextchar = nextchar
commands.previouschar = previouschar
nextword, previousword = patternpair(r'\b\w+\b')
commands.nextword = nextword
commands.previousword = previousword
nextclass, previousclass = patternpair(r'\w+|[ \t]+|[^\w \t\n]+')
commands.nextclass = nextclass
commands.previousclass = previousclass
nextline, previousline = patternpair(r'(?m)^[ \t]*([^\n]*)', group=1)
commands.nextline = nextline
commands.previousline = previousline
nextfullline, previousfullline = patternpair(r'[^\n]*\n?')
commands.nextfullline = nextfullline
commands.previousfullline = previousfullline
nextparagraph, previousparagraph = patternpair(r'(?s)((?:[^\n][\n]?)+)')
commands.nextparagraph = nextparagraph
commands.previousparagraph = previousparagraph
nextwhitespace, previouswhitespace = patternpair(r'\s')
commands.nextwhitespace = nextwhitespace
commands.previouswhitespace = previouswhitespace


def lock(document):
    """Lock current selection."""
    if document.locked_selection == None:
        document.locked_selection = Selection()
    document.locked_selection += document.selection
    assert not document.locked_selection.isempty
commands.lock = lock


def unlock(document):
    """Remove current selection from locked selection."""
    locked = document.locked_selection
    if locked != None:
        nselection = locked - document.selection
        if not nselection.isempty:
            document.locked_selection = nselection
commands.unlock = unlock


def release(document):
    """Release locked selection."""
    if document.locked_selection != None:
        # The text length may be changed after the locked selection was first created
        # So we must bound it to the current text length
        newselection = document.locked_selection.bound(0, len(document.text))
        if not newselection.isempty:
            document.selection = newselection
        document.locked_selection = None
commands.release = release
