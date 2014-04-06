class Undoable:
    def __call__(self, session):
        """Do action."""
        session.undotree.add(self)
        self._call(session)

    def undo(self, session):
        """Undo action."""
        self._undo(session)

    def redo(self, session):
        """Redo action."""
        self._call(session)

    def _call(self, session):
        raise NotImplementedError("An abstract method is not callable.")

    def _undo(self, session):
        raise NotImplementedError("An abstract method is not callable.")


class Interactive:
    finished = False

    def __call__(self, session):
        session.interactionstack.push(self)
        self._call(session)

    def _call(self, session):
        raise NotImplementedError("An abstract method is not callable.")

    def proceed(self, session):
        self.finished = True
        parent = session.interactionstack.backtrack()
        if parent:
            parent.proceed(session)


class Updateable(Undoable, Interactive):
    """An Updateable action is able to update itself by undoing and redoing."""

    def __call__(self, session):
        # TODO: maybe remove duplication from super here
        session.undotree.add(self)
        session.interactionstack.push(self)
        self._call(session)

    def update(self, session):
        """
        Make sure we are up to date with possible (interactive) modifications to us.
        """
        session.undotree.hard_undo()
        session.interactionstack.backtrack()
        self(session)


class CompoundUndoable(Undoable):
    """
    This class can be used to compose multiple undoable actions
    into a single undoable action.
    """
    def __init__(self, session, *subactions):
        """Every subaction must be undoable."""
        for subaction in subactions:
            if not isinstance(subaction, Undoable):
                raise TypeError('Subaction {} is not an instance of Undoable.'
                                .format(repr(subaction)))
        self.subactions = subactions

    def __str__(self):
        result = []
        for subaction in self:
            result.append(str(subaction))
        return '(' + ', '.join(result) + ')'

    def _undo(self):
        """Undo action."""
        for subaction in reversed(self):
            subaction._undo()

    def _call(self):
        """Do action."""
        for subaction in self.subactions:
            subaction._call()


class CompoundUpdatable(CompoundUndoable, Updateable):
    """
    This class can be used to compose multiple possible interactive actions
    into a single action.
    """
    subactions_called = 0

    def _call(self, session):
        """Do subactions until first non finished subaction."""
        self.subactions_called = 0
        for subaction in self.subactions:
            subaction._call()
            self.subactions_called += 1
            if isinstance(subaction, Interactive) and not subaction.finished:
                # Stop here, this subaction is not yet finished
                break

    def _undo(self):
        """Undo all subactions that were executed upon last call."""
        assert len(self[self.subactions_called - 1::-1]) == self.subactions_called
        for subaction in self[self.subactions_called - 1::-1]:
            subaction._undo()

    # TODO: How to make sure that we get updated if a child gets updated?
    # Maybe we don't want to get updated, since only the child changed
    # But then we need to be able to replace the child in the undotree
    # I.e. we must undo the old child, do the new child and place the new child in the undotree
    # Or we must not deepcopy undoable actions into the undotree
    # But then we cannot easily update at all, since we have changed, and thus the undo method has been corrupted
    # Idea: maintain pointer to deepcopied instance to perform undo
    def update(self, session):
        """
        Make sure we are up to date with possible (interactive) modifications to us.
        """
        session.undotree.hard_undo()
        # Backtrack twice, for the pending subaction and for ourselves
        session.interactionstack.backtrack()
        session.interactionstack.backtrack()
        self(session)



def compose(*args):
    """Utility function that can be used to compose several undoable actors into one."""
    return NotImplemented

"""
There is a complication with implementing CompoundUndoable.
Suppose we want to create a compound selection which involves a change to extend mode at some point.
Then extend mode must be executed at creation time, in order to create the intended selection.
However, this violates the principle that the session must not be touched while only creating an action.

The solution must be to state that extend mode only affects selectors that are done live by the user.
For other situations, extend mode must be passed explicitly.
To make things simpler, we require all subactions to be undoable.
"""

#
# ----------- OLD PART --------------
#

# class CompoundAction(Action):
    #"""
    # This class can be used to compose multiple actions into a single
    # action.
    #"""
    # def __init__(self, session, *args):
        #"""Every object in args must be an Action."""
        # Action.__init__(self, session)
        # self.sub_actions = tuple(a for a in args if a)

    # def __str__(self):
        # result = []
        # for sub_action in self:
            # result.append(str(sub_action))
        # return '(' + ', '.join(result) + ')'

    # def _undo(self):
        #"""Undo action."""
        # for sub_action in self:
            # sub_action._undo()

    # def _do(self):
        #"""Do action."""
        # for sub_action in self.sub_actions:
            # sub_action._do()

    # def __iter__(self):
        #"""Iterate linearly through all atomic subactions."""
        # for sub_action in self.sub_actions:
            # if sub_action.__class__ == CompoundAction:
                # for sub_sub_action in sub_action:
                    # if sub_sub_action != None:
                        # yield sub_sub_action
            # else:
                # if sub_action != None:
                    # yield sub_action

    # def contains_class(self, cls):
        #"""
        # Check if an atomic subaction of class _class is contained
        # in self.
        #"""
        # for sub_action in self:
            # if sub_action.__class__ == cls:
                # return True
        # return False

# def compose(*args):
    #"""
    # This function returns the compositional actor from the
    # argument actors, and does the resulting actions upon execution.
    #"""
    #@actor
    # def wrapper(session):
        # actionlist = [f(session, preview=True)
                      # if hasattr(f, 'is_actor') else f(session) for f in args]
        # actionlist = [x for x in actionlist if x]
        # if not actionlist:
            # return
        # return CompoundAction(session, *actionlist)
    # return wrapper
