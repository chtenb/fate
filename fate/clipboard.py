"""
This module contains the class definition for the clipboard and some related commands.

Clipboard related commands (copy, paste) should not be undoable.
Suppose the user notices that he made a major mistake
and wants to undo a bunch of commands.
However, he may still want to keep some intermediate modifications.
Then he should be able to copy several things, go back in history,
and put those modifications where he wants.
For this to work, the clipboard must be usable cross-history.
"""
from .operation import Operation
from . import commands
from .document import Document
from .commandtools import compose
from .operators import delete


class Clipboard:

    """A stackbased clipboard."""
    storage = []

    def push(self, content):
        """Push content on the clipboard stack. Content must be a list of strings."""
        assert isinstance(content, list)
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


def init(document):
    document.clipboard = Clipboard()
Document.OnDocumentInit.add(init)


def copy(document):
    """Copy current selected content to clipboard."""
    document.clipboard.push(document.selection.content(document))
commands.copy = copy


def paste(document, before):
    """
    This is not an actor, but serves as helper function for paste_before and paste_after.
    """
    if document.clipboard:
        old_content = document.selection.content(document)
        clipboard_content = document.clipboard.peek()
        if not clipboard_content:
            return
        new_content = []
        clipboard_len = len(clipboard_content)

        for i, old_interval_content in enumerate(old_content):
            x, y = clipboard_content[i % clipboard_len], old_interval_content
            new_content.append(x + y if before else y + x)

        operation = Operation(document, new_content)
        operation(document)


def paste_before(document):
    """Paste clipboard before current selection."""
    paste(document, before=True)
commands.paste_before = paste_before


def paste_after(document):
    """Paste clipboard after current selection."""
    paste(document, before=False)
commands.paste_after = paste_after


def clear(document):
    """Throw away the value on top of the clipboard stack."""
    document.clipboard.pop()
commands.clear = clear


cut = compose(copy, delete, docs='Copy and delete selected text.')
commands.cut = cut

