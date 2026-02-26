"""Tests for easel.cli.commands."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from easel.cli.app import app

runner = CliRunner()


def _setup_source(tmp_path: Path) -> Path:
    """Create a fake repo root with one command group."""
    repo = tmp_path / "repo"
    src = repo / ".claude" / "commands" / "assess"
    src.mkdir(parents=True)
    (src / "setup.md").write_text("# setup")
    (src / "ai-pass.md").write_text("# ai-pass")
    return repo


def test_commands_install_global(tmp_path):
    """Default install copies to ~/.claude/commands/."""
    repo = _setup_source(tmp_path)
    home = tmp_path / "home"

    with (
        patch("easel.cli.commands._get_repo_root", return_value=repo),
        patch("easel.cli.commands._COMMAND_GROUPS", ["assess"]),
        patch("pathlib.Path.home", return_value=home),
    ):
        result = runner.invoke(app, ["commands", "install"])

    assert result.exit_code == 0
    assert "Installed assess/ai-pass.md" in result.output
    assert "Installed assess/setup.md" in result.output
    assert (home / ".claude" / "commands" / "assess" / "setup.md").is_file()


def test_commands_install_local(tmp_path):
    """--local installs to ./.claude/commands/ in cwd."""
    repo = _setup_source(tmp_path)
    project = tmp_path / "project"
    project.mkdir()

    with (
        patch("easel.cli.commands._get_repo_root", return_value=repo),
        patch("easel.cli.commands._COMMAND_GROUPS", ["assess"]),
        patch("pathlib.Path.cwd", return_value=project),
    ):
        result = runner.invoke(app, ["commands", "install", "--local"])

    assert result.exit_code == 0
    assert "Installed assess/setup.md" in result.output
    dst = project / ".claude" / "commands" / "assess" / "setup.md"
    assert dst.is_file()
    assert dst.read_text() == "# setup"


def test_commands_install_skip_existing(tmp_path):
    """Existing files are skipped without --overwrite."""
    repo = _setup_source(tmp_path)
    home = tmp_path / "home"
    existing = home / ".claude" / "commands" / "assess"
    existing.mkdir(parents=True)
    (existing / "setup.md").write_text("# old")

    with (
        patch("easel.cli.commands._get_repo_root", return_value=repo),
        patch("easel.cli.commands._COMMAND_GROUPS", ["assess"]),
        patch("pathlib.Path.home", return_value=home),
    ):
        result = runner.invoke(app, ["commands", "install"])

    assert result.exit_code == 0
    assert "Skipping assess/setup.md" in result.output
    assert (existing / "setup.md").read_text() == "# old"


def test_commands_install_overwrite(tmp_path):
    """--overwrite replaces existing files."""
    repo = _setup_source(tmp_path)
    home = tmp_path / "home"
    existing = home / ".claude" / "commands" / "assess"
    existing.mkdir(parents=True)
    (existing / "setup.md").write_text("# old")

    with (
        patch("easel.cli.commands._get_repo_root", return_value=repo),
        patch("easel.cli.commands._COMMAND_GROUPS", ["assess"]),
        patch("pathlib.Path.home", return_value=home),
    ):
        result = runner.invoke(app, ["commands", "install", "--overwrite"])

    assert result.exit_code == 0
    assert "Installed assess/setup.md" in result.output
    assert (existing / "setup.md").read_text() == "# setup"
