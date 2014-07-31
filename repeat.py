from .session import Session
from . import actions
from logging import debug

def init(session):
    session.OnUserInput.add(record_input)
    session.input_recording_level = 0

    session.last_user_input = []
    session.last_repeatable_action = None
    session.current_user_input = []
    session.current_repeatable_action = None

Session.OnSessionInit.add(init)

def record_input(session, char):
    if session.input_recording_level > 0:
        session.current_user_input.append(char)

def start_recording(session):
    session.input_recording_level += 1

def stop_recording(session):
    session.input_recording_level -= 1
    if session.input_recording_level < 0:
        raise Exception('input_recording_level must not be < 0')

    if session.input_recording_level == 0:
        debug(session.current_user_input)
        debug(session.current_repeatable_action)
        session.last_user_input = session.current_user_input
        session.last_repeatable_action = session.current_repeatable_action
        session.current_user_input = []
        session.current_repeatable_action = None

def repeat(session):
    if session.last_repeatable_action:
        session.feed(session.last_user_input)
        session.last_repeatable_action(session)
actions.repeat = repeat

