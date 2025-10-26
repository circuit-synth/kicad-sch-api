"""
No-connect element management for KiCAD schematics.

This module provides collection classes for managing no-connect elements,
featuring fast lookup, bulk operations, and validation.
"""

import logging
import uuid
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .types import NoConnect, Point

logger = logging.getLogger(__name__)


class NoConnectElement:
    """
    Enhanced wrapper for schematic no-connect elements with modern API.

    Provides intuitive access to no-connect properties and operations
    while maintaining exact format preservation.
    """

    def __init__(self, no_connect_data: NoConnect, parent_collection: "NoConnectCollection"):
        """
        Initialize no-connect element wrapper.

        Args:
            no_connect_data: Underlying no-connect data
            parent_collection: Parent collection for updates
        """
        self._data = no_connect_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

    # Core properties with validation
    @property
    def uuid(self) -> str:
        """No-connect element UUID."""
        return self._data.uuid

    @property
    def position(self) -> Point:
        """No-connect position."""
        return self._data.position

    @position.setter
    def position(self, value: Union[Point, Tuple[float, float]]):
        """Set no-connect position."""
        if isinstance(value, tuple):
            value = Point(value[0], value[1])
        elif not isinstance(value, Point):
            raise ValidationError(f"Position must be Point or tuple, got {type(value)}")
        self._data.position = value
        self._collection._mark_modified()

    def validate(self) -> List[ValidationIssue]:
        """Validate this no-connect element."""
        return self._validator.validate_no_connect(self._data.__dict__)

    def to_dict(self) -> Dict[str, Any]:
        """Convert no-connect element to dictionary representation."""
        return {
            "uuid": self.uuid,
            "position": {"x": self.position.x, "y": self.position.y},
        }

    def __str__(self) -> str:
        """String representation."""
        return f"<NoConnect @ {self.position}>"


