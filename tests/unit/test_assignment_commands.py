"""Unit tests for assignment commands."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from easel.cli.main import cli
from easel.config.manager import ConfigManager
from easel.config.models import CanvasInstance, EaselConfig


class TestAssignmentCommands:
    """Test assignment commands functionality."""

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

    def test_assignment_list_help(self, runner):
        """Test assignment list help command."""
        result = runner.invoke(cli, ["assignment", "list", "--help"])
        assert result.exit_code == 0
        assert "List assignments" in result.output
        assert "COURSE_ID" in result.output

    def test_assignment_show_help(self, runner):
        """Test assignment show help command."""
        result = runner.invoke(cli, ["assignment", "show", "--help"])
        assert result.exit_code == 0
        assert "Show detailed information" in result.output
        assert "COURSE_ID" in result.output
        assert "ASSIGNMENT_ID" in result.output

    def test_assignment_submissions_help(self, runner):
        """Test assignment submissions help command."""
        result = runner.invoke(cli, ["assignment", "submissions", "--help"])
        assert result.exit_code == 0
        assert "List submissions" in result.output
        assert "--status" in result.output

    @patch("easel.cli.commands.assignment.asyncio.run")
    @patch("easel.cli.commands.assignment.CanvasClient")
    def test_assignment_list_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful assignment list command."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock response
        mock_response = AsyncMock()
        mock_response.data = [
            AsyncMock(
                model_dump=lambda: {
                    "id": 789,
                    "name": "Test Assignment",
                    "course_id": 123,
                    "points_possible": 100.0,
                }
            )
        ]
        mock_response.has_next_page = False
        mock_client.get_assignments.return_value = mock_response

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_response.data

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config._config_dir
        ):
            result = runner.invoke(
                cli, ["assignment", "list", "123", "--format", "json"]
            )

        assert result.exit_code == 0
        mock_client.get_assignments.assert_called_once()

    @patch("easel.cli.commands.assignment.asyncio.run")
    @patch("easel.cli.commands.assignment.CanvasClient")
    def test_assignment_show_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful assignment show command."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock assignment data
        mock_assignment = AsyncMock(
            model_dump=lambda: {
                "id": 789,
                "name": "Test Assignment",
                "course_id": 123,
                "points_possible": 100.0,
            }
        )
        mock_client.get_assignment.return_value = mock_assignment

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_assignment

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config._config_dir
        ):
            result = runner.invoke(
                cli, ["assignment", "show", "123", "789", "--format", "json"]
            )

        assert result.exit_code == 0
        mock_client.get_assignment.assert_called_once_with(
            course_id=123,
            assignment_id=789,
            include=None,
        )

    @patch("easel.cli.commands.assignment.asyncio.run")
    @patch("easel.cli.commands.assignment.CanvasClient")
    def test_assignment_submissions_success(
        self, mock_client_class, mock_asyncio_run, runner, mock_config
    ):
        """Test successful assignment submissions command."""
        # Mock async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock response
        mock_response = AsyncMock()
        mock_response.data = [
            AsyncMock(
                model_dump=lambda: {
                    "id": 111,
                    "user_id": 456,
                    "assignment_id": 789,
                    "workflow_state": "submitted",
                }
            )
        ]
        mock_response.has_next_page = False
        mock_client.get_submissions.return_value = mock_response

        # Mock asyncio.run to return our mock data
        mock_asyncio_run.return_value = mock_response.data

        with patch(
            "easel.config.paths.get_config_dir", return_value=mock_config._config_dir
        ):
            result = runner.invoke(
                cli, ["assignment", "submissions", "123", "789", "--format", "json"]
            )

        assert result.exit_code == 0
        mock_client.get_submissions.assert_called_once_with(
            course_id=123,
            assignment_id=789,
            include=None,
        )

    def test_assignment_list_missing_course_id(self, runner):
        """Test assignment list without course ID."""
        result = runner.invoke(cli, ["assignment", "list"])
        assert result.exit_code != 0

    def test_assignment_show_missing_args(self, runner):
        """Test assignment show without required arguments."""
        result = runner.invoke(cli, ["assignment", "show"])
        assert result.exit_code != 0

        result = runner.invoke(cli, ["assignment", "show", "123"])
        assert result.exit_code != 0

    def test_assignment_submissions_missing_args(self, runner):
        """Test assignment submissions without required arguments."""
        result = runner.invoke(cli, ["assignment", "submissions"])
        assert result.exit_code != 0

        result = runner.invoke(cli, ["assignment", "submissions", "123"])
        assert result.exit_code != 0
