"""Manage easel skill commands — install to ~/.claude/commands/."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer

commands_app = typer.Typer(
    name="commands",
    help="Install Claude Code skill commands to ~/.claude/commands/.",
)

_COMMAND_GROUPS = [
    "assess",
    "assignments",
    "content",
    "course",
    "discuss",
    "grading",
]


@commands_app.command("install")
def commands_install(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files without asking."
    ),
) -> None:
    """Copy bundled skill commands to ~/.claude/commands/.

    Installs all command groups: assess, assignments, content, course,
    discuss, and grading. Existing files are skipped unless --overwrite
    is passed.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    dst_root = Path.home() / ".claude" / "commands"

    installed: list[str] = []
    skipped: list[str] = []

    for group in _COMMAND_GROUPS:
        src_dir = repo_root / ".claude" / "commands" / group
        if not src_dir.is_dir():
            typer.echo(f"Source directory not found: {src_dir}", err=True)
            raise typer.Exit(1)

        dst_dir = dst_root / group
        dst_dir.mkdir(parents=True, exist_ok=True)

        for src_file in sorted(src_dir.glob("*.md")):
            dst_file = dst_dir / src_file.name
            if dst_file.exists() and not overwrite:
                typer.echo(
                    f"Skipping {group}/{src_file.name} (exists, use --overwrite)"
                )
                skipped.append(f"{group}/{src_file.name}")
                continue

            shutil.copy2(src_file, dst_file)
            installed.append(f"{group}/{src_file.name}")
            typer.echo(f"Installed {group}/{src_file.name}")

    if installed:
        typer.echo(f"\n{len(installed)} file(s) installed to {dst_root}")
    if skipped:
        typer.echo(f"{len(skipped)} file(s) skipped")
    if not installed and not skipped:
        typer.echo("No command files found to install.")
