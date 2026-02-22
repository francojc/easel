"""Grading CLI sub-app — submissions, grading, and rubric grading."""

from __future__ import annotations

import json
from typing import Optional

import typer

from easel.cli._async import async_command
from easel.cli._context import get_context
from easel.cli._output import format_output
from easel.services import CanvasError
from easel.services.grading import (
    get_submission,
    list_submissions,
    submit_grade,
    submit_rubric_grade,
)

grading_app = typer.Typer(name="grading", help="Grade submissions.")


@grading_app.command("submissions")
@async_command
async def grading_submissions(
    ctx: typer.Context,
    course: str = typer.Argument(help="Course code or numeric ID."),
    assignment_id: str = typer.Argument(help="Assignment ID."),
) -> None:
    """List all submissions for an assignment."""
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await list_submissions(ectx.client, course_id, assignment_id)
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(
        data,
        fmt,
        headers=[
            "id",
            "user_id",
            "user_name",
            "workflow_state",
            "score",
            "submitted_at",
        ],
    )


@grading_app.command("show")
@async_command
async def grading_show(
    ctx: typer.Context,
    course: str = typer.Argument(help="Course code or numeric ID."),
    assignment_id: str = typer.Argument(help="Assignment ID."),
    user_id: str = typer.Argument(help="User ID."),
) -> None:
    """Show a single submission with rubric assessment detail."""
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await get_submission(
            ectx.client,
            course_id,
            assignment_id,
            user_id,
        )
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(data, fmt)


@grading_app.command("submit")
@async_command
async def grading_submit(
    ctx: typer.Context,
    course: str = typer.Argument(help="Course code or numeric ID."),
    assignment_id: str = typer.Argument(help="Assignment ID."),
    user_id: str = typer.Argument(help="User ID."),
    grade: str = typer.Argument(help="Grade value (points or letter)."),
    comment: Optional[str] = typer.Option(
        None, "--comment", help="Submission comment."
    ),
) -> None:
    """Submit a simple grade for a submission."""
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await submit_grade(
            ectx.client,
            course_id,
            assignment_id,
            user_id,
            grade,
            comment=comment,
        )
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(data, fmt)


@grading_app.command("submit-rubric")
@async_command
async def grading_submit_rubric(
    ctx: typer.Context,
    course: str = typer.Argument(help="Course code or numeric ID."),
    assignment_id: str = typer.Argument(help="Assignment ID."),
    user_id: str = typer.Argument(help="User ID."),
    assessment_json: str = typer.Argument(
        help="Rubric assessment as JSON string, e.g. "
        '\'{"_8027": {"points": 25, "comments": "Good"}}\'.',
    ),
    comment: Optional[str] = typer.Option(
        None, "--comment", help="Overall submission comment."
    ),
) -> None:
    """Submit a rubric-based grade for a submission."""
    try:
        rubric_assessment = json.loads(assessment_json)
    except json.JSONDecodeError as exc:
        typer.echo(f"Invalid JSON: {exc}", err=True)
        raise typer.Exit(1)

    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await submit_rubric_grade(
            ectx.client,
            course_id,
            assignment_id,
            user_id,
            rubric_assessment,
            comment=comment,
        )
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(data, fmt)
