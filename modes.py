"""This module contains constants for the selection modes, and functions to switch modes.
The current constants are `SELECT_MODE`, `EXTEND_MODE` and `REDUCE_MODE`. """
SELECT, EXTEND, REDUCE = 'SELECT', 'EXTEND', 'REDUCE'
from . import actions


def reduce_mode(session):
    """Switch to reduce mode."""
    session.mode = REDUCE
actions.reduce_mode = reduce_mode


def extend_mode(session):
    """Switch to extend mode."""
    session.mode = EXTEND
actions.extend_mode = extend_mode


def select_mode(session):
    """Switch to select mode."""
    session.mode = SELECT
actions.select_mode = select_mode