class NoConnectCollection:
    """
    Collection class for efficient no-connect element management.

    Provides fast lookup, filtering, and bulk operations for schematic no-connect elements.
    """

    def __init__(self, no_connects: List[NoConnect] = None):
        """
        Initialize no-connect collection.

        Args:
            no_connects: Initial list of no-connect data
        """
        self._no_connects: List[NoConnectElement] = []
        self._uuid_index: Dict[str, NoConnectElement] = {}
        self._position_index: Dict[Tuple[float, float], List[NoConnectElement]] = {}
        self._modified = False

        # Add initial no-connects
        if no_connects:
            for no_connect_data in no_connects:
                self._add_to_indexes(NoConnectElement(no_connect_data, self))

        logger.debug(f"NoConnectCollection initialized with {len(self._no_connects)} no-connects")

    def add(
        self,
        position: Union[Point, Tuple[float, float]],
        no_connect_uuid: Optional[str] = None,
    ) -> NoConnectElement:
        """
        Add a new no-connect element to the schematic.

        Args:
            position: No-connect position
            no_connect_uuid: Specific UUID for no-connect (auto-generated if None)

        Returns:
            Newly created NoConnectElement

        Raises:
            ValidationError: If no-connect data is invalid
        """
        # Validate inputs
        if isinstance(position, tuple):
            position = Point(position[0], position[1])
        elif not isinstance(position, Point):
            raise ValidationError(f"Position must be Point or tuple, got {type(position)}")

        # Generate UUID if not provided
        if not no_connect_uuid:
            no_connect_uuid = str(uuid.uuid4())

        # Check for duplicate UUID
        if no_connect_uuid in self._uuid_index:
            raise ValidationError(f"NoConnect UUID {no_connect_uuid} already exists")

        # Create no-connect data
        no_connect_data = NoConnect(
            uuid=no_connect_uuid,
            position=position,
        )

        # Create wrapper and add to collection
        no_connect_element = NoConnectElement(no_connect_data, self)
        self._add_to_indexes(no_connect_element)
        self._mark_modified()

        logger.debug(f"Added no-connect: {no_connect_element}")
        return no_connect_element

    def get(self, no_connect_uuid: str) -> Optional[NoConnectElement]:
        """Get no-connect by UUID."""
        return self._uuid_index.get(no_connect_uuid)

    def remove(self, no_connect_uuid: str) -> bool:
        """
        Remove no-connect by UUID.

        Args:
            no_connect_uuid: UUID of no-connect to remove

        Returns:
            True if no-connect was removed, False if not found
        """
        no_connect_element = self._uuid_index.get(no_connect_uuid)
        if not no_connect_element:
            return False

        # Remove from indexes
        self._remove_from_indexes(no_connect_element)
        self._mark_modified()

        logger.debug(f"Removed no-connect: {no_connect_element}")
        return True

    def find_at_position(
        self, position: Union[Point, Tuple[float, float]], tolerance: float = 0.1
    ) -> List[NoConnectElement]:
        """
        Find no-connects at or near a position.

        Args:
            position: Position to search around
            tolerance: Search tolerance in mm

        Returns:
            List of matching no-connect elements
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        matches = []
        for no_connect_element in self._no_connects:
            distance = no_connect_element.position.distance_to(position)
            if distance <= tolerance:
                matches.append(no_connect_element)
        return matches

    def filter(self, predicate: Callable[[NoConnectElement], bool]) -> List[NoConnectElement]:
        """
        Filter no-connects by predicate function.

        Args:
            predicate: Function that returns True for no-connects to include

        Returns:
            List of no-connects matching predicate
        """
        return [no_connect for no_connect in self._no_connects if predicate(no_connect)]

    def bulk_update(self, criteria: Callable[[NoConnectElement], bool], updates: Dict[str, Any]):
        """
        Update multiple no-connects matching criteria.

        Args:
            criteria: Function to select no-connects to update
            updates: Dictionary of property updates
        """
        updated_count = 0
        for no_connect_element in self._no_connects:
            if criteria(no_connect_element):
                for prop, value in updates.items():
                    if hasattr(no_connect_element, prop):
                        setattr(no_connect_element, prop, value)
                        updated_count += 1

        if updated_count > 0:
            self._mark_modified()
            logger.debug(f"Bulk updated {updated_count} no-connect properties")

    def clear(self):
        """Remove all no-connects from collection."""
        self._no_connects.clear()
        self._uuid_index.clear()
        self._position_index.clear()
        self._mark_modified()

    def _add_to_indexes(self, no_connect_element: NoConnectElement):
        """Add no-connect to internal indexes."""
        self._no_connects.append(no_connect_element)
        self._uuid_index[no_connect_element.uuid] = no_connect_element

        # Add to position index
        pos_key = (no_connect_element.position.x, no_connect_element.position.y)
        if pos_key not in self._position_index:
            self._position_index[pos_key] = []
        self._position_index[pos_key].append(no_connect_element)

    def _remove_from_indexes(self, no_connect_element: NoConnectElement):
        """Remove no-connect from internal indexes."""
        self._no_connects.remove(no_connect_element)
        del self._uuid_index[no_connect_element.uuid]

        # Remove from position index
        pos_key = (no_connect_element.position.x, no_connect_element.position.y)
        if pos_key in self._position_index:
            self._position_index[pos_key].remove(no_connect_element)
            if not self._position_index[pos_key]:
                del self._position_index[pos_key]

    def _mark_modified(self):
        """Mark collection as modified."""
        self._modified = True

    # Collection interface methods
    def __len__(self) -> int:
        """Return number of no-connects."""
        return len(self._no_connects)

    def __iter__(self) -> Iterator[NoConnectElement]:
        """Iterate over no-connects."""
        return iter(self._no_connects)

    def __getitem__(self, index: int) -> NoConnectElement:
        """Get no-connect by index."""
        return self._no_connects[index]

    def __bool__(self) -> bool:
        """Return True if collection has no-connects."""
        return len(self._no_connects) > 0
