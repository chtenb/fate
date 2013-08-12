"""A session represents the state of an editing session"""
from protexted.text import Text
from importlib import import_module
import logging

sessions = []
current = None

plugin_names = ['select_system']
plugins = {}
for name in plugin_names:
    plugins[name] = import_module("protexted." + name + ".main")

class Session():
    """Class containing all objects of one file editing session"""
    # E.g. text, selection, undo tree, jump history

    def __init__(self, filename=""):
        self.text = Text()
        self.filename = filename
        self.logger = logging.getLogger(repr(self))
        global sessions
        sessions.append(self)


        for plugin in plugins.values():
            try:
                if hasattr(plugin, 'init'):
                    plugin.init(self)
            except Exception as e:
                self.logger.error(e, exc_info=True)

        self.read()

    def read(self):
        """Read text from file"""
        if self.filename:
            with open(self.filename, 'r') as fd:
                self.text.set((0, len(self.text)), fd.read())

    def write(self):
        """Write current text to file"""
        if self.filename:
            with open(self.filename, 'w') as fd:
                fd.write(str(self.text))
