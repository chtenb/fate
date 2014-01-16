"""This module exposes the basic action machinery."""


class ActionTree:
    """Stores the action history as a tree with undo/redo functionality."""
    def __init__(self):
        self.root = Node(None, None)
        self.current_node = self.root

    def undo(self):
        """Undo previous action."""
        if hasattr(self.current_node.action, 'undo'):
            self.current_node.action.undo()
        self.current_node = self.current_node.parent

    def redo(self):
        """Redo next action."""
        pass

    def add(self, action):
        """Perform a new action."""
        node = Node(action, self.current_node)
        self.current_node.add_child(node)
        self.current_node = node


class Node:
    """Node of an ActionTree."""
    def __init__(self, action, parent):
        self.action = action
        self.parent = parent
        self.children = []

    def add_child(self, node):
        """Add a child to node."""
        self.children.append(node)


class Action:
    """This class can be used to compose multiple actions into a single action."""
    def __init__(self, session, *args):
        """Every object in args must have an undo and a do function."""
        self.session = session
        self.sub_actions = tuple(a for a in args if a)
        self.args = args

    def undo(self):
        """Undo action."""
        for sub_action in self.sub_actions:
            sub_action.undo()

    def do(self, toplevel=True):
        """Do action."""
        for sub_action in self.sub_actions:
            if sub_action.__class__ == Action:
                sub_action.do(toplevel=False)
            else:
                sub_action.do()

        if toplevel:
            self.session.actiontree.add(self)
            self.session.OnApplyActor.fire(self)

    def __iter__(self):
        """Iterate linearly through all sub_actions."""
        for sub_action in self.sub_actions:
            if sub_action.__class__ == Action:
                for sub_sub_action in sub_action:
                    yield sub_sub_action
            else:
                yield sub_action

    def contains_class(self, _class):
        """Check recursively if a sub_action of class _class is contained in self."""
        for sub_action in self:
            if sub_action.__class__ == _class:
                return True
        return False


def actor(*args):
    """This function returns the compositional actor from the argument actors,
    and does the resulting actions upon execution."""
    def wrapper(session, preview=False):
        action = Action(session, *[f(session, preview=True) if hasattr(f, 'is_actor') else f(session) for f in args])

        if preview:
            return action
        else:
            action.do()

    wrapper.is_actor = True
    return wrapper
