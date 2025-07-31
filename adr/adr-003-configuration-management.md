# ADR 003: Configuration Management Approach

**Status:** Accepted  
**Date:** 2025-07-31  
**Deciders:** Jerid Francom, Development Team  
**Technical Story:** Secure and user-friendly configuration system for Canvas credentials and application settings  

## Context and Problem Statement

Easel needs a configuration management system that balances security, usability, and flexibility. The system must handle sensitive credentials (Canvas API tokens), application settings, and user preferences while following security best practices and providing excellent user experience.

Key requirements:

- Secure storage of Canvas API tokens
- Support for multiple Canvas instances (future consideration)
- Environment variable overrides for CI/CD and automation
- User-friendly setup and validation
- Cross-platform compatibility (Linux, macOS, Windows)
- Configuration validation and error reporting

## Decision Drivers

- **Security:** Sensitive credentials must be stored securely
- **Usability:** Simple setup process for end users
- **Flexibility:** Support for different deployment scenarios
- **Standards Compliance:** Follow XDG Base Directory Specification where applicable
- **Automation Friendly:** Environment variable overrides for scripting
- **Validation:** Clear error messages for configuration issues

## Considered Options

- **YAML Configuration Files** with structured validation
- **JSON Configuration Files** with schema validation
- **TOML Configuration Files** with type safety
- **Environment Variables Only** approach
- **Database-based Configuration** (SQLite)

## Decision Outcome

**Chosen option:** "YAML Configuration Files with structured validation"

**Rationale:** YAML provides the best balance of human readability, comment support, and structured data representation. Combined with Pydantic validation, it offers type safety and excellent error reporting while remaining accessible to non-technical users.

### Positive Consequences

- Human-readable configuration with comment support
- Hierarchical organization of settings
- Strong validation with detailed error messages
- Cross-platform file system compatibility
- Environment variable override support
- Version control friendly (excluding sensitive tokens)

### Negative Consequences

- YAML parsing complexity and potential security issues
- File permissions management required for security
- Additional dependency (PyYAML) required

## Pros and Cons of the Options

### YAML Configuration Files

**Description:** Structured YAML files with Pydantic validation and secure credential handling

**Pros:**

- Excellent human readability and editability
- Support for comments and documentation within config
- Hierarchical data structure matches our needs
- Wide ecosystem support and tooling
- Natural environment variable substitution patterns
- Good version control properties (with secret exclusion)

**Cons:**

- YAML parsing complexity and potential security issues
- File permissions management required
- Less strict typing than some alternatives

### JSON Configuration Files

**Description:** JSON configuration with JSON Schema validation

**Pros:**

- Ubiquitous format with excellent tooling support
- Strict structure and no ambiguity in parsing
- Excellent schema validation ecosystem
- Native Python support without additional dependencies

**Cons:**

- No comment support for user documentation
- Less human-readable for complex configurations
- No native environment variable substitution

### TOML Configuration Files

**Description:** TOML files with tomli/tomllib parsing

**Pros:**

- Excellent type safety and clear syntax
- Good human readability
- Comment support
- Growing adoption in Python ecosystem

**Cons:**

- Less familiar to most users than YAML/JSON
- Limited ecosystem compared to YAML
- More verbose for nested structures

### Environment Variables Only

**Description:** Configuration entirely through environment variables

**Pros:**

- Twelve-factor app compliant
- Excellent for containerized deployments
- No file management required
- Natural CI/CD integration

**Cons:**

- Poor user experience for complex configurations
- Limited data type support
- Difficult to document and validate
- Not suitable for desktop application usage

### Database Configuration

**Description:** SQLite database for configuration storage

**Pros:**

- Excellent data integrity and validation
- Supports complex data relationships
- Good performance for large configurations
- Built-in encryption options

**Cons:**

- Overkill for simple configuration needs
- Poor user experience for manual editing
- Binary format not version control friendly
- Additional complexity for backup/restore

## Implementation Notes

### Configuration Schema

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from pathlib import Path
import os

class CanvasInstance(BaseModel):
    name: str = Field(..., description="Human-readable name for this Canvas instance")
    url: str = Field(..., description="Canvas base URL (e.g., https://university.instructure.com)")
    api_token: Optional[str] = Field(None, description="Canvas API token (stored separately)")
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v.rstrip('/')

class APISettings(BaseModel):
    rate_limit: int = Field(10, description="Requests per second limit")
    timeout: int = Field(30, description="Request timeout in seconds")
    retries: int = Field(3, description="Number of retry attempts")
    page_size: int = Field(100, description="Default pagination size")

class CacheSettings(BaseModel):
    enabled: bool = Field(True, description="Enable response caching")
    ttl: int = Field(300, description="Cache time-to-live in seconds")
    max_size: int = Field(1000, description="Maximum cache entries")

class LoggingSettings(BaseModel):
    level: str = Field("INFO", description="Logging level")
    file: Optional[Path] = Field(None, description="Log file path")
    format: str = Field("human", description="Log format (human|json)")

class EaselConfig(BaseModel):
    version: str = Field("1.0", description="Configuration version")
    canvas: CanvasInstance
    api: APISettings = APISettings()
    cache: CacheSettings = CacheSettings()
    logging: LoggingSettings = LoggingSettings()
    
    class Config:
        env_prefix = "EASEL_"
        env_nested_delimiter = "__"
