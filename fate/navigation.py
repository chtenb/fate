"""
This module contains functionality for navigation/browsing through text without selecting.
"""
from . import commands
from logging import debug

from covenant import pre, post


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


@post(lambda r, text, max_line_width, start, n:
      count_newlines(text, (r, start)) <= n)
def move_n_wrapped_lines_up(text, max_line_width, start, n):
    """Return position that is n lines above start."""
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


# PATTERN 1

# def condition_gen(pre_func):
    # def wrapper(*args, **kwargs):
        # conditions = pre_func(*args, **kwargs)
        # return all(conditions)
    # return wrapper

# @condition_gen
# def move_n_wrapped_lines_down_pre(text, max_line_width, start, n):
    # yield max_line_width > 0
    # yield 0 <= start < len(text)
    # yield n >= 0

# @condition_gen
# def move_n_wrapped_lines_down_post(r, text, max_line_width, start, n):
    # yield count_newlines(text, (start, r)) <= n
    # yield r == len(text) - 1 or count_newlines(text, (r, start)) == n

# @pre(move_n_wrapped_lines_down_pre)
# @post(move_n_wrapped_lines_down_post)

# PATTERN 2

# def move_n_wrapped_lines_down_pre(text, max_line_width, start, n):
    # conditions = []
    # conditions.append(max_line_width > 0)
    # conditions.append(0 <= start < len(text))
    # conditions.append(n >= 0)
    # return all(conditions)

# def move_n_wrapped_lines_down_post(r, text, max_line_width, start, n):
    # conditions = []
    # conditions.append(count_newlines(text, (start, r)) <= n)
    # conditions.append(r == len(text) - 1 or count_newlines(text, (r, start)) == n)
    # return all(conditions)

# @pre(move_n_wrapped_lines_down_pre)
# @post(move_n_wrapped_lines_down_post)

# PATTERN 3

# @pre(lambda text, max_line_width, start, n:
     # max_line_width > 0)
# @pre(lambda text, max_line_width, start, n:
     # 0 <= start < len(text))
# @pre(lambda text, max_line_width, start, n:
     # n >= 0)
# @post(lambda r, text, max_line_width, start, n:
      # count_newlines(text, (start, r)) <= n)
# @post(lambda r, text, max_line_width, start, n:
      # r == len(text) - 1 or count_newlines(text, (r, start)) == n)

# PATTERN 4

@pre(lambda text, max_line_width, start, n:
     max_line_width > 0
     and 0 <= start < len(text)
     and n >= 0)
@post(lambda r, text, max_line_width, start, n:
      count_newlines(text, (start, r)) <= n
      and r == len(text) - 1 or count_newlines(text, (r, start)) == n)

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
    l = len(text) - 1
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


def is_position_visible(doc, pos):
    """Determince whether position is visible on screen."""
    beg = doc.ui.viewport_offset
    width, height = doc.ui.viewport_size
    end = move_n_wrapped_lines_down(doc.text, width, beg, height)
    return beg <= pos < end
