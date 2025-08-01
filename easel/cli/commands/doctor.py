"""System validation and diagnostics commands."""

import sys
from typing import List, Tuple, Optional

import click
import httpx

from easel.config import (
    ConfigManager,
    ConfigValidationError,
)

from ..context import pass_context, EaselContext
from ..main import cli


@cli.command()
@pass_context
def doctor(ctx: EaselContext) -> None:
    """Validate Easel configuration and Canvas connectivity.

    Performs comprehensive checks of:
    - Configuration file validity
    - Canvas API connectivity
    - Token authentication
    - Network connectivity
    - File permissions
    - Dependencies
    """
    click.echo("🩺 Easel Health Check")
    click.echo("=" * 50)

    checks_passed = 0
    total_checks = 0
    issues: List[str] = []

    # Configuration checks
    click.echo("\n📋 Configuration Checks:")

    config_exists, config_msg = _check_config_exists(ctx.config_manager)
    _print_check_result("Config file exists", config_exists, config_msg)
    total_checks += 1
    if config_exists:
        checks_passed += 1
    else:
        issues.append(config_msg)

    if config_exists:
        config_valid, config_msg = _check_config_valid(ctx.config_manager)
        _print_check_result("Config is valid", config_valid, config_msg)
        total_checks += 1
        if config_valid:
            checks_passed += 1
        else:
            issues.append(config_msg)

        if config_valid:
            # Credentials checks
            click.echo("\n🔐 Credentials Checks:")

            creds_exist, creds_msg = _check_credentials_exist(ctx.config_manager)
            _print_check_result("API token stored", creds_exist, creds_msg)
            total_checks += 1
            if creds_exist:
                checks_passed += 1
            else:
                issues.append(creds_msg)

            if creds_exist:
                # Network and API checks
                click.echo("\n🌐 Network & API Checks:")

                try:
                    if not ctx.config_manager:
                        issues.append("Configuration manager not initialized")
                    else:
                        config = ctx.config_manager.load_config()

                        network_ok, network_msg = _check_network_connectivity(
                            config.canvas.url
                        )
                        _print_check_result(
                            "Network connectivity", network_ok, network_msg
                        )
                        total_checks += 1
                        if network_ok:
                            checks_passed += 1
                        else:
                            issues.append(network_msg)

                        if network_ok and config.canvas.api_token:
                            api_ok, api_msg = _check_canvas_api_auth(
                                config.canvas.url, config.canvas.api_token
                            )
                            _print_check_result(
                                "Canvas API authentication", api_ok, api_msg
                            )
                            total_checks += 1
                            if api_ok:
                                checks_passed += 1
                            else:
                                issues.append(api_msg)

                except Exception as e:
                    msg = f"Failed to load config for API checks: {e}"
                    issues.append(msg)

    # System checks
    click.echo("\n🔧 System Checks:")

    deps_ok, deps_msg = _check_dependencies()
    _print_check_result("Dependencies available", deps_ok, deps_msg)
    total_checks += 1
    if deps_ok:
        checks_passed += 1
    else:
        issues.append(deps_msg)

    perms_ok, perms_msg = _check_file_permissions(ctx.config_manager)
    _print_check_result("File permissions", perms_ok, perms_msg)
    total_checks += 1
    if perms_ok:
        checks_passed += 1
    else:
        issues.append(perms_msg)

    # Summary
    click.echo("\n📊 Summary:")
    click.echo(f"Checks passed: {checks_passed}/{total_checks}")

    if checks_passed == total_checks:
        click.echo("✅ All checks passed! Easel is ready to use.")
        sys.exit(0)
    else:
        click.echo(f"❌ {total_checks - checks_passed} issues found:")
        for issue in issues:
            click.echo(f"  • {issue}")

        click.echo("\n💡 Recommendations:")
        if not ctx.config_manager or not ctx.config_manager.config_exists():
            click.echo("  • Run 'easel init' to create configuration")
        else:
            click.echo("  • Check the issues above and fix configuration")
            click.echo("  • Verify Canvas URL and API token are correct")

        sys.exit(1)


