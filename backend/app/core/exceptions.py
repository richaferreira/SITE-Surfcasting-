class ExternalAPIError(RuntimeError):
    """Raised when an external provider cannot supply usable data."""


class ApplicationError(RuntimeError):
    """Base class for expected application errors."""


class AuthenticationError(ApplicationError):
    """Raised when credentials or an access token are invalid."""


class AuthorizationError(ApplicationError):
    """Raised when an authenticated user lacks permission."""


class ConflictError(ApplicationError):
    """Raised when a unique or state constraint would be violated."""


class NotFoundError(ApplicationError):
    """Raised when an application resource does not exist."""
