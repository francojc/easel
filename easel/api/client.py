"""Canvas API client implementation."""

import asyncio
from typing import Optional, Dict, Any, List, TypeVar

import httpx
from pydantic import BaseModel

from .auth import CanvasAuth
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
from .models import Course, User, Assignment, Discussion, Page
from .pagination import PaginatedResponse
from .rate_limit import RateLimiter

T = TypeVar("T", bound=BaseModel)


class CanvasClient:
    """Async Canvas API client with rate limiting and error handling."""

    def __init__(
        self,
        base_url: str,
        auth: CanvasAuth,
        rate_limit: float = 10.0,
        timeout: float = 30.0,
        max_retries: int = 3,
        per_page: int = 100,
    ) -> None:
        """Initialize Canvas API client.

        Args:
            base_url: Canvas instance base URL
            auth: Authentication handler
            rate_limit: Maximum requests per second
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            per_page: Default page size for paginated requests
        """
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.rate_limiter = RateLimiter(rate_limit)
        self.timeout = timeout
        self.max_retries = max_retries
        self.per_page = per_page
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "CanvasClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers=self.auth.get_headers(),
            )
        return self._client

    async def _make_request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> httpx.Response:
        """Make an authenticated API request with rate limiting and retries.

        Args:
            method: HTTP method
            endpoint: API endpoint (if url not provided)
            url: Full URL (overrides endpoint)
            params: Query parameters
            json_data: JSON request body
            **kwargs: Additional httpx request arguments

        Returns:
            HTTP response

        Raises:
            Various CanvasAPIError subclasses based on response
        """
        if url:
            request_url = url
        elif endpoint:
            api_path = endpoint.lstrip("/")
            request_url = f"{self.base_url}/api/v1/{api_path}"
        else:
            raise ValueError("Either endpoint or url must be provided")

        client = await self._ensure_client()

        for attempt in range(self.max_retries + 1):
            try:
                # Apply rate limiting
                await self.rate_limiter.acquire(timeout=self.timeout)

                # Make request
                response = await client.request(
                    method=method,
                    url=request_url,
                    params=params,
                    json=json_data,
                    **kwargs,
                )

                # Handle response
                await self._handle_response(response)
                return response

            except (
                httpx.TimeoutException,
                httpx.ConnectTimeout,
                httpx.ReadTimeout,
            ):
                if attempt == self.max_retries:
                    raise CanvasTimeoutError(
                        f"Request timeout after {self.max_retries} retries"
                    )
                await asyncio.sleep(2**attempt)  # Exponential backoff

            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise CanvasAPIError(f"Request failed: {e}")
                await asyncio.sleep(2**attempt)

            except CanvasRateLimitError as e:
                if attempt == self.max_retries:
                    raise
                # Wait for retry-after header if available
                if e.retry_after:
                    await asyncio.sleep(e.retry_after)
                else:
                    await asyncio.sleep(2**attempt)

        raise CanvasAPIError("Max retries exceeded")

    async def _handle_response(self, response: httpx.Response) -> None:
        """Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response to handle

        Raises:
            Various CanvasAPIError subclasses based on status code
        """
        if response.is_success:
            return

        status_code = response.status_code

        try:
            error_data = response.json()
            error_message = error_data.get("message", f"HTTP {status_code}")
        except Exception:
            error_message = f"HTTP {status_code}: {response.reason_phrase}"

        # Rate limiting
        if status_code == 429:
            retry_after = None
            if "Retry-After" in response.headers:
                try:
                    retry_after = int(response.headers["Retry-After"])
                except ValueError:
                    pass
            raise CanvasRateLimitError(
                error_message,
                status_code=status_code,
                retry_after=retry_after,
            )

        # Authentication errors
        elif status_code == 401:
            raise CanvasAuthError(error_message, status_code=status_code)

        # Permission errors
        elif status_code == 403:
            raise CanvasPermissionError(error_message, status_code=status_code)

        # Not found
        elif status_code == 404:
            raise CanvasNotFoundError(error_message, status_code=status_code)

        # Validation errors
        elif 400 <= status_code < 500:
            raise CanvasValidationError(error_message, status_code=status_code)

        # Server errors
        elif status_code >= 500:
            raise CanvasServerError(error_message, status_code=status_code)

        # Other errors
        else:
            raise CanvasAPIError(error_message, status_code=status_code)

    async def verify_connection(self) -> User:
        """Verify API connection and get current user info.

        Returns:
            Current user information

        Raises:
            CanvasAPIError: If connection fails
        """
        response = await self._make_request("GET", "users/self")
        try:
            user_data = response.json()
        except (ValueError, TypeError) as e:
            raise CanvasAPIError(f"Invalid response format: {e}")
        return User(**user_data)

    # Course methods
    async def get_courses(
        self,
        include: Optional[List[str]] = None,
        state: Optional[List[str]] = None,
        per_page: Optional[int] = None,
    ) -> PaginatedResponse[Course]:
        """Get courses for the current user.

        Args:
            include: Additional data to include
            state: Course workflow states to filter by
            per_page: Number of courses per page

        Returns:
            Paginated course response
        """
        params: Dict[str, Any] = {}
        if include:
            params["include[]"] = include
        if state:
            params["state[]"] = state
        if per_page:
            params["per_page"] = per_page
        else:
            params["per_page"] = self.per_page

        response = await self._make_request("GET", "courses", params=params)
        courses_data = response.json()
        courses = [Course(**course_data) for course_data in courses_data]

        return PaginatedResponse.from_response(response, courses)

    async def get_course(
        self, course_id: int, include: Optional[List[str]] = None
    ) -> Course:
        """Get a specific course by ID.

        Args:
            course_id: Course ID
            include: Additional data to include

        Returns:
            Course information
        """
        params = {}
        if include:
            params["include[]"] = include

        response = await self._make_request(
            "GET", f"courses/{course_id}", params=params
        )
        course_data = response.json()
        return Course(**course_data)

    # Assignment methods
    async def get_assignments(
        self,
        course_id: int,
        include: Optional[List[str]] = None,
        per_page: Optional[int] = None,
    ) -> PaginatedResponse[Assignment]:
        """Get assignments for a course.

        Args:
            course_id: Course ID
            include: Additional data to include
            per_page: Number of assignments per page

        Returns:
            Paginated assignment response
        """
        params: Dict[str, Any] = {"per_page": per_page or self.per_page}
        if include:
            params["include[]"] = include

        response = await self._make_request(
            "GET", f"courses/{course_id}/assignments", params=params
        )
        assignments_data = response.json()
        assignments = [
            Assignment(**assignment_data) for assignment_data in assignments_data
        ]

        return PaginatedResponse.from_response(response, assignments)

    async def get_assignment(
        self,
        course_id: int,
        assignment_id: int,
        include: Optional[List[str]] = None,
    ) -> Assignment:
        """Get a specific assignment.

        Args:
            course_id: Course ID
            assignment_id: Assignment ID
            include: Additional data to include

        Returns:
            Assignment information
        """
        params = {}
        if include:
            params["include[]"] = include

        response = await self._make_request(
            "GET",
            f"courses/{course_id}/assignments/{assignment_id}",
            params=params,
        )
        assignment_data = response.json()
        return Assignment(**assignment_data)

    # Discussion methods
    async def get_discussions(
        self,
        course_id: int,
        per_page: Optional[int] = None,
    ) -> PaginatedResponse[Discussion]:
        """Get discussion topics for a course.

        Args:
            course_id: Course ID
            per_page: Number of discussions per page

        Returns:
            Paginated discussion response
        """
        params = {"per_page": per_page or self.per_page}

        response = await self._make_request(
            "GET", f"courses/{course_id}/discussion_topics", params=params
        )
        discussions_data = response.json()
        discussions = [
            Discussion(**discussion_data) for discussion_data in discussions_data
        ]

        return PaginatedResponse.from_response(response, discussions)

    # Page methods
    async def get_pages(
        self,
        course_id: int,
        per_page: Optional[int] = None,
    ) -> PaginatedResponse[Page]:
        """Get pages for a course.

        Args:
            course_id: Course ID
            per_page: Number of pages per page

        Returns:
            Paginated page response
        """
        params = {"per_page": per_page or self.per_page}

        response = await self._make_request(
            "GET", f"courses/{course_id}/pages", params=params
        )
        pages_data = response.json()
        pages = [Page(**page_data) for page_data in pages_data]

        return PaginatedResponse.from_response(response, pages)

    async def get_page(self, course_id: int, page_url: str) -> Page:
        """Get a specific page.

        Args:
            course_id: Course ID
            page_url: Page URL

        Returns:
            Page information
        """
        response = await self._make_request(
            "GET", f"courses/{course_id}/pages/{page_url}"
        )
        page_data = response.json()
        return Page(**page_data)

    # User methods
    async def get_users(
        self,
        course_id: int,
        enrollment_type: Optional[List[str]] = None,
        per_page: Optional[int] = None,
    ) -> PaginatedResponse[User]:
        """Get users enrolled in a course.

        Args:
            course_id: Course ID
            enrollment_type: Types of enrollments to include
            per_page: Number of users per page

        Returns:
            Paginated user response
        """
        params: Dict[str, Any] = {"per_page": per_page or self.per_page}
        if enrollment_type:
            params["enrollment_type[]"] = enrollment_type

        response = await self._make_request(
            "GET", f"courses/{course_id}/users", params=params
        )
        users_data = response.json()
        users = [User(**user_data) for user_data in users_data]

        return PaginatedResponse.from_response(response, users)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
