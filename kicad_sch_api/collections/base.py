"""
Base collection class for unified schematic element management.

Provides common functionality for indexing, searching, and managing
collections of schematic elements with performance optimization.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Type variable for collection items


class IndexedCollection(Generic[T], ABC):
    """
    Base class for all schematic element collections with automatic indexing.

    Provides unified functionality for:
    - UUID-based fast lookups
    - Automatic index management
    - Modification tracking
    - Consistent iteration interface
    - Performance optimization for large collections
    """

    def __init__(self, items: Optional[List[T]] = None):
        """
        Initialize indexed collection.

        Args:
            items: Initial list of items to add to collection
        """
        self._items: List[T] = []
        self._uuid_index: Dict[str, int] = {}
        self._modified = False
        self._dirty_indexes = False

        # Add initial items if provided
        if items:
            for item in items:
                self._add_item_to_collection(item)

        logger.debug(f"{self.__class__.__name__} initialized with {len(self._items)} items")

    # Abstract methods for subclasses to implement
    @abstractmethod
    def _get_item_uuid(self, item: T) -> str:
        """
        Extract UUID from an item.

        Args:
            item: Item to extract UUID from

        Returns:
            UUID string for the item
        """
        pass

    @abstractmethod
    def _create_item(self, **kwargs) -> T:
        """
        Create a new item with given parameters.

        Args:
            **kwargs: Parameters for item creation

        Returns:
            Newly created item
        """
        pass

    @abstractmethod
    def _build_additional_indexes(self) -> None:
        """
        Build any additional indexes specific to the collection type.

        Called after UUID index is rebuilt. Subclasses should implement
        this to maintain their own specialized indexes.
        """
        pass

    # Core collection operations
    def add(self, item: T) -> T:
        """
        Add an item to the collection.

        Args:
            item: Item to add

        Returns:
            The added item

        Raises:
            ValueError: If item with same UUID already exists
        """
        uuid_str = self._get_item_uuid(item)

        # Ensure indexes are current before checking for duplicates
        self._ensure_indexes_current()

        # Check for duplicate UUID
        if uuid_str in self._uuid_index:
            raise ValueError(f"Item with UUID {uuid_str} already exists")

        return self._add_item_to_collection(item)

    def remove(self, identifier: Union[str, T]) -> bool:
        """
        Remove an item from the collection.

        Args:
            identifier: UUID string or item instance to remove

        Returns:
            True if item was removed, False if not found
        """
        self._ensure_indexes_current()

        if isinstance(identifier, str):
            # Remove by UUID
            if identifier not in self._uuid_index:
                return False

            index = self._uuid_index[identifier]
            item = self._items[index]
        else:
            # Remove by item instance
            item = identifier
            uuid_str = self._get_item_uuid(item)
            if uuid_str not in self._uuid_index:
                return False

            index = self._uuid_index[uuid_str]

        # Remove from main list
        self._items.pop(index)
        self._mark_modified()
        self._mark_indexes_dirty()

        logger.debug(f"Removed item with UUID {self._get_item_uuid(item)}")
        return True

    def get(self, uuid: str) -> Optional[T]:
        """
        Get an item by UUID.

        Args:
            uuid: UUID to search for

        Returns:
            Item if found, None otherwise
        """
        self._ensure_indexes_current()

        if uuid in self._uuid_index:
            index = self._uuid_index[uuid]
            return self._items[index]

        return None

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
        Filter items by attribute criteria.

        Args:
            **criteria: Attribute name/value pairs to match

        Returns:
            List of matching items
        """

        def matches_criteria(item: T) -> bool:
            for attr, value in criteria.items():
                if not hasattr(item, attr) or getattr(item, attr) != value:
                    return False
            return True

        return self.find(matches_criteria)

    def clear(self) -> None:
        """Clear all items from the collection."""
        self._items.clear()
        self._uuid_index.clear()
        self._mark_modified()
        logger.debug(f"Cleared all items from {self.__class__.__name__}")

    # Collection interface methods
    def __len__(self) -> int:
        """Number of items in collection."""
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        """Iterate over items in collection."""
        return iter(self._items)

    def __contains__(self, item: Union[str, T]) -> bool:
        """Check if item or UUID is in collection."""
        if isinstance(item, str):
            # Check by UUID
            self._ensure_indexes_current()
            return item in self._uuid_index
        else:
            # Check by item instance
            uuid_str = self._get_item_uuid(item)
            self._ensure_indexes_current()
            return uuid_str in self._uuid_index

    def __getitem__(self, index: int) -> T:
        """Get item by index."""
        return self._items[index]

    # Internal methods
    def _add_item_to_collection(self, item: T) -> T:
        """
        Internal method to add item to collection.

        Args:
            item: Item to add

        Returns:
            The added item
        """
        self._items.append(item)
        self._mark_modified()
        self._mark_indexes_dirty()

        logger.debug(f"Added item with UUID {self._get_item_uuid(item)}")
        return item

    def _mark_modified(self) -> None:
        """Mark collection as modified."""
        self._modified = True

    def _mark_indexes_dirty(self) -> None:
        """Mark indexes as needing rebuild."""
        self._dirty_indexes = True

    def _ensure_indexes_current(self) -> None:
        """Ensure all indexes are current."""
        if self._dirty_indexes:
            self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes."""
        # Rebuild UUID index
        self._uuid_index = {self._get_item_uuid(item): i for i, item in enumerate(self._items)}

        # Let subclasses rebuild their additional indexes
        self._build_additional_indexes()

        self._dirty_indexes = False
        logger.debug(f"Rebuilt indexes for {self.__class__.__name__}")

    # Collection statistics and debugging
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get collection statistics for debugging and monitoring.

        Returns:
            Dictionary with collection statistics
        """
        self._ensure_indexes_current()
        return {
            "item_count": len(self._items),
            "uuid_index_size": len(self._uuid_index),
            "modified": self._modified,
            "indexes_dirty": self._dirty_indexes,
            "collection_type": self.__class__.__name__,
        }

    @property
    def is_modified(self) -> bool:
        """Whether collection has been modified."""
        return self._modified

    def mark_clean(self) -> None:
        """Mark collection as clean (not modified)."""
        self._modified = False
        logger.debug(f"Marked {self.__class__.__name__} as clean")
