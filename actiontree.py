"""
This module contains the classes ActionTree and Node, to store
the action history.
"""
from copy import deepcopy


class ActionTree:
    """
    Stores the action history as a tree with undo/redo functionality.
    """
    def __init__(self):
        self.root = Node(None, None)
        self.current_node = self.root

    def undo(self):
        """Undo previous action set current_node to its parent."""
        if self.current_node.parent:
            self.current_node.action.undo()
            self.current_node = self.current_node.parent

    def redo(self):
        """Redo most recent next action."""
        if self.current_node and self.current_node.children:
            self.current_node = self.current_node.children[-1]
            self.current_node.action.redo()

    def add(self, action):
        """Perform a new action."""
        #import logging
        #logging.debug(str(action.__dict__))
        #logging.debug(str(action.__class__.__dict__))
        node = Node(deepcopy(action), self.current_node)
        self.current_node.add_child(node)
        self.current_node = node

    def hard_undo(self):
        """
        Actually removes current_node.
        Useful for previewing operations.
        """
        if self.current_node.parent:
            current_node = self.current_node
            # import logging
            # logging.debug(str(current_node.action))
            # logging.debug(str(current_node.action.inverse()))
            self.undo()
            self.current_node.children.remove(current_node)


class Node:
    """Node of an ActionTree."""
    def __init__(self, action, parent):
        self.action = action
        self.parent = parent
        self.children = []

    def add_child(self, node):
        """Add a child to node."""
        self.children.append(node)
