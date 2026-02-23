"""Config sub-app — manage global and local easel configuration."""

from __future__ import annotations

from pathlib import Path

import typer

from easel.core.config_files import (
    GLOBAL_FIELDS,
    LOCAL_FIELDS,
    merge_configs,
    read_global_config,
    read_local_config,
    write_global_config,
    write_local_config,
)

config_app = typer.Typer(name="config", help="Manage easel configuration files.")


def _prompt_bool(prompt: str, default: bool) -> bool:
    """Prompt for a yes/no value."""
    suffix = " [Y/n]" if default else " [y/N]"
    raw = typer.prompt(prompt + suffix, default="y" if default else "n")
    return raw.strip().lower() in ("y", "yes", "true")


def _coerce_value(key: str, raw: str) -> object:
    """Coerce a string prompt value to the appropriate type."""
    if key == "canvas_course_id":
        return int(raw)
    if key == "year":
        return int(raw)
    if key in ("language_learning",):
        return raw.strip().lower() in ("true", "yes", "y")
    return raw


@config_app.command("init")
def config_init(
    base: str = typer.Option(
        ".", "--base", help="Repository root directory."
    ),
) -> None:
    """Create .claude/course_parameters.yaml with interactive prompts."""
    base_path = Path(base).resolve()
    global_cfg = read_global_config()
    existing = read_local_config(base_path)

    data: dict[str, object] = {}
    for key, description in LOCAL_FIELDS.items():
        default = existing.get(key) or global_cfg.get(key, "")
        if isinstance(default, bool):
            data[key] = _prompt_bool(description, default)
        else:
            raw = typer.prompt(description, default=str(default) if default else "")
            data[key] = _coerce_value(key, raw)

    path = write_local_config(data, base_path)
    typer.echo(f"Wrote {path}")


@config_app.command("global")
def config_global() -> None:
    """Create or update ~/.config/easel/config.toml with shared defaults."""
    existing = read_global_config()

    data: dict[str, object] = {}
    for key, description in GLOBAL_FIELDS.items():
        default = existing.get(key, "")
        if key == "language_learning":
            data[key] = _prompt_bool(
                description, bool(default) if default != "" else False
            )
        else:
            raw = typer.prompt(description, default=str(default) if default else "")
            data[key] = raw

    path = write_global_config(data)
    typer.echo(f"Wrote {path}")


@config_app.command("show")
def config_show() -> None:
    """Display merged global + local configuration with source annotations."""
    global_cfg = read_global_config()
    local_cfg = read_local_config()
    merged = merge_configs(global_cfg, local_cfg)

    if not global_cfg and not local_cfg:
        typer.echo("No configuration found.")
        typer.echo("Run 'easel config global' or 'easel config init' to get started.")
        raise typer.Exit()

    max_key = max(len(t[0]) for t in merged)
    for key, value, source in merged:
        if value is None:
            display = "(not set)"
        else:
            display = str(value)
        tag = f"[{source}]"
        typer.echo(f"  {key:<{max_key}}  {display:<30}  {tag}")
