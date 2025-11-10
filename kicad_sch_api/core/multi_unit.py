"""
Multi-unit component group management.

Provides MultiUnitComponentGroup class for managing position overrides
and accessing individual units of multi-unit components like op-amps,
logic gates, and matched transistors.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union

from .types import Point

logger = logging.getLogger(__name__)


class MultiUnitComponentGroup:
    """
    Manages multiple units of a single multi-unit component.

    Provides position overrides and access to individual unit components
    after automatic multi-unit addition with add_all_units=True.

    Example:
        group = sch.components.add("Amplifier_Operational:TL072", "U1", "TL072",
                                   position=(100, 100), add_all_units=True)

        # Override unit 2 position
        group.place_unit(2, (175, 100))

        # Access individual units
        unit_1 = group.get_unit(1)
        unit_2 = group.get_unit(2)

        # Get all positions
        positions = group.get_all_positions()
    """

    def __init__(self, reference: str, lib_id: str, components: List["Component"]):
        """
        Initialize multi-unit component group.

        Args:
            reference: Shared reference for all units (e.g., "U1")
            lib_id: Symbol library ID (e.g., "Amplifier_Operational:TL072")
            components: List of Component wrappers for each unit
        """
        self.reference = reference
        self.lib_id = lib_id
        self._units: Dict[int, "Component"] = {c._data.unit: c for c in components}

        logger.debug(
            f"MultiUnitComponentGroup created for {reference} ({lib_id}) "
            f"with {len(self._units)} units"
        )

    def get_unit(self, unit: int) -> Optional["Component"]:
        """
        Get component for specific unit number.

        Args:
            unit: Unit number (1, 2, 3, ...)

        Returns:
            Component wrapper for the unit, or None if not found

        Example:
            unit_1 = group.get_unit(1)
            print(f"Unit 1 at {unit_1.position}")
        """
        return self._units.get(unit)

    def place_unit(self, unit: int, position: Union[Point, Tuple[float, float]]):
        """
        Move a specific unit to new position.

        Args:
            unit: Unit number to move
            position: New position (Point or (x, y) tuple)

        Raises:
            KeyError: If unit number doesn't exist in this group

        Example:
            # Move unit 2 to (175, 100)
            group.place_unit(2, (175, 100))
        """
        if unit not in self._units:
            available = sorted(self._units.keys())
            raise KeyError(
                f"Unit {unit} not found in {self.reference}. " f"Available units: {available}"
            )

        # Convert tuple to Point if needed
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Update position
        self._units[unit].position = position
        logger.debug(f"Moved {self.reference} unit {unit} to {position}")

    def get_all_positions(self) -> Dict[int, Point]:
        """
        Get positions of all units.

        Returns:
            Dictionary mapping unit number to position

        Example:
            positions = group.get_all_positions()
            # {1: Point(100, 100), 2: Point(125.4, 100), 3: Point(150.8, 100)}
        """
        return {unit: comp.position for unit, comp in self._units.items()}

    def get_all_units(self) -> List["Component"]:
        """
        Get all unit components.

        Returns:
            List of Component wrappers for all units

        Example:
            units = group.get_all_units()
            for unit in units:
                print(f"{unit.reference} unit {unit._data.unit}")
        """
        return list(self._units.values())

    def __len__(self) -> int:
        """Return number of units in group."""
        return len(self._units)

    def __iter__(self):
        """Iterate over unit components."""
        return iter(self._units.values())

    def __repr__(self) -> str:
        """String representation for debugging."""
        units = sorted(self._units.keys())
        return (
            f"MultiUnitComponentGroup(reference='{self.reference}', "
            f"lib_id='{self.lib_id}', units={units})"
        )
