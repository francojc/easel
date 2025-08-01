"""Canvas API authentication."""

from typing import Dict, Optional

import httpx

from .exceptions import CanvasAuthError


class CanvasAuth:
    """Handles Canvas API authentication using Personal Access Tokens."""

    def __init__(self, api_token: str) -> None:
        """Initialize authentication with API token.

        Args:
            api_token: Canvas Personal Access Token
        """
        if not api_token:
            raise CanvasAuthError("API token is required")

        self.api_token = api_token

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary with Authorization header
        """
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def verify_token(self, base_url: str, client: httpx.AsyncClient) -> Dict:
        """Verify the API token by making a test request.

        Args:
            base_url: Canvas base URL
            client: HTTP client to use for the request

        Returns:
            User information if authentication successful

        Raises:
            CanvasAuthError: If authentication fails
        """
        url = f"{base_url}/api/v1/users/self"
        headers = self.get_headers()

        try:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise CanvasAuthError("Invalid API token")
            elif response.status_code == 403:
                raise CanvasAuthError("API token lacks required permissions")
            else:
                raise CanvasAuthError(
                    f"Authentication verification failed: HTTP {response.status_code}"
                )

        except httpx.RequestError as e:
            raise CanvasAuthError(f"Network error during authentication: {e}")

    def __str__(self) -> str:
        """String representation (masked token)."""
        masked = f"{self.api_token[:8]}...{self.api_token[-4:]}"
        return f"CanvasAuth(token={masked})"

    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
