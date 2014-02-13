"""
This module contains the classes ActionTree and Node, to store
the action history.
"""

class ActionTree:
    """
    Stores the action history as a tree with undo/redo functionality.
    """
    def __init__(self):
        self.root = Node(None, None)
        self.current_node = self.root

    def undo(self):
        """Undo previous action set current_node to its parent."""
        if self.current_node and self.current_node.parent:
            self.current_node.action.undo()
            self.current_node = self.current_node.parent

    def redo(self):
        """Redo most recent next action."""
        if self.current_node and self.current_node.children:
            self.current_node = self.current_node.children[-1]
            self.current_node.action.do(redo=True)

    def add(self, action):
        """Perform a new action."""
        node = Node(action, self.current_node)
        self.current_node.add_child(node)
        self.current_node = node

    def hard_undo(self):
        """
        Actually removes current_node.
        Useful for previewing operations.
        """
        current_node = self.current_node
        self.undo()
        self.current_node.children.remove(current_node)

    def dump(self, height=0, width=0):
        """
        Return a multiline string containing the pretty printed tree.
        It should look like this, where X is the current position:
        o-o-o-o-o-X-o-o-o
            |     | ↳ o-o-o-o-o
            |     ↳ o-o-o
            ↳ o-o-o
                ↳ o-o-o
        """
        # We only have to print height/2 children branches
        # and parents branches, and width/2 children and parents

        # So first traverse upwards until exceed height or width
        upperleft = self.current_node.traverse_up(int(height / 2), int(width / 2))
        # Then print tree downwards until exceed height or width
        return '\n'.join(upperleft.dump(self.current_node, height, width))


class Node:
    """Node of an ActionTree."""
    def __init__(self, action, parent):
        self.action = action
        self.parent = parent
        self.children = []

    def add_child(self, node):
        """Add a child to node."""
        self.children.append(node)

    def traverse_up(self, height, width):
        """Traverse upwards until exceed height or width."""
        if not self.parent or height <= 0 or width <= 0:
            return self
        elif len(self.parent.children) == 1:
            return self.parent.traverse_up(height, width - 2)
        else:
            return self.parent.traverse_up(height - 1, width - 2)

    def dump(self, current_node, height=0, width=0):
        """
        Return an array with the pretty printed lines of children
        of self, until we exceed height or width.
        """
        me = 'X' if self is current_node else 'o'

        if not self.children:
            return [me]

        result = []
        for i, child in enumerate(self.children):
            child_dump = child.dump(current_node, height, width - 2)
            height -= len(child_dump)
            last_child = '|' if i < len(self.children) - 1 else ' '

            if i == 0:
                for j, line in enumerate(child_dump):
                    if j == 0:
                        child_dump[j] = me + '-' + line
                    else:
                        child_dump[j] = last_child + ' ' + line
            else:
                for j, line in enumerate(child_dump):
                    if j == 0:
                        child_dump[j] = '↳ ' + line
                    else:
                        child_dump[j] = last_child + ' ' + line

            result.extend(child_dump)
        return result

