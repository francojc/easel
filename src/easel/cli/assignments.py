"""Assignments CLI sub-app — list, show, create, update, and rubrics."""

from __future__ import annotations

from typing import Optional

import typer

from easel.cli._async import async_command
from easel.cli._config_defaults import resolve_course
from easel.cli._context import get_context
from easel.cli._output import format_output
from easel.services import CanvasError
from easel.services.assignments import (
    create_assignment,
    get_assignment,
    list_assignments,
    update_assignment,
)
from easel.services.rubrics import get_rubric, list_rubrics

assignments_app = typer.Typer(
    name="assignments", help="Manage Canvas assignments and rubrics."
)


@assignments_app.command("list")
@async_command
async def assignments_list(
    ctx: typer.Context,
    course: Optional[str] = typer.Argument(
        None, help="Course code or numeric ID. Falls back to config."
    ),
) -> None:
    """List all assignments for a course."""
    course = resolve_course(course)
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await list_assignments(ectx.client, course_id)
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(
        data,
        fmt,
        headers=["id", "name", "due_at", "points_possible", "published"],
    )


@assignments_app.command("show")
@async_command
async def assignments_show(
    ctx: typer.Context,
    course: Optional[str] = typer.Argument(
        None, help="Course code or numeric ID. Falls back to config."
    ),
    assignment_id: str = typer.Argument(help="Assignment ID."),
) -> None:
    """Show details for a single assignment (includes rubric if attached)."""
    course = resolve_course(course)
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await get_assignment(ectx.client, course_id, assignment_id)
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(data, fmt)


@assignments_app.command("create")
@async_command
async def assignments_create(
    ctx: typer.Context,
    course: Optional[str] = typer.Argument(
        None, help="Course code or numeric ID. Falls back to config."
    ),
    name: str = typer.Argument(help="Assignment name."),
    points: Optional[float] = typer.Option(None, "--points", help="Points possible."),
    due: Optional[str] = typer.Option(None, "--due", help="Due date (ISO 8601)."),
    types: Optional[str] = typer.Option(
        None,
        "--types",
        help="Comma-separated submission types.",
    ),
    publish: bool = typer.Option(False, "--publish", help="Publish immediately."),
) -> None:
    """Create a new assignment."""
    course = resolve_course(course)
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    sub_types = [t.strip() for t in types.split(",")] if types else None
    try:
        course_id = await ectx.cache.resolve(course)
        data = await create_assignment(
            ectx.client,
            course_id,
            name,
            points_possible=points,
            due_at=due,
            submission_types=sub_types,
            published=publish,
        )
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(data, fmt)


@assignments_app.command("update")
@async_command
async def assignments_update(
    ctx: typer.Context,
    course: Optional[str] = typer.Argument(
        None, help="Course code or numeric ID. Falls back to config."
    ),
    assignment_id: str = typer.Argument(help="Assignment ID."),
    name: Optional[str] = typer.Option(None, "--name", help="New name."),
    points: Optional[float] = typer.Option(None, "--points", help="Points possible."),
    due: Optional[str] = typer.Option(None, "--due", help="Due date (ISO 8601)."),
    publish: Optional[bool] = typer.Option(
        None, "--publish/--unpublish", help="Publish or unpublish."
    ),
) -> None:
    """Update an existing assignment."""
    course = resolve_course(course)
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await update_assignment(
            ectx.client,
            course_id,
            assignment_id,
            name=name,
            points_possible=points,
            due_at=due,
            published=publish,
        )
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(data, fmt)


@assignments_app.command("rubrics")
@async_command
async def assignments_rubrics(
    ctx: typer.Context,
    course: Optional[str] = typer.Argument(
        None, help="Course code or numeric ID. Falls back to config."
    ),
) -> None:
    """List all rubrics for a course."""
    course = resolve_course(course)
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await list_rubrics(ectx.client, course_id)
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(
        data,
        fmt,
        headers=["id", "title", "points_possible", "criteria_count"],
    )


@assignments_app.command("rubric")
@async_command
async def assignments_rubric(
    ctx: typer.Context,
    course: Optional[str] = typer.Argument(
        None, help="Course code or numeric ID. Falls back to config."
    ),
    assignment_id: str = typer.Argument(help="Assignment ID."),
) -> None:
    """Show the rubric attached to an assignment."""
    course = resolve_course(course)
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        assignment = await get_assignment(
            ectx.client,
            course_id,
            assignment_id,
        )
        rubric_settings = assignment.get("rubric_settings")
        if not rubric_settings or "id" not in rubric_settings:
            typer.echo("No rubric attached to this assignment.", err=True)
            raise typer.Exit(1)
        data = await get_rubric(
            ectx.client,
            course_id,
            str(rubric_settings["id"]),
        )
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    if fmt.value == "json":
        format_output(data, fmt)
    else:
        # Pretty-print rubric criteria for table/plain
        typer.echo(f"Rubric: {data['title']} ({data['points_possible']} pts)")
        typer.echo("")
        for criterion in data.get("criteria", []):
            typer.echo(
                f"  {criterion['id']}: {criterion['description']}"
                f" ({criterion['points']} pts)"
            )
            for rating in criterion.get("ratings", []):
                typer.echo(f"    - {rating['description']}: {rating['points']} pts")
