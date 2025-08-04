"""Factory for creating output formatters."""

from typing import Dict, Type, Optional, List

from .base import OutputFormatter
from .formatters import (
    TableFormatter,
    JSONFormatter,
    CSVFormatter,
    YAMLFormatter,
)


class FormatterFactory:
    """Factory for creating output formatters."""

    _formatters: Dict[str, Type[OutputFormatter]] = {
        "table": TableFormatter,
        "json": JSONFormatter,
        "csv": CSVFormatter,
        "yaml": YAMLFormatter,
    }

    @classmethod
    def create_formatter(
        cls, 
        format_name: str, 
        columns: Optional[List[str]] = None
    ) -> OutputFormatter:
        """Create a formatter for the specified format.

        Args:
            format_name: Name of the format
            columns: Specific columns to display (for table format)

        Returns:
            Formatter instance

        Raises:
            ValueError: If format not supported
        """
        format_name = format_name.lower()

        if format_name not in cls._formatters:
            available = ", ".join(cls._formatters.keys())
            raise ValueError(
                f"Unsupported format '{format_name}'. Available: {available}"
            )

        formatter_class = cls._formatters[format_name]
        
        # Pass columns to TableFormatter, ignore for others
        if format_name == "table" and columns is not None:
            return formatter_class(columns=columns)
        else:
            return formatter_class()

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get list of supported format names.

        Returns:
            List of supported format names
        """
        return list(cls._formatters.keys())

    @classmethod
    def register_formatter(
        cls, format_name: str, formatter_class: Type[OutputFormatter]
    ) -> None:
        """Register a new formatter.

        Args:
            format_name: Name of the format
            formatter_class: Formatter class
        """
        cls._formatters[format_name.lower()] = formatter_class
