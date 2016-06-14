"""This module defines the class Operation."""
from .commandtools import Undoable
from . import texttransformation


class Operation(Undoable, texttransformation.TextTransformation):

    """
    A container of modified content of a selection.
    Can be inverted such that the operation can be undone by applying the inverse.
    """

    def __init__(self, doc, newcontent, selection=None):
        selection = selection or doc.selection
        texttransformation.TextTransformation.__init__(self, selection, newcontent, doc.text)

    def __str__(self):
        attributes = [('old selection', self.selection),
                      ('computed newselection', self.compute_newselection()),
                      ('old content', self.original_content),
                      ('new content', self.replacements)]
        return '\n'.join([k + ': ' + str(v) for k, v in attributes])

    def do(self, doc):
        """Execute operation."""
        new_text = doc.text.transform(self)
        doc.text = new_text
        doc.selection = self.compute_newselection()

    def inverse_operation(self, doc):
        inverse_transformation = self.inverse(doc.text)
        return Operation(doc, inverse_transformation.replacements,
                         selection=inverse_transformation.selection)

    def undo(self, doc):
        """Undo operation."""
        inverse = self.inverse_operation(doc)
        inverse.do(doc)
