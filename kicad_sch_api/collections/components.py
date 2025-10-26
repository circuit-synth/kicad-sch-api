"""
Component collection with specialized indexing and component-specific operations.

Extends the base IndexedCollection to provide component-specific features like
reference indexing, lib_id grouping, and automatic reference generation.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.types import Point, SchematicSymbol
from ..library.cache import get_symbol_cache
from ..utils.validation import SchematicValidator, ValidationError
from .base import IndexedCollection

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

    @property
    def uuid(self) -> str:
        """Component UUID."""
        return self._data.uuid

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
        if self._collection.get_by_reference(value) is not None:
            raise ValidationError(f"Reference {value} already exists")

        old_ref = self._data.reference
        self._data.reference = value
        self._collection._update_reference_index(old_ref, value)
        self._collection._mark_modified()
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
    def lib_id(self) -> str:
        """Component library ID (e.g., 'Device:R')."""
        return self._data.lib_id

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
        self._data.rotation = value
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

    def get_property(self, name: str) -> Optional[str]:
        """Get component property value."""
        return self._data.properties.get(name)

    def set_property(self, name: str, value: str) -> None:
        """Set component property value."""
        self._data.properties[name] = value
        self._collection._mark_modified()

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"Component(ref='{self.reference}', lib_id='{self.lib_id}', "
            f"value='{self.value}', pos={self.position}, rotation={self.rotation})"
        )


class ComponentCollection(IndexedCollection[Component]):
    """
    Collection class for efficient component management.

    Extends IndexedCollection with component-specific features:
    - Reference-based indexing for fast component lookup
    - Lib_id grouping for filtering by component type
    - Value indexing for filtering by component value
    - Automatic reference generation
    - Component validation and conflict detection
    """

    def __init__(self, components: Optional[List[SchematicSymbol]] = None):
        """
        Initialize component collection.

        Args:
            components: Initial list of component data
        """
        self._reference_index: Dict[str, Component] = {}
        self._lib_id_index: Dict[str, List[Component]] = {}
        self._value_index: Dict[str, List[Component]] = {}

        # Initialize base collection
        wrapped_components = []
        if components:
            wrapped_components = [Component(comp_data, self) for comp_data in components]

        super().__init__(wrapped_components)

    # Abstract method implementations
    def _get_item_uuid(self, item: Component) -> str:
        """Extract UUID from component."""
        return item.uuid

    def _create_item(self, **kwargs) -> Component:
        """Create a new component with given parameters."""
        # This will be called by add() methods in subclasses
        raise NotImplementedError("Use add() method instead")

    def _build_additional_indexes(self) -> None:
        """Build component-specific indexes."""
        # Clear existing indexes
        self._reference_index.clear()
        self._lib_id_index.clear()
        self._value_index.clear()

        # Rebuild indexes from current items
        for component in self._items:
            # Reference index
            self._reference_index[component.reference] = component

            # Lib_id index
            if component.lib_id not in self._lib_id_index:
                self._lib_id_index[component.lib_id] = []
            self._lib_id_index[component.lib_id].append(component)

            # Value index
            if component.value not in self._value_index:
                self._value_index[component.value] = []
            self._value_index[component.value].append(component)

    # Component-specific methods
    def add(
        self,
        lib_id: str,
        reference: Optional[str] = None,
        value: str = "",
        position: Optional[Union[Point, Tuple[float, float]]] = None,
        footprint: Optional[str] = None,
        unit: int = 1,
        component_uuid: Optional[str] = None,
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
            component_uuid: Specific UUID for component (auto-generated if None)
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
        self._ensure_indexes_current()
        if reference in self._reference_index:
            raise ValidationError(f"Reference {reference} already exists")

        # Set default position if not provided
        if position is None:
            position = self._find_available_position()
        elif isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Always snap component position to KiCAD grid (1.27mm = 50mil)
        from ..core.geometry import snap_to_grid

        snapped_pos = snap_to_grid((position.x, position.y), grid_size=1.27)
        position = Point(snapped_pos[0], snapped_pos[1])

        # Generate UUID if not provided
        if component_uuid is None:
            component_uuid = str(uuid.uuid4())

        # Create SchematicSymbol data
        symbol_data = SchematicSymbol(
            uuid=component_uuid,
            lib_id=lib_id,
            reference=reference,
            value=value,
            position=position,
            rotation=0.0,
            unit=unit,
            in_bom=True,
            on_board=True,
            footprint=footprint,
            properties=properties.copy(),
        )

        # Create component wrapper
        component = Component(symbol_data, self)

        # Add to collection using base class method
        return super().add(component)

    def get_by_reference(self, reference: str) -> Optional[Component]:
        """
        Get component by reference.

        Args:
            reference: Component reference to find

        Returns:
            Component if found, None otherwise
        """
        self._ensure_indexes_current()
        return self._reference_index.get(reference)

    def get_by_lib_id(self, lib_id: str) -> List[Component]:
        """
        Get all components with a specific lib_id.

        Args:
            lib_id: Library ID to search for

        Returns:
            List of matching components
        """
        self._ensure_indexes_current()
        return self._lib_id_index.get(lib_id, []).copy()

    def get_by_value(self, value: str) -> List[Component]:
        """
        Get all components with a specific value.

        Args:
            value: Component value to search for

        Returns:
            List of matching components
        """
        self._ensure_indexes_current()
        return self._value_index.get(value, []).copy()

    def _generate_reference(self, lib_id: str) -> str:
        """
        Generate a unique reference for a component.

        Args:
            lib_id: Library ID to generate reference for

        Returns:
            Unique reference string
        """
        # Extract base reference from lib_id
        if ":" in lib_id:
            base_ref = lib_id.split(":")[-1]
        else:
            base_ref = lib_id

        # Map common component types to standard prefixes
        ref_prefixes = {
            "R": "R",
            "Resistor": "R",
            "C": "C",
            "Capacitor": "C",
            "L": "L",
            "Inductor": "L",
            "D": "D",
            "Diode": "D",
            "Q": "Q",
            "Transistor": "Q",
            "U": "U",
            "IC": "U",
            "Amplifier": "U",
            "J": "J",
            "Connector": "J",
            "SW": "SW",
            "Switch": "SW",
            "F": "F",
            "Fuse": "F",
            "TP": "TP",
            "TestPoint": "TP",
        }

        prefix = ref_prefixes.get(base_ref, "U")

        # Ensure indexes are current before checking
        self._ensure_indexes_current()

        # Find next available number
        counter = 1
        while f"{prefix}{counter}" in self._reference_index:
            counter += 1

        return f"{prefix}{counter}"

    def _find_available_position(self) -> Point:
        """
        Find an available position for a new component.

        Returns:
            Available position point
        """
        # Start at a reasonable position and check for conflicts
        base_x, base_y = 100.0, 100.0
        spacing = 25.4  # 1 inch spacing

        # Check existing positions to avoid overlap
        used_positions = {(comp.position.x, comp.position.y) for comp in self._items}

        # Find first available position in a grid pattern
        for row in range(10):  # Check up to 10 rows
            for col in range(10):  # Check up to 10 columns
                x = base_x + col * spacing
                y = base_y + row * spacing
                if (x, y) not in used_positions:
                    return Point(x, y)

        # Fallback to random position if grid is full
        return Point(base_x + len(self._items) * spacing, base_y)

    def _update_reference_index(self, old_reference: str, new_reference: str) -> None:
        """
        Update reference index when component reference changes.

        Args:
            old_reference: Previous reference
            new_reference: New reference
        """
        if old_reference in self._reference_index:
            component = self._reference_index.pop(old_reference)
            self._reference_index[new_reference] = component

    # Bulk operations for performance
    def bulk_update(self, criteria: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """
        Perform bulk update on components matching criteria.

        Args:
            criteria: Criteria for selecting components
            updates: Updates to apply

        Returns:
            Number of components updated
        """
        matching_components = self.filter(**criteria)

        for component in matching_components:
            for attr, value in updates.items():
                if hasattr(component, attr):
                    setattr(component, attr, value)

        self._mark_modified()
        self._mark_indexes_dirty()

        logger.info(f"Bulk updated {len(matching_components)} components")
        return len(matching_components)
