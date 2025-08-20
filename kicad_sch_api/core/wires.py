"""
Wire collection and management for KiCAD schematics.

This module provides enhanced wire management with performance optimization,
bulk operations, and professional validation features.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from .types import Point, Wire, WireType

logger = logging.getLogger(__name__)


class WireCollection:
    """
    Professional wire collection with enhanced management features.

    Features:
    - Fast UUID-based lookup and indexing
    - Bulk operations for performance
    - Multi-point wire support
    - Validation and conflict detection
    - Junction management integration
    """

    def __init__(self, wires: Optional[List[Wire]] = None):
        """
        Initialize wire collection.

        Args:
            wires: Initial list of wires
        """
        self._wires: List[Wire] = wires or []
        self._uuid_index: Dict[str, int] = {}
        self._modified = False
        
        # Build UUID index
        self._rebuild_index()
        
        logger.debug(f"WireCollection initialized with {len(self._wires)} wires")

    def _rebuild_index(self):
        """Rebuild UUID index for fast lookups."""
        self._uuid_index = {wire.uuid: i for i, wire in enumerate(self._wires)}

    def __len__(self) -> int:
        """Number of wires in collection."""
        return len(self._wires)

    def __iter__(self):
        """Iterate over wires."""
        return iter(self._wires)

    def __getitem__(self, uuid: str) -> Wire:
        """Get wire by UUID."""
        if uuid not in self._uuid_index:
            raise KeyError(f"Wire with UUID '{uuid}' not found")
        return self._wires[self._uuid_index[uuid]]

    def add(
        self,
        start: Optional[Union[Point, Tuple[float, float]]] = None,
        end: Optional[Union[Point, Tuple[float, float]]] = None,
        points: Optional[List[Union[Point, Tuple[float, float]]]] = None,
        wire_type: WireType = WireType.WIRE,
        stroke_width: float = 0.0,
        uuid: Optional[str] = None
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
        """
        # Generate UUID if not provided
        if uuid is None:
            uuid = str(uuid_module.uuid4())
        elif uuid in self._uuid_index:
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

        # Create wire
        wire = Wire(
            uuid=uuid,
            points=wire_points,
            wire_type=wire_type,
            stroke_width=stroke_width
        )

        # Add to collection
        self._wires.append(wire)
        self._uuid_index[uuid] = len(self._wires) - 1
        self._modified = True

        logger.debug(f"Added wire: {len(wire_points)} points, UUID={uuid}")
        return uuid

    def remove(self, uuid: str) -> bool:
        """
        Remove wire by UUID.

        Args:
            uuid: Wire UUID to remove

        Returns:
            True if wire was removed, False if not found
        """
        if uuid not in self._uuid_index:
            return False

        index = self._uuid_index[uuid]
        del self._wires[index]
        self._rebuild_index()
        self._modified = True

        logger.debug(f"Removed wire: {uuid}")
        return True

    def get_by_point(self, point: Union[Point, Tuple[float, float]], tolerance: float = None) -> List[Wire]:
        """
        Find wires that pass through or near a point.

        Args:
            point: Point to search near
            tolerance: Distance tolerance (uses config default if None)

        Returns:
            List of wires near the point
        """
        if tolerance is None:
            from .config import config
            tolerance = config.tolerance.position_tolerance
        if isinstance(point, tuple):
            point = Point(point[0], point[1])

        matching_wires = []
        for wire in self._wires:
            # Check if any wire point is close
            for wire_point in wire.points:
                if wire_point.distance_to(point) <= tolerance:
                    matching_wires.append(wire)
                    break
            else:
                # Check if point lies on any wire segment
                for i in range(len(wire.points) - 1):
                    if self._point_on_segment(point, wire.points[i], wire.points[i + 1], tolerance):
                        matching_wires.append(wire)
                        break

        return matching_wires

    def _point_on_segment(self, point: Point, seg_start: Point, seg_end: Point, tolerance: float) -> bool:
        """Check if point lies on line segment within tolerance."""
        # Vector from seg_start to seg_end
        seg_vec = Point(seg_end.x - seg_start.x, seg_end.y - seg_start.y)
        seg_length = seg_start.distance_to(seg_end)
        
        from .config import config
        if seg_length < config.tolerance.wire_segment_min:  # Very short segment
            return seg_start.distance_to(point) <= tolerance
        
        # Vector from seg_start to point
        point_vec = Point(point.x - seg_start.x, point.y - seg_start.y)
        
        # Project point onto segment
        dot_product = (point_vec.x * seg_vec.x + point_vec.y * seg_vec.y)
        projection = dot_product / (seg_length * seg_length)
        
        # Check if projection is within segment bounds
        if projection < 0 or projection > 1:
            return False
        
        # Calculate distance from point to line
        proj_point = Point(
            seg_start.x + projection * seg_vec.x,
            seg_start.y + projection * seg_vec.y
        )
        distance = point.distance_to(proj_point)
        
        return distance <= tolerance

    def get_horizontal_wires(self) -> List[Wire]:
        """Get all horizontal wires."""
        return [wire for wire in self._wires if wire.is_horizontal()]

    def get_vertical_wires(self) -> List[Wire]:
        """Get all vertical wires."""
        return [wire for wire in self._wires if wire.is_vertical()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get wire collection statistics."""
        total_length = sum(wire.length for wire in self._wires)
        simple_wires = sum(1 for wire in self._wires if wire.is_simple())
        multi_point_wires = len(self._wires) - simple_wires
        
        return {
            "total_wires": len(self._wires),
            "simple_wires": simple_wires,
            "multi_point_wires": multi_point_wires,
            "total_length": total_length,
            "avg_length": total_length / len(self._wires) if self._wires else 0,
            "horizontal_wires": len(self.get_horizontal_wires()),
            "vertical_wires": len(self.get_vertical_wires())
        }

    def clear(self):
        """Remove all wires from collection."""
        self._wires.clear()
        self._uuid_index.clear()
        self._modified = True
        logger.debug("Cleared all wires")

    @property
    def modified(self) -> bool:
        """Check if collection has been modified."""
        return self._modified

    def mark_saved(self):
        """Mark collection as saved (reset modified flag)."""
        self._modified = False