from logging import debug
from ..selection import Selection, Interval
from .. import commands
from . import SelectModes, normalselectmode
from .decorators import selector, intervalselector, intervalselector_withmode
from .selectpattern import selectfullline, selectnextfullline, selectpreviousfullline

def escape(doc):
    if doc.selectmode != SelectModes.normal:
        normalselectmode(doc)
    else:
        commands.empty(doc)
commands.escape = escape


def selectall(doc, selection, selectmode=None):
    """Select the entire text."""
    return Selection(Interval(0, len(doc.text)))
commands.selectall = selector(selectall)


def select_single_interval(doc, selection, selectmode=None):
    """Reduce the selection to the single uppermost interval."""
    return Selection(selection[0])
commands.select_single_interval = selector(select_single_interval)


def empty(doc, selection, selectmode=None):
    """Reduce the selection to a single uppermost empty interval."""
    beg = selection[0][0]
    return Selection(Interval(beg, beg))
commands.empty = selector(empty)


def join(doc, selection, selectmode=None):
    """Join all intervals together."""
    return Selection(Interval(selection[0][0], selection[-1][1]))
commands.join = selector(join)


def complement(doc, selection, selectmode=None):
    """Return the complement."""
    return Selection(selection.complement(doc))
commands.complement = selector(complement)


def emptybefore(doc, interval, selectmode=None):
    """Return the empty interval before each interval."""
    beg, _ = interval
    return Interval(beg, beg)
commands.emptybefore = intervalselector(emptybefore)


def emptyafter(doc, interval, selectmode=None):
    """Return the empty interval after each interval."""
    _, end = interval
    return Interval(end, end)
commands.emptyafter = intervalselector(emptyafter)


def movedown(doc, interval, reverse=False):
    """Move each interval one line down. Preserve fully selected lines."""
    beg, end = interval
    if end - beg > 0:
        currentline = selectfullline(doc, Interval(end - 1, end))
    else:
        currentline = selectfullline(doc, Interval(end, end))

    if not reverse:
        nextline = selectnextfullline(doc, currentline)
    else:
        nextline = selectpreviousfullline(doc, currentline)

    if nextline == None:
        return

    # Crop interval to fit in current line
    cbeg, cend = Interval(max(currentline[0], beg), min(currentline[1], end))

    # Embed interval in next line
    if nextline[1] == len(doc.text):
        # Exceptional case for the last line which has no eol character
        nbeg = min(nextline[0] + cbeg - currentline[0], nextline[1])
        nend = min(nextline[0] + cend - currentline[0], nextline[1])
    else:
        nbeg = min(nextline[0] + cbeg - currentline[0], nextline[1] - 1)
        nend = min(nextline[0] + cend - currentline[0], nextline[1] - 1)
    assert 0 <= nbeg <= nend

    # Preserve selected eol
    if end == currentline[1]:
        nend = nextline[1]
        nbeg = min(nbeg, nextline[1] - 1)

    return Interval(nbeg, nend)
commands.movedown = intervalselector_withmode(movedown)


def moveup(doc, interval):
    """Move each interval one line up. Preserve fully selected lines."""
    return movedown(doc, interval, reverse=True)
commands.moveup = intervalselector_withmode(moveup)


