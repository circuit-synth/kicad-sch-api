"""
Bus entry collection with position-based queries.

Provides BusEntryCollection using BaseCollection infrastructure with
position-based queries and validation.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.types import BusEntry, Point
from .base import BaseCollection, IndexSpec, ValidationLevel

logger = logging.getLogger(__name__)


class BusEntryCollection(BaseCollection[BusEntry]):
    """
    Bus entry collection with position-based queries.

    Inherits from BaseCollection for UUID indexing and adds bus entry-specific
    position-based search capabilities.

    Features:
    - Fast UUID lookup via IndexRegistry
    - Position-based bus entry queries
    - Lazy index rebuilding
    - Batch mode support
    """

    def __init__(
        self,
        bus_entries: Optional[List[BusEntry]] = None,
        validation_level: ValidationLevel = ValidationLevel.NORMAL,
    ):
        """
        Initialize bus entry collection.

        Args:
            bus_entries: Initial list of bus entries
            validation_level: Validation level for operations
        """
        super().__init__(validation_level=validation_level)

        # Add initial bus entries
        if bus_entries:
            with self.batch_mode():
                for entry in bus_entries:
                    super().add(entry)

        logger.debug(f"BusEntryCollection initialized with {len(self)} bus entries")

    # BaseCollection abstract method implementations
    def _get_item_uuid(self, item: BusEntry) -> str:
        """Extract UUID from bus entry."""
        return item.uuid

    def _create_item(self, **kwargs) -> BusEntry:
        """Create a new bus entry (not typically used directly)."""
        raise NotImplementedError("Use add() method to create bus entries")

    def _get_index_specs(self) -> List[IndexSpec]:
        """Get index specifications for bus entry collection."""
        return [
            IndexSpec(
                name="uuid",
                key_func=lambda e: e.uuid,
                unique=True,
                description="UUID index for fast lookups",
            ),
        ]

    # Bus entry-specific add method
    def add(
        self,
        position: Union[Point, Tuple[float, float]],
        size: Optional[Union[Point, Tuple[float, float]]] = None,
        rotation: int = 0,
        stroke_width: float = 0.0,
        stroke_type: str = "default",
        uuid: Optional[str] = None,
    ) -> str:
        """
        Add a bus entry to the collection.

        Args:
            position: Entry position as Point or (x, y) tuple
            size: Entry size as Point or (width, height) tuple (default: 2.54mm)
            rotation: Rotation angle in degrees (0, 90, 180, 270)
            stroke_width: Line width
            stroke_type: Stroke type (default, dash, dot, etc.)
            uuid: Optional UUID (auto-generated if not provided)

        Returns:
            UUID of the created bus entry

        Raises:
            ValueError: If rotation is not 0, 90, 180, or 270
            ValueError: If UUID already exists
        """
        # Generate UUID if not provided
        if uuid is None:
            uuid = str(uuid_module.uuid4())
        elif uuid in self.registry:
            raise ValueError(f"Bus entry with UUID '{uuid}' already exists")

        # Convert position to Point
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Convert size to Point (or use default)
        if size is not None:
            if isinstance(size, tuple):
                size = Point(size[0], size[1])
        else:
            size = Point(2.54, 2.54)  # Default size

        # Validate rotation
        if rotation not in [0, 90, 180, 270]:
            raise ValueError(f"Bus entry rotation must be 0, 90, 180, or 270, got {rotation}")

        # Create bus entry
        entry = BusEntry(
            uuid=uuid,
            position=position,
            size=size,
            rotation=rotation,
            stroke_width=stroke_width,
            stroke_type=stroke_type,
        )

        # Add to collection using base class method
        super().add(entry)

        logger.debug(
            f"Added bus entry at ({position.x}, {position.y}), rotation={rotation}, UUID={uuid}"
        )
        return uuid

    def get_by_position(
        self, position: Union[Point, Tuple[float, float]], tolerance: float = 0.001
    ) -> List[BusEntry]:
        """
        Find bus entries at or near a position.

        Args:
            position: Position to search near
            tolerance: Distance tolerance in mm

        Returns:
            List of bus entries near the position
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        matching_entries = []
        for entry in self.items:
            if entry.position.distance_to(position) <= tolerance:
                matching_entries.append(entry)

        return matching_entries

    def get_by_rotation(self, rotation: int) -> List[BusEntry]:
        """
        Get all bus entries with a specific rotation.

        Args:
            rotation: Rotation angle (0, 90, 180, 270)

        Returns:
            List of bus entries with matching rotation
        """
        return [entry for entry in self.items if entry.rotation == rotation]

    def get_statistics(self) -> Dict[str, Any]:
        """Get bus entry collection statistics."""
        base_stats = super().get_statistics()

        # Count by rotation
        rotation_counts = {0: 0, 90: 0, 180: 0, 270: 0}
        for entry in self.items:
            rotation_counts[entry.rotation] += 1

        return {
            **base_stats,
            "total_bus_entries": len(self.items),
            "by_rotation": rotation_counts,
        }
