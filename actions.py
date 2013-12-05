"""Actions are functions that act on a session. Macros are sequences of actions."""
from .selectors import next_full_line, previous_full_line, previous_char, next_char, next_white_space, previous_white_space, empty_after, empty_before, local_pattern_selector
from .operators import change_after, change_before
from .operation import Operation
from . import modes
import re
import logging


def reduce_mode(session):
    session.selection_mode = modes.reduce_mode


def extend_mode(session):
    session.selection_mode = modes.extend_mode


def select_mode(session):
    session.selection_mode = modes.select_mode


def copy(session):
    session.clipboard = session.content(session.selection)


def paste(session, before):
    if session.clipboard:
        content = session.content(session.selection)
        new_content = []
        l = len(session.clipboard)
        for i, interval in enumerate(session.selection):
            if before:
                new_content.append(session.clipboard[i % l] + content[i])
            else:
                new_content.append(content[i] + session.clipboard[i % l])

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

