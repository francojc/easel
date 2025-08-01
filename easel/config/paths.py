"""Cross-platform configuration directory and file path management."""

import os
from pathlib import Path


def get_config_dir() -> Path:
    """Get configuration directory following XDG Base Directory Specification.

    Returns:
        Path to the Easel configuration directory
    """
    # Explicit override
    if config_home := os.environ.get("EASEL_CONFIG_DIR"):
        return Path(config_home)

    # XDG Base Directory Specification
    if config_home := os.environ.get("XDG_CONFIG_HOME"):
        return Path(config_home) / "easel"

    # Platform-specific defaults
    home = Path.home()

    if os.name == "nt":  # Windows
        return home / "AppData" / "Local" / "easel"
    elif os.name == "posix":
        # macOS and Linux
        return home / ".config" / "easel"
    else:
        # Fallback
        return home / ".easel"


def get_config_file() -> Path:
    """Get the main configuration file path.

    Returns:
        Path to config.yaml file
    """
    return get_config_dir() / "config.yaml"


def get_credentials_file() -> Path:
    """Get the encrypted credentials file path.

    Returns:
        Path to credentials.yaml file
    """
    return get_config_dir() / "credentials.yaml"


def get_log_dir() -> Path:
    """Get the log directory path.

    Returns:
        Path to logs directory
    """
    return get_config_dir() / "logs"


def get_cache_dir() -> Path:
    """Get the cache directory path.

    Returns:
        Path to cache directory
    """
    # Follow XDG specification for cache
    if cache_home := os.environ.get("XDG_CACHE_HOME"):
        return Path(cache_home) / "easel"

    home = Path.home()

    if os.name == "nt":  # Windows
        return home / "AppData" / "Local" / "easel" / "cache"
    elif os.name == "posix":
        return home / ".cache" / "easel"
    else:
        return get_config_dir() / "cache"


def ensure_config_dirs() -> None:
    """Ensure all necessary configuration directories exist."""
    dirs_to_create = [
        get_config_dir(),
        get_log_dir(),
        get_cache_dir(),
    ]

    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)

        # Set secure permissions on config directory
        if directory == get_config_dir():
            try:
                directory.chmod(0o700)  # User read/write/execute only
            except (OSError, PermissionError):
                # Ignore permission errors on systems that don't support them
                pass
