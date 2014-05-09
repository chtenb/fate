from . import actions
from re import match
from logging import debug


def publics(obj):
    """Return all objects in __dict__ not starting with '_' as a dict"""
    return dict((name, obj) for name, obj in vars(obj).items() if not name.startswith('_'))


def get_scope(session):
    scope = publics(actions)
    scope.update({'self': session})
    return scope


def get_completions(session, string):
    """Get completions given a string."""
    yield (string, '')
    scope = get_scope(session)

    # If string is a completable identifier
    if match(r'^[\w.]*$', string) == None:
        debug('no identifier')
        return

    split_result = string.rsplit('.', 1)
    debug(split_result)
    if len(split_result) == 2:
        obj_name, attr = split_result
        try:
            obj = eval(obj_name, scope)
        except NameError:
            return
        else:
            scope = publics(obj)
            for name, obj in scope.items():
                if name.lower().startswith(attr.lower()):
                    yield (obj_name + '.' + name, repr(obj))
    else:
        for name, obj in scope.items():
            if name.lower().startswith(string.lower()):
                yield (name, repr(obj))


def evaluate(session, command):
    """Evaluate a command."""
    scope = get_scope(session)

    try:
        result = eval(command, scope)
    except SyntaxError:
        # Probably command is a statement, not an expression
        try:
            exec(command, scope)
        except Exception as e:
            return command + ' : ' + str(e)
    except Exception as e:
        return command + ' : ' + str(e)
    else:
        while callable(result):
            result = result(session)
        return result
