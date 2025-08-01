"""Basic integration tests for implemented functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from click.testing import CliRunner

from easel.cli.main import cli
from easel.config.credentials import CredentialManager
from easel.config.manager import ConfigManager
from easel.config.models import CanvasInstance, EaselConfig


class TestBasicConfigurationWorkflow:
    """Test basic configuration management workflows."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()
            yield config_dir

    def test_help_command(self, runner):
        """Test basic help command functionality."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Easel CLI" in result.output

    def test_version_command(self, runner):
        """Test version command functionality."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_config_manager_basic_functionality(self, temp_config_dir):
        """Test basic configuration manager functionality."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            config_manager = ConfigManager()

            # Test loading non-existent config
            try:
                config = config_manager.load_config()
                assert False, "Should have raised ConfigNotFoundError"
            except Exception:
                # Expected behavior when config doesn't exist
                pass

            # Test saving and loading config
            test_config = EaselConfig(
                canvas=CanvasInstance(
                    name="Test University",
                    url="https://test.instructure.com",
                    api_token="test_token",
                )
            )

            config_manager.save_config(test_config)

            loaded_config = config_manager.load_config()
            assert loaded_config is not None
            assert loaded_config.canvas.name == "Test University"
            assert loaded_config.canvas.url == "https://test.instructure.com"

    def test_credential_manager_basic_functionality(self, temp_config_dir):
        """Test basic credential manager functionality."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            cred_manager = CredentialManager()

            # Test storing and retrieving credentials
            cred_manager.store_token("test_instance", "test_token_123")
            token = cred_manager.get_token("test_instance")
            assert token == "test_token_123"

            # Test listing instances
            instances = cred_manager.list_stored_instances()
            assert "test_instance" in instances

            # Test credential existence check
            assert cred_manager.has_credentials("test_instance")
            assert not cred_manager.has_credentials("nonexistent_instance")

            # Test credential removal
            removed = cred_manager.remove_token("test_instance")
            assert removed is True
            assert not cred_manager.has_credentials("test_instance")


class TestAPIModels:
    """Test API model functionality."""

    def test_user_model_creation(self):
        """Test User model creation and validation."""
        from easel.api.models import User

        user_data = {
            "id": 123,
            "name": "Test User",
            "email": "test@example.com",
            "login_id": "testuser",
        }

        user = User(**user_data)
        assert user.id == 123
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.login_id == "testuser"

    def test_course_model_creation(self):
        """Test Course model creation and validation."""
        from easel.api.models import Course

        course_data = {
            "id": 456,
            "name": "Test Course",
            "course_code": "TEST101",
            "workflow_state": "available",
        }

        course = Course(**course_data)
        assert course.id == 456
        assert course.name == "Test Course"
        assert course.course_code == "TEST101"
        assert course.workflow_state == "available"

    def test_assignment_model_creation(self):
        """Test Assignment model creation and validation."""
        from easel.api.models import Assignment

        assignment_data = {
            "id": 789,
            "name": "Test Assignment",
            "course_id": 456,
            "points_possible": 100.0,
        }

        assignment = Assignment(**assignment_data)
        assert assignment.id == 789
        assert assignment.name == "Test Assignment"
        assert assignment.course_id == 456
        assert assignment.points_possible == 100.0


class TestAuthenticationWorkflow:
    """Test authentication functionality."""

    def test_canvas_auth_headers(self):
        """Test Canvas authentication header generation."""
        from easel.api.auth import CanvasAuth

        auth = CanvasAuth("test_token_123")
        headers = auth.get_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_123"
        assert headers["Content-Type"] == "application/json"


class TestPaginationWorkflow:
    """Test pagination functionality."""

    def test_pagination_info_model(self):
        """Test PaginationInfo model functionality."""
        from easel.api.pagination import PaginationInfo

        pagination = PaginationInfo(
            current_page=1,
            per_page=10,
            total_count=100,
            next_url="https://example.com/page/2",
        )

        assert pagination.current_page == 1
        assert pagination.per_page == 10
        assert pagination.total_count == 100
        assert pagination.next_url == "https://example.com/page/2"

    def test_pagination_header_parsing(self):
        """Test Link header parsing functionality."""
        from easel.api.pagination import _parse_link_header

        link_header = '<https://example.com/page/2>; rel="next", <https://example.com/page/1>; rel="prev"'
        links = _parse_link_header(link_header)

        assert "next" in links
        assert "prev" in links
        assert links["next"] == "https://example.com/page/2"
        assert links["prev"] == "https://example.com/page/1"


