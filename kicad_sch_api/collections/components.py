"""
Enhanced component management with IndexRegistry integration.

This module provides the Component wrapper and ComponentCollection using the new
BaseCollection infrastructure with centralized index management, lazy rebuilding,
and batch mode support.
"""

import logging
import uuid
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from ..core.ic_manager import ICManager
from ..core.types import PinInfo, Point, SchematicPin, SchematicSymbol
from ..library.cache import SymbolDefinition, get_symbol_cache
from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .base import BaseCollection, IndexSpec, ValidationLevel

logger = logging.getLogger(__name__)


class Component:
    """
    Enhanced wrapper for schematic components.

    Provides intuitive access to component properties, pins, and operations
    while maintaining exact format preservation. All property modifications
    automatically notify the parent collection for tracking.
    """

    def __init__(self, symbol_data: SchematicSymbol, parent_collection: "ComponentCollection"):
        """
        Initialize component wrapper.

        Args:
            symbol_data: Underlying symbol data
            parent_collection: Parent collection for modification tracking
        """
        self._data = symbol_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

    # Core properties with validation
    @property
    def uuid(self) -> str:
        """Component UUID (read-only)."""
        return self._data.uuid

    @property
    def reference(self) -> str:
        """Component reference designator (e.g., 'R1', 'U2')."""
        return self._data.reference

    @reference.setter
    def reference(self, value: str):
        """
        Set component reference with validation and duplicate checking.

        Args:
            value: New reference designator

        Raises:
            ValidationError: If reference format is invalid or already exists
        """
        if not self._validator.validate_reference(value):
            raise ValidationError(f"Invalid reference format: {value}")

        # Check for duplicates in parent collection
        if self._collection.get(value) is not None:
            raise ValidationError(f"Reference {value} already exists")

        old_ref = self._data.reference
        self._data.reference = value
        self._collection._update_reference_index(old_ref, value)
        self._collection._mark_modified()
        logger.debug(f"Updated reference: {old_ref} -> {value}")

    @property
    def value(self) -> str:
        """Component value (e.g., '10k', '100nF')."""
        return self._data.value

    @value.setter
    def value(self, value: str):
        """Set component value."""
        old_value = self._data.value
        self._data.value = value
        self._collection._update_value_index(self, old_value, value)
        self._collection._mark_modified()

    @property
    def footprint(self) -> Optional[str]:
        """Component footprint (e.g., 'Resistor_SMD:R_0603_1608Metric')."""
        return self._data.footprint

    @footprint.setter
    def footprint(self, value: Optional[str]):
        """Set component footprint."""
        self._data.footprint = value
        self._collection._mark_modified()

    @property
    def position(self) -> Point:
        """Component position in schematic (mm)."""
        return self._data.position

    @position.setter
    def position(self, value: Union[Point, Tuple[float, float]]):
        """
        Set component position.

        Args:
            value: Position as Point or (x, y) tuple
        """
        if isinstance(value, tuple):
            value = Point(value[0], value[1])
        self._data.position = value
        self._collection._mark_modified()

    @property
    def rotation(self) -> float:
        """Component rotation in degrees (0, 90, 180, or 270)."""
        return self._data.rotation

    @rotation.setter
    def rotation(self, value: float):
        """
        Set component rotation.

        KiCad only supports 0, 90, 180, or 270 degree rotations.

        Args:
            value: Rotation angle in degrees

        Raises:
            ValueError: If rotation is not 0, 90, 180, or 270
        """
        # Normalize rotation to 0-360 range
        normalized = float(value) % 360

        # KiCad only accepts specific angles
        VALID_ROTATIONS = {0, 90, 180, 270}
        if normalized not in VALID_ROTATIONS:
            raise ValueError(
                f"Component rotation must be 0, 90, 180, or 270 degrees. "
                f"Got {value}° (normalized to {normalized}°). "
                f"KiCad does not support arbitrary rotation angles."
            )

        self._data.rotation = normalized
        self._collection._mark_modified()

    @property
    def lib_id(self) -> str:
        """Library identifier (e.g., 'Device:R')."""
        return self._data.lib_id

    @property
    def library(self) -> str:
        """Library name (e.g., 'Device' from 'Device:R')."""
        return self._data.library

    @property
    def symbol_name(self) -> str:
        """Symbol name within library (e.g., 'R' from 'Device:R')."""
        return self._data.symbol_name

    # Properties dictionary
    @property
    def properties(self) -> Dict[str, str]:
        """Dictionary of all component properties."""
        return self._data.properties

    @property
    def hidden_properties(self) -> "set[str]":
        """Set of property names that have (hide yes) flag."""
        return self._data.hidden_properties

    def get_property(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get property value by name.

        Args:
            name: Property name
            default: Default value if property doesn't exist

        Returns:
            Property value or default
        """
        return self._data.properties.get(name, default)

    def set_property(self, name: str, value: str):
        """
        Set property value with validation.

        Args:
            name: Property name
            value: Property value

        Raises:
            ValidationError: If name or value are not strings
        """
        if not isinstance(name, str) or not isinstance(value, str):
            raise ValidationError("Property name and value must be strings")

        self._data.properties[name] = value
        self._collection._mark_modified()
        logger.debug(f"Set property {self.reference}.{name} = {value}")

    def remove_property(self, name: str) -> bool:
        """
        Remove property by name.

        Args:
            name: Property name to remove

        Returns:
            True if property was removed, False if it didn't exist
        """
        if name in self._data.properties:
            del self._data.properties[name]
            # Also remove from hidden_properties if present
            self._data.hidden_properties.discard(name)
            self._collection._mark_modified()
            return True
        return False

    def add_property(self, name: str, value: str, hidden: bool = False) -> None:
        """
        Add or update a component property with visibility control.

        Sets the property value and manages its visibility state. If the property
        already exists, both value and visibility are updated.

        Args:
            name: Property name (e.g., "MPN", "Manufacturer", "Tolerance")
            value: Property value
            hidden: If True, property will have (hide yes) flag in S-expression.
                   If False, property will be visible on schematic. Default: False

        Example:
            >>> component.add_property("MPN", "RC0603FR-0710KL", hidden=True)
            >>> component.add_property("Tolerance", "1%", hidden=False)
        """
        self._data.add_property(name, value, hidden)
        self._collection._mark_modified()
        logger.debug(f"Added property {self.reference}.{name} = {value} (hidden={hidden})")

    def add_properties(self, props: Dict[str, str], hidden: bool = False) -> None:
        """
        Add or update multiple properties with same visibility setting.

        Convenience method for bulk property operations. All properties will
        have the same visibility state.

        Args:
            props: Dictionary of property name/value pairs
            hidden: If True, all properties will be hidden. If False, all will
                   be visible. Default: False

        Example:
            >>> component.add_properties({
            ...     "MPN": "RC0603FR-0710KL",
            ...     "Manufacturer": "Yageo",
            ...     "Supplier": "Digikey"
            ... }, hidden=True)
        """
        self._data.add_properties(props, hidden)
        self._collection._mark_modified()
        logger.debug(f"Added {len(props)} properties to {self.reference} (hidden={hidden})")

    # Text effects (position, font, color, etc.)
    def get_property_effects(self, property_name: str) -> Dict[str, Any]:
        """
        Get text effects for a component property.

        Returns a dictionary with all text effects for the specified property
        (Reference, Value, Footprint, etc.), including position, rotation, font
        properties, color, justification, and visibility.

        Args:
            property_name: Property name (e.g., "Reference", "Value", "Footprint")

        Returns:
            Dictionary with effect properties:
            {
                'position': (x, y),           # Position relative to component
                'rotation': float,            # Rotation in degrees
                'font_face': str,             # Font family name (or None for default)
                'font_size': (h, w),          # Font size (height, width) in mm
                'font_thickness': float,      # Font line thickness (or None)
                'bold': bool,                 # Bold flag
                'italic': bool,               # Italic flag
                'color': (r, g, b, a),        # RGBA color (or None)
                'justify_h': str,             # Horizontal justification (or None)
                'justify_v': str,             # Vertical justification (or None)
                'visible': bool,              # Visibility (True = visible, False = hidden)
            }

        Raises:
            ValueError: If property doesn't exist

        Example:
            >>> r1 = sch.components.get("R1")
            >>> effects = r1.get_property_effects("Reference")
            >>> print(f"Font size: {effects['font_size']}")
            >>> print(f"Bold: {effects['bold']}")
        """
        return self._data.get_property_effects(property_name)

    def set_property_effects(self, property_name: str, effects: Dict[str, Any]) -> None:
        """
        Set text effects for a component property.

        Updates text effects for the specified property. Only provided properties
        are updated - existing properties not specified in `effects` are preserved.

        Args:
            property_name: Property name (e.g., "Reference", "Value", "Footprint")
            effects: Dictionary with effect updates (partial updates supported)

        Raises:
            ValueError: If property doesn't exist

        Example:
            >>> r1 = sch.components.get("R1")
            >>> # Make Reference bold and larger
            >>> r1.set_property_effects("Reference", {
            ...     "bold": True,
            ...     "font_size": (2.0, 2.0)
            ... })
            >>>
            >>> # Hide Footprint property
            >>> r1.set_property_effects("Footprint", {"visible": False})
        """
        self._data.set_property_effects(property_name, effects)
        self._collection._mark_modified()
        logger.debug(f"Updated effects for {self.reference}.{property_name}")

    # Pin access
    @property
    def pins(self) -> List[SchematicPin]:
        """List of component pins."""
        return self._data.pins

    @property
    def pin_uuids(self) -> Dict[str, str]:
        """Dictionary mapping pin numbers to their UUIDs."""
        return self._data.pin_uuids

    def get_pin(self, pin_number: str) -> Optional[SchematicPin]:
        """
        Get pin by number.

        Args:
            pin_number: Pin number to find

        Returns:
            SchematicPin if found, None otherwise
        """
        return self._data.get_pin(pin_number)

    def get_pin_position(self, pin_number: str) -> Optional[Point]:
        """
        Get absolute position of a pin.

        Calculates the pin position accounting for component position,
        rotation, and mirroring.

        Args:
            pin_number: Pin number to find position for

        Returns:
            Absolute pin position in schematic coordinates, or None if pin not found
        """
        return self._data.get_pin_position(pin_number)

    # Component state flags
    @property
    def in_bom(self) -> bool:
        """Whether component appears in bill of materials."""
        return self._data.in_bom

    @in_bom.setter
    def in_bom(self, value: bool):
        """Set BOM inclusion flag."""
        self._data.in_bom = bool(value)
        self._collection._mark_modified()

    @property
    def on_board(self) -> bool:
        """Whether component appears on PCB."""
        return self._data.on_board

    @on_board.setter
    def on_board(self, value: bool):
        """Set board inclusion flag."""
        self._data.on_board = bool(value)
        self._collection._mark_modified()

    @property
    def fields_autoplaced(self) -> bool:
        """Whether component properties are auto-placed by KiCAD."""
        return self._data.fields_autoplaced

    @fields_autoplaced.setter
    def fields_autoplaced(self, value: bool):
        """Set fields autoplaced flag."""
        self._data.fields_autoplaced = bool(value)
        self._collection._mark_modified()

    # Utility methods
    def move(self, x: float, y: float):
        """
        Move component to absolute position.

        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
        """
        self.position = Point(x, y)

    def translate(self, dx: float, dy: float):
        """
        Translate component by offset.

        Args:
            dx: X offset in mm
            dy: Y offset in mm
        """
        current = self.position
        self.position = Point(current.x + dx, current.y + dy)

    def rotate(self, angle: float):
        """
        Rotate component by angle (cumulative).

        Args:
            angle: Rotation angle in degrees (will be normalized to 0/90/180/270)
        """
        self.rotation = (self.rotation + angle) % 360

    def align_pin(
        self, pin_number: str, target_position: Union[Point, Tuple[float, float]]
    ) -> None:
        """
        Move component so that the specified pin is at the target position.

        This adjusts the component's position to align a specific pin with the
        target coordinates while maintaining the component's current rotation.
        Useful for aligning existing components in horizontal signal flows.

        Args:
            pin_number: Pin number to align (e.g., "1", "2")
            target_position: Desired position for the pin (Point or (x, y) tuple)

        Raises:
            ValueError: If pin_number doesn't exist in the component

        Example:
            # Move resistor so pin 2 is at (150, 100)
            r1 = sch.components.get("R1")
            r1.align_pin("2", (150, 100))

            # Align capacitor pin 1 on same horizontal line
            c1 = sch.components.get("C1")
            c1.align_pin("1", (200, 100))  # Same Y as resistor pin 2
        """
        from ..core.geometry import calculate_position_for_pin

        # Get symbol definition to find the pin's local position
        symbol_def = self.get_symbol_definition()
        if not symbol_def:
            raise ValueError(f"Symbol definition not found for {self.reference} ({self.lib_id})")

        # Find the pin in the symbol definition
        pin_def = None
        for pin in symbol_def.pins:
            if pin.number == pin_number:
                pin_def = pin
                break

        if not pin_def:
            available_pins = [p.number for p in symbol_def.pins]
            raise ValueError(
                f"Pin '{pin_number}' not found in component {self.reference} ({self.lib_id}). "
                f"Available pins: {', '.join(available_pins)}"
            )

        logger.debug(
            f"Aligning {self.reference} pin {pin_number} "
            f"(local position: {pin_def.position}) to target {target_position}"
        )

        # Calculate new component position
        new_position = calculate_position_for_pin(
            pin_local_position=pin_def.position,
            desired_pin_position=target_position,
            rotation=self.rotation,
            mirror=None,  # TODO: Add mirror support when needed
            grid_size=1.27,
        )

        old_position = self.position
        self.position = new_position

        logger.info(
            f"Aligned {self.reference} pin {pin_number} to {target_position}: "
            f"moved from {old_position} to {new_position}"
        )

    def copy_properties_from(self, other: "Component"):
        """
        Copy all properties from another component.

        Args:
            other: Component to copy properties from
        """
        for name, value in other.properties.items():
            self.set_property(name, value)

    def get_symbol_definition(self) -> Optional[SymbolDefinition]:
        """
        Get the symbol definition from library cache.

        Returns:
            SymbolDefinition if found, None otherwise
        """
        cache = get_symbol_cache()
        return cache.get_symbol(self.lib_id)

    def update_from_library(self) -> bool:
        """
        Update component pins and metadata from library definition.

        Returns:
            True if update successful, False if symbol not found
        """
        symbol_def = self.get_symbol_definition()
        if not symbol_def:
            return False

        # Update pins
        self._data.pins = symbol_def.pins.copy()

        # Warn if reference prefix doesn't match
        if not self.reference.startswith(symbol_def.reference_prefix):
            logger.warning(
                f"Reference {self.reference} doesn't match expected prefix {symbol_def.reference_prefix}"
            )

        self._collection._mark_modified()
        return True

    def validate(self) -> List[ValidationIssue]:
        """
        Validate this component.

        Returns:
            List of validation issues (empty if valid)
        """
        return self._validator.validate_component(self._data.__dict__)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert component to dictionary representation.

        Returns:
            Dictionary with component data
        """
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
        """String representation for display."""
        return f"<Component {self.reference}: {self.lib_id} = '{self.value}' @ {self.position}>"

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"Component(ref='{self.reference}', lib_id='{self.lib_id}', "
            f"value='{self.value}', pos={self.position}, rotation={self.rotation})"
        )


