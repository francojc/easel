"""Unit tests for course commands."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from easel.cli.main import cli
from easel.config.manager import ConfigManager
from easel.config.models import CanvasInstance, EaselConfig


class TestCourseCommands:
    """Test course commands functionality."""

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

    def test_course_list_help(self, runner):
        """Test course list help command."""
        result = runner.invoke(cli, ["course", "list", "--help"])
        assert result.exit_code == 0
        assert "List courses" in result.output
        assert "--active" in result.output
        assert "--include" in result.output

    def test_course_show_help(self, runner):
        """Test course show help command."""
        result = runner.invoke(cli, ["course", "show", "--help"])
        assert result.exit_code == 0
        assert "Show detailed information" in result.output
        assert "COURSE_ID" in result.output

    def test_course_modules_help(self, runner):
        """Test course modules help command."""
        result = runner.invoke(cli, ["course", "modules", "--help"])
        assert result.exit_code == 0
        assert "List modules" in result.output
        assert "COURSE_ID" in result.output

    @patch("easel.cli.commands.course.asyncio.run")
    @patch("easel.cli.commands.course.CanvasClient")
    def test_course_list_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful course list command."""
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
            "easel.config.paths.get_config_dir", return_value=mock_config._config_dir
        ):
            result = runner.invoke(cli, ["course", "list", "--format", "json"])

        assert result.exit_code == 0
        mock_client.get_courses.assert_called_once()

    @patch("easel.cli.commands.course.asyncio.run")
    @patch("easel.cli.commands.course.CanvasClient")
    def test_course_show_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful course show command."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock course data
        mock_course = AsyncMock(
            model_dump=lambda: {
                "id": 123,
                "name": "Test Course",
                "course_code": "TEST101",
                "workflow_state": "available",
            }
        )
        mock_client.get_course.return_value = mock_course

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_course

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config._config_dir
        ):
            result = runner.invoke(cli, ["course", "show", "123", "--format", "json"])

        assert result.exit_code == 0
        mock_client.get_course.assert_called_once_with(
            course_id=123,
            include=None,
        )

    @patch("easel.cli.commands.course.asyncio.run")
    @patch("easel.cli.commands.course.CanvasClient")
    def test_course_modules_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful course modules command."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock response
        mock_response = AsyncMock()
        mock_response.data = [
            AsyncMock(
                model_dump=lambda: {
                    "id": 456,
                    "name": "Module 1",
                    "position": 1,
                    "published": True,
                }
            )
        ]
        mock_response.has_next_page = False
        mock_client.get_modules.return_value = mock_response

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_response.data

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config._config_dir
        ):
            result = runner.invoke(
                cli, ["course", "modules", "123", "--format", "json"]
            )

        assert result.exit_code == 0
        mock_client.get_modules.assert_called_once_with(
            course_id=123,
            include=None,
        )

    def test_course_list_no_config(self, runner):
        """Test course list command without configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / ".easel"
            config_dir.mkdir()

            with patch("easel.config.paths.get_config_dir", return_value=config_dir):
                result = runner.invoke(cli, ["course", "list"])

        assert result.exit_code != 0
        assert "Configuration not found" in result.output

    def test_course_show_invalid_id(self, runner):
        """Test course show with invalid course ID."""
        result = runner.invoke(cli, ["course", "show", "invalid"])
        assert result.exit_code != 0

    def test_course_modules_invalid_id(self, runner):
        """Test course modules with invalid course ID."""
        result = runner.invoke(cli, ["course", "modules", "invalid"])
        assert result.exit_code != 0
