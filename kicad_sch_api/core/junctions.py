"""
Junction collection and management for KiCAD schematics.

This module provides enhanced junction management for wire intersections
and connection points with performance optimization and validation.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from .collections import BaseCollection
from .types import Junction, Point

logger = logging.getLogger(__name__)


class JunctionCollection(BaseCollection[Junction]):
    """
    Professional junction collection with enhanced management features.

    Inherits from BaseCollection for standard operations and adds junction-specific
    functionality.

    Features:
    - Fast UUID-based lookup and indexing (inherited)
    - Position-based junction queries
    - Bulk operations for performance (inherited)
    - Validation and conflict detection
    """

    def __init__(self, junctions: Optional[List[Junction]] = None) -> None:
        """
        Initialize junction collection.

        Args:
            junctions: Initial list of junctions
        """
        super().__init__(junctions, collection_name="junctions")

    def add(
        self,
        position: Union[Point, Tuple[float, float]],
        diameter: float = 0,
        color: Tuple[int, int, int, int] = (0, 0, 0, 0),
        uuid: Optional[str] = None,
        grid_units: bool = False,
        grid_size: float = 1.27,
    ) -> str:
        """
        Add a junction to the collection.

        Args:
            position: Junction position in mm (or grid units if grid_units=True)
            diameter: Junction diameter (0 is KiCAD default)
            color: RGBA color tuple (0,0,0,0 is default)
            uuid: Optional UUID (auto-generated if not provided)
            grid_units: If True, interpret position as grid units instead of mm
            grid_size: Grid size in mm (default 1.27mm = 50 mil KiCAD standard)

        Returns:
            UUID of the created junction

        Raises:
            ValueError: If UUID already exists
        """
        # Generate UUID if not provided
        if uuid is None:
            uuid = str(uuid_module.uuid4())
        elif uuid in self._uuid_index:
            raise ValueError(f"Junction with UUID '{uuid}' already exists")

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

        # Add to collection using base class method
        self._add_item(junction)

        logger.debug(f"Added junction at {position}, UUID={uuid}")
        return uuid

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

    def get_statistics(self) -> Dict[str, Any]:
        """Get junction collection statistics (extends base statistics)."""
        base_stats = super().get_statistics()
        if not self._items:
            return {**base_stats, "total_junctions": 0, "avg_diameter": 0, "positions": []}

        avg_diameter = sum(j.diameter for j in self._items) / len(self._items)
        positions = [(j.position.x, j.position.y) for j in self._items]

        return {
            **base_stats,
            "total_junctions": len(self._items),
            "avg_diameter": avg_diameter,
            "positions": positions,
            "unique_diameters": len(set(j.diameter for j in self._items)),
            "unique_colors": len(set(j.color for j in self._items)),
        }

    @property
    def modified(self) -> bool:
        """Check if collection has been modified."""
        return self.is_modified()

    def mark_saved(self) -> None:
        """Mark collection as saved (reset modified flag)."""
        self.reset_modified_flag()
