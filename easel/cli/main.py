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
    """Custom version callback."""
    if not value or ctx.resilient_parsing:
        return

    click.echo(f"easel, version {__version__}")
    ctx.exit()


@click.group(context_settings={"allow_interspersed_args": False})
@click.option(
    "-C", "--config",
    type=click.Path(exists=True),
    help="Path to configuration file",
)
@click.option(
    "-f", "--format",
    type=click.Choice(["table", "json", "csv", "yaml"]),
    default="table",
    help="Output format",
)
@click.option(
    "-v", "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,  # Process early
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


# Import commands to register them with the CLI
from .commands import (
    assignment,
    config as config_commands,
    course,
    doctor,
    user,
    init,
)  # noqa

# Register commands with the main CLI
cli.add_command(assignment)
cli.add_command(config_commands)
cli.add_command(course)
cli.add_command(doctor)
cli.add_command(user)
cli.add_command(init)


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


if __name__ == "__main__":
    main()
