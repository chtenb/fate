class Mode:
    """Abstract class to make creating new modes more convenient."""
    def __init__(self):
        self.keymap = {}
        self.allowedcommands = []

    def processinput(self, document, userinput):
        if type(userinput) == str:
            key = userinput
            if key in self.keymap:
                self.keymap[key](document)
                return
            if key in document.keymap:
                command = document.keymap[key]
        else:
            command = userinput

        if command in self.allowedcommands:
            command(document)
