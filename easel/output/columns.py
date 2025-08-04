"""Column configuration for output formatting."""

from typing import Dict, List, Set, Optional, Any, Union


# Default column configurations for each model type
DEFAULT_COLUMNS: Dict[str, List[str]] = {
    'Course': ['id', 'name', 'course_code', 'workflow_state'],
    'Assignment': ['id', 'name', 'due_at', 'points_possible'],
    'User': ['id', 'name', 'email'],
    'Module': ['id', 'name', 'position', 'state'],
    'Submission': ['id', 'user_id', 'assignment_id', 'score', 'grade'],
    'Discussion': ['id', 'title', 'posted_at', 'published'],
    'Page': ['url', 'title', 'updated_at', 'published'],
}


def get_default_columns(model_type: str) -> List[str]:
    """Get default columns for a model type.
    
    Args:
        model_type: Name of the model type (e.g., 'Course', 'Assignment')
        
    Returns:
        List of default column names
    """
    return DEFAULT_COLUMNS.get(model_type, [])


def parse_include_columns(include_args: tuple[str, ...]) -> List[str]:
    """Parse --include arguments into column names.
    
    Args:
        include_args: Tuple of include arguments from CLI
        
    Returns:
        List of column names to include
    """
    columns = []
    
    for arg in include_args:
        # Handle comma-separated values
        if ',' in arg:
            columns.extend([col.strip() for col in arg.split(',')])
        else:
            columns.append(arg.strip())
    
    return columns


def filter_columns_for_data(
    data: Union[Dict[str, Any], List[Dict[str, Any]]], 
    columns: Optional[List[str]] = None,
    model_type: Optional[str] = None
) -> List[str]:
    """Filter and validate columns based on available data.
    
    Args:
        data: Data to be formatted
        columns: Requested columns (None for default)
        model_type: Model type for default columns
        
    Returns:
        List of valid column names to display
    """
    # Ensure data is a list
    if isinstance(data, dict):
        data_list = [data]
    elif isinstance(data, list):
        data_list = data
    else:
        return []
    
    if not data_list:
        return []
    
    # Get all available columns from the data
    available_columns: Set[str] = set()
    for item in data_list:
        if isinstance(item, dict):
            available_columns.update(item.keys())
    
    # If no columns specified, use defaults
    if not columns:
        if model_type:
            default_cols = get_default_columns(model_type)
            # Only include default columns that exist in the data
            columns = [col for col in default_cols if col in available_columns]
        else:
            # Fallback to all available columns if no model type
            columns = sorted(available_columns)
    
    # Handle special 'all' keyword
    if 'all' in columns:
        return sorted(available_columns)
    
    # Filter to only valid columns that exist in the data
    valid_columns = [col for col in columns if col in available_columns]
    
    return valid_columns


def infer_model_type(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Optional[str]:
    """Infer the model type from data structure.
    
    Args:
        data: Data to analyze
        
    Returns:
        Inferred model type name or None
    """
    # Ensure data is a list
    if isinstance(data, dict):
        data_list = [data]
    elif isinstance(data, list):
        data_list = data
    else:
        return None
    
    if not data_list:
        return None
    
    # Get first item's keys for analysis
    first_item = data_list[0]
    if not isinstance(first_item, dict):
        return None
    
    keys = set(first_item.keys())
    
    # Model detection based on distinctive field combinations
    if {'id', 'name', 'course_code'}.issubset(keys):
        return 'Course'
    elif {'id', 'name', 'due_at', 'course_id'}.issubset(keys):
        return 'Assignment'
    elif {'id', 'user_id', 'assignment_id', 'score'}.issubset(keys):
        return 'Submission'
    elif {'id', 'name', 'position'}.issubset(keys) and 'items_count' in keys:
        return 'Module'
    elif {'id', 'title', 'message'}.issubset(keys):
        return 'Discussion'
    elif {'url', 'title', 'body'}.issubset(keys):
        return 'Page'
    elif {'id', 'name', 'email'}.issubset(keys):
        return 'User'
    
    return None