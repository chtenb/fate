
class NotInitializedException(Exception):

    """Indicates that some critical parts are not initialized."""
    pass


class ContractViolationError(AssertionError):

    """
    Base class for all contract violations.
    The parameter parameters is a list of pairs containing variables from the context
    of the exception raised to make it easier to debug the contract violation.
    """

    def __init__(self, message, func_name=None, parameters=None):
        if func_name != None and parameters != None:
            header = 'In function {} with context:'.format(func_name)
            params_text = ['    {}: {}'.format(name, value) for name, value in parameters]
            message = '\n'.join([message, header] + params_text)
        super(ContractViolationError, self).__init__(message)


class PreconditionViolationError(ContractViolationError):

    """Raised when a function precondition is violated."""

    def __init__(self, func_name=None, parameters=None):
        super(PreconditionViolationError, self).__init__(
            'Precondition check failed.', func_name, parameters)


class PostconditionViolationError(ContractViolationError):

    """Raised when a function postcondition is violated."""

    def __init__(self, func_name=None, parameters=None):
        super(PostconditionViolationError, self).__init__(
            'Postcondition check failed.', func_name, parameters)


class InvariantViolationError(ContractViolationError):

    """Raised when a class invariant is violated."""
    pass
