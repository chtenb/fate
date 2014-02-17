"""Actors are functions that act on a session.
Sequences of actors are again an actor via the actor decorator."""
from .selectors import (next_full_line, previous_full_line, empty,
                        previous_char, next_char, empty_after,
                        empty_before, local_pattern_selector)
from .operators import change_after, change_before, delete
from .clipboard import copy, paste_before, clear
from .action import compose
from . import modes


def escape(session):
    """Escape"""
    if session.selection_mode != modes.SELECT_MODE:
        modes.select_mode(session)
    else:
        empty(session)


def undo(session):
    """Undo last action."""
    session.actiontree.undo()


def redo(session):
    """Redo last undo."""
    session.actiontree.redo()

select_indent = local_pattern_selector(r'(?m)^([ \t]*)[^ \t]',
                                       reverse=True, group=1, only_within=True)

open_line_after = compose(modes.select_mode, previous_full_line,
                          select_indent, copy,
                          next_full_line, change_after('\n', 0),
                          previous_char, empty_before, paste_before,
                          clear)
open_line_after.__docs__ = """Open a line after interval."""

open_line_before = compose(modes.select_mode, next_full_line,
                           select_indent, copy,
                           next_full_line, change_before('\n', 0),
                           next_char, empty_before, paste_before,
                           clear)
open_line_before.__docs__ = """Open a line before interval."""

cut = compose(copy, delete)
