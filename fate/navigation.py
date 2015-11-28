"""
This module contains functionality for navigation/browsing through text without selecting.
"""
from . import commands
from logging import debug
from functools import partial


def movepage(doc, backward=False):
    """Constructor function for page up/down commands."""
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    if backward:
        new_offset = move_n_wrapped_lines_up(doc.text, width, offset, height)
    else:
        new_offset = move_n_wrapped_lines_down(doc.text, width, offset, height)
    debug('old: {}, new: {}'.format(offset, new_offset))
    doc.ui.viewport_offset = new_offset
commands.pagedown = movepage
commands.pageup = partial(movepage, backward=True)


def center_around_selection(doc):
    """Center offset around last interval of selection."""
    width, height = doc.ui.viewport_size
    doc.ui.viewport_offset = move_n_wrapped_lines_up(doc.text, width,
                                                     doc.selection[-1][1],
                                                     int(height / 2))


def move_n_wrapped_lines_up(text, max_line_width, start, n):
    """Return position that is n lines above start."""
    position = text.rfind('\n', 0, start)
    if position <= 0:
        return 0
    while 1:
        previousline = text.rfind('\n', 0, position - 1)
        if previousline <= 0:
            return 0
        n -= int((position - previousline) / max_line_width) + 1
        if n <= 0:
            return position + 1
        position = previousline


def move_n_wrapped_lines_down(text, max_line_width, start, n):
    """Return position that is n lines below start."""
    position = text.find('\n', start)
    l = len(text) - 1
    if position == -1 or position == l:
        return l
    while 1:
        eol = text.find('\n', position)
        if eol == -1 or eol == l:
            return l
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
