"""
IC management for multi-unit components with auto-layout capabilities.

This module provides intelligent placement and management for multi-unit ICs
like op-amps, logic gates, and other complex components.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from ..library.cache import get_symbol_cache
from .types import Point, SchematicSymbol

logger = logging.getLogger(__name__)


class ICManager:
    """
    Manager for multi-unit IC components with auto-layout capabilities.

    Features:
    - Automatic unit detection and placement
    - Smart layout algorithms (vertical, grid, functional)
    - Individual unit position override
    - Professional spacing and alignment
    """

    def __init__(
        self,
        lib_id: str,
        reference_prefix: str,
        position: Point,
        component_collection: "ComponentCollection",
    ):
        """
        Initialize IC manager.

        Args:
            lib_id: IC library ID (e.g., "74xx:7400")
            reference_prefix: Base reference (e.g., "U1" → U1A, U1B, etc.)
            position: Base position for auto-layout
            component_collection: Parent collection for component management
        """
        self.lib_id = lib_id
        self.reference_prefix = reference_prefix
        self.base_position = position
        self._collection = component_collection
        self._units: Dict[int, SchematicSymbol] = {}
        self._unit_positions: Dict[int, Point] = {}

        # Detect available units from symbol library
        self._detect_available_units()

        # Auto-place all units with default layout
        self._auto_layout_units()

        logger.debug(f"ICManager initialized for {lib_id} with {len(self._units)} units")

    def _detect_available_units(self):
        """Detect available units from symbol library definition."""
        cache = get_symbol_cache()
        symbol_def = cache.get_symbol(self.lib_id)

        if not symbol_def or not hasattr(symbol_def, "raw_kicad_data"):
            logger.warning(f"Could not detect units for {self.lib_id}")
            return

        # Parse symbol data to find unit definitions
        symbol_data = symbol_def.raw_kicad_data
        if isinstance(symbol_data, list):
            for item in symbol_data[1:]:
                if isinstance(item, list) and len(item) >= 2:
                    if item[0] == getattr(item[0], "value", str(item[0])) == "symbol":
                        unit_name = str(item[1]).strip('"')
                        # Extract unit number from name like "7400_1_1" → unit 1
                        unit_num = self._extract_unit_number(unit_name)
                        if unit_num and unit_num not in self._units:
                            logger.debug(f"Detected unit {unit_num} from {unit_name}")

    def _extract_unit_number(self, unit_name: str) -> Optional[int]:
        """Extract unit number from symbol unit name like '7400_1_1' → 1."""
        parts = unit_name.split("_")
        if len(parts) >= 3:
            try:
                return int(parts[-2])  # Second to last part is unit number
            except ValueError:
                pass
        return None

    def _auto_layout_units(self):
        """Auto-place all units using vertical layout algorithm."""
        # Define unit layout based on detected units
        self._place_default_units()

    def _place_default_units(self):
        """Place default units for common IC types."""
        # For 74xx logic ICs, typically have units 1-4 (logic) + unit 5 (power)
        from .config import config

        unit_spacing = config.grid.unit_spacing  # Tight vertical spacing (0.5 inch in mm)
        power_offset = config.grid.power_offset  # Power unit offset (1 inch right)

        # Place logic units (1-4) vertically in a tight column
        for unit in range(1, 5):
            unit_pos = Point(self.base_position.x, self.base_position.y + (unit - 1) * unit_spacing)
            self._unit_positions[unit] = unit_pos

        # Place power unit (5) to the right of logic units
        if 5 not in self._unit_positions:
            power_pos = Point(
                self.base_position.x + power_offset[0],
                self.base_position.y + unit_spacing,  # Align with second gate
            )
            self._unit_positions[5] = power_pos

        logger.debug(f"Auto-placed {len(self._unit_positions)} units with tight spacing")

    def place_unit(self, unit: int, position: Union[Point, Tuple[float, float]]):
        """
        Override the position of a specific unit.

        Args:
            unit: Unit number to place
            position: New position for the unit
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        self._unit_positions[unit] = position

        # If component already exists, update its position
        if unit in self._units:
            self._units[unit].position = position
            self._collection._mark_modified()

        logger.debug(f"Placed unit {unit} at {position}")

    def get_unit_position(self, unit: int) -> Optional[Point]:
        """Get the position of a specific unit."""
        return self._unit_positions.get(unit)

    def get_all_units(self) -> Dict[int, Point]:
        """Get all unit positions."""
        return self._unit_positions.copy()

    def generate_components(self, **common_properties) -> List[SchematicSymbol]:
        """
        Generate all component instances for this IC.

        Args:
            **common_properties: Properties to apply to all units

        Returns:
            List of component symbols for all units
        """
        components = []

        for unit, position in self._unit_positions.items():
            # Generate unit reference (U1 → U1A, U1B, etc.)
            if unit <= 4:
                unit_ref = (
                    f"{self.reference_prefix}{chr(ord('A') + unit - 1)}"  # U1A, U1B, U1C, U1D
                )
            else:
                unit_ref = f"{self.reference_prefix}{chr(ord('A') + unit - 1)}"  # U1E for power

            component = SchematicSymbol(
                uuid=str(uuid_module.uuid4()),
                lib_id=self.lib_id,
                position=position,
                reference=unit_ref,
                value=common_properties.get("value", self.lib_id.split(":")[-1]),
                footprint=common_properties.get("footprint"),
                unit=unit,
                properties=common_properties.get("properties", {}),
            )

            components.append(component)
            self._units[unit] = component

        logger.debug(f"Generated {len(components)} component instances")
        return components

    def get_unit_references(self) -> Dict[int, str]:
        """Get mapping of unit numbers to references."""
        references = {}
        for unit in self._unit_positions.keys():
            if unit <= 4:
                references[unit] = f"{self.reference_prefix}{chr(ord('A') + unit - 1)}"
            else:
                references[unit] = f"{self.reference_prefix}{chr(ord('A') + unit - 1)}"
        return references
