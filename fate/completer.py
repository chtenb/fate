from abc import abstractmethod
from .document import Document

class Completer:

    """Interface that should be implemented by a completion engine."""

    def __init__(self, doc):
        self.doc = doc

    @abstractmethod
    def parse_file(self):
        pass

    @abstractmethod
    def complete(self):
        pass

Document.completer = None
