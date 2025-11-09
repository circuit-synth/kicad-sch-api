"""Base manager class for schematic operations.

Provides a consistent interface for all manager classes and enforces
common patterns for validation and data access.
"""

from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ...utils.validation import ValidationIssue

if TYPE_CHECKING:
    from ..schematic import Schematic


class BaseManager(ABC):
    """Base class for all schematic managers.

    Managers encapsulate complex operations and keep Schematic focused.
    This base class provides a consistent interface and common utilities
    for all managers.

    Attributes:
        _data: Reference to schematic data (optional, varies by manager)
        _schematic: Reference to parent Schematic instance (optional)
    """

    def __init__(self, schematic_data: Optional[Dict[str, Any]] = None, **kwargs):
        """Initialize manager with schematic data reference.

        Args:
            schematic_data: Reference to schematic data dictionary (optional)
            **kwargs: Additional manager-specific parameters
        """
        self._data = schematic_data
        self._schematic: Optional["Schematic"] = None

    def set_schematic(self, schematic: "Schematic") -> None:
        """Set reference to parent schematic.

        This is called by Schematic after manager initialization to establish
        bidirectional relationship.

        Args:
            schematic: The parent Schematic instance
        """
        self._schematic = schematic

    @property
    def schematic(self) -> Optional["Schematic"]:
        """Get the parent schematic instance.

        Returns:
            The parent Schematic, or None if not set
        """
        return self._schematic

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        """Get the schematic data dictionary.

        Returns:
            The schematic data, or None if not set
        """
        return self._data

    def validate(self) -> List[ValidationIssue]:
        """Validate managed elements.

        This is an optional method that managers can override to provide
        validation. Default implementation returns empty list (no issues).

        Returns:
            List of validation issues found
        """
        return []
