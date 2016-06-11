"""This module defines the class Operation."""
from .commandtools import Undoable
from .selection import Selection, Interval
from .texttransformation import TextTransformation


class Operation(Undoable, TextTransformation):

    """
    A container of modified content of a selection.
    Can be inverted such that the operation can be undone by applying the inverse.
    """

    def __init__(self, doc, newcontent, selection=None):
        selection = selection or doc.selection
        TextTransformation.__init__(self, selection, newcontent, doc.text)

    def __str__(self):
        attributes = [('old selection', oldselection),
                      ('computed newselection', self.compute_newselection()),
                      ('old content', self.original_content),
                      ('new content', self.replacements)]
        return '\n'.join([k + ': ' + str(v) for k, v in attributes])

    def do(self, doc):
        """Execute operation."""
        new_text = self.apply(doc.text)
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
