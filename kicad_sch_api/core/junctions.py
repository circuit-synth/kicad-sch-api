"""
Junction collection and management for KiCAD schematics.

This module provides enhanced junction management for wire intersections
and connection points with performance optimization and validation.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from .types import Junction, Point

logger = logging.getLogger(__name__)


class JunctionCollection:
    """
    Professional junction collection with enhanced management features.

    Features:
    - Fast UUID-based lookup and indexing
    - Position-based junction queries
    - Bulk operations for performance
    - Validation and conflict detection
    """

    def __init__(self, junctions: Optional[List[Junction]] = None):
        """
        Initialize junction collection.

        Args:
            junctions: Initial list of junctions
        """
        self._junctions: List[Junction] = junctions or []
        self._uuid_index: Dict[str, int] = {}
        self._modified = False

        # Build UUID index
        self._rebuild_index()

        logger.debug(f"JunctionCollection initialized with {len(self._junctions)} junctions")

    def _rebuild_index(self):
        """Rebuild UUID index for fast lookups."""
        self._uuid_index = {junction.uuid: i for i, junction in enumerate(self._junctions)}

    def __len__(self) -> int:
        """Number of junctions in collection."""
        return len(self._junctions)

    def __iter__(self):
        """Iterate over junctions."""
        return iter(self._junctions)

    def __getitem__(self, uuid: str) -> Junction:
        """Get junction by UUID."""
        if uuid not in self._uuid_index:
            raise KeyError(f"Junction with UUID '{uuid}' not found")
        return self._junctions[self._uuid_index[uuid]]

    def add(
        self,
        position: Union[Point, Tuple[float, float]],
        diameter: float = 0,
        color: Tuple[int, int, int, int] = (0, 0, 0, 0),
        uuid: Optional[str] = None,
    ) -> str:
        """
        Add a junction to the collection.

        Args:
            position: Junction position
            diameter: Junction diameter (0 is KiCAD default)
            color: RGBA color tuple (0,0,0,0 is default)
            uuid: Optional UUID (auto-generated if not provided)

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

        # Convert position
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Create junction
        junction = Junction(uuid=uuid, position=position, diameter=diameter, color=color)

        # Add to collection
        self._junctions.append(junction)
        self._uuid_index[uuid] = len(self._junctions) - 1
        self._modified = True

        logger.debug(f"Added junction at {position}, UUID={uuid}")
        return uuid

    def remove(self, uuid: str) -> bool:
        """
        Remove junction by UUID.

        Args:
            uuid: Junction UUID to remove

        Returns:
            True if junction was removed, False if not found
        """
        if uuid not in self._uuid_index:
            return False

        index = self._uuid_index[uuid]
        del self._junctions[index]
        self._rebuild_index()
        self._modified = True

        logger.debug(f"Removed junction: {uuid}")
        return True

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

        for junction in self._junctions:
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
        for junction in self._junctions:
            if junction.position.distance_to(point) <= tolerance:
                matching_junctions.append(junction)

        return matching_junctions

    def get_statistics(self) -> Dict[str, Any]:
        """Get junction collection statistics."""
        if not self._junctions:
            return {"total_junctions": 0, "avg_diameter": 0, "positions": []}

        avg_diameter = sum(j.diameter for j in self._junctions) / len(self._junctions)
        positions = [(j.position.x, j.position.y) for j in self._junctions]

        return {
            "total_junctions": len(self._junctions),
            "avg_diameter": avg_diameter,
            "positions": positions,
            "unique_diameters": len(set(j.diameter for j in self._junctions)),
            "unique_colors": len(set(j.color for j in self._junctions)),
        }

    def clear(self):
        """Remove all junctions from collection."""
        self._junctions.clear()
        self._uuid_index.clear()
        self._modified = True
        logger.debug("Cleared all junctions")

    @property
    def modified(self) -> bool:
        """Check if collection has been modified."""
        return self._modified

    def mark_saved(self):
        """Mark collection as saved (reset modified flag)."""
        self._modified = False
