"""Main Typer app and global options for easel."""

from __future__ import annotations

import asyncio
from typing import Optional

import typer

from easel import __version__
from easel.cli._context import EaselContext, get_context
from easel.cli._output import OutputFormat

from easel.cli.assessments import assess_app
from easel.cli.assignments import assignments_app
from easel.cli.commands import commands_app
from easel.cli.config import config_app
from easel.cli.courses import courses_app
from easel.cli.discussions import discussions_app
from easel.cli.grading import grading_app
from easel.cli.modules import modules_app
from easel.cli.pages import pages_app

app = typer.Typer(
    name="easel",
    help="Canvas LMS CLI — manage courses, assignments, grading, "
    "and content from the terminal.",
)
app.add_typer(assess_app)
app.add_typer(assignments_app)
app.add_typer(commands_app)
app.add_typer(config_app)
app.add_typer(courses_app)
app.add_typer(discussions_app)
app.add_typer(grading_app)
app.add_typer(modules_app)
app.add_typer(pages_app)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"easel {__version__}")
        raise typer.Exit()


def _test_callback(value: bool) -> None:
    if value:

        async def _run_test() -> tuple[bool, str]:
            ctx = EaselContext()
            try:
                return await ctx.client.test_connection()
            finally:
                await ctx.close()

        try:
            ok, msg = asyncio.run(_run_test())
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(1)
        typer.echo(msg)
        raise typer.Exit(0 if ok else 1)


def _config_callback(value: bool) -> None:
    if value:
        ctx = EaselContext()
        try:
            cfg = ctx.config
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(1)
        token = cfg.canvas_api_key
        masked = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
        typer.echo(f"url:     {cfg.canvas_base_url}")
        typer.echo(f"token:   {masked}")
        typer.echo(f"timeout: {cfg.api_timeout}s")
        raise typer.Exit()


@app.callback()
def callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    fmt: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, json, or plain.",
    ),
    test: Optional[bool] = typer.Option(
        None,
        "--test",
        callback=_test_callback,
        is_eager=True,
        help="Test Canvas API connection.",
    ),
    config: Optional[bool] = typer.Option(
        None,
        "--config",
        callback=_config_callback,
        is_eager=True,
        help="Show current configuration.",
    ),
) -> None:
    """Global options for easel."""
    ctx.ensure_object(dict)
    ctx.obj["format"] = OutputFormat(fmt)
    _ = get_context(ctx.obj)  # initialize EaselContext on ctx.obj


def main() -> None:
    app()
