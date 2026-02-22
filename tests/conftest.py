"""Shared test fixtures for easel."""

import pytest

from easel.core.config import Config


@pytest.fixture()
def config():
    """Config with a fake token for testing."""
    return Config(
        canvas_api_token="fake-test-token",
        canvas_api_url="https://canvas.test/api/v1",
    )
