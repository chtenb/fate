from functools import wraps

from .exceptions import PreconditionViolationError, PostconditionViolationError


def pre(condition):
    """
    Execute a precondition function before the decorated function.

    The `condition` must be a callable that receives the same keyword arguments
    as the function it's being applied to.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if __debug__:
                try:
                    check_result = condition(*args, **kwargs)
                except AssertionError as e:
                    raise e from PreconditionViolationError(
                        *get_context_message_pre(func, args, kwargs))

                if check_result != None and not check_result:
                    raise PreconditionViolationError(
                        *get_context_message_pre(func, args, kwargs))

            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_context_message_pre(func, args, kwargs):
    repr_values = [repr(item) for item in
                   list(args) + list(kwargs.values())]
    return (func.__code__.co_name,
            zip(list(func.__code__.co_varnames), repr_values))


def post(condition):
    """
    Execute a postcondition function before the decorated function.

    The `condition` must be a callable that receives the return value of the
    function it's being applied to as its first parameter, and the keyword
    arguments of the function it's applied to as its remaining parameters.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if __debug__:
                try:
                    check_result = condition(result, *args, **kwargs)
                except AssertionError as e:
                    raise e from PostconditionViolationError(
                        *get_context_message_post(func, result, args, kwargs))

                if check_result != None and not check_result:
                    raise PostconditionViolationError(
                        *get_context_message_post(func, result, args, kwargs))

            return result
        return wrapper
    return decorator


def get_context_message_post(func, result, args, kwargs):
    repr_values = [repr(item) for item in
                   [result] + list(args) + list(kwargs.values())]
    return (func.__code__.co_name,
            zip(['result'] + list(func.__code__.co_varnames), repr_values))
