from . import modes
from . import commands
from .selectors import Empty

def escape(document):
    """Escape"""
    if document.mode != modes.SELECT:
        modes.select_mode(document)
    else:
        return Empty(document)
commands.escape = escape

def command_mode(document):
    document.ui.command_mode()
commands.command_mode = command_mode
