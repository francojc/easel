"""Canvas API configuration via environment variables."""

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Canvas LMS API configuration.

    Reads from environment variables:
      CANVAS_API_TOKEN  — required
      CANVAS_API_URL    — default https://canvas.illinois.edu/api/v1
      API_TIMEOUT       — default 30 (seconds)
      CACHE_TTL         — default 300 (seconds)
    """

    canvas_api_token: str = ""
    canvas_api_url: str = "https://canvas.illinois.edu/api/v1"
    api_timeout: int = 30
    cache_ttl: int = 300

    @field_validator("canvas_api_url")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    def validate_config(self) -> None:
        """Raise ValueError if required settings are missing."""
        if not self.canvas_api_token:
            raise ValueError(
                "CANVAS_API_TOKEN environment variable is required. "
                "Set it to your Canvas API access token."
            )
