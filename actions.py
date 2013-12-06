"""Actions are functions that act on a session. Macros are sequences of actions."""
from .selectors import next_full_line, previous_full_line, previous_char, next_char, next_white_space, previous_white_space, empty_after, empty_before, local_pattern_selector, empty
from .operators import change_after, change_before
from .operation import Operation
from . import modes


def reduce_mode(session):
    """Switch to reduce mode."""
    session.selection_mode = modes.REDUCE_MODE


def extend_mode(session):
    """Switch to extend mode."""
    session.selection_mode = modes.EXTEND_MODE


def select_mode(session):
    """Switch to select mode."""
    session.selection_mode = modes.SELECT_MODE


def escape(session):
    """Escape"""
    if session.selection_mode == modes.SELECT_MODE:
        session.apply(select_mode)
    else:
        session.apply(empty)


def copy(session):
    """Copy current selected content to clipboard."""
    session.clipboard = session.content(session.selection)


def paste(session, before):
    """Paste clipboard before or after current selection."""
    if session.clipboard:
        content = session.content(session.selection)
        new_content = []
        clipboard_len = len(session.clipboard)
        for i in range(len(session.selection)):
            if before:
                new_content.append(session.clipboard[i % clipboard_len] + content[i])
            else:
                new_content.append(content[i] + session.clipboard[i % clipboard_len])

        operation = Operation(session.selection)
        operation.new_content = new_content
        operation.apply()


def paste_before(session):
    paste(session, before=True)


def paste_after(session):
    paste(session, before=False)


open_line_after = [select_mode, empty_after, next_full_line,
        local_pattern_selector(r'[ \t]*\b'), copy, next_full_line,
        change_after('\n', 0), previous_char, empty_before, paste_before]

open_line_before = [select_mode, empty_before, next_full_line,
        local_pattern_selector(r'[ \t]*\b'), copy, next_full_line,
        change_before('\n', 0), next_char, empty_before, paste_before]

