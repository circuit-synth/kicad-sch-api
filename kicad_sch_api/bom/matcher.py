"""Property matching utilities for BOM management."""

import re
import fnmatch
from typing import Dict, Any


class PropertyMatcher:
    """Match components based on criteria with regex/wildcard support."""

    @staticmethod
    def parse_criteria(criteria_str: str) -> Dict[str, str]:
        """Parse criteria string into dict.

        Examples:
            "value=10k,footprint=*0805*"
            "reference=R*,lib_id=Device:R"
            "PartNumber="  # Empty property

        Args:
            criteria_str: Comma-separated key=value pairs

        Returns:
            Dictionary of field names to match patterns
        """
        if not criteria_str:
            return {}

        criteria = {}
        for pair in criteria_str.split(','):
            if '=' in pair:
                key, value = pair.split('=', 1)
                criteria[key.strip()] = value.strip()

        return criteria

    @staticmethod
    def matches(component: Any, criteria: Dict[str, str]) -> bool:
        """Check if component matches all criteria.

        Supports:
          - Exact match: "value=10k"
          - Wildcards: "footprint=*0805*"
          - Regex: "reference=R[0-9]+"
          - Empty check: "PartNumber=" (matches if empty)

        Args:
            component: Component object to check
            criteria: Dictionary of field->pattern mappings

        Returns:
            True if component matches all criteria
        """
        for field, pattern in criteria.items():
            # Get field value from component
            if field in ["reference", "value", "footprint", "lib_id"]:
                component_value = getattr(component, field, "")
            else:
                # Assume it's a property
                component_value = component.get_property(field, "")

            component_value = str(component_value)

            # Empty check
            if pattern == "":
                if component_value != "":
                    return False
                continue

            # Wildcard match
            if '*' in pattern or '?' in pattern:
                if not fnmatch.fnmatch(component_value, pattern):
                    return False
                continue

            # Try regex match
            try:
                if not re.search(pattern, component_value):
                    return False
            except re.error:
                # Not valid regex, try exact match
                if component_value != pattern:
                    return False

        return True
