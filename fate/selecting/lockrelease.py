from ..selection import Selection
from .. import commands

def lock(doc):
    """Lock current selection."""
    if doc.locked_selection == None:
        doc.locked_selection = Selection()
    doc.locked_selection += doc.selection
    assert not doc.locked_selection.isempty
commands.lock = lock


def unlock(doc):
    """Remove current selection from locked selection."""
    locked = doc.locked_selection
    if locked != None:
        nselection = locked - doc.selection
        if not nselection.isempty:
            doc.locked_selection = nselection
commands.unlock = unlock


def release(doc):
    """Release locked selection."""
    if doc.locked_selection != None:
        # The text length may be changed after the locked selection was first created
        # So we must bound it to the current text length
        newselection = doc.locked_selection.bound(0, len(doc.text))
        if not newselection.isempty:
            doc.selection = newselection
        doc.locked_selection = None
commands.release = release
