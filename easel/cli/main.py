"""Main CLI entry point for Easel CLI."""

import sys
from typing import Optional

import click

from easel import __version__
from easel.config import ConfigManager

from .context import EaselContext, pass_context


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
@click.version_option(version=__version__, prog_name="easel")
@pass_context
def cli(ctx: EaselContext, config: Optional[str], format: str, verbose: bool) -> None:
    """Easel CLI - Canvas LMS automation tool.

    Easel provides programmatic access to Canvas LMS via REST API with a focus
    on safety, extensibility, and automation workflows for educational institutions.
    """
    ctx.config_file = config
    ctx.format = format
    ctx.verbose = verbose

    # Initialize configuration manager
    try:
        ctx.config_manager = ConfigManager(config_file=config)
    except Exception as e:
        if verbose:
            click.echo(f"Warning: Failed to initialize config manager: {e}", err=True)


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
from .commands import config, doctor  # noqa: F401


if __name__ == "__main__":
    main()
