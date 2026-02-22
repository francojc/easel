from typing import Optional

import typer

from easel import __version__
from easel.cli._output import OutputFormat

app = typer.Typer(name="easel", help="CLI for the Canvas LMS API")


def _version_callback(value: bool):
    if value:
        typer.echo(f"easel {__version__}")
        raise typer.Exit()


def _test_callback(value: bool):
    if value:
        typer.echo("Connection test not yet implemented.")
        raise typer.Exit()


def _config_callback(value: bool):
    if value:
        typer.echo("Config display not yet implemented.")
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
):
    """Global options for easel."""
    ctx.ensure_object(dict)
    ctx.obj["format"] = OutputFormat(fmt)


def main():
    app()
