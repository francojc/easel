"""CLI context object shared between commands."""

import functools
from typing import Optional

import click

from easel.config import ConfigManager
from easel.config.models import EaselConfig


class EaselContext:
    """CLI context object for passing data between commands."""

    def __init__(self) -> None:
        self.config_manager: Optional[ConfigManager] = None
        self.config_file: Optional[str] = None
        self.format: str = "table"
        self.verbose: bool = False

    def get_config(self) -> EaselConfig:
        """Load and return the configuration.
        
        Returns:
            EaselConfig: The loaded configuration
            
        Raises:
            RuntimeError: If config_manager is not initialized
        """
        if self.config_manager is None:
            raise RuntimeError("Config manager not initialized")
        return self.config_manager.load_config()


pass_context = click.make_pass_decorator(EaselContext, ensure=True)
