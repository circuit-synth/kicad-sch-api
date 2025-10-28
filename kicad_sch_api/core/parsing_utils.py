"""
Utility functions for parsing S-expression data.

This module contains helper functions used by various parsers
to handle common parsing patterns safely and consistently.
"""

import logging
from typing import Any

import sexpdata

logger = logging.getLogger(__name__)


def parse_bool_property(value: Any, default: bool = True) -> bool:
    """
    Parse a boolean property from S-expression data.

    Handles both sexpdata.Symbol and string types, converting yes/no to bool.
    This is the canonical way to parse boolean properties from KiCad files.

    Args:
        value: Value from S-expression (Symbol, str, bool, or None)
        default: Default value if parsing fails or value is None

    Returns:
        bool: Parsed boolean value

    Examples:
        >>> parse_bool_property(sexpdata.Symbol('yes'))
        True
        >>> parse_bool_property('no')
        False
        >>> parse_bool_property(None, default=False)
        False
        >>> parse_bool_property('YES')  # Case insensitive
        True

    Note:
        This function was added to fix a critical bug where Symbol('yes') == 'yes'
        returned False, causing properties like in_bom and on_board to be parsed
        incorrectly.
    """
    # If value is None, use default
    if value is None:
        return default

    # Convert Symbol to string
    if isinstance(value, sexpdata.Symbol):
        value = str(value)

    # Handle string values (case-insensitive)
    if isinstance(value, str):
        return value.lower() == "yes"

    # Handle boolean values directly
    if isinstance(value, bool):
        return value

    # Unexpected type - use default
    logger.warning(f"Unexpected type for boolean property: {type(value)}, using default={default}")
    return default
