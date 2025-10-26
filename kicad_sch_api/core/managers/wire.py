"""
Wire Manager for KiCAD schematic wire operations.

Handles wire creation, removal, pin connections, and auto-routing functionality
while managing component pin position calculations and connectivity analysis.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from ...library.cache import get_symbol_cache
from ..types import Point, Wire, WireType
from ..wires import WireCollection

logger = logging.getLogger(__name__)


class WireManager:
    """
    Manages wire operations and pin connectivity in KiCAD schematics.

    Responsible for:
    - Wire creation and removal
    - Pin position calculations
    - Auto-routing between pins
    - Connectivity analysis
    - Wire-to-pin connections
    """

    def __init__(
        self, schematic_data: Dict[str, Any], wire_collection: WireCollection, component_collection
    ):
        """
        Initialize WireManager.

        Args:
            schematic_data: Reference to schematic data
            wire_collection: Wire collection for management
            component_collection: Component collection for pin lookups
        """
        self._data = schematic_data
        self._wires = wire_collection
        self._components = component_collection
        self._symbol_cache = get_symbol_cache()

    def add_wire(
        self, start: Union[Point, Tuple[float, float]], end: Union[Point, Tuple[float, float]]
    ) -> str:
        """
        Add a wire connection.

        Args:
            start: Start point
            end: End point

        Returns:
            UUID of created wire
        """
        if isinstance(start, tuple):
            start = Point(start[0], start[1])
        if isinstance(end, tuple):
            end = Point(end[0], end[1])

        # Use the wire collection to add the wire
        wire_uuid = self._wires.add(start=start, end=end)

        logger.debug(f"Added wire: {start} -> {end}")
        return wire_uuid

    def remove_wire(self, wire_uuid: str) -> bool:
        """
        Remove wire by UUID.

        Args:
            wire_uuid: UUID of wire to remove

        Returns:
            True if wire was removed, False if not found
        """
        # Remove from wire collection
        removed_from_collection = self._wires.remove(wire_uuid)

        # Also remove from data structure for consistency
        wires = self._data.get("wires", [])
        removed_from_data = False
        for i, wire in enumerate(wires):
            if wire.get("uuid") == wire_uuid:
                del wires[i]
                removed_from_data = True
                break

        success = removed_from_collection or removed_from_data
        if success:
            logger.debug(f"Removed wire: {wire_uuid}")

        return success

    def add_wire_to_pin(
        self, start: Union[Point, Tuple[float, float]], component_ref: str, pin_number: str
    ) -> str:
        """
        Add wire from a point to a component pin.

        Args:
            start: Starting point
            component_ref: Component reference (e.g., "R1")
            pin_number: Pin number on component

        Returns:
            UUID of created wire

        Raises:
            ValueError: If component or pin not found
        """
        pin_position = self.get_component_pin_position(component_ref, pin_number)
        if pin_position is None:
            raise ValueError(f"Pin {pin_number} not found on component {component_ref}")

        return self.add_wire(start, pin_position)

    def add_wire_between_pins(
        self, component1_ref: str, pin1_number: str, component2_ref: str, pin2_number: str
    ) -> str:
        """
        Add wire between two component pins.

        Args:
            component1_ref: First component reference
            pin1_number: First component pin number
            component2_ref: Second component reference
            pin2_number: Second component pin number

        Returns:
            UUID of created wire

        Raises:
            ValueError: If components or pins not found
        """
        pin1_pos = self.get_component_pin_position(component1_ref, pin1_number)
        pin2_pos = self.get_component_pin_position(component2_ref, pin2_number)

        if pin1_pos is None:
            raise ValueError(f"Pin {pin1_number} not found on component {component1_ref}")
        if pin2_pos is None:
            raise ValueError(f"Pin {pin2_number} not found on component {component2_ref}")

        return self.add_wire(pin1_pos, pin2_pos)

    def get_component_pin_position(self, component_ref: str, pin_number: str) -> Optional[Point]:
        """
        Get absolute position of a component pin.

        This consolidates the duplicate implementations in the original schematic class.

        Args:
            component_ref: Component reference (e.g., "R1")
            pin_number: Pin number

        Returns:
            Absolute pin position or None if not found
        """
        # Find component
        component = self._components.get(component_ref)
        if not component:
            logger.warning(f"Component not found: {component_ref}")
            return None

        # Get symbol definition from cache
        symbol_def = self._symbol_cache.get_symbol(component.lib_id)
        if not symbol_def:
            logger.warning(f"Symbol definition not found: {component.lib_id}")
            return None

        # Find pin in symbol definition
        for pin in symbol_def.pins:
            if pin.number == pin_number:
                # Calculate absolute position
                # Apply component rotation/mirroring if needed (simplified for now)
                absolute_x = component.position.x + pin.position.x
                absolute_y = component.position.y + pin.position.y

                return Point(absolute_x, absolute_y)

        logger.warning(f"Pin {pin_number} not found on component {component_ref}")
        return None

    def list_component_pins(self, component_ref: str) -> List[Tuple[str, Point]]:
        """
        List all pins and their positions for a component.

        Args:
            component_ref: Component reference

        Returns:
            List of (pin_number, absolute_position) tuples
        """
        pins = []

        # Find component
        component = self._components.get(component_ref)
        if not component:
            return pins

        # Get symbol definition
        symbol_def = self._symbol_cache.get_symbol(component.lib_id)
        if not symbol_def:
            return pins

        # Calculate absolute positions for all pins
        for pin in symbol_def.pins:
            absolute_x = component.position.x + pin.position.x
            absolute_y = component.position.y + pin.position.y
            pins.append((pin.number, Point(absolute_x, absolute_y)))

        return pins

    def auto_route_pins(
        self,
        component1_ref: str,
        pin1_number: str,
        component2_ref: str,
        pin2_number: str,
        routing_strategy: str = "direct",
    ) -> List[str]:
        """
        Auto-route between two pins with different strategies.

        Args:
            component1_ref: First component reference
            pin1_number: First component pin number
            component2_ref: Second component reference
            pin2_number: Second component pin number
            routing_strategy: "direct" or "manhattan"

        Returns:
            List of wire UUIDs created

        Raises:
            ValueError: If components or pins not found
        """
        pin1_pos = self.get_component_pin_position(component1_ref, pin1_number)
        pin2_pos = self.get_component_pin_position(component2_ref, pin2_number)

        if pin1_pos is None:
            raise ValueError(f"Pin {pin1_number} not found on component {component1_ref}")
        if pin2_pos is None:
            raise ValueError(f"Pin {pin2_number} not found on component {component2_ref}")

        wire_uuids = []

        if routing_strategy == "direct":
            # Direct wire between pins
            wire_uuid = self.add_wire(pin1_pos, pin2_pos)
            wire_uuids.append(wire_uuid)

        elif routing_strategy == "manhattan":
            # Manhattan routing (L-shaped path)
            # Route horizontally first, then vertically
            intermediate_point = Point(pin2_pos.x, pin1_pos.y)

            # Only add intermediate wire if it has length
            if abs(pin1_pos.x - pin2_pos.x) > 0.1:  # Minimum wire length
                wire1_uuid = self.add_wire(pin1_pos, intermediate_point)
                wire_uuids.append(wire1_uuid)

            if abs(pin1_pos.y - pin2_pos.y) > 0.1:  # Minimum wire length
                wire2_uuid = self.add_wire(intermediate_point, pin2_pos)
                wire_uuids.append(wire2_uuid)

        else:
            raise ValueError(f"Unknown routing strategy: {routing_strategy}")

        logger.info(
            f"Auto-routed {component1_ref}:{pin1_number} to {component2_ref}:{pin2_number} using {routing_strategy}"
        )
        return wire_uuids

    def are_pins_connected(
        self, component1_ref: str, pin1_number: str, component2_ref: str, pin2_number: str
    ) -> bool:
        """
        Check if two pins are connected via wires.

        Args:
            component1_ref: First component reference
            pin1_number: First component pin number
            component2_ref: Second component reference
            pin2_number: Second component pin number

        Returns:
            True if pins are connected, False otherwise
        """
        pin1_pos = self.get_component_pin_position(component1_ref, pin1_number)
        pin2_pos = self.get_component_pin_position(component2_ref, pin2_number)

        if pin1_pos is None or pin2_pos is None:
            return False

        # Check for direct wire connection
        for wire in self._wires:
            if (wire.start == pin1_pos and wire.end == pin2_pos) or (
                wire.start == pin2_pos and wire.end == pin1_pos
            ):
                return True

        # TODO: Implement more sophisticated connectivity analysis
        # This would involve following wire networks through junctions
        return False

    def connect_pins_with_wire(
        self, component1_ref: str, pin1_number: str, component2_ref: str, pin2_number: str
    ) -> str:
        """
        Legacy alias for add_wire_between_pins.

        Args:
            component1_ref: First component reference
            pin1_number: First component pin number
            component2_ref: Second component reference
            pin2_number: Second component pin number

        Returns:
            UUID of created wire
        """
        return self.add_wire_between_pins(component1_ref, pin1_number, component2_ref, pin2_number)

    def get_wire_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about wires in the schematic.

        Returns:
            Dictionary with wire statistics
        """
        total_wires = len(self._wires)
        total_length = sum(wire.start.distance_to(wire.end) for wire in self._wires)

        return {
            "total_wires": total_wires,
            "total_length": total_length,
            "average_length": total_length / total_wires if total_wires > 0 else 0,
            "wire_types": {
                "normal": len([w for w in self._wires if w.wire_type == WireType.WIRE]),
                "bus": len([w for w in self._wires if w.wire_type == WireType.BUS]),
            },
        }
