"""
This module contains functionality for navigation/browsing through text without selecting.

Variable name meanings:
eol: end-of-line
bol: beginning-of-line
eowl: end-of-wrapped-line (last character in the wrapped line)
bowl: beginning-of-wrapped-line (first character in the wrapped line)
eof: end-of-file (last character in the file)
bof: beginning-of-file, i.e. 0

It is important to note that a line ending is always counted in the line it ends.
"""
from . import commands
from logging import debug

from .contract import pre, post


def movehalfpagedown(doc):
    """Move half a page down."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_down(doc.text, width, offset, height // 2)
    doc.ui.viewport_offset = new_offset
commands.movehalfpagedown = movehalfpagedown


def movehalfpageup(doc):
    """Move half a page down."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_up(doc.text, width, offset, height // 2)
    doc.ui.viewport_offset = new_offset
commands.movehalfpageup = movehalfpageup


def movepagedown(doc):
    """Move a page down."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_down(doc.text, width, offset, height)
    doc.ui.viewport_offset = new_offset
commands.movepagedown = movepagedown


def movepageup(doc):
    """Move a page up."""
    # TODO: this doesn't count with viewtext
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
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


def count_newlines(text, interval):
    beg, end = interval
    return text.count('\n', beg, end)


def beg_of_wrapped_line(text, wrapped_line_length, pos):
    """
    Return the beginning of the wrapped line that pos is in.
    """
    previous_eol = text.rfind('\n', 0, pos)
    bol = previous_eol + 1
    nr_wrapped_lines_before = (pos - bol) // wrapped_line_length
    bowl = bol + nr_wrapped_lines_before * wrapped_line_length
    assert count_newlines(text, (bol, bowl)) == 0
    return bowl


def move_n_wrapped_lines_up_pre(text, wrapped_line_length, start, n):
    assert wrapped_line_length > 0
    assert 0 <= start < len(text)
    assert n >= 0


def move_n_wrapped_lines_up_post(result, text, wrapped_line_length, start, n):
    assert start - result <= n * wrapped_line_length + wrapped_line_length
    assert count_newlines(text, (result, start)) <= n
    assert 0 <= result <= len(text)


@pre(move_n_wrapped_lines_up_pre)
@post(move_n_wrapped_lines_up_post)
def move_n_wrapped_lines_up(text: str, wrapped_line_length: int, start: int, n: int):
    """
    Return the first position in the line which ends with the nth
    wrapped end-of-line counting back from start (exclusive).

    In other words, return position right after the (n+1)th wrapped end-of-line,
    counting back from position start (exclusive).
    If there are less than n+1 wrapped end-of-lines before start, return 0.

    The reason that we do not return the position of the wrapped end-of-line itself,
    is because the virtual end-of-lines that emerge from the wrapping do not correspond to
    a character in the text and thus do not have a position.

    W.r.t. the wrapped_line_length we count an eol as a character belonging to the line it
    ends.

    Raises AssertionException if preconditions do not hold.
    Should not raise other exceptions.
    """
    # We want to start a the beginning of the current wrapped line that start is in
    bowl = beg_of_wrapped_line(text, wrapped_line_length, start)
    while n > 0 and bowl > 0:
        bowl = beg_of_wrapped_line(text, wrapped_line_length, bowl - 1)
        n -= 1

    return bowl

def end_of_wrapped_line(text, wrapped_line_length, pos):
    """
    Return the end of the wrapped line that pos is in.
    An eol is counted in the line it ends, so if pos is an eol, the eol is returned.
    """
    bowl = beg_of_wrapped_line(text, wrapped_line_length, pos)
    eol = text.find('\n', pos)
    if eol == -1:
        eol = len(text) - 1

    remaining_line_length = eol - bowl + 1 # eol inclusive
    if remaining_line_length > wrapped_line_length:
        return bowl + wrapped_line_length - 1 # Don't count bowl twice
    else:
        return eol

def move_n_wrapped_lines_down_pre(text, wrapped_line_length, start, n):
    assert wrapped_line_length > 0
    assert 0 <= start < len(text)
    assert n >= 0


def move_n_wrapped_lines_down_post(result, text, wrapped_line_length, start, n):
    assert result - start <= n * wrapped_line_length
    assert count_newlines(text, (start, result)) <= n
    assert 0 <= result <= len(text)


@pre(move_n_wrapped_lines_down_pre)
@post(move_n_wrapped_lines_down_post)
def move_n_wrapped_lines_down(text: str, wrapped_line_length: int, start: int, n: int):
    """
    Return position right after the nth wrapped end-of-line,
    counting from position start (inclusive).
    If there are less than n wrapped end-of-lines after start,
    or there are no characters after the nth end-of-line,
    return the first position of the last wrapped lined.

    The reason that we do not return the position of the wrapped end-of-line itself,
    is because the virtual end-of-lines that emerge from the wrapping do not correspond to
    a character in the text and thus do not have a position.

    W.r.t. the wrapped_line_length we count an eol as a character belonging to the line it
    ends.

    Raises AssertionException if preconditions do not hold.
    Should not raise other exceptions.
    """
    # We want to start at the end of the current wrapped line that start is in
    eowl = end_of_wrapped_line(text, wrapped_line_length, start)
    eof = len(text) - 1
    while n > 0 and eowl < eof:
        eowl = end_of_wrapped_line(text, wrapped_line_length, eowl + 1)
        n -= 1

    return beg_of_wrapped_line(text, wrapped_line_length, eowl)


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
