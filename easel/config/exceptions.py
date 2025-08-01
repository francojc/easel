"""Configuration-specific exceptions for Easel CLI."""


class ConfigError(Exception):
    """Base exception for configuration-related errors."""

    pass


class ConfigNotFoundError(ConfigError):
    """Raised when configuration file is not found."""

    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""

    pass


class CredentialError(ConfigError):
    """Base exception for credential-related errors."""

    pass


class CredentialNotFoundError(CredentialError):
    """Raised when required credentials are not found."""

    pass


class CredentialDecryptionError(CredentialError):
    """Raised when credential decryption fails."""

    pass
