"""Base wrapper class for schematic elements."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Optional, TypeVar

if TYPE_CHECKING:
    from ..collections.base import IndexedCollection

# Type variable for the wrapped data type
T = TypeVar("T")


class ElementWrapper(ABC, Generic[T]):
    """Base class for all schematic element wrappers.

    Wrappers enhance raw dataclasses with:
    - Validation on property setters
    - Parent collection tracking for automatic index updates
    - Convenient methods and computed properties
    - Consistent API across different element types
    """

    def __init__(self, data: T, parent_collection: Optional["IndexedCollection[Any]"]):
        """Initialize the wrapper.

        Args:
            data: The underlying dataclass instance
            parent_collection: The collection this element belongs to (can be None)
        """
        self._data = data
        self._collection = parent_collection

    @property
    def data(self) -> T:
        """Get the underlying data object.

        Returns:
            The wrapped dataclass instance
        """
        return self._data

    @property
    @abstractmethod
    def uuid(self) -> str:
        """Get the UUID of the element.

        Returns:
            UUID string
        """
        pass

    def __eq__(self, other: object) -> bool:
        """Compare wrappers by UUID.

        Args:
            other: Another wrapper to compare with

        Returns:
            True if UUIDs match
        """
        if not isinstance(other, ElementWrapper):
            return False
        return self.uuid == other.uuid

    def __hash__(self) -> int:
        """Hash wrapper by UUID.

        Returns:
            Hash of UUID
        """
        return hash(self.uuid)

    def __repr__(self) -> str:
        """Get string representation of wrapper.

        Returns:
            String representation
        """
        return f"{self.__class__.__name__}({self._data})"

    def _mark_modified(self) -> None:
        """Mark the parent collection as modified."""
        if self._collection is not None:
            self._collection._mark_modified()

    def _invalidate_indexes(self) -> None:
        """Invalidate parent collection indexes."""
        if self._collection is not None:
            self._collection._dirty_indexes = True
