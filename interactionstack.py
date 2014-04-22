"""A class definition the interaction stack."""
from .action import Interactive


class InteractionStack:

    """Stack-like datastructure for storing and handling interactive actions."""
    storage = []

    @property
    def isempty(self):
        return len(self.storage) == 0

    def push(self, interaction):
        """Push interaction on the stack."""
        assert isinstance(interaction, Interactive)
        self.storage.append(interaction)

    def peek(self, offset=0):
        """
        Return the interactoin with offset relative to the top of the stack.
        """
        return self.storage[-1 - offset]

    def backtrack(self):
        """Remove current interaction and return parent."""
        self.storage.pop()
        if not self.isempty:
            return self.storage[-1]
