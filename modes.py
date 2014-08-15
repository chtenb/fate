"""This module contains constants for the selection modes, and functions to switch modes.
The current constants are `SELECT_MODE`, `EXTEND_MODE` and `REDUCE_MODE`. """
SELECT, EXTEND, REDUCE = 'SELECT', 'EXTEND', 'REDUCE'
from . import commands


def reduce_mode(document):
    """Switch to reduce mode."""
    document.mode = REDUCE
commands.reduce_mode = reduce_mode


def extend_mode(document):
    """Switch to extend mode."""
    document.mode = EXTEND
commands.extend_mode = extend_mode


def select_mode(document):
    """Switch to select mode."""
    document.mode = SELECT
commands.select_mode = select_mode