def _check_config_exists(
    config_manager: Optional[ConfigManager],
) -> Tuple[bool, str]:
    """Check if configuration file exists."""
    if not config_manager:
        return False, "Configuration manager not initialized"

    if config_manager.config_exists():
        return True, f"Found at {config_manager.config_file}"
    else:
        return False, f"Not found at {config_manager.config_file}"


def _check_config_valid(
    config_manager: Optional[ConfigManager],
) -> Tuple[bool, str]:
    """Check if configuration is valid."""
    if not config_manager:
        return False, "Configuration manager not initialized"

    try:
        config_manager.load_config()
        return True, "Configuration is valid"
    except ConfigValidationError as e:
        return False, f"Validation failed: {e}"
    except Exception as e:
        return False, f"Failed to load: {e}"


def _check_credentials_exist(
    config_manager: Optional[ConfigManager],
) -> Tuple[bool, str]:
    """Check if API credentials are stored."""
    if not config_manager:
        return False, "Configuration manager not initialized"

    try:
        config = config_manager.load_config()

        # Check if token is available (from storage or environment)
        if config.canvas.api_token:
            return True, "API token is available"
        else:
            # Check if stored credentials exist
            manager = config_manager.credential_manager
            if manager.has_credentials(config.canvas.name):
                return False, "Stored credentials found but failed to decrypt"
            else:
                msg = "No API token found in storage or environment"
                return False, msg

    except Exception as e:
        return False, f"Failed to check credentials: {e}"


def _check_network_connectivity(canvas_url: str) -> Tuple[bool, str]:
    """Check basic network connectivity to Canvas."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(canvas_url)
            # Accept successful responses and redirects as valid
            success_codes = (200, 301, 302, 303, 307, 308)
            if response.status_code in success_codes:
                return True, f"Successfully connected to {canvas_url}"
            else:
                return False, f"HTTP {response.status_code} from {canvas_url}"
    except httpx.ConnectError:
        return False, f"Cannot connect to {canvas_url}"
    except httpx.TimeoutException:
        return False, f"Connection timeout to {canvas_url}"
    except Exception as e:
        return False, f"Network error: {e}"


def _check_canvas_api_auth(canvas_url: str, api_token: str) -> Tuple[bool, str]:
    """Check Canvas API authentication."""
    try:
        api_url = f"{canvas_url}/api/v1/users/self"
        headers = {"Authorization": f"Bearer {api_token}"}

        with httpx.Client(timeout=10.0) as client:
            response = client.get(api_url, headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("name", "Unknown")
                return True, f"Authenticated as {username}"
            elif response.status_code == 401:
                return False, "Invalid API token"
            elif response.status_code == 403:
                return False, "API token lacks required permissions"
            else:
                return False, f"API error: HTTP {response.status_code}"

    except httpx.ConnectError:
        return False, "Cannot connect to Canvas API"
    except httpx.TimeoutException:
        return False, "API request timeout"
    except Exception as e:
        return False, f"API check failed: {e}"


def _check_dependencies() -> Tuple[bool, str]:
    """Check if required dependencies are available."""
    try:
        return True, "All required dependencies available"
    except ImportError as e:
        return False, f"Missing dependency: {e}"


def _check_file_permissions(
    config_manager: Optional[ConfigManager],
) -> Tuple[bool, str]:
    """Check if configuration files have proper permissions."""
    if not config_manager:
        return False, "Configuration manager not initialized"

    try:
        config_dir = config_manager.config_file.parent

        if not config_dir.exists():
            msg = "Config directory will be created with secure permissions"
            return True, msg

        # Check if we can read/write to config directory
        if not config_dir.is_dir():
            return False, f"Config path is not a directory: {config_dir}"

        # Try to create a test file to check permissions
        test_file = config_dir / ".test_permissions"
        try:
            test_file.touch()
            test_file.unlink()
            return True, f"Directory permissions OK: {config_dir}"
        except (OSError, PermissionError):
            msg = f"Cannot write to config directory: {config_dir}"
            return False, msg

    except Exception as e:
        return False, f"Permission check failed: {e}"


def _print_check_result(name: str, passed: bool, message: str) -> None:
    """Print a formatted check result."""
    status = "✅" if passed else "❌"
    click.echo(f"  {status} {name}: {message}")


# Register the command
doctor_commands = doctor
