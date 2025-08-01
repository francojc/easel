"""Integration tests for Canvas API client workflows."""

import asyncio
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from easel.api.auth import CanvasAuth
from easel.api.client import CanvasClient
from easel.api.exceptions import (
    CanvasAPIError,
    CanvasAuthError,
    CanvasNotFoundError,
    CanvasRateLimitError,
    CanvasServerError,
    CanvasTimeoutError,
)
from easel.api.models import Course, User, Assignment
from easel.api.pagination import PaginatedResponse


class TestAPIClientWorkflows:
    """Test Canvas API client integration workflows."""

    @pytest.fixture
    def auth(self):
        """Create test authentication."""
        return CanvasAuth("test_token_123")

    @pytest.fixture
    def client(self, auth):
        """Create test API client."""
        return CanvasClient(
            base_url="https://test.instructure.com",
            auth=auth,
            rate_limit=10.0,
            timeout=30.0,
        )

    @pytest.fixture
    def mock_user_response(self):
        """Mock user API response."""
        return {
            "id": 123,
            "name": "Test User",
            "email": "test@university.edu",
            "login_id": "testuser",
            "avatar_url": "https://example.com/avatar.jpg",
        }

    @pytest.fixture
    def mock_course_response(self):
        """Mock course API response."""
        return {
            "id": 456,
            "name": "Test Course",
            "course_code": "TEST101",
            "workflow_state": "available",
            "start_at": "2024-01-15T08:00:00Z",
            "end_at": "2024-05-15T17:00:00Z",
            "enrollment_term_id": 1,
        }

    @pytest.fixture
    def mock_assignment_response(self):
        """Mock assignment API response."""
        return {
            "id": 789,
            "name": "Test Assignment",
            "description": "Test assignment description",
            "points_possible": 100.0,
            "due_at": "2024-02-15T23:59:59Z",
            "submission_types": ["online_text_entry"],
            "course_id": 456,
        }

    @pytest.mark.asyncio
    async def test_verify_connection_success(self, client, mock_user_response):
        """Test successful API connection verification."""
        with patch("easel.api.client.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()

            # Mock successful response
            mock_response = AsyncMock()
            mock_response.is_success = True
            mock_response.json.return_value = mock_user_response
            mock_client.request = AsyncMock(return_value=mock_response)

            async with client:
                user = await client.verify_connection()

                assert isinstance(user, User)
                assert user.id == 123
                assert user.name == "Test User"
                assert user.email == "test@university.edu"

    @pytest.mark.asyncio
    async def test_verify_connection_auth_failure(self, client):
        """Test API connection verification with authentication failure."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock auth failure response
            mock_response = AsyncMock()
            mock_response.is_success = False
            mock_response.status_code = 401
            mock_response.json.return_value = {"message": "Invalid access token"}
            mock_client.request.return_value = mock_response

            async with client:
                with pytest.raises(CanvasAuthError) as exc_info:
                    await client.verify_connection()

                assert exc_info.value.status_code == 401
                assert "Invalid access token" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_courses_success(self, client, mock_course_response):
        """Test successful course retrieval."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock successful response with pagination headers
            mock_response = AsyncMock()
            mock_response.is_success = True
            mock_response.json.return_value = [mock_course_response]
            mock_response.headers = {
                "Link": '<https://test.instructure.com/api/v1/courses?page=2>; rel="next"'
            }
            mock_response.request.url = (
                "https://test.instructure.com/api/v1/courses?page=1"
            )
            mock_client.request.return_value = mock_response

            async with client:
                courses_response = await client.get_courses()

                assert isinstance(courses_response, PaginatedResponse)
                assert len(courses_response.items) == 1

                course = courses_response.items[0]
                assert isinstance(course, Course)
                assert course.id == 456
                assert course.name == "Test Course"
                assert course.course_code == "TEST101"

    @pytest.mark.asyncio
    async def test_get_assignments_success(self, client, mock_assignment_response):
        """Test successful assignment retrieval."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock successful response
            mock_response = AsyncMock()
            mock_response.is_success = True
            mock_response.json.return_value = [mock_assignment_response]
            mock_response.headers = {}
            mock_response.request.url = (
                "https://test.instructure.com/api/v1/courses/456/assignments"
            )
            mock_client.request.return_value = mock_response

            async with client:
                assignments_response = await client.get_assignments(course_id=456)

                assert isinstance(assignments_response, PaginatedResponse)
                assert len(assignments_response.items) == 1

                assignment = assignments_response.items[0]
                assert isinstance(assignment, Assignment)
                assert assignment.id == 789
                assert assignment.name == "Test Assignment"
                assert assignment.points_possible == 100.0

    @pytest.mark.asyncio
    async def test_rate_limiting_workflow(self, client, mock_user_response):
        """Test rate limiting behavior in API workflows."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock rate limit response first, then success
            rate_limit_response = AsyncMock()
            rate_limit_response.is_success = False
            rate_limit_response.status_code = 429
            rate_limit_response.headers = {"Retry-After": "1"}
            rate_limit_response.json.return_value = {"message": "Rate limit exceeded"}

            success_response = AsyncMock()
            success_response.is_success = True
            success_response.json.return_value = mock_user_response

            # First call returns rate limit, second succeeds
            mock_client.request.side_effect = [rate_limit_response, success_response]

            async with client:
                # Should retry after rate limit and succeed
                user = await client.verify_connection()

                assert isinstance(user, User)
                assert user.id == 123
                assert mock_client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_timeout_retry_workflow(self, client):
        """Test timeout retry behavior."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock timeout exception
            mock_client.request.side_effect = httpx.TimeoutException("Request timeout")

            async with client:
                with pytest.raises(CanvasTimeoutError):
                    await client.verify_connection()

                # Should retry max_retries + 1 times
                assert mock_client.request.call_count == client.max_retries + 1

    @pytest.mark.asyncio
    async def test_server_error_handling(self, client):
        """Test server error handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock server error response
            mock_response = AsyncMock()
            mock_response.is_success = False
            mock_response.status_code = 500
            mock_response.json.return_value = {"message": "Internal server error"}
            mock_client.request.return_value = mock_response

            async with client:
                with pytest.raises(CanvasServerError) as exc_info:
                    await client.verify_connection()

                assert exc_info.value.status_code == 500
                assert "Internal server error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_not_found_error_handling(self, client):
        """Test not found error handling."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock not found response
            mock_response = AsyncMock()
            mock_response.is_success = False
            mock_response.status_code = 404
            mock_response.json.return_value = {"message": "Not found"}
            mock_client.request.return_value = mock_response

            async with client:
                with pytest.raises(CanvasNotFoundError) as exc_info:
                    await client.get_course(999999)

                assert exc_info.value.status_code == 404
                assert "Not found" in str(exc_info.value)


class TestPaginationWorkflows:
    """Test pagination integration workflows."""

    @pytest.fixture
    def auth(self):
        """Create test authentication."""
        return CanvasAuth("test_token_123")

    @pytest.fixture
    def client(self, auth):
        """Create test API client."""
        return CanvasClient(
            url="https://test.instructure.com",
            auth=auth,
            per_page=2,  # Small page size for testing
        )

    @pytest.fixture
    def mock_courses_page1(self):
        """Mock first page of courses."""
        return [
            {
                "id": 1,
                "name": "Course 1",
                "course_code": "COURSE1",
                "workflow_state": "available",
            },
            {
                "id": 2,
                "name": "Course 2",
                "course_code": "COURSE2",
                "workflow_state": "available",
            },
        ]

    @pytest.fixture
    def mock_courses_page2(self):
        """Mock second page of courses."""
        return [
            {
                "id": 3,
                "name": "Course 3",
                "course_code": "COURSE3",
                "workflow_state": "available",
            },
        ]

    @pytest.mark.asyncio
    async def test_multi_page_course_retrieval(
        self, client, mock_courses_page1, mock_courses_page2
    ):
        """Test retrieving courses across multiple pages."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock responses for two pages
            page1_response = AsyncMock()
            page1_response.is_success = True
            page1_response.json.return_value = mock_courses_page1
            page1_response.headers = {
                "Link": '<https://test.instructure.com/api/v1/courses?page=2>; rel="next"'
            }
            page1_response.request.url = (
                "https://test.instructure.com/api/v1/courses?page=1"
            )

            page2_response = AsyncMock()
            page2_response.is_success = True
            page2_response.json.return_value = mock_courses_page2
            page2_response.headers = {}
            page2_response.request.url = (
                "https://test.instructure.com/api/v1/courses?page=2"
            )

            mock_client.request.side_effect = [page1_response, page2_response]

            async with client:
                # Get first page
                first_page = await client.get_courses()

                assert len(first_page.items) == 2
                assert first_page.has_next_page()

                # Get second page using the client's _make_request method
                second_page_url = first_page.get_next_page_url()
                assert second_page_url is not None

                # Verify pagination info
                assert first_page.pagination.next_url == second_page_url

    @pytest.mark.asyncio
    async def test_empty_page_handling(self, client):
        """Test handling of empty API responses."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock empty response
            mock_response = AsyncMock()
            mock_response.is_success = True
            mock_response.json.return_value = []
            mock_response.headers = {}
            mock_response.request.url = "https://test.instructure.com/api/v1/courses"
            mock_client.request.return_value = mock_response

            async with client:
                courses_response = await client.get_courses()

                assert isinstance(courses_response, PaginatedResponse)
                assert len(courses_response.items) == 0
                assert not courses_response.has_next_page()


class TestAPIAuthenticationWorkflows:
    """Test API authentication integration workflows."""

    def test_auth_header_creation(self):
        """Test authentication header creation."""
        auth = CanvasAuth("test_token_123")
        headers = auth.get_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_123"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_auth_integration_with_client(self):
        """Test authentication integration with client."""
        auth = CanvasAuth("test_token_123")
        client = CanvasClient(
            url="https://test.instructure.com",
            auth=auth,
        )

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            async with client:
                # Verify that client is initialized with auth headers
                mock_client_class.assert_called_once()
                call_kwargs = mock_client_class.call_args[1]

                assert "headers" in call_kwargs
                headers = call_kwargs["headers"]
                assert headers["Authorization"] == "Bearer test_token_123"

    @pytest.mark.asyncio
    async def test_token_refresh_workflow(self):
        """Test token refresh workflow (placeholder for future implementation)."""
        # This test documents the expected behavior for future token refresh feature
        auth = CanvasAuth("test_token_123")

        # Verify current token
        assert auth.api_token == "test_token_123"

        # Future: Test token refresh logic
        # new_token = await auth.refresh_token()
        # assert new_token != "test_token_123"
        # assert auth.token == new_token


class TestErrorRecoveryWorkflows:
    """Test error recovery and resilience workflows."""

    @pytest.fixture
    def auth(self):
        """Create test authentication."""
        return CanvasAuth("test_token_123")

    @pytest.fixture
    def client(self, auth):
        """Create test API client."""
        return CanvasClient(
            url="https://test.instructure.com",
            auth=auth,
            max_retries=2,  # Lower for faster tests
        )

    @pytest.mark.asyncio
    async def test_network_failure_recovery(self, client):
        """Test recovery from temporary network failures."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock network failure then success
            mock_response = AsyncMock()
            mock_response.is_success = True
            mock_response.json.return_value = {"id": 123, "name": "Test User"}

            mock_client.request.side_effect = [
                httpx.ConnectError("Connection failed"),
                mock_response,
            ]

            async with client:
                user = await client.verify_connection()

                assert isinstance(user, User)
                assert user.id == 123
                assert mock_client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_persistent_failure_handling(self, client):
        """Test handling of persistent failures."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock persistent network failure
            mock_client.request.side_effect = httpx.ConnectError("Connection failed")

            async with client:
                with pytest.raises(CanvasAPIError):
                    await client.verify_connection()

                # Should retry max_retries + 1 times
                assert mock_client.request.call_count == client.max_retries + 1

    @pytest.mark.asyncio
    async def test_partial_response_handling(self, client):
        """Test handling of partial or malformed responses."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock response with invalid JSON
            mock_response = AsyncMock()
            mock_response.is_success = True
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_client.request.return_value = mock_response

            async with client:
                with pytest.raises(CanvasAPIError):
                    await client.verify_connection()


class TestConcurrentAPIWorkflows:
    """Test concurrent API operation workflows."""

    @pytest.fixture
    def auth(self):
        """Create test authentication."""
        return CanvasAuth("test_token_123")

    @pytest.fixture
    def client(self, auth):
        """Create test API client."""
        return CanvasClient(
            url="https://test.instructure.com",
            auth=auth,
            rate_limit=5.0,  # Lower rate limit for testing
        )

    @pytest.mark.asyncio
    async def test_concurrent_requests_rate_limiting(self, client):
        """Test rate limiting with concurrent requests."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Mock successful responses
            mock_response = AsyncMock()
            mock_response.is_success = True
            mock_response.json.return_value = {"id": 123, "name": "Test User"}
            mock_client.request.return_value = mock_response

            async with client:
                # Make multiple concurrent requests
                tasks = [
                    client.verify_connection(),
                    client.verify_connection(),
                    client.verify_connection(),
                ]

                users = await asyncio.gather(*tasks)

                # All should succeed
                assert len(users) == 3
                for user in users:
                    assert isinstance(user, User)
                    assert user.id == 123

                # Should have made 3 requests
                assert mock_client.request.call_count == 3
