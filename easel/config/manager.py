"""Configuration management and loading system."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import ValidationError

from .credentials import CredentialManager
from .exceptions import ConfigNotFoundError, ConfigValidationError
from .models import EaselConfig, CanvasInstance
from .paths import ensure_config_dirs, get_config_file, get_config_dir


class ConfigManager:
    """Manages Easel configuration loading, validation, and storage."""

    def __init__(
        self, config_file: Optional[Path] = None, config_dir: Optional[Path] = None
    ) -> None:
        """Initialize configuration manager.
        Args:
            config_file: Optional path to config file, defaults to
                standard location
            config_dir: Optional path to config directory, defaults to
                standard location
        """
        self.config_dir = config_dir or get_config_dir()
        self.config_file = config_file or get_config_file(self.config_dir)
        self.credential_manager = CredentialManager(config_dir=self.config_dir)
        # Ensure config directories exist
        ensure_config_dirs(self.config_dir)

    def load_config(self) -> EaselConfig:
        """Load and validate configuration from file.

        Returns:
            Validated EaselConfig instance

        Raises:
            ConfigNotFoundError: If configuration file doesn't exist
            ConfigValidationError: If configuration validation fails
        """
        if not self.config_file.exists():
            raise ConfigNotFoundError(
                f"Configuration file not found: {self.config_file}"
            )

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Invalid YAML in config file: {e}") from e
        except Exception as e:
            raise ConfigValidationError(f"Failed to read config file: {e}") from e

        if not config_data:
            raise ConfigValidationError("Configuration file is empty")

        # Environment variable substitution
        config_data = self._substitute_env_vars(config_data)

        try:
            config = EaselConfig(**config_data)
        except ValidationError as e:
            raise ConfigValidationError(f"Configuration validation failed: {e}") from e

        # Load API token separately from secure storage
        instance_name = config.canvas.name
        api_token = self.credential_manager.get_token(instance_name)

        # Fallback to environment variable
        if not api_token:
            api_token = self.credential_manager.get_token_from_env()

        if api_token:
            config.canvas.api_token = api_token

        return config

    def save_config(self, config: EaselConfig, store_token: bool = True) -> None:
        """Save configuration to file.

        Args:
            config: EaselConfig instance to save
            store_token: Whether to store the API token securely
                (default: True)

        Raises:
            ConfigValidationError: If config cannot be saved
        """
        try:
            # Extract token before saving config
            api_token = config.canvas.api_token
            config_copy = config.model_copy()
            config_copy.canvas.api_token = None  # Don't store token in config file

            # Convert to dict for YAML serialization
            config_dict = config_copy.model_dump(exclude_none=True)

            # Ensure parent directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Save configuration file
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

            # Store API token securely if provided
            if store_token and api_token:
                self.credential_manager.store_token(config.canvas.name, api_token)

        except Exception as e:
            raise ConfigValidationError(f"Failed to save configuration: {e}") from e

    def config_exists(self) -> bool:
        """Check if configuration file exists.

        Returns:
            True if config file exists, False otherwise
        """
        return self.config_file.exists()

    def has_valid_config(self) -> bool:
        """Check if valid configuration exists.

        Returns:
            True if valid config exists, False otherwise
        """
        try:
            self.load_config()
            return True
        except (ConfigNotFoundError, ConfigValidationError):
            return False

    def get_config_summary(self) -> Dict[str, Any]:
        """Get non-sensitive configuration summary for display.

        Returns:
            Dictionary with configuration summary (no sensitive data)

        Raises:
            ConfigNotFoundError: If configuration file doesn't exist
            ConfigValidationError: If configuration validation fails
        """
        config = self.load_config()

        return {
            "version": config.version,
            "canvas": {
                "name": config.canvas.name,
                "url": config.canvas.url,
                "has_token": bool(config.canvas.api_token),
            },
            "api": {
                "rate_limit": config.api.rate_limit,
                "timeout": config.api.timeout,
                "retries": config.api.retries,
                "page_size": config.api.page_size,
            },
            "cache": {
                "enabled": config.cache.enabled,
                "ttl": config.cache.ttl,
                "max_size": config.cache.max_size,
            },
            "logging": {
                "level": config.logging.level,
                "file": str(config.logging.file) if config.logging.file else None,
                "format": config.logging.format,
            },
            "config_file": str(self.config_file),
            "has_stored_credentials": self.credential_manager.has_credentials(
                config.canvas.name
            ),
        }

    def _substitute_env_vars(self, data: Any) -> Any:
        """Recursively substitute environment variables in config data.

        Args:
            data: Configuration data to process

        Returns:
            Data with environment variables substituted
        """
        if isinstance(data, dict):
            return {k: self._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            default_value = None

            # Support ${VAR:default} syntax
            if ":" in env_var:
                env_var, default_value = env_var.split(":", 1)

            return os.environ.get(env_var, default_value or data)
        else:
            return data

    def create_default_config(self, canvas_name: str, canvas_url: str) -> EaselConfig:
        """Create a default configuration with minimal required settings.

        Args:
            canvas_name: Human-readable Canvas instance name
            canvas_url: Canvas base URL

        Returns:
            Default EaselConfig instance
        """
        return EaselConfig(
            version="1.0",
            canvas=CanvasInstance(
                name=canvas_name,
                url=canvas_url,
            ),
        )
