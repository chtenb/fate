class Undoable:
    def __call__(self, session):
        session.undotree.add(self)
        self._call(session)

    def undo(self, session):
        self._undo(session)

    def redo(self, session):
        """Redo action."""
        self._call(session)

    def _call(self, session):
        raise Exception("An abstract method is not callable.")

    def _undo(self, session):
        raise Exception("An abstract method is not callable.")

class Interactive:
    finished = False

    def __call__(self, session):
        session.interactionstack.push(self)
        self._call(session)

    def _call(self, session):
        raise Exception("An abstract method is not callable.")

    def proceed(self, session):
        self.finished = True
        parent = session.interactionstack.backtrack()
        if parent:
            parent.proceed(session)


class Updateable(Undoable, Interactive):
    """An Updateable action is able to update itself by undoing and redoing."""

    def __call__(self, session):
        session.undotree.add(self)
        session.interactionstack.push(self)
        self._call(session)

    def update(self, session):
        """
        Make sure we are up to date with possible (interactive) modifications.
        """
        session.undotree.hard_undo()
        self._call(session)

def compose(*args):
    return NotImplemented

#
# ----------- OLD PART --------------
#

#class Action:
    #"""Base class for actions."""

    #def __init__(self, session, *args):
        #"""Every object in args must have an undo and a do function."""
        #self.session = session

    #def _do(self):
        #"""Do implemented by subclass."""
        #pass

    #def _undo(self):
        #"""Undo implemented by subclass."""
        #pass

    #def undo(self):
        #"""Undo action."""
        #self._undo()
        #self.check_text_changed()

    #def do(self, redo=False):
        #"""Do action."""
        #self._do()

        #if not redo:
            #self.session.actiontree.add(self)
        #self.check_text_changed()

    #def check_text_changed(self):
        #"""Check for changes in text."""
        #if self.session.text_changed:
            #self.session.saved = False
            #self.session.OnTextChanged.fire(self.session)
            #self.session.text_changed = False

    #def redo(self):
        #"""Redo action."""
        #self.do(redo=True)


#class CompoundAction(Action):
    #"""
    #This class can be used to compose multiple actions into a single
    #action.
    #"""
    #def __init__(self, session, *args):
        #"""Every object in args must be an Action."""
        #Action.__init__(self, session)
        #self.sub_actions = tuple(a for a in args if a)

    #def __str__(self):
        #result = []
        #for sub_action in self:
            #result.append(str(sub_action))
        #return '(' + ', '.join(result) + ')'

    #def _undo(self):
        #"""Undo action."""
        #for sub_action in self:
            #sub_action._undo()

    #def _do(self):
        #"""Do action."""
        #for sub_action in self.sub_actions:
            #sub_action._do()

    #def __iter__(self):
        #"""Iterate linearly through all atomic subactions."""
        #for sub_action in self.sub_actions:
            #if sub_action.__class__ == CompoundAction:
                #for sub_sub_action in sub_action:
                    #if sub_sub_action != None:
                        #yield sub_sub_action
            #else:
                #if sub_action != None:
                    #yield sub_action

    #def contains_class(self, cls):
        #"""
        #Check if an atomic subaction of class _class is contained
        #in self.
        #"""
        #for sub_action in self:
            #if sub_action.__class__ == cls:
                #return True
        #return False


#def actor(function):
    #"""Base function for actors."""
    #def wrapper(session, preview=False, **kwargs):
        #action = function(session, **kwargs)
        #if action and not preview:
            #action.do()
        #else:
            #return action

    #wrapper.is_actor = True
    #return wrapper


#def compose(*args):
    #"""
    #This function returns the compositional actor from the
    #argument actors, and does the resulting actions upon execution.
    #"""
    #@actor
    #def wrapper(session):
        #actionlist = [f(session, preview=True)
                      #if hasattr(f, 'is_actor') else f(session) for f in args]
        #actionlist = [x for x in actionlist if x]
        #if not actionlist:
            #return
        #return CompoundAction(session, *actionlist)
    #return wrapper
