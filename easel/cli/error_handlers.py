"""Error handling utilities for CLI commands."""

import click
from typing import NoReturn

from easel.api.exceptions import (
    CanvasAPIError,
    CanvasAuthError,
    CanvasNotFoundError,
    CanvasPermissionError,
    CanvasRateLimitError,
    CanvasServerError,
    CanvasTimeoutError,
    CanvasValidationError,
)
from easel.config.exceptions import (
    ConfigError,
    ConfigNotFoundError,
    ConfigValidationError,
    CredentialDecryptionError,
)


def handle_canvas_api_error(error: CanvasAPIError, verbose: bool = False) -> NoReturn:
    """Handle Canvas API errors with actionable messages.
    
    Args:
        error: The Canvas API error to handle
        verbose: Whether to show verbose error information
        
    Raises:
        click.ClickException: Always raises with an appropriate message
    """
    if isinstance(error, CanvasAuthError):
        message = (
            "Authentication failed. Your API token may be invalid or expired.\n"
            "Try running 'easel config init' to set up a new token."
        )
    elif isinstance(error, CanvasPermissionError):
        message = (
            "Permission denied. You don't have access to this resource.\n"
            "Make sure you have the appropriate permissions in Canvas."
        )
    elif isinstance(error, CanvasNotFoundError):
        message = (
            "Resource not found. The requested course, assignment, or user doesn't exist.\n"
            "Verify the ID is correct and that you have access to the resource."
        )
    elif isinstance(error, CanvasRateLimitError):
        retry_msg = ""
        if error.retry_after:
            retry_msg = f" Try again in {error.retry_after} seconds."
        message = f"Rate limit exceeded. Canvas is limiting API requests.{retry_msg}"
    elif isinstance(error, CanvasTimeoutError):
        message = (
            "Request timeout. Canvas is taking too long to respond.\n"
            "This might be temporary - try again in a few moments."
        )
    elif isinstance(error, CanvasServerError):
        message = (
            "Canvas server error. There's an issue on Canvas's side.\n"
            "This is usually temporary - try again later."
        )
    elif isinstance(error, CanvasValidationError):
        message = (
            f"Invalid request: {error}\n"
            "Check your command arguments and try again."
        )
    else:
        message = f"Canvas API error: {error}"
    
    if verbose:
        message += f"\n\nError details: {error}"
        if hasattr(error, 'status_code') and error.status_code:
            message += f"\nHTTP Status: {error.status_code}"
    
    raise click.ClickException(message)


def handle_config_error(error: ConfigError, verbose: bool = False) -> NoReturn:
    """Handle configuration errors with actionable messages.
    
    Args:
        error: The configuration error to handle
        verbose: Whether to show verbose error information
        
    Raises:
        click.ClickException: Always raises with an appropriate message
    """
    if isinstance(error, ConfigNotFoundError):
        message = (
            "Configuration not found. You need to set up Easel first.\n"
            "Run 'easel config init' to create your configuration."
        )
    elif isinstance(error, ConfigValidationError):
        message = (
            f"Invalid configuration: {error}\n"
            "Run 'easel doctor' to check your configuration."
        )
    elif isinstance(error, CredentialDecryptionError):
        message = (
            "Failed to decrypt stored credentials. Your credentials may be corrupted.\n"
            "Try running 'easel config init' to reset your credentials."
        )
    else:
        message = f"Configuration error: {error}"
    
    if verbose:
        message += f"\n\nError details: {error}"
    
    raise click.ClickException(message)


def handle_general_error(error: Exception, verbose: bool = False) -> NoReturn:
    """Handle general errors with appropriate messages.
    
    Args:
        error: The error to handle
        verbose: Whether to show verbose error information
        
    Raises:
        click.ClickException: Always raises with an appropriate message
    """
    if verbose:
        # In verbose mode, let the full exception bubble up for debugging
        raise error
    
    # For non-verbose mode, provide a user-friendly message
    message = f"An unexpected error occurred: {error}"
    
    # Add suggestions based on common error types
    error_str = str(error).lower()
    if "connection" in error_str or "network" in error_str:
        message += "\n\nThis looks like a network issue. Check your internet connection."
    elif "ssl" in error_str or "certificate" in error_str:
        message += "\n\nThis looks like an SSL/certificate issue. Check your network settings."
    elif "permission" in error_str:
        message += "\n\nThis looks like a permission issue. Check file permissions."
    
    message += "\n\nFor more details, use the --verbose flag."
    
    raise click.ClickException(message)


def with_error_handling(func):
    """Decorator to add consistent error handling to CLI commands.
    
    This decorator catches common exceptions and converts them to user-friendly
    messages using the error handlers above.
    
    Args:
        func: The CLI command function to wrap
        
    Returns:
        The wrapped function with error handling
    """
    def wrapper(*args, **kwargs):
        # Extract context from args to get verbose flag
        ctx = None
        for arg in args:
            if hasattr(arg, 'verbose'):
                ctx = arg
                break
        
        verbose = ctx.verbose if ctx else False
        
        try:
            return func(*args, **kwargs)
        except CanvasAPIError as e:
            handle_canvas_api_error(e, verbose)
        except ConfigError as e:
            handle_config_error(e, verbose)
        except click.ClickException:
            # Re-raise click exceptions as-is
            raise
        except Exception as e:
            handle_general_error(e, verbose)
    
    return wrapper