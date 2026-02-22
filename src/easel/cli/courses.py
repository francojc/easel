"""Courses CLI sub-app — list, show, and enrollments."""

from __future__ import annotations

from typing import Optional

import typer

from easel.cli._async import async_command
from easel.cli._context import get_context
from easel.cli._output import format_output
from easel.services import CanvasError
from easel.services.courses import (
    get_course,
    get_enrollments,
    list_courses,
)

courses_app = typer.Typer(name="courses", help="Manage Canvas courses.")


@courses_app.command("list")
@async_command
async def courses_list(
    ctx: typer.Context,
    concluded: Optional[bool] = typer.Option(
        False,
        "--concluded",
        help="Include completed courses.",
    ),
) -> None:
    """List courses where you are a teacher."""
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        data = await list_courses(ectx.client, include_concluded=concluded)
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(
        data,
        fmt,
        headers=["id", "course_code", "name", "term", "total_students"],
    )


@courses_app.command("show")
@async_command
async def courses_show(
    ctx: typer.Context,
    course: str = typer.Argument(help="Course code or numeric ID."),
) -> None:
    """Show details for a single course."""
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await get_course(ectx.client, course_id)
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(data, fmt)


@courses_app.command("enrollments")
@async_command
async def courses_enrollments(
    ctx: typer.Context,
    course: str = typer.Argument(help="Course code or numeric ID."),
) -> None:
    """List enrolled users for a course."""
    ectx = get_context(ctx.obj)
    fmt = ctx.obj["format"]
    try:
        course_id = await ectx.cache.resolve(course)
        data = await get_enrollments(ectx.client, course_id)
    except CanvasError as exc:
        typer.echo(exc.message, err=True)
        raise typer.Exit(1)
    finally:
        await ectx.close()
    format_output(
        data,
        fmt,
        headers=["id", "name", "email", "role"],
    )
