"""
Enhanced wire management with IndexRegistry integration.

Provides WireCollection using BaseCollection infrastructure with
endpoint indexing and wire geometry queries.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.types import Point, Wire, WireType
from .base import BaseCollection, IndexSpec, ValidationLevel

logger = logging.getLogger(__name__)


class WireCollection(BaseCollection[Wire]):
    """
    Wire collection with endpoint indexing and geometry queries.

    Inherits from BaseCollection for UUID indexing and adds wire-specific
    functionality for endpoint queries and wire type filtering.

    Features:
    - Fast UUID lookup via IndexRegistry
    - Multi-point wire support
    - Endpoint-based queries
    - Horizontal/vertical wire detection
    - Lazy index rebuilding
    - Batch mode support
    """

    def __init__(
        self,
        wires: Optional[List[Wire]] = None,
        validation_level: ValidationLevel = ValidationLevel.NORMAL,
    ):
        """
        Initialize wire collection.

        Args:
            wires: Initial list of wires
            validation_level: Validation level for operations
        """
        super().__init__(validation_level=validation_level)

        # Add initial wires
        if wires:
            with self.batch_mode():
                for wire in wires:
                    super().add(wire)

        logger.debug(f"WireCollection initialized with {len(self)} wires")

    # BaseCollection abstract method implementations
    def _get_item_uuid(self, item: Wire) -> str:
        """Extract UUID from wire."""
        return item.uuid

    def _create_item(self, **kwargs) -> Wire:
        """Create a new wire (not typically used directly)."""
        raise NotImplementedError("Use add() method to create wires")

    def _get_index_specs(self) -> List[IndexSpec]:
        """Get index specifications for wire collection."""
        return [
            IndexSpec(
                name="uuid",
                key_func=lambda w: w.uuid,
                unique=True,
                description="UUID index for fast lookups",
            ),
        ]

    # Wire-specific add method
    def add(
        self,
        start: Optional[Union[Point, Tuple[float, float]]] = None,
        end: Optional[Union[Point, Tuple[float, float]]] = None,
        points: Optional[List[Union[Point, Tuple[float, float]]]] = None,
        wire_type: WireType = WireType.WIRE,
        stroke_width: float = 0.0,
        uuid: Optional[str] = None,
    ) -> str:
        """
        Add a wire to the collection.

        Args:
            start: Start point (for simple wires)
            end: End point (for simple wires)
            points: List of points (for multi-point wires)
            wire_type: Wire type (wire or bus)
            stroke_width: Line width
            uuid: Optional UUID (auto-generated if not provided)

        Returns:
            UUID of the created wire

        Raises:
            ValueError: If neither start/end nor points are provided
            ValueError: If UUID already exists
        """
        # Generate UUID if not provided
        if uuid is None:
            uuid = str(uuid_module.uuid4())
        else:
            # Check for duplicate
            self._ensure_indexes_current()
            if self._index_registry.has_key("uuid", uuid):
                raise ValueError(f"Wire with UUID '{uuid}' already exists")

        # Convert points
        wire_points = []
        if points:
            # Multi-point wire
            for point in points:
                if isinstance(point, tuple):
                    wire_points.append(Point(point[0], point[1]))
                else:
                    wire_points.append(point)
        elif start is not None and end is not None:
            # Simple 2-point wire
            if isinstance(start, tuple):
                start = Point(start[0], start[1])
            if isinstance(end, tuple):
                end = Point(end[0], end[1])
            wire_points = [start, end]
        else:
            raise ValueError("Must provide either start/end points or points list")

        # Validate wire has at least 2 points
        if len(wire_points) < 2:
            raise ValueError("Wire must have at least 2 points")

        # Create wire
        wire = Wire(uuid=uuid, points=wire_points, wire_type=wire_type, stroke_width=stroke_width)

        # Add to collection
        super().add(wire)

        logger.debug(f"Added wire: {len(wire_points)} points, UUID={uuid}")
        return uuid

    # Endpoint-based queries
    def get_by_endpoint(
        self, point: Union[Point, Tuple[float, float]], tolerance: float = 0.01
    ) -> List[Wire]:
        """
        Find all wires with an endpoint near a given point.

        Args:
            point: Point to search for
            tolerance: Distance tolerance for matching

        Returns:
            List of wires with endpoint near the point
        """
        if isinstance(point, tuple):
            point = Point(point[0], point[1])

        matching_wires = []
        for wire in self._items:
            # Check first and last point (endpoints)
            if (
                wire.points[0].distance_to(point) <= tolerance
                or wire.points[-1].distance_to(point) <= tolerance
            ):
                matching_wires.append(wire)

        return matching_wires

    def get_at_point(
        self, point: Union[Point, Tuple[float, float]], tolerance: float = 0.01
    ) -> List[Wire]:
        """
        Find all wires that pass through or near a point.

        Args:
            point: Point to search for
            tolerance: Distance tolerance for matching

        Returns:
            List of wires passing through the point
        """
        if isinstance(point, tuple):
            point = Point(point[0], point[1])

        matching_wires = []
        for wire in self._items:
            # Check if any point in wire is near the search point
            for wire_point in wire.points:
                if wire_point.distance_to(point) <= tolerance:
                    matching_wires.append(wire)
                    break  # Found match, move to next wire

        return matching_wires

    # Wire geometry queries
    def get_horizontal(self) -> List[Wire]:
        """
        Get all horizontal wires (Y coordinates equal).

        Returns:
            List of horizontal wires
        """
        horizontal = []
        for wire in self._items:
            if len(wire.points) == 2:
                # Simple 2-point wire
                if abs(wire.points[0].y - wire.points[1].y) < 0.01:
                    horizontal.append(wire)

        return horizontal

    def get_vertical(self) -> List[Wire]:
        """
        Get all vertical wires (X coordinates equal).

        Returns:
            List of vertical wires
        """
        vertical = []
        for wire in self._items:
            if len(wire.points) == 2:
                # Simple 2-point wire
                if abs(wire.points[0].x - wire.points[1].x) < 0.01:
                    vertical.append(wire)

        return vertical

    def get_by_type(self, wire_type: WireType) -> List[Wire]:
        """
        Get all wires of a specific type.

        Args:
            wire_type: Wire type to filter by

        Returns:
            List of wires matching the type
        """
        return [w for w in self._items if w.wire_type == wire_type]

    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get wire collection statistics.

        Returns:
            Dictionary with wire statistics
        """
        if not self._items:
            base_stats = super().get_statistics()
            base_stats.update(
                {
                    "total_wires": 0,
                    "total_segments": 0,
                    "wire_count": 0,
                    "bus_count": 0,
                    "horizontal_count": 0,
                    "vertical_count": 0,
                    "avg_points_per_wire": 0,
                }
            )
            return base_stats

        wire_count = sum(1 for w in self._items if w.wire_type == WireType.WIRE)
        bus_count = sum(1 for w in self._items if w.wire_type == WireType.BUS)
        total_segments = sum(len(w.points) - 1 for w in self._items)
        avg_points = sum(len(w.points) for w in self._items) / len(self._items)

        horizontal = len(self.get_horizontal())
        vertical = len(self.get_vertical())

        base_stats = super().get_statistics()
        base_stats.update(
            {
                "total_wires": len(self._items),
                "total_segments": total_segments,
                "wire_count": wire_count,
                "bus_count": bus_count,
                "horizontal_count": horizontal,
                "vertical_count": vertical,
                "avg_points_per_wire": avg_points,
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
