"""Main CLI entry point for Easel CLI."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from easel import __version__
from easel.config import ConfigManager

from .context import EaselContext, pass_context


def _version_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    """Custom version callback that respects format option."""
    if not value or ctx.resilient_parsing:
        return

    # Get format from context params (should be available since is_eager=False)
    format_option = ctx.params.get("format", "table")

    if format_option == "json":
        version_data = {"program": "easel", "version": __version__}
        click.echo(json.dumps(version_data))
    else:
        click.echo(f"easel, version {__version__}")

    ctx.exit()


@click.group()
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json", "csv", "yaml"]),
    default="table",
    help="Output format",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=False,  # Process after other options
    callback=_version_callback,
    help="Show version and exit",
)
@pass_context
def cli(ctx: EaselContext, config: Optional[str], format: str, verbose: bool) -> None:
    """Easel CLI - Canvas LMS automation tool.

    Easel provides programmatic access to Canvas LMS via REST API with a
    focus on safety, extensibility, and automation workflows for
    educational institutions.
    """
    ctx.config_file = config
    ctx.format = format
    ctx.verbose = verbose

    # Initialize configuration manager
    try:
        config_path = Path(config) if config else None
        ctx.config_manager = ConfigManager(config_file=config_path)
    except Exception as e:
        if verbose:
            msg = f"Warning: Failed to initialize config manager: {e}"
            click.echo(msg, err=True)


def main() -> None:
    """Entry point for the CLI application."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Import commands to register them with the CLI
from .commands import assignment, config as config_commands, course, doctor, user  # noqa


if __name__ == "__main__":
    main()
