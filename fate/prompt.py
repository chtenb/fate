from .mode import Mode
from .document import Document
from logging import error

Document.promptinput = ''

class Prompt(Mode):
    def __init__(self, doc):
        Mode.__init__(self, doc)
        self.inputstring = ''

    def processinput(self, doc, userinput):
        if isinstance(userinput, str):
            key = userinput
            if key == doc.cancelkey:
                self.stop(doc)
            elif key == '\n':
                self.stop(doc)
            elif len(key) > 1:
                # key not supported
                pass
            else:
                self.inputstring += key
        else:
            error('Prompt can not process non-string input')

    def start(self, doc, promptstring='>', callback=None):
        self.inputstring = ''
        self.promptstring = promptstring
        Mode.start(self, doc, callback)

    def stop(self, doc):
        Mode.stop(self, doc)

def init_prompt(doc):
    doc.modes.prompt = Prompt(doc)
Document.OnModeInit.add(init_prompt)

