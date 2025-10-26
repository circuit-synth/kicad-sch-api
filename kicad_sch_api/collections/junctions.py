"""
Junction collection with specialized indexing and junction-specific operations.

Extends the base IndexedCollection to provide junction-specific features like
position-based queries and connectivity analysis support.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.types import Junction, Point
from .base import IndexedCollection

logger = logging.getLogger(__name__)


class JunctionCollection(IndexedCollection[Junction]):
    """
    Professional junction collection with enhanced management features.

    Extends IndexedCollection with junction-specific features:
    - Position-based indexing for fast spatial queries
    - Duplicate position detection
    - Connectivity analysis support
    - Grid alignment validation
    """

    def __init__(self, junctions: Optional[List[Junction]] = None):
        """
        Initialize junction collection.

        Args:
            junctions: Initial list of junctions
        """
        self._position_index: Dict[Tuple[float, float], Junction] = {}

        super().__init__(junctions)

    # Abstract method implementations
    def _get_item_uuid(self, item: Junction) -> str:
        """Extract UUID from junction."""
        return item.uuid

    def _create_item(self, **kwargs) -> Junction:
        """Create a new junction with given parameters."""
        # This will be called by add() methods
        raise NotImplementedError("Use add() method instead")

    def _build_additional_indexes(self) -> None:
        """Build junction-specific indexes."""
        # Clear existing indexes
        self._position_index.clear()

        # Rebuild indexes from current items
        for junction in self._items:
            # Position index - junctions should be unique per position
            pos_key = (junction.position.x, junction.position.y)
            if pos_key in self._position_index:
                logger.warning(f"Duplicate junction at position {pos_key}")
            self._position_index[pos_key] = junction

    # Junction-specific methods
    def add(
        self,
        position: Union[Point, Tuple[float, float]],
        diameter: float = 1.27,
        junction_uuid: Optional[str] = None,
    ) -> Junction:
        """
        Add a new junction to the collection.

        Args:
            position: Junction position
            diameter: Junction diameter (default KiCAD standard)
            junction_uuid: Specific UUID for junction (auto-generated if None)

        Returns:
            Newly created Junction

        Raises:
            ValueError: If junction already exists at position
        """
        # Convert tuple to Point if needed
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Check for existing junction at position
        pos_key = (position.x, position.y)
        if pos_key in self._position_index:
            existing = self._position_index[pos_key]
            raise ValueError(
                f"Junction already exists at position {position} (UUID: {existing.uuid})"
            )

        # Generate UUID if not provided
        if junction_uuid is None:
            junction_uuid = str(uuid_module.uuid4())

        # Create junction
        junction = Junction(uuid=junction_uuid, position=position, diameter=diameter)

        # Add to collection using base class method
        return super().add(junction)

    def get_junction_at_position(
        self, position: Union[Point, Tuple[float, float]], tolerance: float = 0.0
    ) -> Optional[Junction]:
        """
        Get junction at a specific position.

        Args:
            position: Position to search at
            tolerance: Position tolerance for matching

        Returns:
            Junction if found, None otherwise
        """
        self._ensure_indexes_current()

        if isinstance(position, Point):
            pos_key = (position.x, position.y)
        else:
            pos_key = position

        if tolerance == 0.0:
            # Exact match
            return self._position_index.get(pos_key)
        else:
            # Tolerance-based search
            target_x, target_y = pos_key

            for junction in self._items:
                dx = abs(junction.position.x - target_x)
                dy = abs(junction.position.y - target_y)
                distance = (dx**2 + dy**2) ** 0.5

                if distance <= tolerance:
                    return junction

            return None

    def has_junction_at_position(
        self, position: Union[Point, Tuple[float, float]], tolerance: float = 0.0
    ) -> bool:
        """
        Check if a junction exists at a specific position.

        Args:
            position: Position to check
            tolerance: Position tolerance for matching

        Returns:
            True if junction exists at position
        """
        return self.get_junction_at_position(position, tolerance) is not None

    def find_junctions_in_region(
        self, min_x: float, min_y: float, max_x: float, max_y: float
    ) -> List[Junction]:
        """
        Find all junctions within a rectangular region.

        Args:
            min_x: Minimum X coordinate
            min_y: Minimum Y coordinate
            max_x: Maximum X coordinate
            max_y: Maximum Y coordinate

        Returns:
            List of junctions in the region
        """
        matching_junctions = []

        for junction in self._items:
            if min_x <= junction.position.x <= max_x and min_y <= junction.position.y <= max_y:
                matching_junctions.append(junction)

        return matching_junctions

    def update_junction_position(
        self, junction_uuid: str, new_position: Union[Point, Tuple[float, float]]
    ) -> bool:
        """
        Update the position of an existing junction.

        Args:
            junction_uuid: UUID of junction to update
            new_position: New position

        Returns:
            True if junction was updated, False if not found

        Raises:
            ValueError: If another junction exists at new position
        """
        junction = self.get(junction_uuid)
        if not junction:
            return False

        # Convert tuple to Point if needed
        if isinstance(new_position, tuple):
            new_position = Point(new_position[0], new_position[1])

        # Check for existing junction at new position
        new_pos_key = (new_position.x, new_position.y)
        if new_pos_key in self._position_index:
            existing = self._position_index[new_pos_key]
            if existing.uuid != junction_uuid:
                raise ValueError(f"Junction already exists at position {new_position}")

        # Update position
        junction.position = new_position
        self._mark_modified()
        self._mark_indexes_dirty()

        logger.debug(f"Updated junction {junction_uuid} position to {new_position}")
        return True

    def update_junction_diameter(self, junction_uuid: str, new_diameter: float) -> bool:
        """
        Update the diameter of an existing junction.

        Args:
            junction_uuid: UUID of junction to update
            new_diameter: New diameter

        Returns:
            True if junction was updated, False if not found

        Raises:
            ValueError: If diameter is not positive
        """
        if new_diameter <= 0:
            raise ValueError("Junction diameter must be positive")

        junction = self.get(junction_uuid)
        if not junction:
            return False

        # Update diameter
        junction.diameter = new_diameter
        self._mark_modified()

        logger.debug(f"Updated junction {junction_uuid} diameter to {new_diameter}")
        return True

    def get_junction_positions(self) -> List[Point]:
        """
        Get all junction positions.

        Returns:
            List of all junction positions
        """
        return [junction.position for junction in self._items]

    def validate_grid_alignment(self, grid_size: float = 1.27) -> List[Junction]:
        """
        Find junctions that are not aligned to the specified grid.

        Args:
            grid_size: Grid size for alignment check (default KiCAD standard)

        Returns:
            List of junctions not aligned to grid
        """
        misaligned = []

        for junction in self._items:
            # Check if position is aligned to grid
            x_remainder = junction.position.x % grid_size
            y_remainder = junction.position.y % grid_size

            # Allow small tolerance for floating point precision
            tolerance = grid_size * 0.01
            if (x_remainder > tolerance and x_remainder < grid_size - tolerance) or (
                y_remainder > tolerance and y_remainder < grid_size - tolerance
            ):
                misaligned.append(junction)

        return misaligned

    def snap_to_grid(self, grid_size: float = 1.27) -> int:
        """
        Snap all junctions to the specified grid.

        Args:
            grid_size: Grid size for snapping (default KiCAD standard)

        Returns:
            Number of junctions that were moved
        """
        moved_count = 0

        for junction in self._items:
            # Calculate grid-aligned position
            aligned_x = round(junction.position.x / grid_size) * grid_size
            aligned_y = round(junction.position.y / grid_size) * grid_size

            # Check if position needs to change
            if (
                abs(junction.position.x - aligned_x) > 0.001
                or abs(junction.position.y - aligned_y) > 0.001
            ):

                # Update position
                junction.position = Point(aligned_x, aligned_y)
                moved_count += 1

        if moved_count > 0:
            self._mark_modified()
            self._mark_indexes_dirty()

        logger.info(f"Snapped {moved_count} junctions to {grid_size}mm grid")
        return moved_count

    # Bulk operations
    def remove_junctions_in_region(
        self, min_x: float, min_y: float, max_x: float, max_y: float
    ) -> int:
        """
        Remove all junctions within a rectangular region.

        Args:
            min_x: Minimum X coordinate
            min_y: Minimum Y coordinate
            max_x: Maximum X coordinate
            max_y: Maximum Y coordinate

        Returns:
            Number of junctions removed
        """
        junctions_to_remove = self.find_junctions_in_region(min_x, min_y, max_x, max_y)

        for junction in junctions_to_remove:
            self.remove(junction.uuid)

        logger.info(f"Removed {len(junctions_to_remove)} junctions in region")
        return len(junctions_to_remove)

    # Collection statistics
    def get_junction_statistics(self) -> Dict[str, Any]:
        """
        Get junction statistics for the collection.

        Returns:
            Dictionary with junction statistics
        """
        stats = super().get_statistics()

        # Calculate diameter statistics
        diameters = [junction.diameter for junction in self._items]
        if diameters:
            stats.update(
                {
                    "diameter_stats": {
                        "min": min(diameters),
                        "max": max(diameters),
                        "average": sum(diameters) / len(diameters),
                    },
                    "grid_aligned": len(self._items) - len(self.validate_grid_alignment()),
                    "misaligned": len(self.validate_grid_alignment()),
                }
            )

        return stats
