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


class UnprocessableError(ApplicationError):
    """Raised when supplied content cannot be processed safely."""


class PayloadTooLargeError(ApplicationError):
    """Raised when an upload exceeds the configured limit."""


class DependencyUnavailableError(ApplicationError):
    """Raised when a required runtime dependency is unavailable."""


class RateLimitExceededError(ApplicationError):
    """Raised when a client exceeds a bounded public endpoint quota."""
