"""Secure credential storage and management."""

import os
from pathlib import Path
from typing import Optional

import keyring
import yaml
from cryptography.fernet import Fernet

from .exceptions import CredentialDecryptionError
from .paths import get_config_dir, get_credentials_file


class CredentialManager:
    """Manages secure storage and retrieval of Canvas API credentials."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """Initialize credential manager.

        Args:
            config_dir: Optional config directory path, defaults to
                standard location
        """
        self.config_dir = config_dir or get_config_dir()
        self.credentials_file = get_credentials_file()
        self.keyring_service = "easel-cli"

    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for credentials.

        Returns:
            Encryption key as bytes

        Raises:
            CredentialDecryptionError: If key cannot be retrieved or created
        """
        try:
            # Try to get key from system keyring
            key_str = keyring.get_password(self.keyring_service, "encryption_key")
            if key_str:
                return key_str.encode()
        except Exception:
            # Keyring might not be available or configured
            pass

        # Generate new key
        key = Fernet.generate_key()

        try:
            # Try to store in system keyring
            keyring.set_password(self.keyring_service, "encryption_key", key.decode())
        except Exception:
            # Fallback to file-based storage with warning
            key_file = self.config_dir / ".key"
            key_file.parent.mkdir(parents=True, exist_ok=True)
            key_file.write_bytes(key)

            # Set secure permissions (user read/write only)
            try:
                key_file.chmod(0o600)
            except (OSError, PermissionError):
                # Ignore permission errors on systems that don't support them
                pass

        return key

    def _load_key_from_file(self) -> Optional[bytes]:
        """Load encryption key from file as fallback.

        Returns:
            Encryption key if file exists, None otherwise
        """
        key_file = self.config_dir / ".key"
        if key_file.exists():
            try:
                return key_file.read_bytes()
            except (OSError, PermissionError):
                pass
        return None

    def store_token(self, instance_name: str, token: str) -> None:
        """Store Canvas API token securely.

        Args:
            instance_name: Name/identifier for the Canvas instance
            token: Canvas API token to store

        Raises:
            CredentialDecryptionError: If encryption fails
        """
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted_token = fernet.encrypt(token.encode())

            # Load existing credentials
            credentials: dict[str, str] = {}
            if self.credentials_file.exists():
                with open(self.credentials_file, "r", encoding="utf-8") as f:
                    credentials = yaml.safe_load(f) or {}

            # Update credentials
            credentials[instance_name] = encrypted_token.decode()

            # Save with secure permissions
            self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.credentials_file, "w", encoding="utf-8") as f:
                yaml.dump(credentials, f, default_flow_style=False)

            # Set secure permissions
            try:
                self.credentials_file.chmod(0o600)
            except (OSError, PermissionError):
                # Ignore permission errors on systems that don't support them
                pass

        except Exception as e:
            raise CredentialDecryptionError(f"Failed to store credential: {e}") from e

    def get_token(self, instance_name: str) -> Optional[str]:
        """Retrieve Canvas API token.

        Args:
            instance_name: Name/identifier for the Canvas instance

        Returns:
            Decrypted API token if found, None otherwise

        Raises:
            CredentialDecryptionError: If decryption fails
        """
        if not self.credentials_file.exists():
            return None

        try:
            with open(self.credentials_file, "r", encoding="utf-8") as f:
                credentials = yaml.safe_load(f) or {}

            encrypted_token = credentials.get(instance_name)
            if not encrypted_token:
                return None

            # Try to get key from keyring first, then file fallback
            key = None
            try:
                key_str = keyring.get_password(self.keyring_service, "encryption_key")
                if key_str:
                    key = key_str.encode()
            except Exception:
                pass

            if not key:
                key = self._load_key_from_file()

            if not key:
                raise CredentialDecryptionError("Encryption key not found")

            fernet = Fernet(key)
            return fernet.decrypt(encrypted_token.encode()).decode()

        except Exception as e:
            if isinstance(e, CredentialDecryptionError):
                raise
            raise CredentialDecryptionError(
                f"Failed to retrieve credential: {e}"
            ) from e

    def remove_token(self, instance_name: str) -> bool:
        """Remove stored token for an instance.

        Args:
            instance_name: Name/identifier for the Canvas instance

        Returns:
            True if token was removed, False if it didn't exist
        """
        if not self.credentials_file.exists():
            return False

        try:
            with open(self.credentials_file, "r", encoding="utf-8") as f:
                credentials = yaml.safe_load(f) or {}

            if instance_name not in credentials:
                return False

            del credentials[instance_name]

            # Save updated credentials
            with open(self.credentials_file, "w", encoding="utf-8") as f:
                yaml.dump(credentials, f, default_flow_style=False)

            return True

        except Exception:
            return False

    def list_stored_instances(self) -> list[str]:
        """List all Canvas instances with stored credentials.

        Returns:
            List of instance names that have stored credentials
        """
        if not self.credentials_file.exists():
            return []

        try:
            with open(self.credentials_file, "r", encoding="utf-8") as f:
                credentials = yaml.safe_load(f) or {}
            return list(credentials.keys())
        except Exception:
            return []

    def has_credentials(self, instance_name: str) -> bool:
        """Check if credentials exist for an instance.

        Args:
            instance_name: Name/identifier for the Canvas instance

        Returns:
            True if credentials exist, False otherwise
        """
        return instance_name in self.list_stored_instances()

    def get_token_from_env(self, var_name: str = "CANVAS_API_TOKEN") -> Optional[str]:
        """Get API token from environment variable.

        Args:
            var_name: Environment variable name to check

        Returns:
            Token from environment variable if set, None otherwise
        """
        return os.environ.get(var_name)
