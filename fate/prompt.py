from .mode import Mode
from .document import Document
from logging import error

Document.promptinput = ''

class Prompt(Mode):
    def __init__(self, document, callback=None):
        Mode.__init__(self, document, callback)
        self.inputstring = ''
        self.start(document)

    def processinput(self, document, userinput):
        if isinstance(userinput, str):
            key = userinput
            if key == 'Cancel':
                self.stop(document)
            elif key == '\n':
                document.promptinput = self.inputstring
                self.stop(document)
            elif len(key) > 1:
                # key not supported
                pass
            else:
                self.inputstring += key
        else:
            error('Prompt can not process non-string input')

    def start(self, doc):
        Mode.start(self, doc)
        doc.OnPrompt.fire(doc)

    def stop(self, doc):
        Mode.stop(self, doc)
        doc.OnPrompt.fire(doc)

def prompt(promptstring='>'):
    """Constructor for the prompt mode."""
    class PromptWithString(Prompt):
        def __init__(self, document, callback=None):
            Prompt.__init__(self, document, callback)
            self.promptstring = promptstring
    return PromptWithString
