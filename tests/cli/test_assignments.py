"""Tests for easel.cli.assignments."""

from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from easel.cli.app import app
from easel.services import CanvasError

runner = CliRunner()

MOCK_ASSIGNMENTS = [
    {
        "id": 101,
        "name": "Homework 1",
        "due_at": "2026-02-01T23:59:00Z",
        "points_possible": 100,
        "published": True,
        "submission_types": "online_upload",
    },
]

MOCK_ASSIGNMENT_DETAIL = {
    "id": 101,
    "name": "Homework 1",
    "description": "Write an essay.",
    "due_at": "2026-02-01T23:59:00Z",
    "points_possible": 100,
    "published": True,
    "submission_types": "online_upload",
    "rubric": [{"id": "_8027", "points": 10}],
    "rubric_settings": {"id": 5, "points_possible": 10},
}

MOCK_RUBRICS = [
    {
        "id": 5,
        "title": "Essay Rubric",
        "points_possible": 100,
        "criteria_count": 2,
    },
]

MOCK_RUBRIC_DETAIL = {
    "id": 5,
    "title": "Essay Rubric",
    "points_possible": 100,
    "criteria": [
        {
            "id": "_8027",
            "description": "Thesis",
            "points": 25,
            "ratings": [
                {"id": "r1", "description": "Excellent", "points": 25},
            ],
        },
    ],
}

MOCK_CREATED = {
    "id": 201,
    "name": "New Assignment",
    "due_at": None,
    "points_possible": 50,
    "published": False,
}

MOCK_UPDATED = {
    "id": 101,
    "name": "Updated",
    "due_at": None,
    "points_possible": 75,
    "published": True,
}


def _patch_context():
    mock_ctx = AsyncMock()
    mock_ctx.client = AsyncMock()
    mock_ctx.cache = AsyncMock()
    mock_ctx.cache.resolve = AsyncMock(return_value="1")
    mock_ctx.close = AsyncMock()
    return patch(
        "easel.cli.assignments.get_context",
        return_value=mock_ctx,
    )


# -- assignments list --


@patch("easel.cli.assignments.list_assignments", new_callable=AsyncMock)
def test_assignments_list(mock_list):
    mock_list.return_value = MOCK_ASSIGNMENTS
    with _patch_context():
        result = runner.invoke(app, ["assignments", "list", "--course", "IS505"])
    assert result.exit_code == 0
    assert "Homework 1" in result.output


@patch("easel.cli.assignments.list_assignments", new_callable=AsyncMock)
def test_assignments_list_json(mock_list):
    mock_list.return_value = MOCK_ASSIGNMENTS
    with _patch_context():
        result = runner.invoke(
            app,
            ["--format", "json", "assignments", "list", "--course", "IS505"],
        )
    assert result.exit_code == 0
    assert '"Homework 1"' in result.output


@patch("easel.cli.assignments.list_assignments", new_callable=AsyncMock)
def test_assignments_list_error(mock_list):
    mock_list.side_effect = CanvasError("forbidden", status_code=403)
    with _patch_context():
        result = runner.invoke(app, ["assignments", "list", "--course", "IS505"])
    assert result.exit_code == 1
    assert "forbidden" in result.output


# -- assignments show --


@patch("easel.cli.assignments.get_assignment", new_callable=AsyncMock)
def test_assignments_show(mock_get):
    mock_get.return_value = MOCK_ASSIGNMENT_DETAIL
    with _patch_context():
        result = runner.invoke(app, ["assignments", "show", "--course", "IS505", "101"])
    assert result.exit_code == 0
    assert "101" in result.output
    assert "Homew" in result.output


@patch("easel.cli.assignments.get_assignment", new_callable=AsyncMock)
def test_assignments_show_error(mock_get):
    mock_get.side_effect = CanvasError("not found", status_code=404)
    with _patch_context():
        result = runner.invoke(app, ["assignments", "show", "--course", "IS505", "999"])
    assert result.exit_code == 1
    assert "not found" in result.output


# -- assignments create --


@patch("easel.cli.assignments.create_assignment", new_callable=AsyncMock)
def test_assignments_create(mock_create):
    mock_create.return_value = MOCK_CREATED
    with _patch_context():
        result = runner.invoke(
            app,
            ["assignments", "create", "--course", "IS505", "New Assignment", "--points", "50"],
        )
    assert result.exit_code == 0
    assert "New Assignment" in result.output


@patch("easel.cli.assignments.create_assignment", new_callable=AsyncMock)
def test_assignments_create_error(mock_create):
    mock_create.side_effect = CanvasError("invalid", status_code=422)
    with _patch_context():
        result = runner.invoke(
            app,
            ["assignments", "create", "--course", "IS505", "Bad"],
        )
    assert result.exit_code == 1
    assert "invalid" in result.output


# -- assignments update --


@patch("easel.cli.assignments.update_assignment", new_callable=AsyncMock)
def test_assignments_update(mock_update):
    mock_update.return_value = MOCK_UPDATED
    with _patch_context():
        result = runner.invoke(
            app,
            ["assignments", "update", "--course", "IS505", "101", "--name", "Updated"],
        )
    assert result.exit_code == 0
    assert "Updated" in result.output


# -- assignments rubrics --


@patch("easel.cli.assignments.list_rubrics", new_callable=AsyncMock)
def test_assignments_rubrics(mock_list):
    mock_list.return_value = MOCK_RUBRICS
    with _patch_context():
        result = runner.invoke(app, ["assignments", "rubrics", "--course", "IS505"])
    assert result.exit_code == 0
    assert "Essay Rubric" in result.output


@patch("easel.cli.assignments.list_rubrics", new_callable=AsyncMock)
def test_assignments_rubrics_error(mock_list):
    mock_list.side_effect = CanvasError("forbidden", status_code=403)
    with _patch_context():
        result = runner.invoke(app, ["assignments", "rubrics", "--course", "IS505"])
    assert result.exit_code == 1
    assert "forbidden" in result.output


# -- assignments rubric --


@patch("easel.cli.assignments.get_rubric", new_callable=AsyncMock)
@patch("easel.cli.assignments.get_assignment", new_callable=AsyncMock)
def test_assignments_rubric(mock_get_assign, mock_get_rubric):
    mock_get_assign.return_value = MOCK_ASSIGNMENT_DETAIL
    mock_get_rubric.return_value = MOCK_RUBRIC_DETAIL
    with _patch_context():
        result = runner.invoke(
            app,
            ["assignments", "rubric", "--course", "IS505", "101"],
        )
    assert result.exit_code == 0
    assert "Essay Rubric" in result.output
    assert "Thesis" in result.output


@patch("easel.cli.assignments.get_assignment", new_callable=AsyncMock)
def test_assignments_rubric_no_rubric(mock_get_assign):
    mock_get_assign.return_value = {
        **MOCK_ASSIGNMENT_DETAIL,
        "rubric_settings": None,
    }
    with _patch_context():
        result = runner.invoke(
            app,
            ["assignments", "rubric", "--course", "IS505", "101"],
        )
    assert result.exit_code == 1
    assert "No rubric" in result.output


@patch("easel.cli.assignments.get_assignment", new_callable=AsyncMock)
def test_assignments_rubric_error(mock_get_assign):
    mock_get_assign.side_effect = CanvasError("not found", status_code=404)
    with _patch_context():
        result = runner.invoke(
            app,
            ["assignments", "rubric", "--course", "IS505", "999"],
        )
    assert result.exit_code == 1
    assert "not found" in result.output
