from ..session import Session
from ..event import Event
from .. import filetype_system
from .labeling import Labeling
from importlib import import_module
import logging

Session.OnGenerateLabeling = Event()
Session.labeling = Labeling()

def load_filetype_syntax(session):
    if session.filetype:
        try:
            import_module('.labeling_system.' + session.filetype, 'protexted')
        except ImportError:
            logging.info('No labeling script found for filetype ' + session.filetype)

def generate_labeling(session, *args):
    session.labeling = Labeling()
    session.OnGenerateLabeling.fire(session)

Session.OnSessionInit.add(load_filetype_syntax)
Session.OnApplyOperation.add(generate_labeling)
Session.OnRead.add(generate_labeling)

import logging
logging.info('labeling system loaded')
