"""This module provides a repeat mechanism for user input."""
from .document import Document
from . import commands
from functools import wraps


class RepeatData:

    """A container object for all data we need."""

    def __init__(self):
        self.last_user_input = []
        self.last_command = None
        self.current_user_input = []
        self.current_command = None
        self.recording_level = 0


def init(document):
    document.ui.OnUserInput.add(record_input)
    document.ui.repeat_data = RepeatData()

Document.OnDocumentInit.add(init)


def record_input(ui, key):
    data = ui.repeat_data
    if data.recording_level > 0:
        data.current_user_input.append(key)


def start_recording(document):
    data = document.ui.repeat_data
    data.recording_level += 1


def stop_recording(document):
    data = document.ui.repeat_data
    data.recording_level -= 1
    if data.recording_level < 0:
        raise Exception('input_recording_level must not be < 0')

    if data.recording_level == 0:
        data.last_user_input = data.current_user_input
        data.last_command = data.current_command
        data.current_user_input = []
        data.current_command = None


def repeat(document):
    data = document.ui.repeat_data
    if data.last_command:
        document.ui.feedinput(data.last_user_input)
        data.last_command(document)
commands.repeat = repeat


def repeatable(command):
    """Action decorator which stores command in last_command field in document."""
    @wraps(command)
    def wrapper(document):
        document.ui.repeat_data.current_command = command
        start_recording(document)
        result = command(document)
        stop_recording(document)
        return result
    return wrapper
