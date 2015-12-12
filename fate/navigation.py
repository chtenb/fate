"""
This module contains functionality for navigation/browsing through text without selecting.
"""
from . import commands
from logging import debug

from .contract import pre, post


def movehalfpagedown(doc):
    """Move half a page down."""
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_down(doc.text, width, offset, int(height / 2))
    doc.ui.viewport_offset = new_offset
commands.movehalfpagedown = movehalfpagedown


def movehalfpageup(doc):
    """Move half a page down."""
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_up(doc.text, width, offset, int(height / 2))
    doc.ui.viewport_offset = new_offset
commands.movehalfpageup = movehalfpageup


def movepagedown(doc):
    """Move a page down."""
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_down(doc.text, width, offset, height)
    doc.ui.viewport_offset = new_offset
commands.movepagedown = movepagedown


def movepageup(doc):
    """Move a page up."""
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_up(doc.text, width, offset, height)
    doc.ui.viewport_offset = new_offset
commands.movepageup = movepageup


def center_around_selection(doc):
    """Center offset around last interval of selection."""
    width, height = doc.ui.viewport_size
    debug('Viewport height: {}, {}'.format(height, doc.selection[-1][1]))
    nr_lines = move_n_wrapped_lines_up(
        doc.text, width, doc.selection[-1][1], int(height / 2))
    doc.ui.viewport_offset = nr_lines


def count_newlines(text, interval):
    beg, end = interval
    return text.count('\n', beg, end)


def move_n_wrapped_lines_up_pre(text, max_line_width, start, n):
    assert max_line_width > 0
    assert 0 <= start < len(text)
    assert n >= 0

def move_n_wrapped_lines_up_post(result, text, max_line_width, start, n):
    nr_eols = count_newlines(text, (result, start))
    assert nr_eols <= n
    assert result == 0 or nr_eols == n

@pre(move_n_wrapped_lines_up_pre)
@post(move_n_wrapped_lines_up_post)
def move_n_wrapped_lines_up(text, max_line_width, start, n):
    """
    Return the first position in the line which ends with the nth
    wrapped end-of-line counting back from start (exclusive).

    In other words, return position right after the (n+1)th wrapped end-of-line,
    counting back from position start (exclusive).
    If there are less than n+1 wrapped end-of-lines before start, return 0.

    The reason that we do not return the position of the wrapped end-of-line itself,
    is because the virtual eols that emerge from the wrapping do not correspond to
    a character in the text and thus do not have a position.
    """
    position = start
    while 1:
        # Note that for rfind, the end parameter is exclusive
        previousline = text.rfind('\n', 0, position)
        if previousline <= 0:
            return 0
        n -= int((position - previousline) / max_line_width) + 1
        if n <= 0:
            return position + 1
        position = previousline


def move_n_wrapped_lines_down_pre(text, max_line_width, start, n):
    assert max_line_width > 0
    assert 0 <= start < len(text)
    assert n >= 0

def move_n_wrapped_lines_down_post(result, text, max_line_width, start, n):
    nr_eols = count_newlines(text, (start, result))
    assert nr_eols <= n
    assert result == len(text) or nr_eols == n

@pre(move_n_wrapped_lines_down_pre)
@post(move_n_wrapped_lines_down_post)
def move_n_wrapped_lines_down(text: str, max_line_width: int, start: int, n: int):
    """
    Return position right after the nth wrapped end-of-line,
    counting from position start (inclusive).
    If there are less than n wrapped end-of-lines after start,
    return the position of the eof position.
    So if the nth wrapped end-of-line would be the an actual eol and happed to be the last
    character in the file, return the eof position.

    The reason that we do not return the position of the wrapped end-of-line itself,
    is because the virtual eols that emerge from the wrapping do not correspond to
    a character in the text and thus do not have a position.
    """
    position = start
    eof = len(text)
    while 1:
        eol = text.find('\n', position)
        if eol == -1 or eol == eof - 1:
            return eof
        nextline = eol + 1
        n -= int((nextline - position) / max_line_width) + 1
        if n <= 0:
            return position + 1
        position = nextline


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


def is_position_visible(doc, pos):
    """Determince whether position is visible on screen."""
    beg = doc.ui.viewport_offset
    width, height = doc.ui.viewport_size
    end = move_n_wrapped_lines_down(doc.text, width, beg, height)
    return beg <= pos < end
