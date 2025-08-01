"""Configuration-related CLI commands."""

import json

import click
import yaml

from easel.config import (
    ConfigError,
    ConfigManager,
    ConfigNotFoundError,
    ConfigValidationError,
)

from ..context import pass_context, EaselContext
from ..main import cli


@cli.group()
def config() -> None:
    """Configuration management commands."""
    pass


@config.command("list")
@click.option(
    "--show-sensitive",
    is_flag=True,
    help="Show sensitive configuration values (use with caution)",
)
@pass_context
def config_list(ctx: EaselContext, show_sensitive: bool) -> None:
    """Display current configuration."""
    try:
        if not ctx.config_manager:
            raise ConfigError("Configuration manager not initialized")

        if not ctx.config_manager.config_exists():
            click.echo(
                "No configuration found. Run 'easel init' to create one.",
                err=True,
            )
            click.get_current_context().exit(1)

        if show_sensitive:
            # Load full config (including tokens)
            config = ctx.config_manager.load_config()
            config_dict = config.model_dump(exclude_none=True)
        else:
            # Load safe summary (no sensitive data)
            config_dict = ctx.config_manager.get_config_summary()

        if ctx.format == "json":
            click.echo(json.dumps(config_dict, indent=2))
        elif ctx.format == "yaml":
            click.echo(yaml.dump(config_dict, default_flow_style=False))
        else:
            # Table format
            _display_config_table(config_dict)

    except ConfigNotFoundError:
        click.echo(
            "Configuration file not found. Run 'easel init' to create one.",
            err=True,
        )
        ctx.exit(1)
    except ConfigValidationError as e:
        click.echo(f"Configuration validation error: {e}", err=True)
        ctx.exit(1)
    except ConfigError as e:
        click.echo(f"Configuration error: {e}", err=True)
        ctx.exit(1)


@cli.command()
@pass_context
def init(ctx: EaselContext) -> None:
    """Initialize Easel configuration with interactive setup."""
    click.echo("🎨 Welcome to Easel CLI Setup!")
    click.echo("Let's configure your Canvas connection.\n")

    # Check if config already exists
    if ctx.config_manager and ctx.config_manager.config_exists():
        if not click.confirm("Configuration already exists. Overwrite?"):
            click.echo("Configuration setup cancelled.")
            return

    # Canvas instance configuration
    canvas_name = click.prompt(
        "Canvas instance name",
        default="My University",
        type=str,
    )

    canvas_url = click.prompt(
        "Canvas URL (e.g., https://university.instructure.com)",
        type=str,
    )

    # Validate URL format
    if not canvas_url.startswith(("http://", "https://")):
        canvas_url = f"https://{canvas_url}"

    # API token setup
    click.echo("\n📝 Canvas API Token Setup:")
    click.echo("1. Go to your Canvas Account Settings")
    click.echo("2. Scroll to 'Approved Integrations'")
    click.echo("3. Click '+ New Access Token'")
    click.echo("4. Give it a purpose like 'Easel CLI Access'")
    click.echo("5. Copy the generated token\n")

    api_token = click.prompt(
        "Canvas API token",
        hide_input=True,
        type=str,
    )

    # Create configuration
    try:
        config_manager = ConfigManager()
        config = config_manager.create_default_config(canvas_name, canvas_url)
        config.canvas.api_token = api_token

        # Save configuration and credentials
        config_manager.save_config(config, store_token=True)

        click.echo(f"\n✅ Configuration saved to {config_manager.config_file}")
        click.echo("🔐 API token stored securely")
        click.echo("\nRun 'easel doctor' to validate your setup!")

    except ConfigError as e:
        click.echo(f"Failed to save configuration: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error during setup: {e}", err=True)
        raise click.Abort()


def _display_config_table(config_dict: dict) -> None:
    """Display configuration in a human-readable table format."""
    click.echo("Current Easel Configuration:")
    click.echo("=" * 50)

    # Canvas configuration
    click.echo("\n📚 Canvas Instance:")
    canvas = config_dict.get("canvas", {})
    click.echo(f"  Name: {canvas.get('name', 'Not set')}")
    click.echo(f"  URL:  {canvas.get('url', 'Not set')}")

    has_token = canvas.get("has_token", False)
    click.echo(f"  Token: {'✅ Configured' if has_token else '❌ Not configured'}")

    # API settings
    click.echo("\n🔧 API Settings:")
    api = config_dict.get("api", {})
    click.echo(f"  Rate limit: {api.get('rate_limit', 'Not set')} req/sec")
    click.echo(f"  Timeout:    {api.get('timeout', 'Not set')} seconds")
    click.echo(f"  Retries:    {api.get('retries', 'Not set')}")
    click.echo(f"  Page size:  {api.get('page_size', 'Not set')}")

    # Cache settings
    click.echo("\n💾 Cache Settings:")
    cache = config_dict.get("cache", {})
    enabled = cache.get("enabled", False)
    click.echo(f"  Enabled: {'✅ Yes' if enabled else '❌ No'}")
    if enabled:
        click.echo(f"  TTL:      {cache.get('ttl', 'Not set')} seconds")
        click.echo(f"  Max size: {cache.get('max_size', 'Not set')} entries")

    # Logging settings
    click.echo("\n📝 Logging:")
    logging = config_dict.get("logging", {})
    click.echo(f"  Level:  {logging.get('level', 'Not set')}")
    click.echo(f"  Format: {logging.get('format', 'Not set')}")

    log_file = logging.get("file")
    if log_file:
        click.echo(f"  File:   {log_file}")

    # File locations
    click.echo("\n📁 Files:")
    config_file = config_dict.get("config_file")
    if config_file:
        click.echo(f"  Config: {config_file}")

    has_creds = config_dict.get("has_stored_credentials", False)
    click.echo(f"  Credentials: {'✅ Stored securely' if has_creds else '❌ Not found'}")


# Register the commands group
config_commands = config
