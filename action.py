"""This module exposes the basic action machinery."""


class ActionTree:
    """Stores the action history as a tree with undo/redo functionality."""
    def __init__(self):
        self.root = Node(None, None)
        self.current_node = self.root

    def undo(self):
        """Undo previous action."""
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

    def pretty_print(self):
        """Return a multiline string containing the pretty printed tree.
        It should look like this, where X is the current position:
        o-o-o-o-o-X-o-o-o
            |     | ↳ o-o-o-o-o
            |     ↳ o-o-o
            ↳ o-o-o
                ↳ o-o-o
        """
        return '\n'.join(self.root.pretty_print(self.current_node))


class Node:
    """Node of an ActionTree."""
    def __init__(self, action, parent):
        self.action = action
        self.parent = parent
        self.children = []

    def add_child(self, node):
        """Add a child to node."""
        self.children.append(node)

    def pretty_print(self, current_node):
        """Return an array with the pretty printed lines of all children of self."""
        me = 'X' if self is current_node else 'o'

        if not self.children:
            return [me]

        result = []
        for i, child in enumerate(self.children):
            child_dump = child.pretty_print(current_node)
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
        """Iterate linearly through all atomic subactions."""
        for sub_action in self.sub_actions:
            if sub_action.__class__ == Action:
                for sub_sub_action in sub_action:
                    if sub_sub_action != None:
                        yield sub_sub_action
            else:
                if sub_action != None:
                    yield sub_action

    def contains_class(self, _class):
        """Check if an atomic subaction of class _class is contained in self."""
        for sub_action in self:
            if sub_action.__class__ == _class:
                return True
        return False


def actor(*args):
    """This function returns the compositional actor from the argument actors,
    and does the resulting actions upon execution."""
    def wrapper(session, preview=False):
        action = Action(session, *[f(session, preview=True)
            if hasattr(f, 'is_actor') else f(session) for f in args])

        if preview:
            return action
        else:
            action.do()

    wrapper.is_actor = True
    return wrapper
