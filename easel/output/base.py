"""Base output formatter interface."""

from abc import ABC, abstractmethod
from typing import Any, List, Dict, Union


class OutputFormatter(ABC):
    """Base class for output formatters."""

    @abstractmethod
    def format(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """Format data for output.

        Args:
            data: Data to format (single dict or list of dicts)

        Returns:
            Formatted string ready for display
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """Get the name of this format.

        Returns:
            Format name (e.g., 'table', 'json')
        """
        pass

    def _ensure_list(
        self, data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Ensure data is a list of dictionaries.

        Args:
            data: Input data

        Returns:
            List of dictionaries
        """
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    def _flatten_dict(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dictionaries for table display.

        Args:
            data: Dictionary to flatten
            prefix: Prefix for nested keys

        Returns:
            Flattened dictionary
        """
        result = {}

        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                result.update(self._flatten_dict(value, new_key))
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # For lists of dicts, just show count
                    result[new_key] = f"[{len(value)} items]"
                else:
                    # For simple lists, join with commas
                    result[new_key] = ", ".join(str(v) for v in value)
            else:
                result[new_key] = value

        return result
