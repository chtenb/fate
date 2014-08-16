"""
This module contains the classes ActionTree and Node, to store
the command history.
"""
from logging import debug
from . import commands
from . import modes
from .document import (
    Document, next_document, previous_document, quit_document,
    quit_all, open_document, force_quit
)


class UndoTree:

    """
    Stores the command history as a tree with undo/redo functionality.
    """
    sequence = None
    sequence_depth = 0

    def __init__(self, document):
        self.document = document
        self.root = Node(None)
        self.current_node = self.root

    def undo(self):
        """Undo previous command set current_node to its parent."""
        if self.sequence != None:
            raise Exception('Cannot perform undo; a sequence of commands is being added')

        if self.current_node.parent:
            for command in reversed(self.current_node.commands):
                command.undo(self.document)
            self.current_node = self.current_node.parent

    def redo(self, child_index=-1):
        """Redo most recent next command."""
        if self.sequence != None:
            raise Exception('Cannot perform redo; a sequence of commands is being added')

        if self.current_node and self.current_node.children:
            l = len(self.current_node.children)
            assert -l <= child_index < l

            self.current_node = self.current_node.children[child_index]
            for command in self.current_node.commands:
                command.do(self.document)

    def add(self, command):
        """Add a new undoable command."""
        if self.sequence:
            self.sequence.add_command(command)
        else:
            node = Node(self.current_node)
            node.add_command(command)
            self.current_node.add_child(node)
            self.current_node = node

    def hard_undo(self):
        """
        Actually removes current_node.
        Useful for previewing operations.
        """
        if self.sequence != None:
            raise Exception(
                'Cannot perform hard undo; a sequence of commands is being added'
            )

        if self.current_node.parent:
            current_node = self.current_node
            self.undo()
            self.current_node.children.remove(current_node)

    def start_sequence(self):
        """
        Indicate start of a sequence.
        All incoming commands should be gathered and put into one compound command.
        """
        if self.sequence_depth == 0:
            self.sequence = Node(self.current_node)
        self.sequence_depth += 1

    def end_sequence(self):
        """
        End of sequence.
        """
        if self.sequence_depth < 1:
            raise Exception('Cannot end sequence; no sequence present.')

        if self.sequence_depth == 1:
            if self.sequence.commands != []:
                self.current_node.add_child(self.sequence)
                self.current_node = self.sequence
            self.sequence_depth = 0
            self.sequence = None
        else:
            self.sequence_depth -= 1


class Node:

    """
    Node of an ActionTree.
    Each node can have a single parent, a list of commands and a list of children.
    """

    def __init__(self, parent):
        self.parent = parent
        self.commands = []
        self.children = []

    def add_command(self, command):
        """Add an command to node."""
        self.commands.append(command)

    def add_child(self, node):
        """Add a child to node."""
        self.children.append(node)


def init(document):
    document.undotree = UndoTree(document)
Document.OnDocumentInit.add(init)

modes.UNDO = 'UNDO'


# Some commands for interacting with the undo tree
def undo(document):
    """Undo last command."""
    document.undotree.undo()
commands.undo = undo


def redo(document):
    """Redo last undo."""
    document.undotree.redo()
commands.redo = redo


class UndoMode:

    """
    Walk around in undo tree using arrow keys.
    You can only switch branches between siblings.
    """

    def __init__(self):
        self.keymap = {
            'Left': self.left,
            'Right': self.right,
            'Up': self.up,
            'Down': self.down,
            'Esc': self.stop
        }
        self.allowedcommands = [
            next_document, previous_document, quit_document,
            quit_all, open_document, force_quit
        ]

    def __call__(self, document):
        document.mode = modes.UNDO

        document.ui.touch()

        # Make sure the child_index is set to the index we now have
        self.child_index = self.current_index(document)

        # Notify the the document that we are in undomode now
        document.persistentcommand = self

        #debug('length: ' + str(len(undotree.current_node.children)))
        #debug('index: ' + str(child_index))

        # Proceed according to user input
        # while 1:
        #key = document.ui.getkey()
        # if key in self.keymap:
        # self.keymap[key](document)
        # break

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

    def __str__(self):
        return 'UNDO'

    def stop(self, document):
        document.mode = modes.SELECT
        document.persistentcommand = None

    def left(self, document):
        # We can always just call undo; if there is no parent it will do nothing
        document.undotree.undo()

    def right(self, document):
        # We can always just call redo(0); if there is no child it will do nothing
        self.child_index = 0
        document.undotree.redo()

    def up(self, document):
        self.child_index -= 1
        # update() will take care of having a valid child_index
        self.update_child_index(document)

    def down(self, document):
        self.child_index += 1
        # update() will take care of having a valid child_index
        self.update_child_index(document)

    def update_child_index(self, document):
        """Undo and execute the child pointed by the current child_index."""
        if document.undotree.current_node.parent != None:
            document.undotree.undo()

            # The child index must be bound to the correct domain
            self.child_index = self.bound(self.child_index, document)

            document.undotree.redo(self.child_index)

    def bound(self, child_index, document):
        """Bound the given child_index to be a valid index."""
        l = len(document.undotree.current_node.children)
        if l > 0:
            child_index = min(child_index, l - 1)
            child_index = max(child_index, 0)
            assert 0 <= child_index < l
        return child_index

    def current_index(self, document):
        node = document.undotree.current_node
        return node.parent.children.index(node) if node.parent != None else 0

commands.undo_mode = UndoMode()
