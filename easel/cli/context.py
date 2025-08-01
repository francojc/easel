"""CLI context object shared between commands."""

from typing import Optional

import click

from easel.config import ConfigManager


class EaselContext:
    """CLI context object for passing data between commands."""

    def __init__(self) -> None:
        self.config_manager: Optional[ConfigManager] = None
        self.config_file: Optional[str] = None
        self.format: str = "table"
        self.verbose: bool = False


pass_context = click.make_pass_decorator(EaselContext, ensure=True)
