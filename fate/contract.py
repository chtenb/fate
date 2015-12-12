from functools import wraps

from .exceptions import PreconditionViolationError, PostconditionViolationError


def pre(condition):
    """
    Execute a precondition function before the decorated function.

    The `condition` must be a callable that receives the same keyword arguments
    as the function it's being applied to.
    """
    def decorator(func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                check_result = condition(*args, **kwargs)
            except AssertionError as e:
                raise PreconditionViolationError("Precondition check failed.") from e

            if check_result != None and not check_result:
                raise PreconditionViolationError("Precondition check failed")

            return func(*args, **kwargs)
        return wrapper
    return decorator


def post(condition):
    """
    Execute a postcondition function before the decorated function.

    The `condition` must be a callable that receives the return value of the
    function it's being applied to as its first parameter, and the keyword
    arguments of the function it's applied to as its remaining parameters.
    """
    def decorator(func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            try:
                check_result = condition(result, *args, **kwargs)
            except AssertionError as e:
                raise PostconditionViolationError("Precondition check failed.") from e

            if check_result != None and not check_result:
                raise PostconditionViolationError("Postcondition check failed")

            return result
        return wrapper
    return decorator
