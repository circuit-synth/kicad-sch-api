"""
Base collection infrastructure with centralized index management.

Provides:
- IndexSpec: Index specification and declaration
- IndexRegistry: Centralized index management with lazy rebuilding
- PropertyDict: Auto-tracking dictionary for modification detection
- ValidationLevel: Configurable validation levels
- BaseCollection: Abstract base class for all collections
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Any, Callable, Dict, Generic, Iterator, List, Optional, Set, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Type variable for collection items


@total_ordering
class ValidationLevel(Enum):
    """
    Validation level for collection operations.

    Controls the amount of validation performed during collection operations.
    Higher levels provide more safety but lower performance.
    """

    NONE = 0  # No validation (maximum performance)
    BASIC = 1  # Basic checks (duplicates, nulls)
    NORMAL = 2  # Standard validation (default)
    STRICT = 3  # Strict validation (referential integrity)
    PARANOID = 4  # Maximum validation (everything, very slow)

    def __lt__(self, other):
        """Compare validation levels by value."""
        if isinstance(other, ValidationLevel):
            return self.value < other.value
        return NotImplemented


@dataclass
class IndexSpec:
    """
    Specification for a collection index.

    Defines how to build and maintain an index for fast lookups.
    """

    name: str
    key_func: Callable[[Any], Any]
    unique: bool = True
    description: str = ""

    def __post_init__(self):
        """Validate index specification."""
        if not self.name:
            raise ValueError("Index name cannot be empty")
        if not callable(self.key_func):
            raise ValueError("Index key_func must be callable")


class IndexRegistry:
    """
    Centralized registry for managing collection indexes.

    Provides:
    - Lazy index rebuilding (only when needed)
    - Multiple index support (uuid, reference, lib_id, etc.)
    - Duplicate detection for unique indexes
    - Unified index management API
    """

    def __init__(self, specs: List[IndexSpec]):
        """
        Initialize index registry.

        Args:
            specs: List of index specifications to manage
        """
        self.specs = {spec.name: spec for spec in specs}
        self.indexes: Dict[str, Dict[Any, Any]] = {spec.name: {} for spec in specs}
        self._dirty = False

        logger.debug(
            f"IndexRegistry initialized with {len(specs)} indexes: {list(self.specs.keys())}"
        )

    def mark_dirty(self) -> None:
        """Mark all indexes as needing rebuild."""
        self._dirty = True
        logger.debug("Indexes marked dirty")

    def is_dirty(self) -> bool:
        """Check if indexes need rebuilding."""
        return self._dirty

    def rebuild(self, items: List[Any]) -> None:
        """
        Rebuild all indexes from items.

        Args:
            items: List of items to index

        Raises:
            ValueError: If unique index has duplicates
        """
        logger.debug(f"Rebuilding {len(self.indexes)} indexes for {len(items)} items")

        # Clear all indexes
        for index_name in self.indexes:
            self.indexes[index_name].clear()

        # Rebuild each index
        for spec in self.specs.values():
            self._rebuild_index(spec, items)

        self._dirty = False
        logger.debug("Index rebuild complete")

    def _rebuild_index(self, spec: IndexSpec, items: List[Any]) -> None:
        """
        Rebuild a single index.

        Args:
            spec: Index specification
            items: Items to index

        Raises:
            ValueError: If unique index has duplicates
        """
        index = self.indexes[spec.name]

        for i, item in enumerate(items):
            try:
                key = spec.key_func(item)

                if spec.unique:
                    if key in index:
                        raise ValueError(f"Duplicate key '{key}' in unique index '{spec.name}'")
                    index[key] = i
                else:
                    # Non-unique index: multiple items per key
                    if key not in index:
                        index[key] = []
                    index[key].append(i)

            except ValueError:
                # Re-raise ValueError (e.g., duplicate key)
                raise
            except Exception as e:
                # Log and skip other errors (e.g., key_func failure)
                logger.warning(f"Failed to index item {i} in '{spec.name}': {e}")
                # Continue indexing other items

    def get(self, index_name: str, key: Any) -> Optional[Any]:
        """
        Get value from an index.

        Args:
            index_name: Name of the index
            key: Key to look up

        Returns:
            Index value if found, None otherwise
        """
        if index_name not in self.indexes:
            raise KeyError(f"Unknown index: {index_name}")

        return self.indexes[index_name].get(key)

    def has_key(self, index_name: str, key: Any) -> bool:
        """
        Check if key exists in index.

        Args:
            index_name: Name of the index
            key: Key to check

        Returns:
            True if key exists, False otherwise
        """
        if index_name not in self.indexes:
            raise KeyError(f"Unknown index: {index_name}")

        return key in self.indexes[index_name]

    def add_spec(self, spec: IndexSpec) -> None:
        """
        Add a new index specification.

        Args:
            spec: Index specification to add
        """
        if spec.name in self.specs:
            raise ValueError(f"Index '{spec.name}' already exists")

        self.specs[spec.name] = spec
        self.indexes[spec.name] = {}
        self.mark_dirty()

        logger.debug(f"Added index spec: {spec.name}")


class PropertyDict(MutableMapping):
    """
    Dictionary that automatically tracks modifications.

    Wraps a dictionary and notifies a callback when any changes occur.
    Implements the full MutableMapping interface.
    """

    def __init__(
        self, data: Optional[Dict[str, Any]] = None, on_modify: Optional[Callable[[], None]] = None
    ):
        """
        Initialize property dictionary.

        Args:
            data: Initial dictionary data
            on_modify: Callback to invoke when dict is modified
        """
        self._data = data or {}
        self._on_modify = on_modify

    def __getitem__(self, key: str) -> Any:
        """Get item by key."""
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item and trigger modification callback."""
        self._data[key] = value
        if self._on_modify:
            self._on_modify()

    def __delitem__(self, key: str) -> None:
        """Delete item and trigger modification callback."""
        del self._data[key]
        if self._on_modify:
            self._on_modify()

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Number of items."""
        return len(self._data)

    def __repr__(self) -> str:
        """String representation."""
        return f"PropertyDict({self._data!r})"

    def set_callback(self, on_modify: Callable[[], None]) -> None:
        """Set or update the modification callback."""
        self._on_modify = on_modify


class BaseCollection(Generic[T], ABC):
    """
    Abstract base class for all schematic element collections.

    Provides unified functionality for:
    - Lazy index rebuilding via IndexRegistry
    - Automatic modification tracking
    - Configurable validation levels
    - Batch mode for performance
    - Consistent collection operations (add, remove, get, filter)

    Subclasses must implement:
    - _get_item_uuid(item): Extract UUID from item
    - _create_item(**kwargs): Create new item instance
    - _get_index_specs(): Return list of IndexSpec for this collection
    """

    def __init__(
        self,
        items: Optional[List[T]] = None,
        validation_level: ValidationLevel = ValidationLevel.NORMAL,
    ):
        """
        Initialize base collection.

        Args:
            items: Initial list of items
            validation_level: Validation level for operations
        """
        self._items: List[T] = []
        self._validation_level = validation_level
        self._modified = False
        self._batch_mode = False

        # Set up index registry with subclass-specific indexes
        index_specs = self._get_index_specs()
        self._index_registry = IndexRegistry(index_specs)

        # Add initial items
        if items:
            for item in items:
                self._add_item_to_collection(item)

        logger.debug(f"{self.__class__.__name__} initialized with {len(self._items)} items")

    # Abstract methods for subclasses
    @abstractmethod
    def _get_item_uuid(self, item: T) -> str:
        """
        Extract UUID from an item.

        Args:
            item: Item to extract UUID from

        Returns:
            UUID string
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
    def _get_index_specs(self) -> List[IndexSpec]:
        """
        Get index specifications for this collection.

        Returns:
            List of IndexSpec defining indexes for this collection
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
        # Validation
        if self._validation_level >= ValidationLevel.BASIC:
            if item is None:
                raise ValueError("Cannot add None item to collection")

            uuid_str = self._get_item_uuid(item)

            # Check for duplicate UUID
            self._ensure_indexes_current()
            if self._index_registry.has_key("uuid", uuid_str):
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
            index = self._index_registry.get("uuid", identifier)
            if index is None:
                return False
            item = self._items[index]
        else:
            # Remove by item instance
            item = identifier
            uuid_str = self._get_item_uuid(item)
            index = self._index_registry.get("uuid", uuid_str)
            if index is None:
                return False

        # Remove from main list
        self._items.pop(index)
        self._mark_modified()
        self._index_registry.mark_dirty()

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

        index = self._index_registry.get("uuid", uuid)
        if index is not None:
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

    def all(self) -> Iterator[T]:
        """
        Get iterator over all items in the collection.

        Returns:
            Iterator over all items

        Example:
            # Iterate over all components
            for component in sch.components.all():
                print(component.reference)

            # Convert to list
            all_components = list(sch.components.all())
        """
        return iter(self._items)

    def clear(self) -> None:
        """Clear all items from the collection."""
        self._items.clear()
        self._index_registry.mark_dirty()
        self._mark_modified()
        logger.debug(f"Cleared all items from {self.__class__.__name__}")

    # Batch mode operations
    def batch_mode(self):
        """
        Context manager for batch operations.

        Defers index rebuilding until the batch is complete.

        Example:
            with collection.batch_mode():
                for i in range(1000):
                    collection.add(create_item(i))
            # Indexes rebuilt only once here
        """
        return BatchContext(self)

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
            return self._index_registry.has_key("uuid", item)
        else:
            # Check by item instance
            uuid_str = self._get_item_uuid(item)
            self._ensure_indexes_current()
            return self._index_registry.has_key("uuid", uuid_str)

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

        # Always mark indexes as dirty when items change
        # Batch mode just defers the rebuild, not the dirty flag
        self._index_registry.mark_dirty()

        logger.debug(f"Added item with UUID {self._get_item_uuid(item)}")
        return item

    def _mark_modified(self) -> None:
        """Mark collection as modified."""
        self._modified = True

    def _ensure_indexes_current(self) -> None:
        """Ensure all indexes are current (unless in batch mode)."""
        if not self._batch_mode and self._index_registry.is_dirty():
            self._rebuild_indexes()

    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes."""
        self._index_registry.rebuild(self._items)
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
            "index_count": len(self._index_registry.indexes),
            "modified": self._modified,
            "indexes_dirty": self._index_registry.is_dirty(),
            "collection_type": self.__class__.__name__,
            "validation_level": self._validation_level.name,
            "batch_mode": self._batch_mode,
        }

    @property
    def is_modified(self) -> bool:
        """Whether collection has been modified."""
        return self._modified

    def mark_clean(self) -> None:
        """Mark collection as clean (not modified)."""
        self._modified = False
        logger.debug(f"Marked {self.__class__.__name__} as clean")

    @property
    def validation_level(self) -> ValidationLevel:
        """Current validation level."""
        return self._validation_level

    def set_validation_level(self, level: ValidationLevel) -> None:
        """
        Set validation level.

        Args:
            level: New validation level
        """
        self._validation_level = level
        logger.debug(f"Set validation level to {level.name}")


class BatchContext:
    """Context manager for batch operations."""

    def __init__(self, collection: BaseCollection):
        """
        Initialize batch context.

        Args:
            collection: Collection to batch operations on
        """
        self.collection = collection

    def __enter__(self):
        """Enter batch mode - defers index rebuilds."""
        self.collection._batch_mode = True
        logger.debug(f"Entered batch mode for {self.collection.__class__.__name__}")
        return self.collection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit batch mode and rebuild indexes if needed."""
        self.collection._batch_mode = False
        # Indexes are already marked dirty by add operations
        # Just ensure they're rebuilt now
        self.collection._ensure_indexes_current()
        logger.debug(f"Exited batch mode for {self.collection.__class__.__name__}")
        return False
