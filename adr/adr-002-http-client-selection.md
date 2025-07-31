# ADR 002: HTTP Client Selection

**Status:** Accepted  
**Date:** 2025-07-31  
**Deciders:** Jerid Francom, Development Team  
**Technical Story:** Foundation for Canvas API communication and request handling  

## Context and Problem Statement

Easel requires a robust HTTP client to communicate with the Canvas REST API. The client must handle authentication, rate limiting, pagination, error handling, and potentially large file downloads/uploads. Given Canvas API's complexity and rate limiting requirements, the HTTP client choice is critical for performance and reliability.

The client must support:

- Bearer token authentication
- Request/response interceptors for rate limiting
- Async/await patterns for concurrent operations
- Connection pooling and keep-alive
- Timeout handling and retry logic
- Large file handling with streaming
- Comprehensive error handling

## Decision Drivers

- **Performance:** Efficient handling of concurrent requests and large responses
- **Rate Limiting:** Built-in or easy-to-implement rate limiting capabilities
- **Future-Proofing:** Async/await support for scalability
- **Reliability:** Robust error handling and retry mechanisms
- **Ecosystem:** Active development and community support
- **Canvas Compatibility:** Proven to work well with Canvas API patterns

## Considered Options

- **httpx** - Modern async-first HTTP client
- **requests** - Traditional synchronous HTTP library
- **aiohttp** - Async HTTP client and server framework
- **urllib3** - Low-level HTTP client library

## Decision Outcome

**Chosen option:** "httpx"

**Rationale:** httpx provides the best combination of modern async support, requests-compatible API, and built-in features needed for Canvas API integration. It offers both sync and async interfaces, excellent performance, and is specifically designed for the kind of API client we're building.

### Positive Consequences

- Built-in async/await support enables concurrent operations
- Requests-compatible API reduces learning curve
- Excellent HTTP/2 and HTTP/3 support for future Canvas upgrades
- Built-in connection pooling and keep-alive
- Comprehensive timeout and retry configuration
- Active development and strong ecosystem

### Negative Consequences

- Additional dependency beyond requests
- Some team members may need to learn async patterns
- Slightly more complex setup than simple requests usage

## Pros and Cons of the Options

### httpx

**Description:** Modern HTTP client with async/await support and requests-compatible API

**Pros:**

- Full async/await support for concurrent operations
- Requests-compatible synchronous API for gradual migration
- Built-in HTTP/2 and HTTP/3 support
- Excellent connection pooling and performance
- Built-in timeout and retry configuration
- Streaming request/response support for large files
- Comprehensive middleware support for rate limiting
- Active development and modern Python practices

**Cons:**

- Additional learning curve for async programming
- Newer library with smaller ecosystem than requests
- More complex setup for advanced features

### requests

**Description:** The de facto standard HTTP library for Python

**Pros:**

- Extremely familiar to Python developers
- Massive ecosystem and community support
- Simple and intuitive API
- Battle-tested in production environments
- Extensive documentation and examples

**Cons:**

- Synchronous only - limits concurrency options
- No built-in async support for future scalability
- Manual implementation required for advanced rate limiting
- Connection pooling configuration more complex
- Less efficient for high-throughput scenarios

### aiohttp

**Description:** Async HTTP client and server framework

**Pros:**

- Full async/await support with excellent performance
- Built-in session management and connection pooling
- Comprehensive middleware system
- Active development in async ecosystem

**Cons:**

- Client and server combined - unnecessary complexity for our use case
- Different API from requests - steeper learning curve
- More complex setup and configuration
- Primarily focused on web server development

### urllib3

**Description:** Low-level HTTP client library underlying requests

**Pros:**

- Maximum control over HTTP behavior
- No additional dependencies
- Excellent performance and flexibility
- Used by requests internally

**Cons:**

- Very low-level API requiring significant boilerplate
- Manual implementation of common patterns
- No built-in async support
- Steep learning curve for team members

## Implementation Notes

### Basic Client Setup

```python
import httpx
from typing import Optional, Dict, Any
import asyncio

class CanvasAPIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        
        # Configure httpx client with sensible defaults
        self.client = httpx.AsyncClient(
            base_url=f"{self.base_url}/api/v1",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=5)
        )
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated GET request to Canvas API"""
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_paginated(self, endpoint: str, params: Optional[Dict] = None):
        """Handle Canvas API pagination automatically"""
        url = endpoint
        while url:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            # Yield page results
            data = response.json()
            for item in data:
                yield item
            
            # Check for next page
            links = response.headers.get('Link', '')
            url = self._parse_next_link(links)
            params = None  # Only use params on first request
```

### Rate Limiting Implementation

```python
import asyncio
from time import time

class RateLimiter:
    def __init__(self, max_requests: int = 10, time_window: int = 1):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make a request"""
        now = time()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        # Wait if we've hit the limit
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.requests.append(now)

# Integration with httpx
class RateLimitedClient:
    def __init__(self, *args, **kwargs):
        self.client = httpx.AsyncClient(*args, **kwargs)
        self.rate_limiter = RateLimiter()
    
    async def request(self, method: str, url: str, **kwargs):
        await self.rate_limiter.acquire()
        return await self.client.request(method, url, **kwargs)
```

### Error Handling and Retry Logic

```python
import httpx
from typing import Optional
import asyncio
import random

async def make_request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    max_retries: int = 3,
    **kwargs
) -> httpx.Response:
    """Make HTTP request with exponential backoff retry"""
    
    for attempt in range(max_retries + 1):
        try:
            response = await client.request(method, url, **kwargs)
            
            # Don't retry on client errors (4xx)
            if 400 <= response.status_code < 500:
                response.raise_for_status()
            
            # Retry on server errors (5xx) and specific client errors
            if response.status_code >= 500 or response.status_code == 429:
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)
                    continue
            
            response.raise_for_status()
            return response
            
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            if attempt < max_retries:
                delay = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)
                continue
            raise
    
    # This should never be reached, but just in case
    raise httpx.RequestError("Max retries exceeded")
```

### Sync/Async Compatibility

```python
# Provide both sync and async interfaces
class CanvasAPI:
    def __init__(self, base_url: str, token: str):
        self.async_client = AsyncCanvasAPI(base_url, token)
    
    def get_courses(self) -> List[Dict]:
        """Synchronous interface for simple usage"""
        return asyncio.run(self.async_client.get_courses())
    
    async def get_courses_async(self) -> List[Dict]:
        """Async interface for advanced usage"""
        return await self.async_client.get_courses()
```

## Links

- [httpx Documentation](https://www.python-httpx.org/)
- [httpx GitHub Repository](https://github.com/encode/httpx)
- [Canvas API Rate Limiting](https://canvas.instructure.com/doc/api/file.throttling.html)
- [Async Programming in Python](https://docs.python.org/3/library/asyncio.html)