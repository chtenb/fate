"""A class definition for the clipboard and some actors."""
from .operation import Operation


class Clipboard:
    """A stackbased clipboard."""
    storage = []

    def push(self, content):
        """Push content on the clipboard stack. Content must be a list of strings."""
        self.storage.append(content)

    def peek(self, offset=0):
        """Return the content with offset relative to the top of the clipboard stack."""
        try:
            return self.storage[-1 - offset]
        except IndexError:
            return

    def pop(self):
        """Return and remove the content on top of the clipboard stack."""
        try:
            return self.storage.pop()
        except IndexError:
            return


def copy(session):
    """Copy current selected content to clipboard."""
    session.clipboard.push(session.selection.content)


def paste(session, before):
    """
    This is not an actor, but serves as helper function for PasteBefore and PasteAfter.
    """
    if session.clipboard:
        old_content = session.selection.content
        clipboard_content = session.clipboard.peek()
        if not clipboard_content:
            return
        new_content = []
        clipboard_len = len(clipboard_content)

        for i, old_interval_content in enumerate(old_content):
            x, y = clipboard_content[i % clipboard_len], old_interval_content
            new_content.append(x + y if before else y + x)

        return new_content


class PasteBefore(Operation):
    """Paste clipboard before current selection."""
    def __init__(self, session):
        Operation.__init__(self, session, paste(session, before=True))

class PasteAfter(Operation):
    """Paste clipboard after current selection."""
    def __init__(self, session):
        Operation.__init__(self, session, paste(session, before=False))


def clear(session):
    """Throw away the value on top of the clipboard stack."""
    session.clipboard.pop()

