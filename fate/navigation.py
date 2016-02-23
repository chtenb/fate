"""
This module contains functionality for navigation/browsing through text without selecting.

Variable name meanings:
bol: beginning-of-line
bowl: beginning-of-wrapped-line (first character in the wrapped line)
bof: beginning-of-file, i.e. 0

eolchar: (position of) end-of-line character, e.g. '\\n'
eowlchar: last character in the wrapped line
eofchar: last character in the file

eol: eolchar + 1
eowl: eowlchar + 1
eof: eofchar + 1

It is important to note that a line ending is always counted in the line it ends.
Newline character are thought of as end-of-line characters.

REFACTORING:
    We only work with bols and bowls.
    These are always existent, also in empty texts.
    TODO:
        - Rename everything.
        - Write something about slicing space and indexing space.
            - We work mostly with slicing space.
            - TODO: have different naming for indexing variables.

"""
from math import ceil
from logging import debug
from . import commands

from .contract import pre, post


def movehalfpagedown(doc):
    """Move half a page down."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    offset = min(len(doc.text), doc.ui.viewport_offset)
    new_offset = move_n_wrapped_lines_down(doc.text, width, offset, height // 2)
    doc.ui.viewport_offset = new_offset
commands.movehalfpagedown = movehalfpagedown


def movehalfpageup(doc):
    """Move half a page down."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    offset = min(len(doc.text), doc.ui.viewport_offset)
    new_offset = move_n_wrapped_lines_up(doc.text, width, offset, height // 2)
    doc.ui.viewport_offset = new_offset
commands.movehalfpageup = movehalfpageup


def movepagedown(doc):
    """Move a page down."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    offset = min(len(doc.text), doc.ui.viewport_offset)
    new_offset = move_n_wrapped_lines_down(doc.text, width, offset, height)
    doc.ui.viewport_offset = new_offset
commands.movepagedown = movepagedown


def movepageup(doc):
    """Move a page up."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    offset = min(len(doc.text), doc.ui.viewport_offset)
    new_offset = move_n_wrapped_lines_up(doc.text, width, offset, height)
    doc.ui.viewport_offset = new_offset
commands.movepageup = movepageup


def is_position_visible(doc, pos):
    """
    Determine whether position is visible on screen.
    Uses doc.ui.viewport properties and doc.view to determine answer.
    """
    return NotImplemented


def center_around_selection(doc):
    """Center offset around last interval of selection."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    pos = doc.selection[-1][1]
    center = max(0, min(pos, len(doc.text) - 1))
    debug('Viewport height: {}, center: {}'.format(height, center))

    offset = move_n_wrapped_lines_up(doc.text, width, center, height // 2)
    doc.ui.viewport_offset = offset


#
# line translation functionality
#


def count_wrapped_lines(text, max_width, interval=None):
    if interval:
        beg, end = interval
        text = text[beg:end]
    return sum(ceil(max(1, len(line)) / max_width) for line in text.splitlines())


def count_newlines(text, interval):
    beg, end = interval
    return text.count('\n', beg, end)


def beg_of_wrapped_line(text, max_width, pos):
    """
    Return the beginning of the wrapped line that pos is in.
    """
    previous_eol = text.rfind('\n', 0, pos)
    bol = previous_eol + 1
    nr_wrapped_lines_before = (pos - bol) // max_width
    bowl = bol + nr_wrapped_lines_before * max_width

    assert count_newlines(text, (bol, bowl)) == 0
    assert 0 <= bowl <= len(text), '0 <= {} <= {}'.format(bowl, len(text))
    return bowl


def move_n_wrapped_lines_up_pre(text, max_width, start, n):
    assert max_width > 0, '{} > 0'.format(max_width)
    assert 0 <= start <= len(text), '0 <= {} <= {}'.format(start, len(text))
    assert n >= 0, '{} >= 0'.format(n)


def move_n_wrapped_lines_up_post(result, text, max_width, start, n):
    assert start - result <= n * max_width + max_width
    assert count_newlines(text, (result, start)) <= n
    assert count_wrapped_lines(text, max_width, (result, start)) <= n + 1
    assert 0 <= result <= len(text)


@pre(move_n_wrapped_lines_up_pre)
@post(move_n_wrapped_lines_up_post)
def move_n_wrapped_lines_up(text: str, max_width: int, start: int, n: int):
    """
    Return the first position in the line which ends with the nth
    wrapped end-of-line counting back from start (exclusive).

    In other words, return position right after the (n+1)th wrapped end-of-line,
    counting back from position start (exclusive).
    If there are less than n+1 wrapped end-of-lines before start, return 0.

    The reason that we do not return the position of the wrapped end-of-line itself,
    is because the virtual end-of-lines that emerge from the wrapping do not correspond to
    a character in the text and thus do not have a position.

    W.r.t. the max_width we count an eol as a character belonging to the line it
    ends.

    Raises AssertionException if preconditions do not hold.
    Should not raise other exceptions.
    """
    # We want to start a the beginning of the current wrapped line that start is in
    bowl = beg_of_wrapped_line(text, max_width, start)
    while n > 0 and bowl > 0:
        bowl = beg_of_wrapped_line(text, max_width, bowl - 1)
        n -= 1

    return bowl

def next_beg_of_wrapped_line(text, max_width, pos):
    """
    Return the beginning of the next wrapped line.
    If none exists, return the beginning of the current wrapped line.
    """
    current_bowl = beg_of_wrapped_line(text, max_width, pos)
    eol = text.find('\n', pos)
    if eol == -1:
        remaining_line_length = len(text) - current_bowl
        if remaining_line_length >= max_width:
            result = current_bowl + max_width
        else:
            result = current_bowl
    else:
        remaining_line_length = eol - current_bowl # eol inclusive
        if remaining_line_length >= max_width:
            result = current_bowl + max_width
        else:
            result = eol + 1

    assert 0 <= result <= len(text), '0 <= {} <= {}'.format(result, len(text))
    return result

def move_n_wrapped_lines_down_pre(text, max_width, start, n):
    assert max_width > 0
    assert 0 <= start <= len(text)
    assert n >= 0


def move_n_wrapped_lines_down_post(result, text, max_width, start, n):
    assert result - start <= n * max_width + 1
    assert count_newlines(text, (start, result)) <= n
    assert count_wrapped_lines(text, max_width, (start, result)) <= n + 1
    assert 0 <= result <= len(text), '0 <= {} <= {}'.format(result, len(text))


@pre(move_n_wrapped_lines_down_pre)
@post(move_n_wrapped_lines_down_post)
def move_n_wrapped_lines_down(text: str, max_width: int, start: int, n: int):
    """
    Return position right after the nth wrapped end-of-line,
    i.e. the first position of the (n+1)th wrapped line,
    counting from position start (inclusive).
    If there are less than n wrapped end-of-lines after start,
    or there are no characters after the nth end-of-line,
    return the first position of the last wrapped lined.

    The reason that we do not return the position of the wrapped end-of-line itself,
    is because the virtual end-of-lines that emerge from the wrapping do not correspond to
    a character in the text and thus do not have a position.

    W.r.t. the max_width we count an eol as a character belonging to the line it
    ends.

    Raises AssertionException if preconditions do not hold.
    Should not raise other exceptions.
    """
    # We want to start at the beginning of the current wrapped line that start is in
    eowl = beg_of_wrapped_line(text, max_width, start)
    eof = len(text)
    while n > 0 and eowl < eof:
        eowl = next_beg_of_wrapped_line(text, max_width, eowl)
        n -= 1

    return eowl


def coord_to_position(line, column, text, crop=False):
    pos = 0
    while line > 1:  # line numbers start with 1
        eol = text.find('\n', pos)
        if eol == -1:
            if crop:
                return len(text) - 1
            raise ValueError('Line number reaches beyond text.')

        pos = eol + 1
        line -= 1

    pos += column - 1  # column numbers start with 1
    if pos >= len(text) and not crop:
        raise ValueError('Column number reaches beyond text.')
    pos = min(pos, len(text) - 1)

    #assert (line, column) == position_to_coord(pos, text)
    return pos


def position_to_coord(pos, text):
    if pos >= len(text):
        raise ValueError('Position reaches beyond text.')

    i = 0  # First character of current line
    line = 1  # Line numbers start with 1
    while i < pos:
        eol = text.find('\n', i)
        if eol >= pos:
            break
        else:
            line += 1
            i = eol + 1
    column = pos - i + 1  # Column numbers start with 1

    assert pos == coord_to_position(line, column, text)
    return line, column
