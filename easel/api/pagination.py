"""Pagination support for Canvas API responses."""

import re
from typing import Optional, Dict, Any, List, AsyncIterator, TypeVar, Generic
from urllib.parse import parse_qs, urlparse

import httpx
from pydantic import BaseModel

T = TypeVar("T")


class PaginationInfo(BaseModel):
    """Information about pagination state."""

    current_page: Optional[int] = None
    per_page: Optional[int] = None
    total_count: Optional[int] = None
    first_url: Optional[str] = None
    prev_url: Optional[str] = None
    next_url: Optional[str] = None
    last_url: Optional[str] = None


class PaginatedResponse(Generic[T]):
    """Container for paginated API responses."""

    def __init__(
        self,
        items: List[T],
        pagination: PaginationInfo,
        raw_response: httpx.Response,
    ) -> None:
        """Initialize paginated response.

        Args:
            items: List of items in current page
            pagination: Pagination metadata
            raw_response: Raw HTTP response
        """
        self.items = items
        self.pagination = pagination
        self.raw_response = raw_response

    @classmethod
    def from_response(
        cls,
        response: httpx.Response,
        items: List[T],
    ) -> "PaginatedResponse[T]":
        """Create paginated response from HTTP response.

        Args:
            response: HTTP response with pagination headers
            items: Parsed items from response body

        Returns:
            PaginatedResponse instance
        """
        pagination = cls._parse_pagination_headers(response)
        return cls(items, pagination, response)

    @staticmethod
    def _parse_pagination_headers(response: httpx.Response) -> PaginationInfo:
        """Parse Canvas pagination headers.

        Args:
            response: HTTP response with Link header

        Returns:
            Parsed pagination information
        """
        pagination = PaginationInfo()

        # Parse Link header for pagination URLs
        link_header = response.headers.get("Link")
        if link_header:
            links = _parse_link_header(link_header)
            pagination.first_url = links.get("first")
            pagination.prev_url = links.get("prev")
            pagination.next_url = links.get("next")
            pagination.last_url = links.get("last")

        # Parse current page info from request URL
        request_url = str(response.request.url)
        parsed_url = urlparse(request_url)
        query_params = parse_qs(parsed_url.query)

        if "page" in query_params:
            try:
                pagination.current_page = int(query_params["page"][0])
            except (ValueError, IndexError):
                pass

        if "per_page" in query_params:
            try:
                pagination.per_page = int(query_params["per_page"][0])
            except (ValueError, IndexError):
                pass

        # Canvas sometimes includes total count in X-Total header
        total_header = response.headers.get("X-Total")
        if total_header:
            try:
                pagination.total_count = int(total_header)
            except ValueError:
                pass

        return pagination

    def has_next_page(self) -> bool:
        """Check if there is a next page available.

        Returns:
            True if next page exists
        """
        return self.pagination.next_url is not None

    def has_prev_page(self) -> bool:
        """Check if there is a previous page available.

        Returns:
            True if previous page exists
        """
        return self.pagination.prev_url is not None

    def get_next_page_url(self) -> Optional[str]:
        """Get URL for next page.

        Returns:
            Next page URL or None
        """
        return self.pagination.next_url

    def get_prev_page_url(self) -> Optional[str]:
        """Get URL for previous page.

        Returns:
            Previous page URL or None
        """
        return self.pagination.prev_url

    def __len__(self) -> int:
        """Number of items in current page."""
        return len(self.items)

    def __iter__(self):
        """Iterate over items in current page."""
        return iter(self.items)

    def __getitem__(self, index):
        """Get item by index."""
        return self.items[index]


class PaginatedIterator(Generic[T]):
    """Async iterator for paginated Canvas API responses."""

    def __init__(
        self,
        client,  # CanvasClient
        initial_response: PaginatedResponse[T],
        item_parser: callable,
    ) -> None:
        """Initialize paginated iterator.

        Args:
            client: Canvas API client
            initial_response: First page response
            item_parser: Function to parse items from response data
        """
        self.client = client
        self.current_response = initial_response
        self.item_parser = item_parser
        self._current_index = 0

    def __aiter__(self) -> AsyncIterator[T]:
        """Async iterator protocol."""
        return self

    async def __anext__(self) -> T:
        """Get next item across all pages."""
        # If we've exhausted current page, try to get next page
        if self._current_index >= len(self.current_response.items):
            if not self.current_response.has_next_page():
                raise StopAsyncIteration

            # Fetch next page
            next_url = self.current_response.get_next_page_url()
            response = await self.client._make_request("GET", url=next_url)
            items = [self.item_parser(item) for item in response.json()]
            self.current_response = PaginatedResponse.from_response(response, items)
            self._current_index = 0

        # Return current item and advance index
        item = self.current_response.items[self._current_index]
        self._current_index += 1
        return item

    async def collect_all(self, limit: Optional[int] = None) -> List[T]:
        """Collect all items from all pages into a single list.

        Args:
            limit: Maximum number of items to collect

        Returns:
            List of all items across pages
        """
        all_items = []
        count = 0

        async for item in self:
            all_items.append(item)
            count += 1

            if limit and count >= limit:
                break

        return all_items


def _parse_link_header(link_header: str) -> Dict[str, str]:
    """Parse HTTP Link header into a dictionary.

    Args:
        link_header: Link header value

    Returns:
        Dictionary mapping rel values to URLs
    """
    links = {}

    # Split by comma to get individual links
    for link in link_header.split(","):
        link = link.strip()

        # Extract URL and rel using regex
        match = re.match(r'<([^>]+)>;\s*rel="([^"]+)"', link)
        if match:
            url, rel = match.groups()
            links[rel] = url

    return links
