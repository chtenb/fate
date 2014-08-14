"""This module provides a repeat mechanism for user input."""
from .document import Document
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


def init(document):
    document.OnUserInput.add(record_input)
    document.repeat_data = RepeatData()

Document.OnDocumentInit.add(init)


def record_input(document, char):
    data = document.repeat_data
    if data.recording_level > 0:
        data.current_user_input.append(char)


def start_recording(document):
    data = document.repeat_data
    data.recording_level += 1


def stop_recording(document):
    data = document.repeat_data
    data.recording_level -= 1
    if data.recording_level < 0:
        raise Exception('input_recording_level must not be < 0')

    if data.recording_level == 0:
        data.last_user_input = data.current_user_input
        data.last_action = data.current_action
        data.current_user_input = []
        data.current_action = None


def repeat(document):
    data = document.repeat_data
    if data.last_action:
        document.feed_input(data.last_user_input)
        data.last_action(document)
actions.repeat = repeat


def repeatable(action):
    """Action decorator which stores action in last_action field in document."""
    @wraps(action)
    def wrapper(document):
        document.repeat_data.current_action = action
        start_recording(document)
        result = action(document)
        stop_recording(document)
        return result
    return wrapper
