"""
This module contains the classes ActionTree and Node, to store
the action history.
"""
from logging import debug
from . import actions
from . import modes

class UndoTree:

    """
    Stores the action history as a tree with undo/redo functionality.
    """
    sequence = None
    sequence_depth = 0

    def __init__(self, session):
        self.session = session
        self.root = Node(None)
        self.current_node = self.root

    def undo(self):
        """Undo previous action set current_node to its parent."""
        if self.sequence != None:
            raise Exception('Cannot perform undo; a sequence of actions is being added')

        if self.current_node.parent:
            for action in reversed(self.current_node.actions):
                action.undo(self.session)
            self.current_node = self.current_node.parent

    def redo(self, child_index=-1):
        """Redo most recent next action."""
        if self.sequence != None:
            raise Exception('Cannot perform redo; a sequence of actions is being added')

        if self.current_node and self.current_node.children:
            l = len(self.current_node.children)
            assert -l <= child_index < l

            self.current_node = self.current_node.children[child_index]
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
        if self.sequence != None:
            raise Exception(
                'Cannot perform hard undo; a sequence of actions is being added'
            )

        if self.current_node.parent:
            current_node = self.current_node
            self.undo()
            self.current_node.children.remove(current_node)

    def start_sequence(self):
        """
        Indicate start of a sequence.
        All incoming actions should be gathered and put into one compound action.
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
            if self.sequence.actions != []:
                self.current_node.add_child(self.sequence)
                self.current_node = self.sequence
            self.sequence_depth = 0
            self.sequence = None
        else:
            self.sequence_depth -= 1


class Node:

    """
    Node of an ActionTree.
    Each node can have a single parent, a list of actions and a list of children.
    """

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

modes.UNDO = 'UNDO'

class UndoMode:
    """
    Walk around in undo tree using arrow keys.
    You can only switch branches between siblings.
    """
    def __init__(self):
        self.keymap = {
            'Left' : self.left,
            'Right' : self.right,
            'Up' : self.up,
            'Down' : self.down,
            'Esc' : self.stop
            }

    def __call__(self, session):
        session.mode = modes.UNDO

        self.running = True
        while self.running:
            session.ui.touch()

            # Make sure the child_index is set to the index we now have
            self.child_index = self.current_index(session)

            #debug('length: ' + str(len(undotree.current_node.children)))
            #debug('index: ' + str(child_index))

            # Proceed according to user input
            while 1:
                char = session.ui.getchar()
                if char in self.keymap:
                    self.keymap[char](session)
                    break

    def stop(self, session):
        session.mode = modes.SELECT
        self.running = False

    def left(self, session):
        # We can always just call undo; if there is no parent it will do nothing
        session.undotree.undo()

    def right(self, session):
        # We can always just call redo(0); if there is no child it will do nothing
        self.child_index = 0
        session.undotree.redo()

    def up(self, session):
        self.child_index -= 1
        # update() will take care of having a valid child_index
        self.update_child_index(session)

    def down(self, session):
        self.child_index += 1
        # update() will take care of having a valid child_index
        self.update_child_index(session)

    def update_child_index(self, session):
        """Undo and execute the child pointed by the current child_index."""
        if session.undotree.current_node.parent != None:
            session.undotree.undo()

            # The child index must be bound to the correct domain
            self.child_index = self.bound(self.child_index, session)

            session.undotree.redo(self.child_index)

    def bound(self, child_index, session):
        """Bound the given child_index to be a valid index."""
        l = len(session.undotree.current_node.children)
        if l > 0:
            child_index = min(child_index, l - 1)
            child_index = max(child_index, 0)
            assert 0 <= child_index < l
        return child_index

    def current_index(self, session):
        node = session.undotree.current_node
        return node.parent.children.index(node) if node.parent != None else 0

actions.undo_mode = UndoMode()

