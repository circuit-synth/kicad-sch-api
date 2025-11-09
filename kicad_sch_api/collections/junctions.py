"""
Enhanced junction management with IndexRegistry integration.

Provides JunctionCollection using BaseCollection infrastructure with
position-based queries and validation.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.types import Junction, Point
from .base import BaseCollection, IndexSpec, ValidationLevel

logger = logging.getLogger(__name__)


class JunctionCollection(BaseCollection[Junction]):
    """
    Junction collection with position-based queries.

    Inherits from BaseCollection for UUID indexing and adds junction-specific
    position-based search capabilities.

    Features:
    - Fast UUID lookup via IndexRegistry
    - Position-based junction queries
    - Lazy index rebuilding
    - Batch mode support
    """

    def __init__(
        self,
        junctions: Optional[List[Junction]] = None,
        validation_level: ValidationLevel = ValidationLevel.NORMAL,
    ):
        """
        Initialize junction collection.

        Args:
            junctions: Initial list of junctions
            validation_level: Validation level for operations
        """
        super().__init__(validation_level=validation_level)

        # Add initial junctions
        if junctions:
            with self.batch_mode():
                for junction in junctions:
                    super().add(junction)

        logger.debug(f"JunctionCollection initialized with {len(self)} junctions")

    # BaseCollection abstract method implementations
    def _get_item_uuid(self, item: Junction) -> str:
        """Extract UUID from junction."""
        return item.uuid

    def _create_item(self, **kwargs) -> Junction:
        """Create a new junction (not typically used directly)."""
        raise NotImplementedError("Use add() method to create junctions")

    def _get_index_specs(self) -> List[IndexSpec]:
        """Get index specifications for junction collection."""
        return [
            IndexSpec(
                name="uuid",
                key_func=lambda j: j.uuid,
                unique=True,
                description="UUID index for fast lookups",
            ),
        ]

    # Junction-specific add method
    def add(
        self,
        position: Union[Point, Tuple[float, float]],
        diameter: float = 0,
        color: Tuple[int, int, int, int] = (0, 0, 0, 0),
        uuid: Optional[str] = None,
        grid_units: Optional[bool] = None,
        grid_size: Optional[float] = None,
    ) -> str:
        """
        Add a junction to the collection.

        Args:
            position: Junction position in mm (or grid units if grid_units=True)
            diameter: Junction diameter (0 is KiCAD default)
            color: RGBA color tuple (0,0,0,0 is default)
            uuid: Optional UUID (auto-generated if not provided)
            grid_units: If True, interpret position as grid units; if None, use config.positioning.use_grid_units
            grid_size: Grid size in mm; if None, use config.positioning.grid_size

        Returns:
            UUID of the created junction

        Raises:
            ValueError: If UUID already exists
        """
        # Generate UUID if not provided
        if uuid is None:
            uuid = str(uuid_module.uuid4())
        else:
            # Check for duplicate
            self._ensure_indexes_current()
            if self._index_registry.has_key("uuid", uuid):
                raise ValueError(f"Junction with UUID '{uuid}' already exists")

        # Use config defaults if not explicitly provided
        from ..core.config import config

        if grid_units is None:
            grid_units = config.positioning.use_grid_units
        if grid_size is None:
            grid_size = config.positioning.grid_size

        # Convert grid units to mm if requested
        if grid_units:
            if isinstance(position, tuple):
                position = Point(position[0] * grid_size, position[1] * grid_size)
            else:
                position = Point(position.x * grid_size, position.y * grid_size)
        # Convert position
        elif isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Create junction
        junction = Junction(uuid=uuid, position=position, diameter=diameter, color=color)

        # Add to collection
        super().add(junction)

        logger.debug(f"Added junction at {position}, UUID={uuid}")
        return uuid

    # Position-based queries
    def get_at_position(
        self, position: Union[Point, Tuple[float, float]], tolerance: float = 0.01
    ) -> Optional[Junction]:
        """
        Find junction at or near a specific position.

        Args:
            position: Position to search
            tolerance: Distance tolerance for matching

        Returns:
            Junction if found, None otherwise
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        for junction in self._items:
            if junction.position.distance_to(position) <= tolerance:
                return junction

        return None

    def get_by_point(
        self, point: Union[Point, Tuple[float, float]], tolerance: float = 0.01
    ) -> List[Junction]:
        """
        Find all junctions near a point.

        Args:
            point: Point to search near
            tolerance: Distance tolerance

        Returns:
            List of junctions near the point
        """
        if isinstance(point, tuple):
            point = Point(point[0], point[1])

        matching_junctions = []
        for junction in self._items:
            if junction.position.distance_to(point) <= tolerance:
                matching_junctions.append(junction)

        return matching_junctions

    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get junction collection statistics.

        Returns:
            Dictionary with junction statistics
        """
        if not self._items:
            base_stats = super().get_statistics()
            base_stats.update(
                {
                    "total_junctions": 0,
                    "avg_diameter": 0,
                    "positions": [],
                    "unique_diameters": 0,
                    "unique_colors": 0,
                }
            )
            return base_stats

        avg_diameter = sum(j.diameter for j in self._items) / len(self._items)
        positions = [(j.position.x, j.position.y) for j in self._items]

        base_stats = super().get_statistics()
        base_stats.update(
            {
                "total_junctions": len(self._items),
                "avg_diameter": avg_diameter,
                "positions": positions,
                "unique_diameters": len(set(j.diameter for j in self._items)),
                "unique_colors": len(set(j.color for j in self._items)),
            }
        )

        return base_stats

    # Compatibility methods
    @property
    def modified(self) -> bool:
        """Check if collection has been modified (compatibility)."""
        return self.is_modified

    def mark_saved(self) -> None:
        """Mark collection as saved (reset modified flag)."""
        self.mark_clean()