```

### Configuration File Location Strategy

```python
import os
from pathlib import Path
from typing import Optional

def get_config_dir() -> Path:
    """Get configuration directory following XDG Base Directory Specification"""
    
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
    """Get the main configuration file path"""
    return get_config_dir() / "config.yaml"

def get_credentials_file() -> Path:
    """Get the encrypted credentials file path"""
    return get_config_dir() / "credentials.yaml"
```

### Secure Credential Storage

```python
import os
from cryptography.fernet import Fernet
from pathlib import Path
import keyring
import yaml

class CredentialManager:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.keyring_service = "easel-cli"
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for credentials"""
        try:
            # Try to get key from system keyring
            key_str = keyring.get_password(self.keyring_service, "encryption_key")
            if key_str:
                return key_str.encode()
        except Exception:
            pass
        
        # Generate new key
        key = Fernet.generate_key()
        try:
            keyring.set_password(self.keyring_service, "encryption_key", key.decode())
        except Exception:
            # Fallback to file-based storage with warning
            key_file = self.config_dir / ".key"
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # User read/write only
        
        return key
    
    def store_token(self, instance_name: str, token: str) -> None:
        """Store Canvas API token securely"""
        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted_token = fernet.encrypt(token.encode())
        
        credentials_file = self.config_dir / "credentials.yaml"
        
        # Load existing credentials
        credentials = {}
        if credentials_file.exists():
            with open(credentials_file, 'r') as f:
                credentials = yaml.safe_load(f) or {}
        
        # Update credentials
        credentials[instance_name] = encrypted_token.decode()
        
        # Save with secure permissions
        credentials_file.parent.mkdir(parents=True, exist_ok=True)
        with open(credentials_file, 'w') as f:
            yaml.dump(credentials, f)
        credentials_file.chmod(0o600)
    
    def get_token(self, instance_name: str) -> Optional[str]:
        """Retrieve Canvas API token"""
        credentials_file = self.config_dir / "credentials.yaml"
        if not credentials_file.exists():
            return None
        
        with open(credentials_file, 'r') as f:
            credentials = yaml.safe_load(f) or {}
        
        encrypted_token = credentials.get(instance_name)
        if not encrypted_token:
            return None
        
        key = self._get_encryption_key()
        fernet = Fernet(key)
        try:
            return fernet.decrypt(encrypted_token.encode()).decode()
        except Exception:
            return None
```

### Configuration Loading and Validation

```python
import yaml
from pathlib import Path
from typing import Optional
import os

class ConfigManager:
    def __init__(self):
        self.config_dir = get_config_dir()
        self.config_file = get_config_file()
        self.credential_manager = CredentialManager(self.config_dir)
    
    def load_config(self) -> EaselConfig:
        """Load and validate configuration"""
        if not self.config_file.exists():
            raise ConfigError(f"Configuration file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Environment variable substitution
        config_data = self._substitute_env_vars(config_data)
        
        try:
            config = EaselConfig(**config_data)
        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed: {e}")
        
        # Load API token separately
        api_token = self.credential_manager.get_token(config.canvas.name)
        if api_token:
            config.canvas.api_token = api_token
        
        return config
    
    def _substitute_env_vars(self, data):
        """Recursively substitute environment variables in config"""
        if isinstance(data, dict):
            return {k: self._substitute_env_vars(v) for k, v in data.items()}
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            return os.environ.get(env_var, data)
        else:
            return data
```

### Interactive Setup Wizard

```python
import click
from typing import Optional

def interactive_setup() -> EaselConfig:
    """Interactive configuration setup wizard"""
    click.echo("🎨 Welcome to Easel CLI Setup!")
    click.echo("Let's configure your Canvas connection.\n")
    
    # Canvas instance configuration
    canvas_name = click.prompt("Canvas instance name", default="My University")
    canvas_url = click.prompt("Canvas URL (e.g., https://university.instructure.com)")
    
    # API token setup
    click.echo("\n📝 Canvas API Token Setup:")
    click.echo("1. Go to your Canvas Account Settings")
    click.echo("2. Scroll to 'Approved Integrations'")
    click.echo("3. Click '+ New Access Token'")
    click.echo("4. Give it a purpose like 'Easel CLI Access'")
    click.echo("5. Copy the generated token\n")
    
    api_token = click.prompt("Canvas API token", hide_input=True)
    
    # Create configuration
    config_data = {
        "version": "1.0",
        "canvas": {
            "name": canvas_name,
            "url": canvas_url
        }
    }
    
    config = EaselConfig(**config_data)
    
    # Save configuration and credentials
    config_manager = ConfigManager()
    config_manager.save_config(config)
    config_manager.credential_manager.store_token(canvas_name, api_token)
    
    click.echo(f"\n✅ Configuration saved to {config_manager.config_file}")
    click.echo("Run 'easel doctor' to validate your setup!")
    
    return config
```

## Links

- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [PyYAML Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation)
- [Cryptography Library](https://cryptography.io/en/latest/)
- [Python Keyring](https://pypi.org/project/keyring/)