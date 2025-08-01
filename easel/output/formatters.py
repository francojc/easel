"""Output formatters for different formats."""

import csv
import json
from io import StringIO
from typing import Any, List, Dict, Union

import yaml
from rich.console import Console
from rich.table import Table

from .base import OutputFormatter


class TableFormatter(OutputFormatter):
    """Format data as a rich table."""

    def __init__(self, max_width: int = 120) -> None:
        """Initialize table formatter.

        Args:
            max_width: Maximum table width
        """
        self.max_width = max_width
        self.console = Console(width=max_width)

    def format(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """Format data as a rich table.

        Args:
            data: Data to format

        Returns:
            Formatted table string
        """
        data_list = self._ensure_list(data)

        if not data_list:
            return "No data to display."

        # Flatten nested structures for table display
        flattened_data = [self._flatten_dict(item) for item in data_list]

        # Get all unique keys across all items
        all_keys: set[str] = set()
        for item in flattened_data:
            all_keys.update(item.keys())

        # Sort keys for consistent column order
        columns = sorted(all_keys)

        # Create rich table
        table = Table(show_header=True, header_style="bold magenta")

        # Add columns
        for column in columns:
            table.add_column(column, overflow="fold", max_width=20)

        # Add rows
        for item in flattened_data:
            row = []
            for column in columns:
                value = item.get(column, "")
                if value is None:
                    value = ""
                elif isinstance(value, bool):
                    value = "✓" if value else "✗"
                else:
                    value = str(value)
                row.append(value)
            table.add_row(*row)

        # Capture table output
        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def get_format_name(self) -> str:
        """Get format name."""
        return "table"


class JSONFormatter(OutputFormatter):
    """Format data as JSON."""

    def __init__(self, indent: int = 2) -> None:
        """Initialize JSON formatter.

        Args:
            indent: JSON indentation level
        """
        self.indent = indent

    def format(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """Format data as JSON.

        Args:
            data: Data to format

        Returns:
            JSON string
        """
        return json.dumps(data, indent=self.indent, default=str, ensure_ascii=False)

    def get_format_name(self) -> str:
        """Get format name."""
        return "json"


class CSVFormatter(OutputFormatter):
    """Format data as CSV."""

    def format(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """Format data as CSV.

        Args:
            data: Data to format

        Returns:
            CSV string
        """
        data_list = self._ensure_list(data)

        if not data_list:
            return ""

        # Flatten nested structures
        flattened_data = [self._flatten_dict(item) for item in data_list]

        # Get all unique keys
        all_keys: set[str] = set()
        for item in flattened_data:
            all_keys.update(item.keys())

        # Sort keys for consistent column order
        fieldnames = sorted(all_keys)

        # Write CSV to string buffer
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")

        writer.writeheader()
        for item in flattened_data:
            # Convert all values to strings and handle None
            csv_row = {}
            for key in fieldnames:
                value = item.get(key, "")
                if value is None:
                    csv_row[key] = ""
                elif isinstance(value, bool):
                    csv_row[key] = "true" if value else "false"
                else:
                    csv_row[key] = str(value)
            writer.writerow(csv_row)

        return output.getvalue()

    def get_format_name(self) -> str:
        """Get format name."""
        return "csv"


class YAMLFormatter(OutputFormatter):
    """Format data as YAML."""

    def format(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """Format data as YAML.

        Args:
            data: Data to format

        Returns:
            YAML string
        """
        return yaml.dump(
            data,
            default_flow_style=False,
            indent=2,
            allow_unicode=True,
            sort_keys=True,
        )

    def get_format_name(self) -> str:
        """Get format name."""
        return "yaml"