class ComponentCollection(BaseCollection[Component]):
    """
    Collection class for efficient component management using IndexRegistry.

    Provides fast lookup, filtering, and bulk operations with lazy index rebuilding
    and batch mode support. Uses centralized IndexRegistry for managing all indexes
    (UUID, reference, lib_id, value).
    """

    def __init__(
        self,
        components: Optional[List[SchematicSymbol]] = None,
        parent_schematic=None,
        validation_level: ValidationLevel = ValidationLevel.NORMAL,
    ):
        """
        Initialize component collection.

        Args:
            components: Initial list of component data
            parent_schematic: Reference to parent Schematic (for hierarchy context)
            validation_level: Validation level for operations
        """
        # Initialize base collection with validation level
        super().__init__(validation_level=validation_level)

        # Store parent schematic reference for hierarchy context
        self._parent_schematic = parent_schematic

        # Manual indexes for special cases not handled by IndexRegistry
        # (These are maintained separately for complex operations)
        self._lib_id_index: Dict[str, List[Component]] = {}
        self._value_index: Dict[str, List[Component]] = {}

        # Add initial components
        if components:
            with self.batch_mode():
                for comp_data in components:
                    component = Component(comp_data, self)
                    super().add(component)
                    self._add_to_manual_indexes(component)

        logger.debug(f"ComponentCollection initialized with {len(self)} components")

    # BaseCollection abstract method implementations
    def _get_item_uuid(self, item: Component) -> str:
        """Extract UUID from component."""
        return item.uuid

    def _create_item(self, **kwargs) -> Component:
        """
        Create a new component (not typically used directly).

        Use add() method instead for proper component creation.
        """
        raise NotImplementedError("Use add() method to create components")

    def _get_index_specs(self) -> List[IndexSpec]:
        """
        Get index specifications for component collection.

        Returns:
            List of IndexSpec for UUID and reference indexes
        """
        return [
            IndexSpec(
                name="uuid",
                key_func=lambda c: c.uuid,
                unique=True,
                description="UUID index for fast lookups",
            ),
            IndexSpec(
                name="reference",
                key_func=lambda c: c.reference,
                unique=False,  # Allow duplicate references for multi-unit components
                description="Reference designator index (R1, U2, etc.)",
            ),
        ]

    # Component-specific add method
    def add(
        self,
        lib_id: str,
        reference: Optional[str] = None,
        value: str = "",
        position: Optional[Union[Point, Tuple[float, float]]] = None,
        footprint: Optional[str] = None,
        unit: int = 1,
        add_all_units: bool = False,
        unit_spacing: float = 25.4,
        rotation: float = 0.0,
        component_uuid: Optional[str] = None,
        grid_units: Optional[bool] = None,
        grid_size: Optional[float] = None,
        **properties,
    ) -> Union[Component, "MultiUnitComponentGroup"]:
        """
        Add a new component to the schematic.

        Args:
            lib_id: Library identifier (e.g., "Device:R")
            reference: Component reference (auto-generated if None)
            value: Component value
            position: Component position in mm (or grid units if grid_units=True)
            footprint: Component footprint
            unit: Unit number for multi-unit components (1-based, default: 1)
            add_all_units: If True, add all units with automatic layout (default: False)
            unit_spacing: Horizontal spacing between units in mm (default: 25.4mm = 1 inch)
            rotation: Component rotation in degrees (0, 90, 180, 270)
            component_uuid: Specific UUID for component (auto-generated if None)
            grid_units: If True, interpret position as grid units; if None, use config.positioning.use_grid_units
            grid_size: Grid size in mm; if None, use config.positioning.grid_size (default 1.27mm)
            **properties: Additional component properties

        Returns:
            Component if adding single unit, MultiUnitComponentGroup if add_all_units=True

        Raises:
            ValidationError: If component data is invalid
            LibraryError: If symbol library not found

        Examples:
            # Single unit (default behavior)
            sch.components.add('Device:R', 'R1', '10k', position=(25.4, 50.8))

            # Multi-unit automatic (all units with one call)
            group = sch.components.add('Amplifier_Operational:TL072', 'U1', 'TL072',
                                       position=(100, 100), add_all_units=True)

            # Multi-unit manual (add each unit individually)
            sch.components.add('Amplifier_Operational:TL072', 'U1', 'TL072',
                              position=(100, 100), unit=1)
            sch.components.add('Amplifier_Operational:TL072', 'U1', 'TL072',
                              position=(150, 100), unit=2)
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

        # Validate multi-unit add (allows duplicate reference with different units)
        if not add_all_units:
            # For manual unit addition, validate unit number and reference consistency
            self._validate_multi_unit_add(lib_id, reference, unit)
        # For add_all_units=True, validation happens in _add_multi_unit()

        # Use config defaults if not explicitly provided
        from ..core.config import config

        if grid_units is None:
            grid_units = config.positioning.use_grid_units
        if grid_size is None:
            grid_size = config.positioning.grid_size

        # Set default position if not provided
        if position is None:
            position = self._find_available_position()
        elif isinstance(position, tuple):
            # Convert grid units to mm if requested
            if grid_units:
                position = Point(position[0] * grid_size, position[1] * grid_size)
            else:
                position = Point(position[0], position[1])
        elif grid_units and isinstance(position, Point):
            # Convert Point from grid units to mm
            position = Point(position.x * grid_size, position.y * grid_size)

        # Always snap component position to KiCAD grid (1.27mm = 50mil)
        from ..core.geometry import snap_to_grid

        snapped_pos = snap_to_grid((position.x, position.y), grid_size=1.27)
        position = Point(snapped_pos[0], snapped_pos[1])

        logger.debug(
            f"Component {reference} position snapped to grid: ({position.x:.3f}, {position.y:.3f})"
        )

        # Handle add_all_units=True: add all units with automatic layout
        if add_all_units:
            return self._add_multi_unit(
                lib_id=lib_id,
                reference=reference,
                value=value,
                position=position,
                unit_spacing=unit_spacing,
                rotation=rotation,
                footprint=footprint,
                **properties,
            )

        # Continue with single unit addition below

        # Normalize and validate rotation
        rotation = rotation % 360
        VALID_ROTATIONS = {0, 90, 180, 270}
        if rotation not in VALID_ROTATIONS:
            raise ValidationError(
                f"Component rotation must be 0, 90, 180, or 270 degrees. "
                f"Got {rotation}°. KiCad does not support arbitrary rotation angles."
            )

        # Add hierarchy_path if parent schematic has hierarchy context
        if self._parent_schematic and hasattr(self._parent_schematic, "_hierarchy_path"):
            if self._parent_schematic._hierarchy_path:
                properties = dict(properties)
                properties["hierarchy_path"] = self._parent_schematic._hierarchy_path
                logger.debug(
                    f"Setting hierarchy_path for component {reference}: "
                    f"{self._parent_schematic._hierarchy_path}"
                )

        # Create component data
        component_data = SchematicSymbol(
            uuid=component_uuid if component_uuid else str(uuid.uuid4()),
            lib_id=lib_id,
            position=position,
            reference=reference,
            value=value,
            footprint=footprint,
            unit=unit,
            rotation=rotation,
            properties=properties,
        )

        # Get symbol definition and update pins
        from ..core.exceptions import LibraryError

        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(lib_id)
        if not symbol_def:
            library_name = lib_id.split(":")[0] if ":" in lib_id else "unknown"
            raise LibraryError(
                f"Symbol '{lib_id}' not found in KiCAD libraries. "
                f"Please verify the library name '{library_name}' and symbol name are correct. "
                f"Common libraries include: Device, Connector_Generic, Regulator_Linear, RF_Module",
                field="lib_id",
                value=lib_id,
            )
        component_data.pins = symbol_def.pins.copy()

        # Create component wrapper
        component = Component(component_data, self)

        # Add to collection (includes IndexRegistry)
        super().add(component)

        # Add to manual indexes (lib_id, value)
        self._add_to_manual_indexes(component)

        logger.info(f"Added component: {reference} ({lib_id})")
        return component

    def add_with_pin_at(
        self,
        lib_id: str,
        pin_number: str,
        pin_position: Union[Point, Tuple[float, float]],
        reference: Optional[str] = None,
        value: str = "",
        rotation: float = 0.0,
        footprint: Optional[str] = None,
        unit: int = 1,
        component_uuid: Optional[str] = None,
        **properties,
    ) -> Component:
        """
        Add component positioned by a specific pin location.

        Instead of specifying the component's center position, this method allows
        you to specify where a particular pin should be placed. This is extremely
        useful for aligning components in horizontal signal flows without manual
        offset calculations.

        Args:
            lib_id: Library identifier (e.g., "Device:R", "Device:C")
            pin_number: Pin number to position (e.g., "1", "2")
            pin_position: Desired position for the specified pin
            reference: Component reference (auto-generated if None)
            value: Component value
            rotation: Component rotation in degrees (0, 90, 180, 270)
            footprint: Component footprint
            unit: Unit number for multi-unit components (1-based)
            component_uuid: Specific UUID for component (auto-generated if None)
            **properties: Additional component properties

        Returns:
            Newly created Component with the specified pin at pin_position

        Raises:
            ValidationError: If component data is invalid
            LibraryError: If symbol library not found
            ValueError: If pin_number doesn't exist in the component

        Example:
            # Place resistor with pin 2 at (150, 100)
            r1 = sch.components.add_with_pin_at(
                lib_id="Device:R",
                pin_number="2",
                pin_position=(150, 100),
                value="10k"
            )

            # Place capacitor with pin 1 aligned on same horizontal line
            c1 = sch.components.add_with_pin_at(
                lib_id="Device:C",
                pin_number="1",
                pin_position=(200, 100),  # Same Y as resistor pin 2
                value="100nF"
            )
        """
        from ..core.exceptions import LibraryError
        from ..core.geometry import calculate_position_for_pin

        # Get symbol definition to find the pin's local position
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(lib_id)
        if not symbol_def:
            library_name = lib_id.split(":")[0] if ":" in lib_id else "unknown"
            raise LibraryError(
                f"Symbol '{lib_id}' not found in KiCAD libraries. "
                f"Please verify the library name '{library_name}' and symbol name are correct. "
                f"Common libraries include: Device, Connector_Generic, Regulator_Linear, RF_Module",
                field="lib_id",
                value=lib_id,
            )

        # Find the pin in the symbol definition
        pin_def = None
        for pin in symbol_def.pins:
            if pin.number == pin_number:
                pin_def = pin
                break

        if not pin_def:
            available_pins = [p.number for p in symbol_def.pins]
            raise ValueError(
                f"Pin '{pin_number}' not found in symbol '{lib_id}'. "
                f"Available pins: {', '.join(available_pins)}"
            )

        logger.debug(
            f"Pin {pin_number} found at local position ({pin_def.position.x}, {pin_def.position.y})"
        )

        # Calculate component position that will place the pin at the desired location
        component_position = calculate_position_for_pin(
            pin_local_position=pin_def.position,
            desired_pin_position=pin_position,
            rotation=rotation,
            mirror=None,  # TODO: Add mirror support when needed
            grid_size=1.27,
        )

        logger.info(
            f"Calculated component position ({component_position.x}, {component_position.y}) "
            f"to place pin {pin_number} at ({pin_position if isinstance(pin_position, Point) else Point(*pin_position)})"
        )

        # Use the regular add() method with the calculated position
        return self.add(
            lib_id=lib_id,
            reference=reference,
            value=value,
            position=component_position,
            footprint=footprint,
            unit=unit,
            rotation=rotation,
            component_uuid=component_uuid,
            **properties,
        )

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
            value=value, footprint=footprint, properties=properties
        )

        # Add all units to the collection using batch mode for performance
        with self.batch_mode():
            for component_data in unit_components:
                component = Component(component_data, self)
                super().add(component)
                self._add_to_manual_indexes(component)

        logger.info(
            f"Added multi-unit IC: {reference_prefix} ({lib_id}) with {len(unit_components)} units"
        )

        return ic_manager

    # Remove operations
    def remove(self, reference: str) -> bool:
        """
        Remove component by reference designator.

        Args:
            reference: Component reference to remove (e.g., "R1")

        Returns:
            True if component was removed, False if not found

        Raises:
            TypeError: If reference is not a string
        """
        if not isinstance(reference, str):
            raise TypeError(f"reference must be a string, not {type(reference).__name__}")

        self._ensure_indexes_current()

        # Get component from reference index
        ref_idx = self._index_registry.get("reference", reference)
        if ref_idx is None:
            return False

        # Handle non-unique index (returns list of indices)
        if isinstance(ref_idx, list):
            if len(ref_idx) == 0:
                return False
            # For multi-unit components, remove the first one
            component = self._items[ref_idx[0]]
        else:
            # For backward compatibility if index becomes unique
            component = self._items[ref_idx]

        # Remove from manual indexes
        self._remove_from_manual_indexes(component)

        # Remove from base collection (UUID index)
        super().remove(component.uuid)

        logger.info(f"Removed component: {reference}")
        return True

    def remove_by_uuid(self, component_uuid: str) -> bool:
        """
        Remove component by UUID.

        Args:
            component_uuid: Component UUID to remove

        Returns:
            True if component was removed, False if not found

        Raises:
            TypeError: If UUID is not a string
        """
        if not isinstance(component_uuid, str):
            raise TypeError(f"component_uuid must be a string, not {type(component_uuid).__name__}")

        # Get component from UUID index
        component = self.get_by_uuid(component_uuid)
        if not component:
            return False

        # Remove from manual indexes
        self._remove_from_manual_indexes(component)

        # Remove from base collection
        super().remove(component_uuid)

        logger.info(f"Removed component by UUID: {component_uuid}")
        return True

    def remove_component(self, component: Component) -> bool:
        """
        Remove component by component object.

        Args:
            component: Component object to remove

        Returns:
            True if component was removed, False if not found

        Raises:
            TypeError: If component is not a Component instance
        """
        if not isinstance(component, Component):
            raise TypeError(
                f"component must be a Component instance, not {type(component).__name__}"
            )

        # Check if component exists
        if component.uuid not in self:
            return False

        # Remove from manual indexes
        self._remove_from_manual_indexes(component)

        # Remove from base collection
        super().remove(component.uuid)

        logger.info(f"Removed component: {component.reference}")
        return True

    # Lookup methods
    def get(self, reference: str) -> Optional[Component]:
        """
        Get component by reference designator.

        Args:
            reference: Component reference (e.g., "R1")

        Returns:
            Component if found, None otherwise. If multiple components have
            the same reference (e.g., multi-unit components), returns the first one.
        """
        self._ensure_indexes_current()
        ref_idx = self._index_registry.get("reference", reference)
        if ref_idx is not None:
            # Handle non-unique index (returns list of indices)
            if isinstance(ref_idx, list):
                if len(ref_idx) > 0:
                    return self._items[ref_idx[0]]
            else:
                # For backward compatibility if index becomes unique
                return self._items[ref_idx]
        return None

    def get_by_uuid(self, component_uuid: str) -> Optional[Component]:
        """
        Get component by UUID.

        Args:
            component_uuid: Component UUID

        Returns:
            Component if found, None otherwise
        """
        return super().get(component_uuid)

    # Filter and search methods
    def filter(self, **criteria) -> List[Component]:
        """
        Filter components by various criteria.

        Supported criteria:
            lib_id: Filter by library ID (exact match)
            value: Filter by value (exact match)
            value_pattern: Filter by value pattern (contains)
            reference_pattern: Filter by reference pattern (regex)
            footprint: Filter by footprint (exact match)
            in_area: Filter by area (tuple of (x1, y1, x2, y2))
            has_property: Filter components that have a specific property

        Args:
            **criteria: Filter criteria

        Returns:
            List of matching components
        """
        results = list(self._items)

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
        """
        Filter components by type prefix.

        Args:
            component_type: Type prefix (e.g., 'R' for resistors, 'C' for capacitors)

        Returns:
            List of matching components
        """
        return [c for c in self._items if c.symbol_name.upper().startswith(component_type.upper())]

    def in_area(self, x1: float, y1: float, x2: float, y2: float) -> List[Component]:
        """
        Get components within rectangular area.

        Args:
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner

        Returns:
            List of components in area
        """
        return self.filter(in_area=(x1, y1, x2, y2))

    def near_point(
        self, point: Union[Point, Tuple[float, float]], radius: float
    ) -> List[Component]:
        """
        Get components within radius of a point.

        Args:
            point: Center point (Point or (x, y) tuple)
            radius: Search radius in mm

        Returns:
            List of components within radius
        """
        if isinstance(point, tuple):
            point = Point(point[0], point[1])

        results = []
        for component in self._items:
            if component.position.distance_to(point) <= radius:
                results.append(component)
        return results

    def find_pins_by_name(
        self, reference: str, name_pattern: str, case_sensitive: bool = False
    ) -> Optional[List[str]]:
        """
        Find pin numbers matching a name pattern.

        Supports both exact matches and wildcard patterns (e.g., "CLK*", "*IN*").
        By default, matching is case-insensitive for maximum flexibility.

        Args:
            reference: Component reference designator (e.g., "R1", "U2")
            name_pattern: Name pattern to search for (e.g., "VCC", "CLK", "OUT", "CLK*", "*IN*")
            case_sensitive: If False (default), matching is case-insensitive

        Returns:
            List of matching pin numbers (e.g., ["1", "2"]), or None if component not found

        Raises:
            ValueError: If name_pattern is empty

        Example:
            # Find all clock pins
            pins = sch.components.find_pins_by_name("U1", "CLK*")
            # Returns: ["5", "10"] (whatever the clock pins are numbered)

            # Find power pins
            pins = sch.components.find_pins_by_name("U1", "VCC")
            # Returns: ["1", "20"] for a common IC
        """
        import fnmatch

        logger.debug(f"[PIN_DISCOVERY] find_pins_by_name() called for {reference}")
        logger.debug(
            f"[PIN_DISCOVERY]   Pattern: '{name_pattern}' (case_sensitive={case_sensitive})"
        )

        if not name_pattern:
            raise ValueError("name_pattern cannot be empty")

        # Step 1: Get component
        component = self.get(reference)
        if not component:
            logger.warning(f"[PIN_DISCOVERY] Component not found: {reference}")
            return None

        logger.debug(f"[PIN_DISCOVERY] Found component {reference} ({component.lib_id})")

        # Step 2: Get symbol definition
        symbol_def = component.get_symbol_definition()
        if not symbol_def:
            logger.warning(
                f"[PIN_DISCOVERY] Symbol definition not found for {reference} ({component.lib_id})"
            )
            return None

        logger.debug(f"[PIN_DISCOVERY] Symbol has {len(symbol_def.pins)} total pins to search")

        # Step 3: Match pins by name
        matching_pins = []
        search_pattern = name_pattern if case_sensitive else name_pattern.lower()

        for pin in symbol_def.pins:
            pin_name = pin.name if case_sensitive else pin.name.lower()

            # Use fnmatch for wildcard matching
            if fnmatch.fnmatch(pin_name, search_pattern):
                logger.debug(
                    f"[PIN_DISCOVERY]   Pin {pin.number} ({pin.name}) matches pattern '{name_pattern}'"
                )
                matching_pins.append(pin.number)

        logger.info(
            f"[PIN_DISCOVERY] Found {len(matching_pins)} pins matching '{name_pattern}' "
            f"in {reference}: {matching_pins}"
        )
        return matching_pins

    def find_pins_by_type(
        self, reference: str, pin_type: Union[str, "PinType"]
    ) -> Optional[List[str]]:
        """
        Find pin numbers by electrical type.

        Returns all pins of a specific electrical type (e.g., all inputs, all power pins).

        Args:
            reference: Component reference designator (e.g., "R1", "U2")
            pin_type: Electrical type filter. Can be:
                     - String: "input", "output", "passive", "power_in", "power_out", etc.
                     - PinType enum value

        Returns:
            List of matching pin numbers, or None if component not found

        Example:
            # Find all input pins
            pins = sch.components.find_pins_by_type("U1", "input")
            # Returns: ["1", "2", "3"]

            # Find all power pins
            pins = sch.components.find_pins_by_type("U1", "power_in")
            # Returns: ["20", "40"] for a common IC
        """
        from ..core.types import PinType

        logger.debug(f"[PIN_DISCOVERY] find_pins_by_type() called for {reference}")

        # Normalize pin_type to PinType enum
        if isinstance(pin_type, str):
            try:
                pin_type_enum = PinType(pin_type)
                logger.debug(f"[PIN_DISCOVERY]   Type filter: {pin_type}")
            except ValueError:
                logger.error(f"[PIN_DISCOVERY] Invalid pin type: {pin_type}")
                raise ValueError(
                    f"Invalid pin type: {pin_type}. "
                    f"Must be one of: {', '.join(pt.value for pt in PinType)}"
                )
        else:
            pin_type_enum = pin_type
            logger.debug(f"[PIN_DISCOVERY]   Type filter: {pin_type_enum.value}")

        # Step 1: Get component
        component = self.get(reference)
        if not component:
            logger.warning(f"[PIN_DISCOVERY] Component not found: {reference}")
            return None

        logger.debug(f"[PIN_DISCOVERY] Found component {reference} ({component.lib_id})")

        # Step 2: Get symbol definition
        symbol_def = component.get_symbol_definition()
        if not symbol_def:
            logger.warning(
                f"[PIN_DISCOVERY] Symbol definition not found for {reference} ({component.lib_id})"
            )
            return None

        logger.debug(f"[PIN_DISCOVERY] Symbol has {len(symbol_def.pins)} total pins to filter")

        # Step 3: Filter pins by type
        matching_pins = []
        for pin in symbol_def.pins:
            if pin.pin_type == pin_type_enum:
                logger.debug(
                    f"[PIN_DISCOVERY]   Pin {pin.number} ({pin.name}) is type {pin_type_enum.value}"
                )
                matching_pins.append(pin.number)

        logger.info(
            f"[PIN_DISCOVERY] Found {len(matching_pins)} pins of type '{pin_type_enum.value}' "
            f"in {reference}: {matching_pins}"
        )
        return matching_pins

    def get_pins_info(self, reference: str) -> Optional[List[PinInfo]]:
        """
        Get comprehensive pin information for a component.

        Returns all pins for the specified component with complete metadata
        including electrical type, shape, absolute position (accounting for
        rotation and mirroring), and orientation.

        Args:
            reference: Component reference designator (e.g., "R1", "U2")

        Returns:
            List of PinInfo objects with complete pin metadata, or None if component not found

        Raises:
            LibraryError: If component's symbol library is not available

        Example:
            pins = sch.components.get_pins_info("U1")
            if pins:
                for pin in pins:
                    print(f"Pin {pin.number}: {pin.name} @ {pin.position}")
                    print(f"  Electrical type: {pin.electrical_type.value}")
                    print(f"  Shape: {pin.shape.value}")
        """
        logger.debug(f"[PIN_DISCOVERY] get_pins_info() called for reference: {reference}")

        # Step 1: Find the component
        component = self.get(reference)
        if not component:
            logger.warning(f"[PIN_DISCOVERY] Component not found: {reference}")
            return None

        logger.debug(f"[PIN_DISCOVERY] Found component {reference} ({component.lib_id})")

        # Step 2: Get symbol definition from library cache
        symbol_def = component.get_symbol_definition()
        if not symbol_def:
            from ..core.exceptions import LibraryError

            lib_id = component.lib_id
            logger.error(
                f"[PIN_DISCOVERY] Symbol library not found for component {reference}: {lib_id}"
            )
            raise LibraryError(
                f"Symbol '{lib_id}' not found in KiCAD libraries. "
                f"Please verify the library name and symbol name are correct.",
                field="lib_id",
                value=lib_id,
            )

        logger.debug(
            f"[PIN_DISCOVERY] Retrieved symbol definition for {reference}: "
            f"{len(symbol_def.pins)} pins"
        )

        # Step 3: Build PinInfo list with absolute positions
        pins_info = []
        for pin in symbol_def.pins:
            logger.debug(
                f"[PIN_DISCOVERY] Processing pin {pin.number} ({pin.name}) "
                f"in local coords: {pin.position}"
            )

            # Get absolute position accounting for component rotation
            absolute_position = component.get_pin_position(pin.number)
            if not absolute_position:
                logger.warning(
                    f"[PIN_DISCOVERY] Could not calculate position for pin {pin.number} on {reference}"
                )
                continue

            logger.debug(f"[PIN_DISCOVERY] Pin {pin.number} absolute position: {absolute_position}")

            # Create PinInfo with absolute position
            pin_info = PinInfo(
                number=pin.number,
                name=pin.name,
                position=absolute_position,
                electrical_type=pin.pin_type,
                shape=pin.pin_shape,
                length=pin.length,
                orientation=pin.rotation,  # Note: pin rotation in symbol space
                uuid=f"{component.uuid}:{pin.number}",  # Composite UUID
            )

            logger.debug(
                f"[PIN_DISCOVERY] Created PinInfo for pin {pin.number}: "
                f"type={pin_info.electrical_type.value}, shape={pin_info.shape.value}"
            )

            pins_info.append(pin_info)

        logger.info(f"[PIN_DISCOVERY] Successfully retrieved {len(pins_info)} pins for {reference}")
        return pins_info

    # Bulk operations
    def bulk_update(self, criteria: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """
        Update multiple components matching criteria.

        Args:
            criteria: Filter criteria (same as filter method)
            updates: Dictionary of property updates

        Returns:
            Number of components updated

        Example:
            # Update all 10k resistors to 1% tolerance
            count = sch.components.bulk_update(
                criteria={'value': '10k'},
                updates={'properties': {'Tolerance': '1%'}}
            )
        """
        matching = self.filter(**criteria)

        for component in matching:
            for key, value in updates.items():
                if key == "properties" and isinstance(value, dict):
                    # Handle properties dictionary specially
                    for prop_name, prop_value in value.items():
                        component.set_property(prop_name, str(prop_value))
                elif hasattr(component, key) and key not in ["properties"]:
                    setattr(component, key, value)
                else:
                    # Add as custom property
                    component.set_property(key, str(value))

        if matching:
            self._mark_modified()

        logger.info(f"Bulk updated {len(matching)} components")
        return len(matching)

    # Sorting
    def sort_by_reference(self):
        """Sort components by reference designator (in-place)."""
        self._items.sort(key=lambda c: c.reference)
        self._index_registry.mark_dirty()

    def sort_by_position(self, by_x: bool = True):
        """
        Sort components by position (in-place).

        Args:
            by_x: If True, sort by X then Y; if False, sort by Y then X
        """
        if by_x:
            self._items.sort(key=lambda c: (c.position.x, c.position.y))
        else:
            self._items.sort(key=lambda c: (c.position.y, c.position.x))
        self._index_registry.mark_dirty()

    # Validation
    def validate_all(self) -> List[ValidationIssue]:
        """
        Validate all components in collection.

        Returns:
            List of validation issues found
        """
        all_issues = []
        validator = SchematicValidator()

        # Validate individual components
        for component in self._items:
            issues = component.validate()
            all_issues.extend(issues)

        # Validate collection-level rules (e.g., duplicate references)
        self._ensure_indexes_current()
        references = [c.reference for c in self._items]
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

    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with component statistics
        """
        lib_counts = {}
        value_counts = {}

        for component in self._items:
            # Count by library
            lib = component.library
            lib_counts[lib] = lib_counts.get(lib, 0) + 1

            # Count by value
            value = component.value
            if value:
                value_counts[value] = value_counts.get(value, 0) + 1

        # Get base statistics and extend
        base_stats = super().get_statistics()
        base_stats.update(
            {
                "unique_references": len(self._items),  # After rebuild, should equal item_count
                "libraries_used": len(lib_counts),
                "library_breakdown": lib_counts,
                "most_common_values": sorted(
                    value_counts.items(), key=lambda x: x[1], reverse=True
                )[:10],
            }
        )

        return base_stats

    # Collection interface
    def __getitem__(self, key: Union[int, str]) -> Component:
        """
        Get component by index, UUID, or reference.

        Args:
            key: Integer index, UUID string, or reference string

        Returns:
            Component at the specified location

        Raises:
            KeyError: If UUID or reference not found
            IndexError: If index out of range
            TypeError: If key is invalid type
        """
        if isinstance(key, int):
            # Integer index
            return self._items[key]
        elif isinstance(key, str):
            # Try reference first (most common)
            component = self.get(key)
            if component is not None:
                return component

            # Try UUID
            component = self.get_by_uuid(key)
            if component is not None:
                return component

            raise KeyError(f"Component not found: {key}")
        else:
            raise TypeError(f"Invalid key type: {type(key).__name__}")

    def __contains__(self, item: Union[str, Component]) -> bool:
        """
        Check if reference, UUID, or component exists in collection.

        Args:
            item: Reference string, UUID string, or Component instance

        Returns:
            True if item exists, False otherwise
        """
        if isinstance(item, str):
            # Check reference or UUID
            return self.get(item) is not None or self.get_by_uuid(item) is not None
        elif isinstance(item, Component):
            # Check by UUID
            return item.uuid in self
        else:
            return False

    # Internal helper methods
    def _add_to_manual_indexes(self, component: Component):
        """Add component to manual indexes (lib_id, value)."""
        # Add to lib_id index (non-unique)
        lib_id = component.lib_id
        if lib_id not in self._lib_id_index:
            self._lib_id_index[lib_id] = []
        self._lib_id_index[lib_id].append(component)

        # Add to value index (non-unique)
        value = component.value
        if value:
            if value not in self._value_index:
                self._value_index[value] = []
            self._value_index[value].append(component)

    def _remove_from_manual_indexes(self, component: Component):
        """Remove component from manual indexes (lib_id, value)."""
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
        """
        Update reference index when component reference changes.

        This marks the index as dirty so it will be rebuilt with the new reference.
        """
        self._index_registry.mark_dirty()
        logger.debug(f"Reference index marked dirty: {old_ref} -> {new_ref}")

    def _update_value_index(self, component: Component, old_value: str, new_value: str):
        """Update value index when component value changes."""
        # Remove from old value
        if old_value and old_value in self._value_index:
            self._value_index[old_value].remove(component)
            if not self._value_index[old_value]:
                del self._value_index[old_value]

        # Add to new value
        if new_value:
            if new_value not in self._value_index:
                self._value_index[new_value] = []
            self._value_index[new_value].append(component)

    def _validate_multi_unit_add(self, lib_id: str, reference: str, unit: int):
        """
        Validate that adding a specific unit of a reference is allowed.

        Checks for:
        - Duplicate unit numbers for same reference
        - Mismatched lib_id for same reference
        - Invalid unit numbers for the symbol

        Args:
            lib_id: Library identifier
            reference: Component reference
            unit: Unit number to add

        Raises:
            ValidationError: If validation fails
        """
        # Check unit number is valid (>= 1)
        if unit < 1:
            raise ValidationError(f"Unit number must be >= 1, got {unit}")

        # Get symbol definition to check valid unit range
        # NOTE: Only enforce if symbol library reports multi-unit (units > 1)
        # If library reports units=1, it may be a parsing limitation, so allow manual addition
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(lib_id)
        if symbol_def and symbol_def.units > 1:
            # Symbol library detected multi-unit - enforce range
            if unit > symbol_def.units:
                raise ValidationError(
                    f"Unit {unit} invalid for symbol '{lib_id}' "
                    f"(valid units: 1-{symbol_def.units})"
                )
        # If symbol_def.units == 1 or 0, allow any unit number (manual override)

        # Check for existing components with same reference
        existing_components = self.filter(reference_pattern=f"^{reference}$")

        if existing_components:
            # Verify lib_id matches
            existing_lib_id = existing_components[0].lib_id
            if existing_lib_id != lib_id:
                raise ValidationError(
                    f"Reference '{reference}' already exists with different lib_id "
                    f"'{existing_lib_id}' (attempting to add '{lib_id}')"
                )

            # Check for duplicate unit
            existing_units = [c._data.unit for c in existing_components]
            if unit in existing_units:
                raise ValidationError(
                    f"Unit {unit} of reference '{reference}' already exists in schematic"
                )

        logger.debug(f"Validation passed for {reference} unit {unit}")

    def _add_multi_unit(
        self,
        lib_id: str,
        reference: str,
        value: str,
        position: Point,
        unit_spacing: float,
        rotation: float = 0.0,
        footprint: Optional[str] = None,
        **properties,
    ):
        """
        Add all units of a multi-unit component with automatic horizontal layout.

        Args:
            lib_id: Library identifier
            reference: Component reference (shared by all units)
            value: Component value
            position: Starting position for unit 1
            unit_spacing: Horizontal spacing between units (mm)
            rotation: Rotation for all units
            footprint: Footprint for all units
            **properties: Properties for all units

        Returns:
            MultiUnitComponentGroup with all units

        Raises:
            LibraryError: If symbol not found
        """
        from ..core.exceptions import LibraryError
        from ..core.multi_unit import MultiUnitComponentGroup

        # Get symbol definition to determine unit count
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(lib_id)
        if not symbol_def:
            library_name = lib_id.split(":")[0] if ":" in lib_id else "unknown"
            raise LibraryError(
                f"Symbol '{lib_id}' not found in KiCAD libraries. "
                f"Please verify the library name '{library_name}' and symbol name are correct.",
                field="lib_id",
                value=lib_id,
            )

        unit_count = symbol_def.units if symbol_def.units > 0 else 1

        logger.info(
            f"Adding {unit_count} units of {reference} ({lib_id}) " f"with {unit_spacing}mm spacing"
        )

        # Add each unit
        components = []
        for unit_num in range(1, unit_count + 1):
            # Calculate position for this unit (horizontal layout)
            unit_x = position.x + (unit_num - 1) * unit_spacing
            unit_position = Point(unit_x, position.y)

            # Add unit using existing add() method with unit parameter
            comp = self.add(
                lib_id=lib_id,
                reference=reference,
                value=value,
                position=unit_position,
                unit=unit_num,
                rotation=rotation,
                footprint=footprint,
                add_all_units=False,  # Prevent recursion
                **properties,
            )

            components.append(comp)
            logger.debug(f"Added {reference} unit {unit_num} at {unit_position}")

        # Return MultiUnitComponentGroup
        group = MultiUnitComponentGroup(reference, lib_id, components)
        logger.info(f"Created MultiUnitComponentGroup for {reference} with {len(group)} units")
        return group

    def _generate_reference(self, lib_id: str) -> str:
        """
        Generate unique reference for component.

        Args:
            lib_id: Library identifier to determine prefix

        Returns:
            Generated reference (e.g., "R1", "U2")
        """
        # Get reference prefix from symbol definition
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(lib_id)
        prefix = symbol_def.reference_prefix if symbol_def else "U"

        # Ensure indexes are current
        self._ensure_indexes_current()

        # Find next available number
        counter = 1
        while self._index_registry.has_key("reference", f"{prefix}{counter}"):
            counter += 1

        return f"{prefix}{counter}"

    def _find_available_position(self) -> Point:
        """
        Find an available position for automatic placement.

        Uses simple grid layout algorithm.

        Returns:
            Point for component placement
        """
        # Simple grid placement - could be enhanced with collision detection
        grid_size = 10.0  # 10mm grid
        max_per_row = 10

        row = len(self._items) // max_per_row
        col = len(self._items) % max_per_row

        return Point(col * grid_size, row * grid_size)

    # Compatibility methods for legacy Schematic integration
    @property
    def modified(self) -> bool:
        """Check if collection has been modified (compatibility)."""
        return self.is_modified

    def mark_saved(self) -> None:
        """Mark collection as saved (reset modified flag)."""
        self.mark_clean()
