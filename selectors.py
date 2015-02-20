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
Because of this, it is a good habit to only decorate the function that is placed in
the commands module, not the function itself.
"""
import re
from functools import partial, wraps

from . import commands
from .selection import Selection, Interval
from logging import debug, info


def escape(document):
    if document.selectmode != '':
        normalselectmode(document)
    else:
        commands.empty(document)
commands.escape = escape


def headselectmode(document):
    document.selectmode = 'head'
commands.headselectmode = headselectmode


def tailselectmode(document):
    document.selectmode = 'tail'
commands.tailselectmode = tailselectmode


def normalselectmode(document):
    document.selectmode = ''
commands.normalselectmode = normalselectmode


def selector(function):
    """Turn given selector in a command that takes a document."""
    @wraps(function)
    def wrapper(document, selection=None, selectmode=None, preview=False):
        selection = selection or document.selection
        selectmode = selectmode or document.selectmode

        # Process according to selectmode
        #if selectmode == 'extend forward':
            #start = Selection([Interval(end, end) for beg, end in selection])
        #elif selectmode == 'extend backward':
            #start = Selection([Interval(beg, beg) for beg, end in selection])
        #else:
            #start = selection

        result = function(document, selection, selectmode='')
        # TODO: XOR/symmetric difference result with original selection?
        # + join result etc..

        if preview:
            return result
        if result != None:
            result(document)
    return wrapper


def selectall(document, selection, selectmode=''):
    """Select the entire text."""
    return Selection(Interval(0, len(document.text)))
commands.selectall = selector(selectall)


def select_single_interval(document, selection, selectmode=''):
    """Reduce the selection to the single uppermost interval."""
    return Selection(selection[0])
commands.select_single_interval = selector(select_single_interval)


def empty(document, selection, selectmode=''):
    """Reduce the selection to a single uppermost empty interval."""
    beg = selection[0][0]
    return Selection(Interval(beg, beg))
commands.empty = selector(empty)


def join(document, selection, selectmode=''):
    """Join all intervals together."""
    return Selection(Interval(selection[0][0], selection[-1][1]))
commands.join = selector(join)


def complement(document, selection, selectmode=''):
    """Return the complement."""
    return Selection(selection.complement(document))
commands.complement = selector(complement)


def intervalselector(function):
    """Turn given intervalselector in a command that takes a document."""
    @wraps(function)
    @selector
    def wrapper(document, selection, selectmode=''):
        new_intervals = []
        for interval in selection:
            new_interval = function(document, interval, selectmode='')
            if new_interval == None:
                return
            new_intervals.append(new_interval)
        return Selection(new_intervals)
    return wrapper


def emptybefore(document, interval, selectmode=''):
    """Return the empty interval before each interval."""
    beg, _ = interval
    return Interval(beg, beg)
commands.emptybefore = intervalselector(emptybefore)


def emptyafter(document, interval, selectmode=''):
    """Return the empty interval after each interval."""
    _, end = interval
    return Interval(end, end)
commands.emptyafter = intervalselector(emptyafter)


def movedown(document, interval, selectmode=''):
    """Move each interval one line down. Preserve fully selected lines."""
    beg, end = interval
    if selectmode == 'tail':
        currentline = selectfullline(document, Interval(beg, beg))
    else:
        currentline = selectfullline(document, Interval(end, end))
    nextline = selectnextfullline(document, currentline)

    if nextline == None:
        return

    # Crop interval to fit in current line
    beg, end = interval = Interval(beg, min(currentline[1], end))

    if currentline == interval:
        # Preserve fully selected lines
        nbeg, nend = nextline
    else:
        # Embed interval in next line
        nbeg = min(nextline[0] + beg - currentline[0], nextline[1] - 1)
        nend = min(nextline[0] + end - currentline[0], nextline[1] - 1)

    if selectmode == 'head' and beg <= nend:
        return Interval(beg, nend)
    elif selectmode == 'tail' and nbeg <= end:
        debug('asdf')
        return Interval(nbeg, end)
    elif selectmode == '':
        return Interval(nbeg, nend)
commands.movedown = intervalselector(movedown)


def moveup(document, interval, selectmode=''):
    """Move each interval one line up. Preserve fully selected lines."""
    beg, end = interval
    currentline = selectfullline(document, interval, selectmode)
    previousline = selectpreviousfullline(document, currentline, selectmode)

    if previousline == None:
        return

    # Crop interval to fit in current line
    beg, end = interval = Interval(beg, min(currentline[1], end))

    # Preserve fully selected lines
    if currentline == interval:
        return previousline

    # Embed interval in previous line
    nbeg = min(previousline[0] + beg - currentline[0], previousline[1] - 1)
    nend = min(previousline[0] + end - currentline[0], previousline[1] - 1)

    if selectmode == 'head' and beg <= nbeg:
        return Interval(beg, nbeg)
    elif selectmode == 'tail' and nbeg <= end:
        return Interval(nbeg, end)
    elif selectmode == '':
        return Interval(nbeg, nend)
commands.moveup = intervalselector(moveup)


def findpattern(text, pattern, reverse=False, group=0):
    """Find intervals that match given pattern."""
    matches = re.finditer(pattern, text)
    if reverse:
        matches = reversed(list(matches))
    return [Interval(match.start(group), match.end(group))
            for match in matches]


def selectpattern(pattern, document, selection, selectmode='', reverse=False, group=0):
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
            if new_selection and selection != new_selection:
                newselection.add(new_selection)
                return newselection

    return newselection


def select_local_pattern(pattern, document, interval, selectmode='', reverse=False,
                         group=0, only_within=False, allow_same_interval=False):

    match_intervals = findpattern(document.text, pattern, reverse, group)

    beg, end = interval
    new_interval = None

    for mbeg, mend in match_intervals:
        # If only_within is True, match must be within current interval
        if only_within and not (beg <= mbeg and mend <= end):
            continue

        # If allow_same_interval is True, allow same interval as original
        if allow_same_interval and (beg, end) == (mbeg, mend):
            return Interval(mbeg, mend)

        if not reverse:
            if selectmode == 'head' and end < mend:
                new_interval = Interval(beg, mend)
            elif selectmode == 'tail' and beg < mend <= end:
                new_interval = Interval(mend, end)
            elif selectmode == '' and beg < mend:
                new_interval = Interval(mbeg, mend)

        if reverse:
            if selectmode == 'head' and beg <= mbeg <= end:
                new_interval = Interval(beg, mbeg)
            elif selectmode == 'tail' and mbeg < beg:
                new_interval = Interval(mbeg, end)
            elif selectmode == '' and mbeg < end:
                new_interval = Interval(mbeg, mend)

        # If suitable interval found, return it
        if new_interval and new_interval != interval:
            return new_interval


selectindent = partial(select_local_pattern, r'(?m)^([ \t]*)', reverse=True, group=1,
                       allow_same_interval=True)
commands.selectindent = intervalselector(selectindent)


selectline = partial(select_local_pattern, r'(?m)^[ \t]*([^\n]*)', group=1,
                     allow_same_interval=True)
commands.selectline = intervalselector(selectline)


selectfullline = partial(select_local_pattern, r'[^\n]*\n?',
                         allow_same_interval=True)
commands.selectfullline = intervalselector(selectfullline)


def patternpair(pattern, **kwargs):
    """
    Return two local pattern selectors for given pattern,
    one matching forward and one matching backward.
    """
    return (partial(select_local_pattern, pattern, **kwargs),
            partial(select_local_pattern, pattern, reverse=True, **kwargs))

selectnextchar, selectpreviouschar = patternpair(r'(?s).')
commands.selectnextchar = intervalselector(selectnextchar)
commands.selectpreviouschar = intervalselector(selectpreviouschar)
selectnextword, selectpreviousword = patternpair(r'\b\w+\b')
commands.selectnextword = intervalselector(selectnextword)
commands.selectpreviousword = intervalselector(selectpreviousword)
selectnextclass, selectpreviousclass = patternpair(r'\w+|[ \t]+|[^\w \t\n]+')
commands.selectnextclass = intervalselector(selectnextclass)
commands.selectpreviousclass = intervalselector(selectpreviousclass)
selectnextline, selectpreviousline = patternpair(r'(?m)^[ \t]*([^\n]*)', group=1)
commands.selectnextline = intervalselector(selectnextline)
commands.selectpreviousline = intervalselector(selectpreviousline)
selectnextfullline, selectpreviousfullline = patternpair(r'[^\n]*\n?')
commands.selectnextfullline = intervalselector(selectnextfullline)
commands.selectpreviousfullline = intervalselector(selectpreviousfullline)
selectnextparagraph, selectpreviousparagraph = patternpair(r'(?s)((?:[^\n][\n]?)+)')
commands.selectnextparagraph = intervalselector(selectnextparagraph)
commands.selectpreviousparagraph = intervalselector(selectpreviousparagraph)
selectnextwhitespace, selectpreviouswhitespace = patternpair(r'\s')
commands.selectnextwhitespace = intervalselector(selectnextwhitespace)
commands.selectpreviouswhitespace = intervalselector(selectpreviouswhitespace)


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
