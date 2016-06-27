from logging import debug, error
from ..selection import Selection, Interval
from .. import commands
from ..commandtools import compose
from . import SelectModes, normalselectmode
from .decorators import selector, intervalselector, intervalselector_withmode
from .selectpattern import selectfullline, selectnextfullline, selectpreviousfullline

def escape(doc):
    if doc.selectmode != SelectModes.normal:
        normalselectmode(doc)
    elif [interval for interval in doc.selection if not interval.isempty]:
        # If selection contains non empty intervals
        commands.emptybefore(doc)
    else:
        commands.empty(doc)
commands.escape = escape


def get_line_position(text, linenumber):
    """
    :linenumber: count from zero
    :return: position right after last new line character of the line before linenumber
    """
    currentline = 0
    pos_after_last_newline = 0
    while currentline < linenumber:
        try:
            pos_after_last_newline = text.index('\n', pos_after_last_newline) + 1
            currentline += 1
        except ValueError:
            break
    return pos_after_last_newline

def ask_linenumber(doc):
    doc.modes.prompt.promptstring = '/'
    return doc.modes.prompt

def selectline(doc):
    try:
        linenumber = int(doc.modes.prompt.inputstring)
    except ValueError as e:
        error(str(e))
        doc.ui.notify(str(e))
        return

    line_beg = get_line_position(doc.text, linenumber)
    Selection([Interval(line_beg, line_beg)])(doc)
    commands.selectfullline(doc)
commands.selectline = compose(ask_linenumber, selectline)



def selectall(text, selection, selectmode=None):
    """Select the entire text."""
    return Selection(Interval(0, len(text)))
commands.selectall = selector(selectall)


def select_single_interval(text, selection, selectmode=None):
    """Reduce the selection to the single uppermost interval."""
    return Selection(selection[0])
commands.select_single_interval = selector(select_single_interval)


def empty(text, selection, selectmode=None):
    """Reduce the selection to a single uppermost empty interval."""
    beg = selection[0][0]
    return Selection(Interval(beg, beg))
commands.empty = selector(empty)


def join(text, selection, selectmode=None):
    """Join all intervals together."""
    return Selection(Interval(selection[0][0], selection[-1][1]))
commands.join = selector(join)


def complement(text, selection, selectmode=None):
    """Return the complement."""
    return Selection(selection.complement(text))
commands.complement = selector(complement)


def emptybefore(text, interval, selectmode=None):
    """Return the empty interval before each interval."""
    beg, _ = interval
    return Interval(beg, beg)
commands.emptybefore = intervalselector(emptybefore)


def emptyafter(text, interval, selectmode=None):
    """Return the empty interval after each interval."""
    _, end = interval
    return Interval(end, end)
commands.emptyafter = intervalselector(emptyafter)


def movedown(text, interval, reverse=False):
    """Move each interval one line down. Preserve fully selected lines."""
    beg, end = interval
    if end - beg > 0:
        currentline = selectfullline(text, Interval(end - 1, end))
    else:
        currentline = selectfullline(text, Interval(end, end))

    if not reverse:
        nextline = selectnextfullline(text, currentline)
    else:
        nextline = selectpreviousfullline(text, currentline)

    if nextline == None:
        return

    # Crop interval to fit in current line
    cbeg, cend = Interval(max(currentline[0], beg), min(currentline[1], end))

    # Embed interval in next line
    if nextline[1] == len(text):
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


def moveup(text, interval):
    """Move each interval one line up. Preserve fully selected lines."""
    return movedown(text, interval, reverse=True)
commands.moveup = intervalselector_withmode(moveup)


