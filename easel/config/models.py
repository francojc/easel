"""Pydantic models for Easel configuration validation."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CanvasInstance(BaseModel):
    """Configuration for a Canvas instance."""

    name: str = Field(..., description="Human-readable name for this Canvas instance")
    url: str = Field(
        ...,
        description="Canvas base URL (e.g., " "https://university.instructure.com)",
    )
    api_token: Optional[str] = Field(
        None, description="Canvas API token (stored separately)"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate and normalize Canvas URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip("/")


class APISettings(BaseModel):
    """API client configuration settings."""

    rate_limit: int = Field(10, description="Requests per second limit", ge=1, le=100)
    timeout: int = Field(30, description="Request timeout in seconds", ge=5, le=300)
    retries: int = Field(3, description="Number of retry attempts", ge=0, le=10)
    page_size: int = Field(100, description="Default pagination size", ge=10, le=1000)


class CacheSettings(BaseModel):
    """Cache configuration settings."""

    enabled: bool = Field(True, description="Enable response caching")
    ttl: int = Field(300, description="Cache time-to-live in seconds", ge=0)
    max_size: int = Field(1000, description="Maximum cache entries", ge=0)


class LoggingSettings(BaseModel):
    """Logging configuration settings."""

    level: str = Field("INFO", description="Logging level")
    file: Optional[Path] = Field(None, description="Log file path")
    format: str = Field("human", description="Log format (human|json)")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid log level. Must be one of: {', '.join(valid_levels)}"
            )
        return v_upper

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate log format."""
        valid_formats = {"human", "json"}
        if v not in valid_formats:
            raise ValueError(
                f"Invalid log format. Must be one of: " f"{', '.join(valid_formats)}"
            )
        return v


class EaselConfig(BaseModel):
    """Main Easel configuration model."""

    version: str = Field("1.0", description="Configuration version")
    canvas: CanvasInstance
    api: APISettings = Field(default_factory=lambda: APISettings())
    cache: CacheSettings = Field(default_factory=lambda: CacheSettings())
    logging: LoggingSettings = Field(default_factory=lambda: LoggingSettings())

    # Configuration for environment variable reading
    # model_config = ConfigDict(env_prefix="EASEL_", env_nested_delimiter="__")
