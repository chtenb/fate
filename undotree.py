"""
This module contains the classes ActionTree and Node, to store
the action history.
"""


class UndoTree:

    """
    Stores the action history as a tree with undo/redo functionality.
    """
    sequence = None

    def __init__(self, session):
        self.session = session
        self.root = Node(None)
        self.current_node = self.root

    def undo(self):
        """Undo previous action set current_node to its parent."""
        if self.current_node.parent:
            for action in reversed(self.current_node.actions):
                action.undo(self.session)
            self.current_node = self.current_node.parent

    def redo(self):
        """Redo most recent next action."""
        if self.current_node and self.current_node.children:
            self.current_node = self.current_node.children[-1]
            for action in self.current_node.actions:
                action.do(self.session)

    def add(self, action):
        """Add a new undoable action."""
        if self.sequence:
            self.sequence.add_action(action)
        else:
            node = Node(self.current_node)
            node.add_action(action)
            self.current_node.add_child(node)
            self.current_node = node

    def hard_undo(self):
        """
        Actually removes current_node.
        Useful for previewing operations.
        """
        if self.current_node.parent:
            current_node = self.current_node
            self.undo()
            self.current_node.children.remove(current_node)

    def start_sequence(self):
        """
        Indicate start of a sequence.
        All incoming actions should be gathered and put into one compound action.
        """
        self.sequence = Node(self.current_node)

    def end_sequence(self):
        """
        End of sequence.
        """
        if self.sequence.actions != []:
            self.current_node.add_child(self.sequence)
            self.current_node = self.sequence
        self.sequence = None


class Node:

    """Node of an ActionTree."""

    def __init__(self, parent):
        self.parent = parent
        self.actions = []
        self.children = []

    def add_action(self, action):
        """Add an action to node."""
        self.actions.append(action)

    def add_child(self, node):
        """Add a child to node."""
        self.children.append(node)
