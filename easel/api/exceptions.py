"""Canvas API exceptions."""

from typing import Optional, Dict, Any


class CanvasAPIError(Exception):
    """Base exception for Canvas API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class CanvasAuthError(CanvasAPIError):
    """Authentication failed with Canvas API."""

    pass


class CanvasNotFoundError(CanvasAPIError):
    """Resource not found on Canvas."""

    pass


class CanvasRateLimitError(CanvasAPIError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class CanvasServerError(CanvasAPIError):
    """Canvas server error (5xx status codes)."""

    pass


class CanvasTimeoutError(CanvasAPIError):
    """Request timeout."""

    pass


class CanvasValidationError(CanvasAPIError):
    """Request validation error (4xx status codes)."""

    pass


class CanvasPermissionError(CanvasAPIError):
    """Insufficient permissions for requested action."""

    pass
