"""Unit tests for grade commands."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from click.testing import CliRunner

from easel.cli.commands.grade import grade
from easel.api.exceptions import CanvasAPIError
from easel.config.exceptions import ConfigError


@pytest.fixture
def mock_context():
    """Create a mock context for testing."""
    context = Mock()
    context.get_config.return_value = Mock(
        token="test_token",
        base_url="https://test.instructure.com",
        rate_limit=10.0,
        timeout=30.0,
    )
    return context


@pytest.fixture
def mock_client():
    """Create a mock Canvas client."""
    client = AsyncMock()

    # Mock course
    client.get_course.return_value = Mock(id=123, name="Test Course")

    # Mock assignments
    client.get_assignments.return_value = [
        Mock(
            id=1,
            name="Assignment 1",
            points_possible=100,
            assignment_group=Mock(name="Homework"),
            published=True,
        ),
        Mock(
            id=2,
            name="Assignment 2",
            points_possible=50,
            assignment_group=Mock(name="Quizzes"),
            published=True,
        ),
    ]

    # Mock enrollments
    client.get_enrollments.return_value = [
        {"user": {"id": 101, "name": "Student One", "email": "student1@test.com"}},
        {"user": {"id": 102, "name": "Student Two", "email": "student2@test.com"}},
    ]

    # Mock submissions
    client.get_submissions.return_value = [
        Mock(
            user_id=101,
            score=85.0,
            grade="B",
            submission_type="online_text_entry",
            submitted_at=None,
            graded_at=None,
            late=False,
            missing=False,
            excused=False,
        ),
        Mock(
            user_id=102,
            score=92.0,
            grade="A-",
            submission_type="online_upload",
            submitted_at=None,
            graded_at=None,
            late=False,
            missing=False,
            excused=False,
        ),
    ]

    return client


@pytest.mark.asyncio
async def test_grade_export_basic(mock_context, mock_client):
    """Test basic grade export functionality."""
    runner = CliRunner()

    with patch("easel.cli.commands.grade.CanvasAuth"), patch(
        "easel.cli.commands.grade.CanvasClient"
    ) as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock the context passing
        with patch("easel.cli.commands.grade.pass_context", return_value=mock_context):
            result = runner.invoke(grade, ["export", "123", "--format", "json"])

    assert result.exit_code == 0
    assert "Test Course" in result.output or "grades" in result.output.lower()


@pytest.mark.asyncio
async def test_grade_analytics_basic(mock_context, mock_client):
    """Test basic grade analytics functionality."""
    runner = CliRunner()

    with patch("easel.cli.commands.grade.CanvasAuth"), patch(
        "easel.cli.commands.grade.CanvasClient"
    ) as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock the context passing
        with patch("easel.cli.commands.grade.pass_context", return_value=mock_context):
            result = runner.invoke(grade, ["analytics", "123"])

    assert result.exit_code == 0
    assert "Test Course" in result.output or "analyzing" in result.output.lower()


@pytest.mark.asyncio
async def test_grade_export_api_error(mock_context):
    """Test grade export with API error."""
    runner = CliRunner()

    with patch("easel.cli.commands.grade.CanvasAuth"), patch(
        "easel.cli.commands.grade.CanvasClient"
    ) as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get_course.side_effect = CanvasAPIError("API Error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch("easel.cli.commands.grade.pass_context", return_value=mock_context):
            result = runner.invoke(grade, ["export", "123"])

    assert result.exit_code != 0
    assert "API Error" in result.output


@pytest.mark.asyncio
async def test_grade_export_no_assignments(mock_context, mock_client):
    """Test grade export with no assignments."""
    runner = CliRunner()

    # Override to return no assignments
    mock_client.get_assignments.return_value = []

    with patch("easel.cli.commands.grade.CanvasAuth"), patch(
        "easel.cli.commands.grade.CanvasClient"
    ) as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch("easel.cli.commands.grade.pass_context", return_value=mock_context):
            result = runner.invoke(grade, ["export", "123"])

    assert result.exit_code == 0
    assert "No assignments found" in result.output


@pytest.mark.asyncio
async def test_grade_export_with_filter(mock_context, mock_client):
    """Test grade export with assignment group filter."""
    runner = CliRunner()

    with patch("easel.cli.commands.grade.CanvasAuth"), patch(
        "easel.cli.commands.grade.CanvasClient"
    ) as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch("easel.cli.commands.grade.pass_context", return_value=mock_context):
            result = runner.invoke(
                grade, ["export", "123", "--assignment-group", "Homework"]
            )

    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_grade_export_csv_output(mock_context, mock_client, tmp_path):
    """Test grade export with CSV output to file."""
    runner = CliRunner()
    output_file = tmp_path / "grades.csv"

    with patch("easel.cli.commands.grade.CanvasAuth"), patch(
        "easel.cli.commands.grade.CanvasClient"
    ) as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch("easel.cli.commands.grade.pass_context", return_value=mock_context):
            result = runner.invoke(
                grade,
                ["export", "123", "--format", "csv", "--output", str(output_file)],
            )

    assert result.exit_code == 0
    assert output_file.exists()


def test_grade_analytics_statistics():
    """Test grade analytics statistical calculations."""
    # This would test the statistical calculation functions
    # For now, just verify the command structure
    runner = CliRunner()
    result = runner.invoke(grade, ["--help"])

    assert result.exit_code == 0
    assert "export" in result.output
    assert "analytics" in result.output


@pytest.mark.asyncio
async def test_grade_analytics_export_raw(mock_context, mock_client):
    """Test grade analytics with raw data export."""
    runner = CliRunner()

    with patch("easel.cli.commands.grade.CanvasAuth"), patch(
        "easel.cli.commands.grade.CanvasClient"
    ) as mock_client_class:
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch("easel.cli.commands.grade.pass_context", return_value=mock_context):
            result = runner.invoke(grade, ["analytics", "123", "--export-raw"])

    assert result.exit_code == 0


def test_grade_command_help():
    """Test grade command help output."""
    runner = CliRunner()
    result = runner.invoke(grade, ["--help"])

    assert result.exit_code == 0
    assert "Grade management and analytics commands" in result.output
    assert "export" in result.output
    assert "analytics" in result.output
