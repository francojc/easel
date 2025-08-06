"""Unit tests for user commands."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from easel.cli.main import cli
from easel.config.manager import ConfigManager
from easel.config.models import CanvasInstance, EaselConfig


class TestUserCommands:
    """Test user commands functionality."""

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

    @pytest.fixture
    def mock_config(self, temp_config_dir):
        """Mock configuration setup."""
        with patch("easel.config.paths.get_config_dir", return_value=temp_config_dir):
            config_manager = ConfigManager()
            test_config = EaselConfig(
                canvas=CanvasInstance(
                    name="Test University",
                    url="https://test.instructure.com",
                    api_token="test_token_123",
                )
            )
            config_manager.save_config(test_config)
            yield config_manager

    def test_user_profile_help(self, runner):
        """Test user profile help command."""
        result = runner.invoke(cli, ["user", "profile", "--help"])
        assert result.exit_code == 0
        assert "Show current user" in result.output

    def test_user_courses_help(self, runner):
        """Test user courses help command."""
        result = runner.invoke(cli, ["user", "courses", "--help"])
        assert result.exit_code == 0
        assert "List courses" in result.output
        assert "--role" in result.output
        assert "--state" in result.output

    def test_user_roster_help(self, runner):
        """Test user roster help command."""
        result = runner.invoke(cli, ["user", "roster", "--help"])
        assert result.exit_code == 0
        assert "List users enrolled" in result.output
        assert "COURSE_ID" in result.output

    @patch("easel.cli.commands.user.asyncio.run")
    @patch("easel.cli.commands.user.CanvasClient")
    def test_user_profile_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful user profile command."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock user data
        mock_user = AsyncMock(
            model_dump=lambda: {
                "id": 456,
                "name": "Test User",
                "email": "test@example.com",
                "login_id": "testuser",
            }
        )
        mock_client.verify_connection.return_value = mock_user

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_user

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config.config_dir
        ):
            result = runner.invoke(cli, ["user", "profile", "--format", "json"])

        assert result.exit_code == 0
        mock_client.verify_connection.assert_called_once()

    @patch("easel.cli.commands.user.asyncio.run")
    @patch("easel.cli.commands.user.CanvasClient")
    def test_user_courses_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful user courses command."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock response
        mock_response = AsyncMock()
        mock_response.data = [
            AsyncMock(
                model_dump=lambda: {
                    "id": 123,
                    "name": "Test Course",
                    "course_code": "TEST101",
                    "workflow_state": "available",
                }
            )
        ]
        mock_response.has_next_page = False
        mock_client.get_courses.return_value = mock_response

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_response.data

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config.config_dir
        ):
            result = runner.invoke(cli, ["user", "courses", "--format", "json"])

        assert result.exit_code == 0
        mock_client.get_courses.assert_called_once()

    @patch("easel.cli.commands.user.asyncio.run")
    @patch("easel.cli.commands.user.CanvasClient")
    def test_user_roster_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful user roster command."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock response
        mock_response = AsyncMock()
        mock_response.data = [
            AsyncMock(
                model_dump=lambda: {
                    "id": 456,
                    "name": "Student User",
                    "email": "student@example.com",
                    "login_id": "student1",
                }
            )
        ]
        mock_response.has_next_page = False
        mock_client.get_users.return_value = mock_response

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_response.data

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config.config_dir
        ):
            result = runner.invoke(cli, ["user", "roster", "123", "--format", "json"])

        assert result.exit_code == 0
        mock_client.get_users.assert_called_once_with(
            course_id=123,
            enrollment_type=None,
            include=None,
        )

    @patch("easel.cli.commands.user.asyncio.run")
    @patch("easel.cli.commands.user.CanvasClient")
    def test_user_roster_with_role_filter(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test user roster command with role filter."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock response
        mock_response = AsyncMock()
        mock_response.data = []
        mock_response.has_next_page = False
        mock_client.get_users.return_value = mock_response

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_response.data

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config.config_dir
        ):
            result = runner.invoke(
                cli, ["user", "roster", "123", "--role", "student", "--format", "json"]
            )

        assert result.exit_code == 0
        mock_client.get_users.assert_called_once_with(
            course_id=123,
            enrollment_type=["StudentEnrollment"],
            include=None,
        )

    def test_user_roster_missing_course_id(self, runner):
        """Test user roster without course ID."""
        result = runner.invoke(cli, ["user", "roster"])
        assert result.exit_code != 0

    def test_user_roster_invalid_course_id(self, runner):
        """Test user roster with invalid course ID."""
        result = runner.invoke(cli, ["user", "roster", "invalid"])
        assert result.exit_code != 0
