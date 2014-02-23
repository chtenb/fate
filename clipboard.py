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
    session.clipboard.push(session.content(session.selection))


def paste(session, before):
    """This is not an actor,
    but serves as a helper function for paste_before and paste_after."""
    if session.clipboard:
        old_content = session.content(session.selection)
        clipboard_content = session.clipboard.peek()
        if not clipboard_content:
            return
        new_content = []
        clipboard_len = len(clipboard_content)

        for i, old_interval_content in enumerate(old_content):
            x, y = clipboard_content[i % clipboard_len], old_interval_content
            new_content.append(x + y if before else y + x)

        return Operation(session.selection, new_content)


def paste_before(session):
    """Paste clipboard before current selection."""
    return paste(session, before=True)


def paste_after(session):
    """Paste clipboard after current selection."""
    return paste(session, before=False)

def clear(session):
    """Throw away the value on top of the clipboard stack."""
    session.clipboard.pop()

