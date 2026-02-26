"""Tests for easel.cli._config_defaults."""

from unittest.mock import patch

import click
import pytest
from typer.testing import CliRunner

from easel.cli._config_defaults import (
    resolve_anonymize,
    resolve_assess_defaults,
    resolve_course,
)
from easel.cli.app import app

runner = CliRunner()


# -- resolve_course --


@patch("easel.cli._config_defaults.read_global_config", return_value={})
@patch(
    "easel.cli._config_defaults.read_local_config",
    return_value={"canvas_course_id": 12345},
)
def test_resolve_course_from_local_config(_local, _global):
    assert resolve_course(None) == "12345"


@patch(
    "easel.cli._config_defaults.read_global_config",
    return_value={"canvas_course_id": 99},
)
@patch("easel.cli._config_defaults.read_local_config", return_value={})
def test_resolve_course_from_global_config(_local, _global):
    assert resolve_course(None) == "99"


def test_resolve_course_explicit_wins():
    assert resolve_course("SPA101") == "SPA101"


@patch("easel.cli._config_defaults.read_global_config", return_value={})
@patch("easel.cli._config_defaults.read_local_config", return_value={})
def test_resolve_course_missing_exits(_local, _global):
    with pytest.raises(click.exceptions.Exit):
        resolve_course(None)


@patch(
    "easel.cli._config_defaults.read_local_config",
    return_value={"canvas_course_id": 111},
)
@patch(
    "easel.cli._config_defaults.read_global_config",
    return_value={"canvas_course_id": 222},
)
def test_resolve_course_local_beats_global(_local, _global):
    assert resolve_course(None) == "111"


# -- resolve_assess_defaults --


@patch("easel.cli._config_defaults.read_global_config", return_value={})
@patch(
    "easel.cli._config_defaults.read_local_config",
    return_value={
        "level": "graduate",
        "formality": "formal",
        "feedback_language": "Spanish",
    },
)
def test_resolve_assess_defaults_from_config(_local, _global):
    kwargs = {
        "level": None,
        "formality": None,
        "feedback_language": None,
        "language_learning": None,
        "language_level": None,
        "anonymize": None,
        "course_name": None,
    }
    result = resolve_assess_defaults(kwargs)
    assert result["level"] == "graduate"
    assert result["formality"] == "formal"
    assert result["feedback_language"] == "Spanish"


@patch("easel.cli._config_defaults.read_global_config", return_value={})
@patch(
    "easel.cli._config_defaults.read_local_config",
    return_value={"level": "graduate"},
)
def test_resolve_assess_defaults_explicit_wins(_local, _global):
    kwargs = {
        "level": "professional",
        "formality": None,
        "feedback_language": None,
        "language_learning": None,
        "language_level": None,
        "anonymize": None,
        "course_name": None,
    }
    result = resolve_assess_defaults(kwargs)
    assert result["level"] == "professional"


@patch(
    "easel.cli._config_defaults.read_global_config",
    return_value={"formality": "formal"},
)
@patch("easel.cli._config_defaults.read_local_config", return_value={})
def test_resolve_assess_defaults_global_fallback(_local, _global):
    kwargs = {"formality": None, "course_name": None}
    result = resolve_assess_defaults(kwargs)
    assert result["formality"] == "formal"


# -- resolve_anonymize --


@patch("easel.cli._config_defaults.read_global_config", return_value={})
@patch(
    "easel.cli._config_defaults.read_local_config",
    return_value={"anonymize": True},
)
def test_resolve_anonymize_from_config(_local, _global):
    assert resolve_anonymize(None) is True


def test_resolve_anonymize_explicit_wins():
    assert resolve_anonymize(False) is False
    assert resolve_anonymize(True) is True


@patch("easel.cli._config_defaults.read_global_config", return_value={})
@patch("easel.cli._config_defaults.read_local_config", return_value={})
def test_resolve_anonymize_defaults_false(_local, _global):
    assert resolve_anonymize(None) is False


# -- CLI integration: commands work without explicit course arg --


def _patch_context(module_path):
    """Patch EaselContext so CLI commands don't need real config."""
    from unittest.mock import AsyncMock

    mock_ctx = AsyncMock()
    mock_ctx.client = AsyncMock()
    mock_ctx.cache = AsyncMock()
    mock_ctx.cache.resolve = AsyncMock(return_value="12345")
    mock_ctx.close = AsyncMock()

    return patch(f"easel.cli.{module_path}.get_context", return_value=mock_ctx)


@patch(
    "easel.cli.courses.list_courses",
    new_callable=lambda: __import__("unittest.mock", fromlist=["AsyncMock"]).AsyncMock,
)
@patch(
    "easel.cli._config_defaults.read_local_config",
    return_value={"canvas_course_id": 12345},
)
@patch("easel.cli._config_defaults.read_global_config", return_value={})
def test_courses_show_no_course_arg(_global, _local, mock_get):
    from unittest.mock import AsyncMock

    with (
        _patch_context("courses"),
        patch(
            "easel.cli.courses.get_course",
            new_callable=AsyncMock,
            return_value={"id": 12345, "name": "Test"},
        ),
    ):
        result = runner.invoke(app, ["courses", "show"])
    assert result.exit_code == 0


@patch(
    "easel.cli._config_defaults.read_local_config",
    return_value={"canvas_course_id": 12345},
)
@patch("easel.cli._config_defaults.read_global_config", return_value={})
def test_assignments_list_no_course_arg(_global, _local):
    from unittest.mock import AsyncMock

    with (
        _patch_context("assignments"),
        patch(
            "easel.cli.assignments.list_assignments",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        result = runner.invoke(app, ["assignments", "list"])
    assert result.exit_code == 0
