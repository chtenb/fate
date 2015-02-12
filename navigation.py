"""
This module contains functionality for navigation/browsing through text without selecting.
"""
from . import commands
from logging import info
from functools import partial

def movepage(document, backward=False):
    width, height = document.ui.viewport_size
    offset = document.ui.viewport_offset
    if backward:
        new_offset = move_n_wrapped_lines_up(document.text, width, offset, height)
    else:
        new_offset = move_n_wrapped_lines_down(document.text, width, offset, height)
    info('old: {}, new: {}'.format(offset, new_offset))
    document.ui.viewport_offset = new_offset
commands.pagedown = movepage
commands.pageup = partial(movepage, backward=True)


def center_around_selection(document):
    width, height = document.ui.viewport_size
    document.ui.viewport_offset = move_n_wrapped_lines_up(document.text, width,
                                                          document.selection[0][0],
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

