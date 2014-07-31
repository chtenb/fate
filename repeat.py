"""This module provides a repeat mechanism for user input."""
from .session import Session
from . import actions
from functools import wraps


class RepeatData:

    """A container object for all data we need."""

    def __init__(self):
        self.last_user_input = []
        self.last_action = None
        self.current_user_input = []
        self.current_action = None
        self.recording_level = 0


def init(session):
    session.OnUserInput.add(record_input)
    session.repeat_data = RepeatData()

Session.OnSessionInit.add(init)


def record_input(session, char):
    data = session.repeat_data
    if data.recording_level > 0:
        data.current_user_input.append(char)


def start_recording(session):
    data = session.repeat_data
    data.recording_level += 1


def stop_recording(session):
    data = session.repeat_data
    data.recording_level -= 1
    if data.recording_level < 0:
        raise Exception('input_recording_level must not be < 0')

    if data.recording_level == 0:
        data.last_user_input = data.current_user_input
        data.last_action = data.current_action
        data.current_user_input = []
        data.current_action = None


def repeat(session):
    data = session.repeat_data
    if data.last_action:
        session.feed_input(data.last_user_input)
        data.last_action(session)
actions.repeat = repeat


def repeatable(action):
    """Action decorator which stores action in last_action field in session."""
    @wraps(action)
    def wrapper(session):
        session.repeat_data.current_action = action
        start_recording(session)
        result = action(session)
        stop_recording(session)
        return result
    return wrapper
