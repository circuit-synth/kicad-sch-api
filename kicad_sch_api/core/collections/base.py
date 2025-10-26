"""
Base collection class for schematic elements.

Provides common functionality for all collection types including UUID indexing,
modification tracking, and standard collection operations.
"""

import logging
from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, Protocol, TypeVar

logger = logging.getLogger(__name__)


class HasUUID(Protocol):
    """Protocol for objects that have a UUID attribute."""

    @property
    def uuid(self) -> str:
        """UUID of the object."""
        ...


T = TypeVar("T", bound=HasUUID)


class BaseCollection(Generic[T]):
    """
    Generic base class for schematic element collections.

    Provides common functionality:
    - UUID-based indexing for fast lookup
    - Modification tracking
    - Standard collection operations (__len__, __iter__, __getitem__)
    - Index rebuilding and management

    Type parameter T must implement the HasUUID protocol.
    """

    def __init__(self, items: Optional[List[T]] = None, collection_name: str = "items") -> None:
        """
        Initialize base collection.

        Args:
            items: Initial list of items
            collection_name: Name for logging (e.g., "wires", "junctions")
        """
        self._items: List[T] = items or []
        self._uuid_index: Dict[str, int] = {}
        self._modified = False
        self._collection_name = collection_name

        # Build UUID index
        self._rebuild_index()

        logger.debug(f"{collection_name} collection initialized with {len(self._items)} items")

    def _rebuild_index(self) -> None:
        """Rebuild UUID index for fast lookups."""
        self._uuid_index = {item.uuid: i for i, item in enumerate(self._items)}

    def _mark_modified(self) -> None:
        """Mark collection as modified."""
        self._modified = True

    def is_modified(self) -> bool:
        """Check if collection has been modified."""
        return self._modified

    def reset_modified_flag(self) -> None:
        """Reset modified flag (typically after save)."""
        self._modified = False

    # Standard collection protocol methods
    def __len__(self) -> int:
        """Return number of items in collection."""
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        """Iterate over items in collection."""
        return iter(self._items)

    def __getitem__(self, key: Any) -> T:
        """
        Get item by UUID or index.

        Args:
            key: UUID string or integer index

        Returns:
            Item at the specified location

        Raises:
            KeyError: If UUID not found
            IndexError: If index out of range
            TypeError: If key is neither string nor int
        """
        if isinstance(key, str):
            # UUID lookup
            if key not in self._uuid_index:
                raise KeyError(f"Item with UUID '{key}' not found")
            return self._items[self._uuid_index[key]]
        elif isinstance(key, int):
            # Index lookup
            return self._items[key]
        else:
            raise TypeError(f"Key must be string (UUID) or int (index), got {type(key)}")

    def __contains__(self, key: Any) -> bool:
        """
        Check if item exists in collection.

        Args:
            key: UUID string or item object

        Returns:
            True if item exists
        """
        if isinstance(key, str):
            return key in self._uuid_index
        elif hasattr(key, "uuid"):
            return key.uuid in self._uuid_index
        return False

    def get(self, uuid: str) -> Optional[T]:
        """
        Get item by UUID.

        Args:
            uuid: Item UUID

        Returns:
            Item if found, None otherwise
        """
        if uuid not in self._uuid_index:
            return None
        return self._items[self._uuid_index[uuid]]

    def remove(self, uuid: str) -> bool:
        """
        Remove item by UUID.

        Args:
            uuid: UUID of item to remove

        Returns:
            True if item was removed, False if not found
        """
        if uuid not in self._uuid_index:
            return False

        index = self._uuid_index[uuid]
        del self._items[index]
        self._rebuild_index()
        self._mark_modified()

        logger.debug(f"Removed item with UUID {uuid} from {self._collection_name}")
        return True

    def clear(self) -> None:
        """Remove all items from collection."""
        self._items.clear()
        self._uuid_index.clear()
        self._mark_modified()
        logger.debug(f"Cleared all items from {self._collection_name}")

    def find(self, predicate: Callable[[T], bool]) -> List[T]:
        """
        Find all items matching a predicate.

        Args:
            predicate: Function that returns True for matching items

        Returns:
            List of matching items
        """
        return [item for item in self._items if predicate(item)]

    def filter(self, **criteria) -> List[T]:
        """
        Filter items by attribute values.

        Args:
            **criteria: Attribute name/value pairs to match

        Returns:
            List of matching items

        Example:
            collection.filter(wire_type=WireType.BUS, stroke_width=0.5)
        """
        matches = []
        for item in self._items:
            if all(getattr(item, key, None) == value for key, value in criteria.items()):
                matches.append(item)
        return matches

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_items": len(self._items),
            "modified": self._modified,
            "indexed_items": len(self._uuid_index),
        }

    def _add_item(self, item: T) -> None:
        """
        Add item to internal storage and index.

        Args:
            item: Item to add

        Raises:
            ValueError: If item UUID already exists
        """
        if item.uuid in self._uuid_index:
            raise ValueError(f"Item with UUID '{item.uuid}' already exists")

        self._items.append(item)
        self._uuid_index[item.uuid] = len(self._items) - 1
        self._mark_modified()

    def bulk_update(self, criteria: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """
        Update multiple items matching criteria.

        Args:
            criteria: Attribute name/value pairs to match
            updates: Attribute name/value pairs to update

        Returns:
            Number of items updated
        """
        matching_items = self.filter(**criteria)
        for item in matching_items:
            for key, value in updates.items():
                if hasattr(item, key):
                    setattr(item, key, value)

        if matching_items:
            self._mark_modified()

        logger.debug(f"Bulk updated {len(matching_items)} items in {self._collection_name}")
        return len(matching_items)
