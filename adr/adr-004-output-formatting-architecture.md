# ADR 004: Output Formatting Architecture

**Status:** Accepted
**Date:** 2025-07-31
**Deciders:** Jerid Francom, Development Team
**Technical Story:** Flexible and extensible output formatting system for multiple data presentation needs

## Context and Problem Statement

Easel needs a flexible output formatting system that can present Canvas data in multiple formats to serve different use cases. Users need human-readable tables for interactive use, JSON for programmatic consumption, CSV for Excel integration, and YAML for configuration-style outputs.

The system must support:

- Multiple output formats with consistent data structure
- Extensible architecture for future format additions
- Field selection and customization capabilities
- Streaming support for large datasets
- Format-specific optimizations (e.g., Excel-compatible CSV)
- Consistent error handling across formats

## Decision Drivers

- **User Experience:** Clean, readable output for interactive CLI usage
- **Automation:** Machine-readable formats for scripting and integration
- **Extensibility:** Easy to add new formats without code changes
- **Performance:** Efficient handling of large datasets
- **Standards Compliance:** Follow format specifications (RFC 4180 for CSV, etc.)
- **Tool Integration:** Work seamlessly with common tools (jq, Excel, etc.)

## Considered Options

- **Rich Library** with pluggable formatter architecture
- **Tabulate Library** with custom format extensions
- **Template-based** formatting (Jinja2)
- **Built-in Formatters** with manual implementation
- **Pandas DataFrame** approach for unified data handling

## Decision Outcome

**Chosen option:** "Rich Library with pluggable formatter architecture"

**Rationale:** Rich provides excellent table formatting capabilities while allowing us to build a clean plugin architecture for other formats. This approach gives us the best terminal output experience while maintaining flexibility for adding new formats.

### Positive Consequences

- Excellent table formatting with colors, borders, and alignment
- Clean plugin architecture for extensibility
- Built-in progress bars and status indicators
- Consistent API across all formatters
- Performance optimizations for large datasets
- Rich ecosystem integration

### Negative Consequences

- Additional dependency with some complexity
- Terminal-focused library may be overkill for simple formats
- Learning curve for Rich's advanced features

## Pros and Cons of the Options

### Rich Library with Plugin Architecture

**Description:** Use Rich for table formatting with custom plugin system for other formats

**Pros:**

- Outstanding table formatting with styling and colors
- Built-in progress indicators and status displays
- Clean plugin architecture possible with Python entry points
- Excellent performance for terminal output
- Active development and community support
- Handles terminal detection and fallbacks automatically

**Cons:**

- Primarily terminal-focused (though programmatic use is supported)
- Additional learning curve for advanced features
- May be overkill for simple text formatting needs

### Tabulate Library

**Description:** Use tabulate as the core with custom extensions for other formats

**Pros:**

- Lightweight and focused on table formatting
- Simple API with minimal learning curve
- Good performance for basic table needs
- Wide format support built-in

**Cons:**

- Limited styling and color support
- No built-in support for progress indicators
- Would need significant extension for rich formatting
- Less active development than Rich

### Template-based (Jinja2)

**Description:** Use Jinja2 templates for all output formatting

**Pros:**

- Maximum flexibility and customization
- Template-based approach familiar to many developers
- Easy to modify output without code changes
- Good separation of concerns

**Cons:**

- Performance overhead for simple formatting
- Complex setup for tabular data
- No built-in table formatting optimizations
- Would need significant infrastructure development

### Built-in Manual Implementation

**Description:** Implement all formatters manually without external dependencies

**Pros:**

- No external dependencies
- Complete control over implementation
- Optimized for our specific needs
- Minimal complexity

**Cons:**

- Significant development effort required
- Reinventing well-solved problems
- Maintenance burden for formatting edge cases
- Limited styling and presentation capabilities

### Pandas DataFrame Approach

**Description:** Use pandas for data manipulation with its built-in formatting

**Pros:**

- Excellent data manipulation capabilities
- Built-in support for multiple export formats
- Optimized for large datasets
- Consistent data structure handling

**Cons:**

- Heavy dependency for simple formatting needs
- CLI tools typically avoid pandas due to size
- Limited customization of output presentation
- Overkill for most Canvas API data

## Implementation Notes

### Formatter Interface Design

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Iterator
from rich.console import Console
import io

