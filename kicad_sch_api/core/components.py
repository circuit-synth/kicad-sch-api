"""
Enhanced component management for KiCAD schematics.

This module provides a modern, intuitive API for working with schematic components,
featuring fast lookup, bulk operations, and advanced filtering capabilities.
"""

import logging
import uuid
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from ..library.cache import SymbolDefinition, get_symbol_cache
from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .types import Point, SchematicPin, SchematicSymbol
from .ic_manager import ICManager

logger = logging.getLogger(__name__)


class Component:
    """
    Enhanced wrapper for schematic components with modern API.

    Provides intuitive access to component properties, pins, and operations
    while maintaining exact format preservation for professional use.
    """

    def __init__(self, symbol_data: SchematicSymbol, parent_collection: "ComponentCollection"):
        """
        Initialize component wrapper.

        Args:
            symbol_data: Underlying symbol data
            parent_collection: Parent collection for updates
        """
        self._data = symbol_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

    # Core properties with validation
    @property
    def reference(self) -> str:
        """Component reference (e.g., 'R1')."""
        return self._data.reference

    @reference.setter
    def reference(self, value: str):
        """Set component reference with validation."""
        if not self._validator.validate_reference(value):
            raise ValidationError(f"Invalid reference format: {value}")

        # Check for duplicates in parent collection
        if self._collection.get(value) is not None:
            raise ValidationError(f"Reference {value} already exists")

        old_ref = self._data.reference
        self._data.reference = value
        self._collection._update_reference_index(old_ref, value)
        logger.debug(f"Updated reference: {old_ref} -> {value}")

    @property
    def value(self) -> str:
        """Component value (e.g., '10k')."""
        return self._data.value

    @value.setter
    def value(self, value: str):
        """Set component value."""
        self._data.value = value
        self._collection._mark_modified()

    @property
    def footprint(self) -> Optional[str]:
        """Component footprint."""
        return self._data.footprint

    @footprint.setter
    def footprint(self, value: Optional[str]):
        """Set component footprint."""
        self._data.footprint = value
        self._collection._mark_modified()

    @property
    def position(self) -> Point:
        """Component position."""
        return self._data.position

    @position.setter
    def position(self, value: Union[Point, Tuple[float, float]]):
        """Set component position."""
        if isinstance(value, tuple):
            value = Point(value[0], value[1])
        self._data.position = value
        self._collection._mark_modified()

    @property
    def rotation(self) -> float:
        """Component rotation in degrees."""
        return self._data.rotation

    @rotation.setter
    def rotation(self, value: float):
        """Set component rotation."""
        self._data.rotation = float(value) % 360
        self._collection._mark_modified()

    @property
    def lib_id(self) -> str:
        """Library ID (e.g., 'Device:R')."""
        return self._data.lib_id

    @property
    def library(self) -> str:
        """Library name."""
        return self._data.library

    @property
    def symbol_name(self) -> str:
        """Symbol name within library."""
        return self._data.symbol_name

    # Properties dictionary
    @property
    def properties(self) -> Dict[str, str]:
        """Dictionary of all component properties."""
        return self._data.properties

    def get_property(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get property value by name."""
        return self._data.properties.get(name, default)

    def set_property(self, name: str, value: str):
        """Set property value with validation."""
        if not isinstance(name, str) or not isinstance(value, str):
            raise ValidationError("Property name and value must be strings")

        self._data.properties[name] = value
        self._collection._mark_modified()
        logger.debug(f"Set property {self.reference}.{name} = {value}")

    def remove_property(self, name: str) -> bool:
        """Remove property by name."""
        if name in self._data.properties:
            del self._data.properties[name]
            self._collection._mark_modified()
            return True
        return False

    # Pin access
    @property
    def pins(self) -> List[SchematicPin]:
        """List of component pins."""
        return self._data.pins

    def get_pin(self, pin_number: str) -> Optional[SchematicPin]:
        """Get pin by number."""
        return self._data.get_pin(pin_number)

    def get_pin_position(self, pin_number: str) -> Optional[Point]:
        """Get absolute position of pin."""
        return self._data.get_pin_position(pin_number)

    # Component state
    @property
    def in_bom(self) -> bool:
        """Whether component appears in bill of materials."""
        return self._data.in_bom

    @in_bom.setter
    def in_bom(self, value: bool):
        """Set BOM inclusion."""
        self._data.in_bom = bool(value)
        self._collection._mark_modified()

    @property
    def on_board(self) -> bool:
        """Whether component appears on PCB."""
        return self._data.on_board

    @on_board.setter
    def on_board(self, value: bool):
        """Set board inclusion."""
        self._data.on_board = bool(value)
        self._collection._mark_modified()

    # Utility methods
    def move(self, x: float, y: float):
        """Move component to new position."""
        self.position = Point(x, y)

    def translate(self, dx: float, dy: float):
        """Translate component by offset."""
        current = self.position
        self.position = Point(current.x + dx, current.y + dy)

    def rotate(self, angle: float):
        """Rotate component by angle (degrees)."""
        self.rotation = (self.rotation + angle) % 360

    def copy_properties_from(self, other: "Component"):
        """Copy all properties from another component."""
        for name, value in other.properties.items():
            self.set_property(name, value)

    def get_symbol_definition(self) -> Optional[SymbolDefinition]:
        """Get the symbol definition from library cache."""
        cache = get_symbol_cache()
        return cache.get_symbol(self.lib_id)

    def update_from_library(self) -> bool:
        """Update component pins and metadata from library definition."""
        symbol_def = self.get_symbol_definition()
        if not symbol_def:
            return False

        # Update pins
        self._data.pins = symbol_def.pins.copy()

        # Update reference prefix if needed
        if not self.reference.startswith(symbol_def.reference_prefix):
            logger.warning(
                f"Reference {self.reference} doesn't match expected prefix {symbol_def.reference_prefix}"
            )

        self._collection._mark_modified()
        return True

    def validate(self) -> List[ValidationIssue]:
        """Validate this component."""
        return self._validator.validate_component(self._data.__dict__)

    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary representation."""
        return {
            "reference": self.reference,
            "lib_id": self.lib_id,
            "value": self.value,
            "footprint": self.footprint,
            "position": {"x": self.position.x, "y": self.position.y},
            "rotation": self.rotation,
            "properties": self.properties.copy(),
            "in_bom": self.in_bom,
            "on_board": self.on_board,
            "pin_count": len(self.pins),
        }

    def __str__(self) -> str:
        """String representation."""
        return f"<Component {self.reference}: {self.lib_id} = '{self.value}' @ {self.position}>"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Component(ref='{self.reference}', lib_id='{self.lib_id}', "
            f"value='{self.value}', pos={self.position}, rotation={self.rotation})"
        )


class ComponentCollection:
    """
    Collection class for efficient component management.

    Provides fast lookup, filtering, and bulk operations for schematic components.
    Optimized for schematics with hundreds or thousands of components.
    """

    def __init__(self, components: List[SchematicSymbol] = None):
        """
        Initialize component collection.

        Args:
            components: Initial list of component data
        """
        self._components: List[Component] = []
        self._reference_index: Dict[str, Component] = {}
        self._lib_id_index: Dict[str, List[Component]] = {}
        self._value_index: Dict[str, List[Component]] = {}
        self._modified = False

        # Add initial components
        if components:
            for comp_data in components:
                self._add_to_indexes(Component(comp_data, self))

        logger.debug(f"ComponentCollection initialized with {len(self._components)} components")

    def add(
        self,
        lib_id: str,
        reference: Optional[str] = None,
        value: str = "",
        position: Optional[Union[Point, Tuple[float, float]]] = None,
        footprint: Optional[str] = None,
        unit: int = 1,
        **properties,
    ) -> Component:
        """
        Add a new component to the schematic.

        Args:
            lib_id: Library identifier (e.g., "Device:R")
            reference: Component reference (auto-generated if None)
            value: Component value
            position: Component position (auto-placed if None)
            footprint: Component footprint
            unit: Unit number for multi-unit components (1-based)
            **properties: Additional component properties

        Returns:
            Newly created Component

        Raises:
            ValidationError: If component data is invalid
        """
        # Validate lib_id
        validator = SchematicValidator()
        if not validator.validate_lib_id(lib_id):
            raise ValidationError(f"Invalid lib_id format: {lib_id}")

        # Generate reference if not provided
        if not reference:
            reference = self._generate_reference(lib_id)

        # Validate reference
        if not validator.validate_reference(reference):
            raise ValidationError(f"Invalid reference format: {reference}")

        # Check for duplicate reference
        if reference in self._reference_index:
            raise ValidationError(f"Reference {reference} already exists")

        # Set default position if not provided
        if position is None:
            position = self._find_available_position()
        elif isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Create component data
        component_data = SchematicSymbol(
            uuid=str(uuid.uuid4()),
            lib_id=lib_id,
            position=position,
            reference=reference,
            value=value,
            footprint=footprint,
            unit=unit,
            properties=properties,
        )

        # Get symbol definition and update pins
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(lib_id)
        if symbol_def:
            component_data.pins = symbol_def.pins.copy()

        # Create component wrapper
        component = Component(component_data, self)

        # Add to collection
        self._add_to_indexes(component)
        self._modified = True

        logger.info(f"Added component: {reference} ({lib_id})")
        return component

    def add_ic(
        self,
        lib_id: str,
        reference_prefix: str,
        position: Optional[Union[Point, Tuple[float, float]]] = None,
        value: str = "",
        footprint: Optional[str] = None,
        layout_style: str = "vertical",
        **properties,
    ) -> ICManager:
        """
        Add a multi-unit IC with automatic unit placement.

        Args:
            lib_id: Library identifier for the IC (e.g., "74xx:7400")
            reference_prefix: Base reference (e.g., "U1" → U1A, U1B, etc.)
            position: Base position for auto-layout (auto-placed if None)
            value: IC value (defaults to symbol name)
            footprint: IC footprint
            layout_style: Layout algorithm ("vertical", "grid", "functional")
            **properties: Common properties for all units

        Returns:
            ICManager object for position overrides and management

        Example:
            ic = sch.components.add_ic("74xx:7400", "U1", position=(100, 100))
            ic.place_unit(1, position=(150, 80))  # Override Gate A position
        """
        # Set default position if not provided
        if position is None:
            position = self._find_available_position()
        elif isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Set default value to symbol name if not provided
        if not value:
            value = lib_id.split(":")[-1]  # "74xx:7400" → "7400"

        # Create IC manager for this multi-unit component
        ic_manager = ICManager(lib_id, reference_prefix, position, self)
        
        # Generate all unit components
        unit_components = ic_manager.generate_components(
            value=value,
            footprint=footprint,
            properties=properties
        )

        # Add all units to the collection
        for component_data in unit_components:
            component = Component(component_data, self)
            self._add_to_indexes(component)

        self._modified = True
        logger.info(f"Added multi-unit IC: {reference_prefix} ({lib_id}) with {len(unit_components)} units")
        
        return ic_manager

    def remove(self, reference: str) -> bool:
        """
        Remove component by reference.

        Args:
            reference: Component reference to remove

        Returns:
            True if component was removed
        """
        component = self._reference_index.get(reference)
        if not component:
            return False

        # Remove from all indexes
        self._remove_from_indexes(component)
        self._modified = True

        logger.info(f"Removed component: {reference}")
        return True

    def get(self, reference: str) -> Optional[Component]:
        """Get component by reference."""
        return self._reference_index.get(reference)

    def filter(self, **criteria) -> List[Component]:
        """
        Filter components by various criteria.

        Args:
            lib_id: Filter by library ID
            value: Filter by value (exact match)
            value_pattern: Filter by value pattern (contains)
            reference_pattern: Filter by reference pattern
            footprint: Filter by footprint
            in_area: Filter by area (tuple of (x1, y1, x2, y2))

        Returns:
            List of matching components
        """
        results = list(self._components)

        # Apply filters
        if "lib_id" in criteria:
            lib_id = criteria["lib_id"]
            results = [c for c in results if c.lib_id == lib_id]

        if "value" in criteria:
            value = criteria["value"]
            results = [c for c in results if c.value == value]

        if "value_pattern" in criteria:
            pattern = criteria["value_pattern"].lower()
            results = [c for c in results if pattern in c.value.lower()]

        if "reference_pattern" in criteria:
            import re

            pattern = re.compile(criteria["reference_pattern"])
            results = [c for c in results if pattern.match(c.reference)]

        if "footprint" in criteria:
            footprint = criteria["footprint"]
            results = [c for c in results if c.footprint == footprint]

        if "in_area" in criteria:
            x1, y1, x2, y2 = criteria["in_area"]
            results = [c for c in results if x1 <= c.position.x <= x2 and y1 <= c.position.y <= y2]

        if "has_property" in criteria:
            prop_name = criteria["has_property"]
            results = [c for c in results if prop_name in c.properties]

        return results

    def filter_by_type(self, component_type: str) -> List[Component]:
        """Filter components by type (e.g., 'R' for resistors)."""
        return [
            c for c in self._components if c.symbol_name.upper().startswith(component_type.upper())
        ]

    def in_area(self, x1: float, y1: float, x2: float, y2: float) -> List[Component]:
        """Get components within rectangular area."""
        return self.filter(in_area=(x1, y1, x2, y2))

    def near_point(
        self, point: Union[Point, Tuple[float, float]], radius: float
    ) -> List[Component]:
        """Get components within radius of a point."""
        if isinstance(point, tuple):
            point = Point(point[0], point[1])

        results = []
        for component in self._components:
            if component.position.distance_to(point) <= radius:
                results.append(component)
        return results

    def bulk_update(self, criteria: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """
        Update multiple components matching criteria.

        Args:
            criteria: Filter criteria (same as filter method)
            updates: Dictionary of property updates

        Returns:
            Number of components updated
        """
        matching = self.filter(**criteria)

        for component in matching:
            # Update basic properties and handle special cases
            for key, value in updates.items():
                if key == 'properties' and isinstance(value, dict):
                    # Handle properties dictionary specially
                    for prop_name, prop_value in value.items():
                        component.set_property(prop_name, str(prop_value))
                elif hasattr(component, key) and key not in ['properties']:
                    setattr(component, key, value)
                else:
                    # Add as custom property
                    component.set_property(key, str(value))

        if matching:
            self._modified = True

        logger.info(f"Bulk updated {len(matching)} components")
        return len(matching)

    def sort_by_reference(self):
        """Sort components by reference designator."""
        self._components.sort(key=lambda c: c.reference)

    def sort_by_position(self, by_x: bool = True):
        """Sort components by position."""
        if by_x:
            self._components.sort(key=lambda c: (c.position.x, c.position.y))
        else:
            self._components.sort(key=lambda c: (c.position.y, c.position.x))

    def validate_all(self) -> List[ValidationIssue]:
        """Validate all components in collection."""
        all_issues = []
        validator = SchematicValidator()

        # Validate individual components
        for component in self._components:
            issues = component.validate()
            all_issues.extend(issues)

        # Validate collection-level rules
        references = [c.reference for c in self._components]
        if len(references) != len(set(references)):
            # Find duplicates
            seen = set()
            duplicates = set()
            for ref in references:
                if ref in seen:
                    duplicates.add(ref)
                seen.add(ref)

            for ref in duplicates:
                all_issues.append(
                    ValidationIssue(
                        category="reference", message=f"Duplicate reference: {ref}", level="error"
                    )
                )

        return all_issues

    def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics."""
        lib_counts = {}
        value_counts = {}

        for component in self._components:
            # Count by library
            lib = component.library
            lib_counts[lib] = lib_counts.get(lib, 0) + 1

            # Count by value
            value = component.value
            if value:
                value_counts[value] = value_counts.get(value, 0) + 1

        return {
            "total_components": len(self._components),
            "unique_references": len(self._reference_index),
            "libraries_used": len(lib_counts),
            "library_breakdown": lib_counts,
            "most_common_values": sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[
                :10
            ],
            "modified": self._modified,
        }

    # Collection interface
    def __len__(self) -> int:
        """Number of components."""
        return len(self._components)

    def __iter__(self) -> Iterator[Component]:
        """Iterate over components."""
        return iter(self._components)

    def __getitem__(self, key: Union[int, str]) -> Component:
        """Get component by index or reference."""
        if isinstance(key, int):
            return self._components[key]
        elif isinstance(key, str):
            component = self._reference_index.get(key)
            if component is None:
                raise KeyError(f"Component not found: {key}")
            return component
        else:
            raise TypeError(f"Invalid key type: {type(key)}")

    def __contains__(self, reference: str) -> bool:
        """Check if reference exists."""
        return reference in self._reference_index

    # Internal methods
    def _add_to_indexes(self, component: Component):
        """Add component to all indexes."""
        self._components.append(component)
        self._reference_index[component.reference] = component

        # Add to lib_id index
        lib_id = component.lib_id
        if lib_id not in self._lib_id_index:
            self._lib_id_index[lib_id] = []
        self._lib_id_index[lib_id].append(component)

        # Add to value index
        value = component.value
        if value:
            if value not in self._value_index:
                self._value_index[value] = []
            self._value_index[value].append(component)

    def _remove_from_indexes(self, component: Component):
        """Remove component from all indexes."""
        self._components.remove(component)
        del self._reference_index[component.reference]

        # Remove from lib_id index
        lib_id = component.lib_id
        if lib_id in self._lib_id_index:
            self._lib_id_index[lib_id].remove(component)
            if not self._lib_id_index[lib_id]:
                del self._lib_id_index[lib_id]

        # Remove from value index
        value = component.value
        if value and value in self._value_index:
            self._value_index[value].remove(component)
            if not self._value_index[value]:
                del self._value_index[value]

    def _update_reference_index(self, old_ref: str, new_ref: str):
        """Update reference index when component reference changes."""
        if old_ref in self._reference_index:
            component = self._reference_index[old_ref]
            del self._reference_index[old_ref]
            self._reference_index[new_ref] = component

    def _mark_modified(self):
        """Mark collection as modified."""
        self._modified = True

    def _generate_reference(self, lib_id: str) -> str:
        """Generate unique reference for component."""
        # Get reference prefix from symbol definition
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(lib_id)
        prefix = symbol_def.reference_prefix if symbol_def else "U"

        # Find next available number
        counter = 1
        while f"{prefix}{counter}" in self._reference_index:
            counter += 1

        return f"{prefix}{counter}"

    def _find_available_position(self) -> Point:
        """Find an available position for automatic placement."""
        # Simple grid placement - could be enhanced with collision detection
        grid_size = 10.0  # 10mm grid
        max_per_row = 10

        row = len(self._components) // max_per_row
        col = len(self._components) % max_per_row

        return Point(col * grid_size, row * grid_size)
