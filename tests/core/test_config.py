"""Tests for easel.core.config."""

import pytest

from easel.core.config import Config


def test_defaults():
    """Config loads with defaults when env vars are empty."""
    cfg = Config(canvas_api_token="test-token")
    assert cfg.canvas_api_url == "https://canvas.illinois.edu/api/v1"
    assert cfg.api_timeout == 30
    assert cfg.cache_ttl == 300


def test_trailing_slash_stripped():
    cfg = Config(
        canvas_api_token="t",
        canvas_api_url="https://example.com/api/v1/",
    )
    assert not cfg.canvas_api_url.endswith("/")


def test_validate_missing_token():
    cfg = Config(canvas_api_token="")
    with pytest.raises(ValueError, match="CANVAS_API_KEY"):
        cfg.validate_config()


def test_validate_with_token():
    cfg = Config(canvas_api_token="some-token")
    cfg.validate_config()  # should not raise