class OutputFormatter(ABC):
    """Base class for all output formatters"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Formatter name for CLI selection"""
        pass

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Default file extension for this format"""
        pass

    @abstractmethod
    def format(self, data: List[Dict[str, Any]], **kwargs) -> str:
        """Format data and return string representation"""
        pass

    def format_stream(self, data: Iterator[Dict[str, Any]], **kwargs) -> Iterator[str]:
        """Stream formatting for large datasets (optional override)"""
        # Default implementation - collect all data then format
        collected_data = list(data)
        yield self.format(collected_data, **kwargs)

    def validate_data(self, data: List[Dict[str, Any]]) -> None:
        """Validate data structure (optional override)"""
        pass

class FormatterRegistry:
    """Registry for managing output formatters"""

    def __init__(self):
        self._formatters: Dict[str, OutputFormatter] = {}

    def register(self, formatter: OutputFormatter) -> None:
        """Register a new formatter"""
        self._formatters[formatter.name] = formatter

    def get(self, name: str) -> OutputFormatter:
        """Get formatter by name"""
        if name not in self._formatters:
            available = ", ".join(self._formatters.keys())
            raise ValueError(f"Unknown formatter '{name}'. Available: {available}")
        return self._formatters[name]

    def list_formatters(self) -> List[str]:
        """List all available formatter names"""
        return list(self._formatters.keys())

# Global registry instance
formatter_registry = FormatterRegistry()
```

### Rich Table Formatter Implementation

```python
from rich.table import Table
from rich.console import Console
from typing import List, Dict, Any, Optional
import io

class TableFormatter(OutputFormatter):
    """Rich table formatter for terminal output"""

    @property
    def name(self) -> str:
        return "table"

    @property
    def file_extension(self) -> str:
        return "txt"

    def format(self, data: List[Dict[str, Any]], **kwargs) -> str:
        if not data:
            return "No data to display."

        # Create Rich table
        table = Table(show_header=True, header_style="bold blue")

        # Add columns from first row
        first_row = data[0]
        for column in first_row.keys():
            table.add_column(column.replace('_', ' ').title())

        # Add rows
        for row in data:
            values = [str(value) if value is not None else "-" for value in row.values()]
            table.add_row(*values)

        # Render to string
        console = Console(file=io.StringIO(), width=120, legacy_windows=False)
        console.print(table)
        return console.file.getvalue()

# Register the formatter
formatter_registry.register(TableFormatter())
```

### JSON Formatter with jq Compatibility

```python
import json
from typing import List, Dict, Any

class JSONFormatter(OutputFormatter):
    """JSON formatter optimized for jq compatibility"""

    @property
    def name(self) -> str:
        return "json"

    @property
    def file_extension(self) -> str:
        return "json"

    def format(self, data: List[Dict[str, Any]], **kwargs) -> str:
        # Ensure consistent field ordering for predictable jq queries
        if data:
            # Sort keys for consistent output
            sorted_data = []
            for item in data:
                sorted_item = {k: item[k] for k in sorted(item.keys())}
                sorted_data.append(sorted_item)
            data = sorted_data

        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)

    def format_stream(self, data: Iterator[Dict[str, Any]], **kwargs) -> Iterator[str]:
        """Stream JSON objects for large datasets"""
        yield "[\n"
        first = True
        for item in data:
            if not first:
                yield ",\n"
            yield json.dumps(item, ensure_ascii=False, sort_keys=True)
            first = False
        yield "\n]"

formatter_registry.register(JSONFormatter())
```

### CSV Formatter with Excel Compatibility

```python
import csv
import io
from typing import List, Dict, Any, Iterator

class CSVFormatter(OutputFormatter):
    """CSV formatter with Excel compatibility"""

    @property
    def name(self) -> str:
        return "csv"

    @property
    def file_extension(self) -> str:
        return "csv"

    def format(self, data: List[Dict[str, Any]], **kwargs) -> str:
        if not data:
            return ""

        output = io.StringIO()

        # Use Excel dialect for maximum compatibility
        writer = csv.DictWriter(
            output,
            fieldnames=data[0].keys(),
            dialect='excel',
            lineterminator='\n'
        )

        writer.writeheader()
        writer.writerows(data)

        # Add BOM for Excel UTF-8 compatibility
        content = output.getvalue()
        return '\ufeff' + content

    def format_stream(self, data: Iterator[Dict[str, Any]], **kwargs) -> Iterator[str]:
        """Stream CSV for large datasets"""
        first_item = next(data, None)
        if first_item is None:
            return

        # Yield header with BOM
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=first_item.keys(), dialect='excel')
        writer.writeheader()
        yield '\ufeff' + output.getvalue()

        # Yield first row
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=first_item.keys(), dialect='excel')
        writer.writerow(first_item)
        yield output.getvalue()

        # Yield remaining rows
        for item in data:
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=first_item.keys(), dialect='excel')
            writer.writerow(item)
            yield output.getvalue()

formatter_registry.register(CSVFormatter())
```

### Field Selection and Filtering

```python
from typing import List, Dict, Any, Optional, Set

class FieldSelector:
    """Handle field selection and filtering for output"""

    @staticmethod
    def select_fields(data: List[Dict[str, Any]], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Select specific fields from data"""
        if not fields or not data:
            return data

        # Validate fields exist
        available_fields = set(data[0].keys()) if data else set()
        invalid_fields = set(fields) - available_fields
        if invalid_fields:
            raise ValueError(f"Invalid fields: {', '.join(invalid_fields)}. "
                           f"Available: {', '.join(available_fields)}")

        return [{field: row.get(field) for field in fields} for row in data]

    @staticmethod
    def exclude_fields(data: List[Dict[str, Any]], exclude: List[str]) -> List[Dict[str, Any]]:
        """Exclude specific fields from data"""
        if not exclude or not data:
            return data

        exclude_set = set(exclude)
        return [{k: v for k, v in row.items() if k not in exclude_set} for row in data]

    @staticmethod
    def rename_fields(data: List[Dict[str, Any]], field_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Rename fields in data"""
        if not field_mapping or not data:
            return data

        return [{field_mapping.get(k, k): v for k, v in row.items()} for row in data]
```

### CLI Integration

```python
import click
from typing import List, Dict, Any, Optional

@click.command()
@click.option('--format', 'output_format',
              type=click.Choice(formatter_registry.list_formatters()),
              default='table',
              help='Output format')
@click.option('--fields',
              help='Comma-separated list of fields to include')
@click.option('--exclude',
              help='Comma-separated list of fields to exclude')
@click.option('--output', 'output_file',
              type=click.Path(),
              help='Output file (default: stdout)')
def format_and_output(data: List[Dict[str, Any]],
                     output_format: str,
                     fields: Optional[str] = None,
                     exclude: Optional[str] = None,
                     output_file: Optional[str] = None):
    """Format and output data using specified formatter"""

    # Apply field selection
    if fields:
        field_list = [f.strip() for f in fields.split(',')]
        data = FieldSelector.select_fields(data, field_list)

    if exclude:
        exclude_list = [f.strip() for f in exclude.split(',')]
        data = FieldSelector.exclude_fields(data, exclude_list)

    # Get formatter and format data
    formatter = formatter_registry.get(output_format)
    formatted_output = formatter.format(data)

    # Output to file or stdout
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        click.echo(f"Output written to {output_file}")
    else:
        click.echo(formatted_output)
```

### Plugin Architecture for Extensions

```python
# Entry points in pyproject.toml for plugins
[tool.poetry.plugins."easel.formatters"]
table = "easel.formatters.table:TableFormatter"
json = "easel.formatters.json:JSONFormatter"
csv = "easel.formatters.csv:CSVFormatter"
yaml = "easel.formatters.yaml:YAMLFormatter"

# Plugin discovery
import pkg_resources

def load_formatter_plugins():
    """Load formatters from entry points"""
    for entry_point in pkg_resources.iter_entry_points('easel.formatters'):
        try:
            formatter_class = entry_point.load()
            formatter = formatter_class()
            formatter_registry.register(formatter)
        except Exception as e:
            click.echo(f"Warning: Failed to load formatter {entry_point.name}: {e}")
```

## Links

- [Rich Documentation](https://rich.readthedocs.io/)
- [CSV RFC 4180 Specification](https://tools.ietf.org/html/rfc4180)
- [JSON Specification](https://www.json.org/)
- [YAML Specification](https://yaml.org/spec/)
- [jq Manual](https://stedolan.github.io/jq/manual/)
