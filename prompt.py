from .mode import Mode
from .document import Document

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
            raise NotImplementedError('To be done.')

def prompt(promptstring='>'):
    """Constructor for the prompt mode."""
    class PromptWithString(Prompt):
        def __init__(self, document, callback=None):
            Prompt.__init__(self, document, callback)
            self.promptstring = promptstring
    return PromptWithString
