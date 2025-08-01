"""Canvas API client for Easel CLI."""

from .auth import CanvasAuth
from .client import CanvasClient
from .exceptions import (
    CanvasAPIError,
    CanvasAuthError,
    CanvasNotFoundError,
    CanvasRateLimitError,
    CanvasServerError,
    CanvasTimeoutError,
    CanvasValidationError,
    CanvasPermissionError,
)
from .models import Course, User, Assignment, Discussion, Page, Submission
from .pagination import PaginatedResponse
from .rate_limit import RateLimiter

__all__ = [
    "CanvasClient",
    "CanvasAuth",
    "RateLimiter",
    "PaginatedResponse",
    "Course",
    "User",
    "Assignment",
    "Discussion",
    "Page",
    "Submission",
    "CanvasAPIError",
    "CanvasAuthError",
    "CanvasNotFoundError",
    "CanvasRateLimitError",
    "CanvasServerError",
    "CanvasTimeoutError",
    "CanvasValidationError",
    "CanvasPermissionError",
]
