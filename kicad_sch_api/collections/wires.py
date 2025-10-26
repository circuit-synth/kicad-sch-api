"""
Wire collection with specialized indexing and wire-specific operations.

Extends the base IndexedCollection to provide wire-specific features like
endpoint indexing, multi-point wire support, and connectivity management.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.types import Point, Wire, WireType
from .base import IndexedCollection

logger = logging.getLogger(__name__)


class WireCollection(IndexedCollection[Wire]):
    """
    Professional wire collection with enhanced management features.

    Extends IndexedCollection with wire-specific features:
    - Endpoint indexing for connectivity analysis
    - Multi-point wire support
    - Wire type classification (normal, bus, etc.)
    - Bulk operations for performance
    - Junction management integration
    """

    def __init__(self, wires: Optional[List[Wire]] = None):
        """
        Initialize wire collection.

        Args:
            wires: Initial list of wires
        """
        self._endpoint_index: Dict[Tuple[float, float], List[Wire]] = {}
        self._type_index: Dict[WireType, List[Wire]] = {}

        super().__init__(wires)

    # Abstract method implementations
    def _get_item_uuid(self, item: Wire) -> str:
        """Extract UUID from wire."""
        return item.uuid

    def _create_item(self, **kwargs) -> Wire:
        """Create a new wire with given parameters."""
        # This will be called by add() methods
        raise NotImplementedError("Use add() method instead")

    def _build_additional_indexes(self) -> None:
        """Build wire-specific indexes."""
        # Clear existing indexes
        self._endpoint_index.clear()
        self._type_index.clear()

        # Rebuild indexes from current items
        for wire in self._items:
            # Endpoint index - index by all endpoints
            for point in wire.points:
                endpoint = (point.x, point.y)
                if endpoint not in self._endpoint_index:
                    self._endpoint_index[endpoint] = []
                self._endpoint_index[endpoint].append(wire)

            # Type index
            wire_type = getattr(wire, 'wire_type', WireType.WIRE)
            if wire_type not in self._type_index:
                self._type_index[wire_type] = []
            self._type_index[wire_type].append(wire)

    # Wire-specific methods
    def add(
        self,
        start: Union[Point, Tuple[float, float]],
        end: Union[Point, Tuple[float, float]],
        wire_type: WireType = WireType.WIRE,
        stroke_width: float = 0.0,
        stroke_type: str = "default",
        wire_uuid: Optional[str] = None,
    ) -> Wire:
        """
        Add a new wire to the collection.

        Args:
            start: Starting point of the wire
            end: Ending point of the wire
            wire_type: Type of wire (normal, bus, etc.)
            stroke_width: Wire stroke width
            stroke_type: Wire stroke type
            wire_uuid: Specific UUID for wire (auto-generated if None)

        Returns:
            Newly created Wire
        """
        # Convert tuples to Points if needed
        if isinstance(start, tuple):
            start = Point(start[0], start[1])
        if isinstance(end, tuple):
            end = Point(end[0], end[1])

        # Validate wire points
        if start == end:
            raise ValueError("Wire start and end points cannot be the same")

        # Generate UUID if not provided
        if wire_uuid is None:
            wire_uuid = str(uuid_module.uuid4())

        # Create wire
        wire = Wire(
            uuid=wire_uuid,
            points=[start, end],
            wire_type=wire_type,
            stroke_width=stroke_width,
            stroke_type=stroke_type
        )

        # Add to collection using base class method
        return super().add(wire)

    def add_multi_point(
        self,
        points: List[Union[Point, Tuple[float, float]]],
        wire_type: WireType = WireType.WIRE,
        stroke_width: float = 0.0,
        stroke_type: str = "default",
        wire_uuid: Optional[str] = None,
    ) -> Wire:
        """
        Add a multi-point wire to the collection.

        Args:
            points: List of points defining the wire path
            wire_type: Type of wire (normal, bus, etc.)
            stroke_width: Wire stroke width
            stroke_type: Wire stroke type
            wire_uuid: Specific UUID for wire (auto-generated if None)

        Returns:
            Newly created Wire

        Raises:
            ValueError: If less than 2 points provided
        """
        if len(points) < 2:
            raise ValueError("Wire must have at least 2 points")

        # Convert tuples to Points if needed
        converted_points = []
        for point in points:
            if isinstance(point, tuple):
                converted_points.append(Point(point[0], point[1]))
            else:
                converted_points.append(point)

        # Generate UUID if not provided
        if wire_uuid is None:
            wire_uuid = str(uuid_module.uuid4())

        # Create wire
        wire = Wire(
            uuid=wire_uuid,
            points=converted_points,
            wire_type=wire_type,
            stroke_width=stroke_width,
            stroke_type=stroke_type
        )

        # Add to collection using base class method
        return super().add(wire)

    def get_wires_at_point(self, point: Union[Point, Tuple[float, float]]) -> List[Wire]:
        """
        Get all wires that pass through a specific point.

        Args:
            point: Point to search at

        Returns:
            List of wires passing through the point
        """
        self._ensure_indexes_current()

        if isinstance(point, Point):
            endpoint = (point.x, point.y)
        else:
            endpoint = point

        return self._endpoint_index.get(endpoint, []).copy()

    def get_wires_by_type(self, wire_type: WireType) -> List[Wire]:
        """
        Get all wires of a specific type.

        Args:
            wire_type: Type of wires to find

        Returns:
            List of wires of the specified type
        """
        self._ensure_indexes_current()
        return self._type_index.get(wire_type, []).copy()

    def get_connected_wires(self, wire: Wire) -> List[Wire]:
        """
        Get all wires connected to the given wire.

        Args:
            wire: Wire to find connections for

        Returns:
            List of connected wires (excluding the input wire)
        """
        connected = set()

        # Check connections at all endpoints
        for point in wire.points:
            endpoint_wires = self.get_wires_at_point(point)
            for endpoint_wire in endpoint_wires:
                if endpoint_wire.uuid != wire.uuid:
                    connected.add(endpoint_wire)

        return list(connected)

    def find_wire_networks(self) -> List[List[Wire]]:
        """
        Find all connected wire networks in the collection.

        Returns:
            List of wire networks, each network is a list of connected wires
        """
        visited = set()
        networks = []

        for wire in self._items:
            if wire.uuid in visited:
                continue

            # Start a new network with this wire
            network = []
            to_visit = [wire]

            while to_visit:
                current_wire = to_visit.pop()
                if current_wire.uuid in visited:
                    continue

                visited.add(current_wire.uuid)
                network.append(current_wire)

                # Add all connected wires to visit list
                connected = self.get_connected_wires(current_wire)
                for connected_wire in connected:
                    if connected_wire.uuid not in visited:
                        to_visit.append(connected_wire)

            if network:
                networks.append(network)

        return networks

    def modify_wire_path(
        self,
        wire_uuid: str,
        new_points: List[Union[Point, Tuple[float, float]]]
    ) -> bool:
        """
        Modify the path of an existing wire.

        Args:
            wire_uuid: UUID of wire to modify
            new_points: New points for the wire path

        Returns:
            True if wire was modified, False if not found

        Raises:
            ValueError: If less than 2 points provided
        """
        if len(new_points) < 2:
            raise ValueError("Wire must have at least 2 points")

        wire = self.get(wire_uuid)
        if not wire:
            return False

        # Convert tuples to Points if needed
        converted_points = []
        for point in new_points:
            if isinstance(point, tuple):
                converted_points.append(Point(point[0], point[1]))
            else:
                converted_points.append(point)

        # Update wire points
        wire.points = converted_points
        self._mark_modified()
        self._mark_indexes_dirty()

        logger.debug(f"Modified wire {wire_uuid} path with {len(new_points)} points")
        return True

    # Bulk operations for performance
    def remove_wires_at_point(self, point: Union[Point, Tuple[float, float]]) -> int:
        """
        Remove all wires passing through a specific point.

        Args:
            point: Point where wires should be removed

        Returns:
            Number of wires removed
        """
        wires_to_remove = self.get_wires_at_point(point)

        for wire in wires_to_remove:
            self.remove(wire.uuid)

        logger.info(f"Removed {len(wires_to_remove)} wires at point {point}")
        return len(wires_to_remove)

    def bulk_update_stroke(
        self,
        wire_type: Optional[WireType] = None,
        stroke_width: Optional[float] = None,
        stroke_type: Optional[str] = None
    ) -> int:
        """
        Bulk update stroke properties for wires.

        Args:
            wire_type: Filter by wire type (None for all)
            stroke_width: New stroke width (None to keep existing)
            stroke_type: New stroke type (None to keep existing)

        Returns:
            Number of wires updated
        """
        # Get wires to update
        if wire_type is not None:
            wires_to_update = self.get_wires_by_type(wire_type)
        else:
            wires_to_update = list(self._items)

        # Apply updates
        for wire in wires_to_update:
            if stroke_width is not None:
                wire.stroke_width = stroke_width
            if stroke_type is not None:
                wire.stroke_type = stroke_type

        if wires_to_update:
            self._mark_modified()

        logger.info(f"Bulk updated stroke properties for {len(wires_to_update)} wires")
        return len(wires_to_update)

    # Collection statistics
    def get_connection_statistics(self) -> Dict[str, Any]:
        """
        Get connection statistics for the wire collection.

        Returns:
            Dictionary with connection statistics
        """
        stats = super().get_statistics()

        # Add wire-specific statistics
        stats.update({
            "endpoint_count": len(self._endpoint_index),
            "wire_types": {
                wire_type.value: len(wires)
                for wire_type, wires in self._type_index.items()
            },
            "networks": len(self.find_wire_networks()),
            "total_length": sum(self._calculate_wire_length(wire) for wire in self._items)
        })

        return stats

    def _calculate_wire_length(self, wire: Wire) -> float:
        """
        Calculate the total length of a wire.

        Args:
            wire: Wire to calculate length for

        Returns:
            Total wire length
        """
        if len(wire.points) < 2:
            return 0.0

        total_length = 0.0
        for i in range(len(wire.points) - 1):
            start_point = wire.points[i]
            end_point = wire.points[i + 1]

            dx = end_point.x - start_point.x
            dy = end_point.y - start_point.y
            segment_length = (dx ** 2 + dy ** 2) ** 0.5

            total_length += segment_length

        return total_length