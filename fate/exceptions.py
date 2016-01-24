
class NotInitializedException(Exception):
    """Indicates that some critical parts are not initialized."""
    pass

class ContractViolationError(AssertionError):
    """Base class for all contract violations."""
    pass


class PreconditionViolationError(ContractViolationError):
    """Raised when a function precondition is violated."""
    pass


class PostconditionViolationError(ContractViolationError):
    """Raised when a function postcondition is violated."""
    pass


class InvariantViolationError(ContractViolationError):
    """Raised when a class invariant is violated."""
    pass
