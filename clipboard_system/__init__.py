from ..session import Session

Session.clipboard = []

def copy(self):
    self.clipboard = self.content(self.selection)
Session.copy = copy
