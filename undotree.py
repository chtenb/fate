"""
This module contains the classes ActionTree and Node, to store
the action history.
"""
from .actiontools import Undoable

class UndoTree:

    """
    Stores the action history as a tree with undo/redo functionality.
    """
    def __init__(self, session):
        self.session = session
        self.root = Node(None, None)
        self.current_node = self.root

    def undo(self):
        """Undo previous action and set self.current_node to its parent."""
        if self.current_node.parent:
            self.current_node.action.undo(self.session)
            self.current_node = self.current_node.parent

    def redo(self):
        """
        Redo most recent next action,
        i.e. execute it without it being added to the undotree again.
        """
        if self.current_node and self.current_node.children:
            self.current_node = self.current_node.children[-1]
            self.current_node.action.do(self.session)

    def add(self, action):
        """Add a new undoable action."""
        assert isinstance(action, Undoable)

        node = Node(self.current_node, action)
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

class Node:

    """Node of an ActionTree."""

    def __init__(self, parent, action):
        self.parent = parent
        self.action = action
        self.children = []

    def __str__(self):
        return str(self.action)

    def add_child(self, node):
        """Add a child to node."""
        self.children.append(node)