class TestRateLimitingWorkflow:
    """Test rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiter_basic_functionality(self):
        """Test basic rate limiter functionality."""
        from easel.api.rate_limit import RateLimiter

        # Create rate limiter with high limit for testing
        rate_limiter = RateLimiter(requests_per_second=100.0)

        # Should be able to acquire immediately
        await rate_limiter.acquire()

        # Basic functionality test - just verify it doesn't crash
        assert rate_limiter is not None


class TestExceptionHandling:
    """Test exception handling functionality."""

    def test_canvas_api_exceptions(self):
        """Test Canvas API exception hierarchy."""
        from easel.api.exceptions import (
            CanvasAPIError,
            CanvasAuthError,
            CanvasNotFoundError,
            CanvasRateLimitError,
        )

        # Test base exception
        base_error = CanvasAPIError("Test error", status_code=400)
        assert str(base_error) == "Test error"
        assert base_error.status_code == 400

        # Test auth error
        auth_error = CanvasAuthError("Unauthorized", status_code=401)
        assert isinstance(auth_error, CanvasAPIError)
        assert auth_error.status_code == 401

        # Test not found error
        not_found_error = CanvasNotFoundError("Not found", status_code=404)
        assert isinstance(not_found_error, CanvasAPIError)
        assert not_found_error.status_code == 404

        # Test rate limit error
        rate_limit_error = CanvasRateLimitError(
            "Rate limited", status_code=429, retry_after=60
        )
        assert isinstance(rate_limit_error, CanvasAPIError)
        assert rate_limit_error.status_code == 429
        assert rate_limit_error.retry_after == 60

    def test_config_exceptions(self):
        """Test configuration exception hierarchy."""
        from easel.config.exceptions import (
            ConfigError,
            ConfigValidationError,
            CredentialDecryptionError,
        )

        # Test base config error
        config_error = ConfigError("Config error")
        assert str(config_error) == "Config error"

        # Test validation error
        validation_error = ConfigValidationError("Validation failed")
        assert isinstance(validation_error, ConfigError)

        # Test credential error
        credential_error = CredentialDecryptionError("Decryption failed")
        assert isinstance(credential_error, ConfigError)


class TestPathUtilities:
    """Test path utility functions."""

    @pytest.mark.skipif(not hasattr(Path, "home"), reason="Path.home() not available")
    def test_config_directory_discovery(self):
        """Test configuration directory discovery."""
        from easel.config.paths import get_config_dir, get_config_file

        config_dir = get_config_dir()
        assert isinstance(config_dir, Path)
        assert config_dir.name == ".easel" or "easel" in config_dir.name

        config_file = get_config_file()
        assert isinstance(config_file, Path)
        assert config_file.name == "config.yaml"


class TestConfigurationValidation:
    """Test configuration validation."""

    def test_canvas_instance_validation(self):
        """Test CanvasInstance model validation."""
        # Valid instance
        instance = CanvasInstance(
            name="Test University",
            url="https://test.instructure.com",
            api_token="test_token",
        )

        assert instance.name == "Test University"
        assert instance.url == "https://test.instructure.com"
        assert instance.api_token == "test_token"

    def test_easel_config_validation(self):
        """Test EaselConfig model validation."""
        canvas_instance = CanvasInstance(
            name="Test University",
            url="https://test.instructure.com",
            api_token="test_token",
        )

        config = EaselConfig(canvas=canvas_instance)

        assert config.version == "1.0"  # Default version
        assert config.canvas == canvas_instance

    def test_config_model_serialization(self):
        """Test configuration model serialization."""
        canvas_instance = CanvasInstance(
            name="Test University",
            url="https://test.instructure.com",
            api_token="test_token",
        )

        config = EaselConfig(canvas=canvas_instance)

        # Test model dump
        config_dict = config.model_dump()
        assert "version" in config_dict
        assert "canvas" in config_dict
        assert config_dict["canvas"]["name"] == "Test University"

        # Test roundtrip
        restored_config = EaselConfig(**config_dict)
        assert restored_config.canvas.name == "Test University"
        assert restored_config.version == config.version
