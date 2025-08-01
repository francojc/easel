"""Rate limiting for Canvas API requests."""

import asyncio
import time
from typing import Optional

from .exceptions import CanvasRateLimitError


class RateLimiter:
    """Token bucket rate limiter for Canvas API requests."""

    def __init__(self, requests_per_second: float = 10.0) -> None:
        """Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second allowed
        """
        self.requests_per_second = requests_per_second
        self.bucket_capacity = requests_per_second
        self.tokens = self.bucket_capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, timeout: Optional[float] = None) -> None:
        """Acquire permission to make a request.

        Args:
            timeout: Maximum time to wait for permission (seconds)

        Raises:
            CanvasRateLimitError: If timeout exceeded while waiting
        """
        start_time = time.monotonic()

        async with self._lock:
            while True:
                self._refill_bucket()

                if self.tokens >= 1:
                    self.tokens -= 1
                    return

                # Check timeout
                if timeout is not None:
                    elapsed = time.monotonic() - start_time
                    if elapsed >= timeout:
                        raise CanvasRateLimitError(
                            f"Rate limit timeout after {elapsed:.2f}s"
                        )

                # Wait for next token
                wait_time = 1.0 / self.requests_per_second
                await asyncio.sleep(wait_time)

    def _refill_bucket(self) -> None:
        """Refill the token bucket based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.requests_per_second
        self.tokens = min(self.bucket_capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def set_rate_limit(self, requests_per_second: float) -> None:
        """Update the rate limit.

        Args:
            requests_per_second: New rate limit
        """
        self.requests_per_second = requests_per_second
        self.bucket_capacity = requests_per_second

        # Don't exceed new capacity
        if self.tokens > self.bucket_capacity:
            self.tokens = self.bucket_capacity

    def get_current_rate(self) -> float:
        """Get current rate limit setting.

        Returns:
            Current requests per second limit
        """
        return self.requests_per_second

    def get_available_tokens(self) -> float:
        """Get number of available tokens in bucket.

        Returns:
            Number of available request tokens
        """
        self._refill_bucket()
        return self.tokens

    def reset(self) -> None:
        """Reset the rate limiter to full capacity."""
        self.tokens = self.bucket_capacity
        self.last_refill = time.monotonic()
