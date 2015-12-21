"""
This module contains functionality for navigation/browsing through text without selecting.

Variable name meanings:
eol: end-of-line
bol: beginning-of-line
eowl: end-of-wrapped-line (last character in the wrapped line)
bowl: beginning-of-wrapped-line
eof: end-of-file
bof: beginning-of-file
"""
from . import commands
from logging import debug

from .contract import pre, post


def movehalfpagedown(doc):
    """Move half a page down."""
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_down(doc.text, width, offset, height // 2)
    doc.ui.viewport_offset = new_offset
commands.movehalfpagedown = movehalfpagedown


def movehalfpageup(doc):
    """Move half a page down."""
    width, height = doc.ui.viewport_size
    offset = doc.ui.viewport_offset
    new_offset = move_n_wrapped_lines_up(doc.text, width, offset, height // 2)
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


def is_position_visible(doc, pos):
    """Determince whether position is visible on screen."""
    beg = doc.ui.viewport_offset
    width, height = doc.ui.viewport_size
    end = move_n_wrapped_lines_down(doc.text, width, beg, height)
    return beg <= pos < end


def center_around_selection(doc):
    """Center offset around last interval of selection."""
    width, height = doc.ui.viewport_size
    debug('Viewport height: {}, {}'.format(height, doc.selection[-1][1]))

    end = max(0, min(doc.selection[-1][1], len(doc.text) - 1))
    target = height // 2

    nr_lines = move_n_wrapped_lines_up(doc.text, width, end, target)
    doc.ui.viewport_offset = nr_lines


#
# line translation functionality
#


def count_newlines(text, interval):
    beg, end = interval
    return text.count('\n', beg, end)


def beg_of_wrapped_line(text, max_line_width, pos):
    previous_eol = text.rfind('\n', 0, pos)
    bol = previous_eol + 1
    nr_wrapped_lines_before = (pos - bol) // max_line_width
    bowl = bol + nr_wrapped_lines_before * max_line_width
    assert count_newlines(text, (bol, bowl)) == 0
    return bowl


def move_n_wrapped_lines_up_pre(text, max_line_width, start, n):
    print(max_line_width, start, n)
    assert max_line_width > 0
    assert 0 <= start < len(text)
    assert n >= 0


def move_n_wrapped_lines_up_post(result, text, max_line_width, start, n):
    print(result)
    assert start - result <= n * max_line_width + max_line_width
    assert count_newlines(text, (result, start)) <= n
    assert 0 <= result <= len(text)


@pre(move_n_wrapped_lines_up_pre)
@post(move_n_wrapped_lines_up_post)
def move_n_wrapped_lines_up(text: str, max_line_width: int, start: int, n: int):
    """
    Return the first position in the line which ends with the nth
    wrapped end-of-line counting back from start (exclusive).

    In other words, return position right after the (n+1)th wrapped end-of-line,
    counting back from position start (exclusive).
    If there are less than n+1 wrapped end-of-lines before start, return 0.

    The reason that we do not return the position of the wrapped end-of-line itself,
    is because the virtual eols that emerge from the wrapping do not correspond to
    a character in the text and thus do not have a position.

    W.r.t. the max_line_width we count an eol as a character belonging to the line it
    ends.

    Raises AssertionException if preconditions do not hold.
    Should not raise other exceptions.
    """
    # We want to start a the beginning of the current wrapped line start is in
    bowl = beg_of_wrapped_line(text, max_line_width, start)

    # Now we can really start
    current_bowl = bowl
    while n > 0:
        if current_bowl == 0:
            return 0
        previous_eowl = current_bowl - 1
        previous_bol = text.rfind('\n', 0, previous_eowl) + 1

        remaining_line_length = current_bowl - previous_bol
        if remaining_line_length > max_line_width:
            previous_bowl = max_line_width
        else:
            assert text[previous_eowl] == '\n'
            previous_bowl = previous_eowl

        # Move on
        n -= 1
        current_bowl = previous_bowl

    return current_bowl


def move_n_wrapped_lines_down_pre(text, max_line_width, start, n):
    print(max_line_width, start, n)
    assert max_line_width > 0
    assert 0 <= start < len(text)
    assert n >= 0


def move_n_wrapped_lines_down_post(result, text, max_line_width, start, n):
    print(result)
    assert result - start <= n * max_line_width
    assert count_newlines(text, (start, result)) <= n
    assert 0 <= result <= len(text)


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

    W.r.t. the max_line_width we count an eol as a character belonging to the line it
    ends.

    Raises AssertionException if preconditions do not hold.
    Should not raise other exceptions.
    """
    # We want to start a the beginning of the current wrapped line start is in
    bowl = beg_of_wrapped_line(text, max_line_width, start)

    # Now we can really start
    current_bowl = bowl
    eof = len(text)
    while n > 0:
        current_eol = text.find('\n', current_bowl)
        if current_eol == -1 or current_eol == eof - 1:
            return eof

        remaining_line_length = current_eol - current_bowl + 1 # eol inclusive
        if remaining_line_length > max_line_width:
            current_eowl = current_bowl + max_line_width - 1 # Don't count bowl twice
        else:
            current_eowl = current_eol

        # Move on
        n -= 1
        # It does not matter if current_bowl is possibly at eof
        # As return value this is just fine, and the next iteration can deal with it
        current_bowl = current_eowl + 1

    return current_bowl


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
