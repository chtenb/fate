from ..session import Session
from ..event import Event
from .. import filetype_system
from .labeling import Labeling
from importlib import import_module
import logging

Session.OnGenerateLabeling = Event()
Session.labeling = Labeling()


def load_filetype_syntax(session):
    """If we have a filetype, try to import the corresponding labeling module."""
    if session.filetype:
        try:
            import_module(__name__ + '.' + session.filetype)
        except ImportError:
            logging.info('No labeling script found for filetype ' + session.filetype)


def generate_labeling(session, *args):
    """Create the labeling."""
    session.labeling = Labeling()
    session.OnGenerateLabeling.fire(session)

Session.OnSessionInit.add(load_filetype_syntax)
Session.OnTextChanged.add(generate_labeling)
Session.OnRead.add(generate_labeling)

logging.info('labeling system loaded')
