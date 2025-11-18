"""
Core data types for KiCAD schematic manipulation.

This module defines the fundamental data structures used throughout kicad-sch-api,
providing a clean, type-safe interface for working with schematic elements.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4


@dataclass(frozen=True)
class Point:
    """2D point with x,y coordinates in mm."""

    x: float
    y: float

    def __post_init__(self) -> None:
        # Ensure coordinates are float
        object.__setattr__(self, "x", float(self.x))
        object.__setattr__(self, "y", float(self.y))

    def distance_to(self, other: "Point") -> float:
        """Calculate distance to another point."""
        return float(((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5)

    def offset(self, dx: float, dy: float) -> "Point":
        """Create new point offset by dx, dy."""
        return Point(self.x + dx, self.y + dy)

    def __str__(self) -> str:
        return f"({self.x:.3f}, {self.y:.3f})"


def point_from_dict_or_tuple(
    position: Union[Point, Dict[str, float], Tuple[float, float], List[float], Any],
) -> Point:
    """
    Convert various position formats to a Point object.

    Supports multiple input formats for maximum flexibility:
    - Point: Returns as-is
    - Dict with 'x' and 'y' keys: Extracts and creates Point
    - Tuple/List with 2 elements: Creates Point from coordinates
    - Other: Returns as-is (assumes it's already a Point-like object)

    Args:
        position: Position in any supported format

    Returns:
        Point object

    Example:
        >>> point_from_dict_or_tuple({"x": 10, "y": 20})
        Point(x=10.0, y=20.0)
        >>> point_from_dict_or_tuple((10, 20))
        Point(x=10.0, y=20.0)
        >>> point_from_dict_or_tuple(Point(10, 20))
        Point(x=10.0, y=20.0)
    """
    if isinstance(position, Point):
        return position
    elif isinstance(position, dict):
        return Point(position.get("x", 0), position.get("y", 0))
    elif isinstance(position, (list, tuple)) and len(position) >= 2:
        return Point(position[0], position[1])
    else:
        # Assume it's already a Point-like object or will be handled by caller
        return position


@dataclass(frozen=True)
class Rectangle:
    """Rectangle defined by two corner points."""

    top_left: Point
    bottom_right: Point

    @property
    def width(self) -> float:
        """Rectangle width."""
        return abs(self.bottom_right.x - self.top_left.x)

    @property
    def height(self) -> float:
        """Rectangle height."""
        return abs(self.bottom_right.y - self.top_left.y)

    @property
    def center(self) -> Point:
        """Rectangle center point."""
        return Point(
            (self.top_left.x + self.bottom_right.x) / 2, (self.top_left.y + self.bottom_right.y) / 2
        )

    def contains(self, point: Point) -> bool:
        """Check if point is inside rectangle."""
        return (
            self.top_left.x <= point.x <= self.bottom_right.x
            and self.top_left.y <= point.y <= self.bottom_right.y
        )


class PinType(Enum):
    """KiCAD pin electrical types."""

    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    TRISTATE = "tri_state"
    PASSIVE = "passive"
    FREE = "free"
    UNSPECIFIED = "unspecified"
    POWER_IN = "power_in"
    POWER_OUT = "power_out"
    OPEN_COLLECTOR = "open_collector"
    OPEN_EMITTER = "open_emitter"
    NO_CONNECT = "no_connect"


class PinShape(Enum):
    """KiCAD pin graphical shapes."""

    LINE = "line"
    INVERTED = "inverted"
    CLOCK = "clock"
    INVERTED_CLOCK = "inverted_clock"
    INPUT_LOW = "input_low"
    CLOCK_LOW = "clock_low"
    OUTPUT_LOW = "output_low"
    EDGE_CLOCK_HIGH = "edge_clock_high"
    NON_LOGIC = "non_logic"


@dataclass
class SchematicPin:
    """Pin definition for schematic symbols."""

    number: str
    name: str
    position: Point
    pin_type: PinType = PinType.PASSIVE
    pin_shape: PinShape = PinShape.LINE
    length: float = 2.54  # Standard pin length in mm
    rotation: float = 0.0  # Rotation in degrees

    def __post_init__(self) -> None:
        # Ensure types are correct
        self.pin_type = PinType(self.pin_type) if isinstance(self.pin_type, str) else self.pin_type
        self.pin_shape = (
            PinShape(self.pin_shape) if isinstance(self.pin_shape, str) else self.pin_shape
        )


@dataclass
class PinInfo:
    """
    Complete pin information for a component pin.

    This dataclass provides comprehensive pin metadata including position,
    electrical properties, and graphical representation. Positions are in
    schematic coordinates (absolute positions accounting for component
    rotation and mirroring).
    """

    number: str  # Pin number (e.g., "1", "2", "A1")
    name: str  # Pin name (e.g., "VCC", "GND", "CLK")
    position: Point  # Absolute position in schematic coordinates (mm)
    electrical_type: PinType = PinType.PASSIVE  # Electrical type (input, output, passive, etc.)
    shape: PinShape = PinShape.LINE  # Graphical shape (line, inverted, clock, etc.)
    length: float = 2.54  # Pin length in mm
    orientation: float = 0.0  # Pin orientation in degrees (0, 90, 180, 270)
    uuid: str = ""  # Unique identifier for this pin instance

    def __post_init__(self) -> None:
        """Validate and normalize pin information."""
        # Ensure types are correct
        self.electrical_type = (
            PinType(self.electrical_type)
            if isinstance(self.electrical_type, str)
            else self.electrical_type
        )
        self.shape = PinShape(self.shape) if isinstance(self.shape, str) else self.shape

        # Generate UUID if not provided
        if not self.uuid:
            self.uuid = str(uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert pin info to dictionary representation."""
        return {
            "number": self.number,
            "name": self.name,
            "position": {"x": self.position.x, "y": self.position.y},
            "electrical_type": self.electrical_type.value,
            "shape": self.shape.value,
            "length": self.length,
            "orientation": self.orientation,
            "uuid": self.uuid,
        }


@dataclass
class SchematicSymbol:
    """Component symbol in a schematic."""

    uuid: str
    lib_id: str  # e.g., "Device:R"
    position: Point
    reference: str  # e.g., "R1"
    value: str = ""
    footprint: Optional[str] = None
    properties: Dict[str, str] = field(default_factory=dict)
    pins: List[SchematicPin] = field(default_factory=list)
    pin_uuids: Dict[str, str] = field(default_factory=dict)  # Maps pin number to UUID
    hidden_properties: "set[str]" = field(default_factory=set)  # Properties with (hide yes) flag
    rotation: float = 0.0
    in_bom: bool = True
    on_board: bool = True
    fields_autoplaced: bool = False
    unit: int = 1
    instances: List["SymbolInstance"] = field(
        default_factory=list
    )  # FIX: Add instances field for hierarchical support

    def __post_init__(self) -> None:
        # Generate UUID if not provided
        if not self.uuid:
            self.uuid = str(uuid4())

    @property
    def library(self) -> str:
        """Extract library name from lib_id."""
        return self.lib_id.split(":")[0] if ":" in self.lib_id else ""

    @property
    def symbol_name(self) -> str:
        """Extract symbol name from lib_id."""
        return self.lib_id.split(":")[-1] if ":" in self.lib_id else self.lib_id

    def get_pin(self, pin_number: str) -> Optional[SchematicPin]:
        """Get pin by number."""
        for pin in self.pins:
            if pin.number == pin_number:
                return pin
        return None

    def get_pin_position(self, pin_number: str) -> Optional[Point]:
        """Get absolute position of a pin with rotation transformation.

        Args:
            pin_number: Pin number to get position for

        Returns:
            Absolute position of the pin in schematic coordinates, or None if pin not found

        Note:
            Applies standard 2D rotation matrix to transform pin position from
            symbol's local coordinate system to schematic's global coordinate system.
        """
        import math

        pin = self.get_pin(pin_number)
        if not pin:
            return None

        # Apply rotation transformation using standard 2D rotation matrix
        # [x'] = [cos(θ)  -sin(θ)] [x]
        # [y']   [sin(θ)   cos(θ)] [y]
        angle_rad = math.radians(self.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Rotate pin position from symbol's local coordinates
        rotated_x = pin.position.x * cos_a - pin.position.y * sin_a
        rotated_y = pin.position.x * sin_a + pin.position.y * cos_a

        # Add to component position to get absolute position
        return Point(self.position.x + rotated_x, self.position.y + rotated_y)

    def get_property_effects(self, property_name: str) -> Dict[str, Any]:
        """
        Get text effects for a component property.

        Extracts and parses the effects (font, position, rotation, color, etc.)
        from the property's S-expression.

        Args:
            property_name: Name of property ("Reference", "Value", "Footprint", etc.)

        Returns:
            Dictionary with effect properties:
            {
                'position': (x, y),
                'rotation': float,
                'font_face': str or None,
                'font_size': (height, width),
                'font_thickness': float or None,
                'bold': bool,
                'italic': bool,
                'color': (r, g, b, a) or None,
                'justify_h': str or None,
                'justify_v': str or None,
                'visible': bool,
            }

        Raises:
            ValueError: If property doesn't exist

        Example:
            >>> comp = sch.components[0]
            >>> effects = comp.get_property_effects("Reference")
            >>> print(effects['font_size'])
            (1.27, 1.27)
            >>> print(effects['bold'])
            False
        """
        from ..utils.text_effects import parse_effects_from_sexp

        # Check if property exists
        sexp_key = f"__sexp_{property_name}"
        if sexp_key not in self.properties:
            raise ValueError(
                f"Property '{property_name}' not found. "
                f"Available properties: {[k.replace('__sexp_', '') for k in self.properties.keys() if k.startswith('__sexp_')]}"
            )

        # Parse effects from preserved S-expression
        property_sexp = self.properties[sexp_key]
        return parse_effects_from_sexp(property_sexp)

    def set_property_effects(self, property_name: str, effects: Dict[str, Any]) -> None:
        """
        Set text effects for a component property.

        Modifies the property's text effects (font, position, rotation, color, etc.).
        Only specified effects are changed - others are preserved.

        Args:
            property_name: Name of property ("Reference", "Value", "Footprint", etc.)
            effects: Dictionary with effect properties to change:
                     {
                         'position': (x, y),           # Optional
                         'rotation': float,            # Optional
                         'font_face': str,             # Optional
                         'font_size': (h, w),          # Optional
                         'font_thickness': float,      # Optional
                         'bold': bool,                 # Optional
                         'italic': bool,               # Optional
                         'color': (r, g, b, a),        # Optional
                         'justify_h': str,             # Optional ('left', 'right', 'center')
                         'justify_v': str,             # Optional ('top', 'bottom')
                         'visible': bool,              # Optional
                     }

        Raises:
            ValueError: If property doesn't exist

        Example:
            >>> comp = sch.components[0]
            >>> # Make Reference bold and larger
            >>> comp.set_property_effects("Reference", {
            ...     'bold': True,
            ...     'font_size': (2.0, 2.0)
            ... })
            >>> # Hide Footprint
            >>> comp.set_property_effects("Footprint", {'visible': False})
        """
        from sexpdata import Symbol

        from ..utils.text_effects import (
            create_effects_sexp,
            merge_effects,
            parse_effects_from_sexp,
            update_property_sexp_with_effects,
        )

        # Check if property exists
        sexp_key = f"__sexp_{property_name}"

        # If S-expression doesn't exist, create a default one for standard properties
        if sexp_key not in self.properties:
            # Only allow standard properties (Reference, Value, Footprint)
            if property_name not in ["Reference", "Value", "Footprint"]:
                raise ValueError(
                    f"Property '{property_name}' not found. "
                    f"Can only set effects for standard properties (Reference, Value, Footprint) or existing custom properties."
                )

            # Get the property value
            prop_value = getattr(self, property_name.lower(), "")
            if prop_value is None:
                prop_value = ""

            # Create default S-expression structure
            # Format: (property "Name" "Value" (at x y rotation) (effects ...))
            property_sexp = [
                Symbol("property"),
                property_name,
                str(prop_value),
                [Symbol("at"), self.position.x, self.position.y, 0],
                create_effects_sexp({"font_size": (1.27, 1.27), "visible": True}),
            ]

            # Store it
            self.properties[sexp_key] = property_sexp

        # Get current effects
        property_sexp = self.properties[sexp_key]
        current_effects = parse_effects_from_sexp(property_sexp)

        # Merge with updates
        merged_effects = merge_effects(current_effects, effects)

        # Update S-expression with new effects
        updated_sexp = update_property_sexp_with_effects(property_sexp, merged_effects)

        # Store updated S-expression
        self.properties[sexp_key] = updated_sexp

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
        # Set property value
        self.properties[name] = value

        # Manage visibility
        if hidden:
            self.hidden_properties.add(name)
        else:
            self.hidden_properties.discard(name)

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
        # Update all property values
        self.properties.update(props)

        # Manage visibility for all properties
        if hidden:
            self.hidden_properties.update(props.keys())
        else:
            for name in props.keys():
                self.hidden_properties.discard(name)


class WireType(Enum):
    """Wire types in KiCAD schematics."""

    WIRE = "wire"
    BUS = "bus"


@dataclass
class Wire:
    """Wire connection in schematic."""

    uuid: str
    points: List[Point]  # Support for multi-point wires
    wire_type: WireType = WireType.WIRE
    stroke_width: float = 0.0
    stroke_type: str = "default"

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())

        self.wire_type = (
            WireType(self.wire_type) if isinstance(self.wire_type, str) else self.wire_type
        )

        # Ensure we have at least 2 points
        if len(self.points) < 2:
            raise ValueError("Wire must have at least 2 points")

    @classmethod
    def from_start_end(cls, uuid: str, start: Point, end: Point, **kwargs: Any) -> "Wire":
        """Create wire from start and end points (convenience method)."""
        return cls(uuid=uuid, points=[start, end], **kwargs)

    @property
    def start(self) -> Point:
        """First point of the wire."""
        return self.points[0]

    @property
    def end(self) -> Point:
        """Last point of the wire."""
        return self.points[-1]

    @property
    def length(self) -> float:
        """Total wire length (sum of all segments)."""
        total = 0.0
        for i in range(len(self.points) - 1):
            total += self.points[i].distance_to(self.points[i + 1])
        return total

    def is_simple(self) -> bool:
        """Check if wire is a simple 2-point wire."""
        return len(self.points) == 2

    def is_horizontal(self) -> bool:
        """Check if wire is horizontal (only for simple wires)."""
        if not self.is_simple():
            return False
        return abs(self.start.y - self.end.y) < 0.001

    def is_vertical(self) -> bool:
        """Check if wire is vertical (only for simple wires)."""
        if not self.is_simple():
            return False
        return abs(self.start.x - self.end.x) < 0.001


@dataclass
class BusEntry:
    """Bus entry point connecting individual wires to buses."""

    uuid: str
    position: Point
    size: Point = None  # Default size set in __post_init__
    rotation: int = 0  # 0, 90, 180, or 270 degrees
    stroke_width: float = 0.0
    stroke_type: str = "default"

    def __post_init__(self) -> None:
        """Initialize defaults and validate rotation."""
        if not self.uuid:
            self.uuid = str(uuid4())

        # Set default size (2.54mm = 100 mil = 0.1 inch)
        if self.size is None:
            self.size = Point(2.54, 2.54)

        # Validate rotation
        if self.rotation not in [0, 90, 180, 270]:
            raise ValueError(f"Bus entry rotation must be 0, 90, 180, or 270, got {self.rotation}")


@dataclass
class Junction:
    """Junction point where multiple wires meet."""

    uuid: str
    position: Point
    diameter: float = 0  # KiCAD default diameter
    color: Tuple[int, int, int, int] = (0, 0, 0, 0)  # RGBA color

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())


class LabelType(Enum):
    """Label types in KiCAD schematics."""

    LOCAL = "label"
    GLOBAL = "global_label"
    HIERARCHICAL = "hierarchical_label"


class HierarchicalLabelShape(Enum):
    """Hierarchical label shapes/directions."""

    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"
    TRISTATE = "tri_state"
    PASSIVE = "passive"
    UNSPECIFIED = "unspecified"


@dataclass
class Label:
    """Text label in schematic."""

    uuid: str
    position: Point
    text: str
    label_type: LabelType = LabelType.LOCAL
    rotation: float = 0.0
    size: float = 1.27
    shape: Optional[HierarchicalLabelShape] = None  # Only for hierarchical labels
    justify_h: str = "left"  # Horizontal justification: "left", "right", "center"
    justify_v: str = "bottom"  # Vertical justification: "top", "bottom", "center"

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())

        self.label_type = (
            LabelType(self.label_type) if isinstance(self.label_type, str) else self.label_type
        )

        if self.shape:
            self.shape = (
                HierarchicalLabelShape(self.shape) if isinstance(self.shape, str) else self.shape
            )


@dataclass
class Text:
    """Free text element in schematic."""

    uuid: str
    position: Point
    text: str
    rotation: float = 0.0
    size: float = 1.27
    exclude_from_sim: bool = False
    # Font effects (optional, for styling)
    bold: bool = False
    italic: bool = False
    thickness: Optional[float] = None  # Stroke width (None = use default)
    color: Optional[Tuple[int, int, int, float]] = None  # RGBA (None = use default)
    face: Optional[str] = None  # Font face name (None = use default)

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())


@dataclass
class TextBox:
    """Text box element with border in schematic."""

    uuid: str
    position: Point
    size: Point  # Width, height
    text: str
    rotation: float = 0.0
    font_size: float = 1.27
    margins: Tuple[float, float, float, float] = (
        0.9525,
        0.9525,
        0.9525,
        0.9525,
    )  # top, right, bottom, left
    stroke_width: float = 0.0
    stroke_type: str = "solid"
    fill_type: str = "none"
    justify_horizontal: str = "left"
    justify_vertical: str = "top"
    exclude_from_sim: bool = False

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())


@dataclass
class SchematicRectangle:
    """Graphical rectangle element in schematic."""

    uuid: str
    start: Point
    end: Point
    stroke_width: float = 0.0
    stroke_type: str = "default"
    fill_type: str = "none"

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())

    @property
    def width(self) -> float:
        """Rectangle width."""
        return abs(self.end.x - self.start.x)

    @property
    def height(self) -> float:
        """Rectangle height."""
        return abs(self.end.y - self.start.y)

    @property
    def center(self) -> Point:
        """Rectangle center point."""
        return Point((self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2)


@dataclass
class Image:
    """Image element in schematic."""

    uuid: str
    position: Point
    data: str  # Base64-encoded image data
    scale: float = 1.0

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())


@dataclass
class NoConnect:
    """No-connect symbol in schematic."""

    uuid: str
    position: Point

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())


@dataclass
class Net:
    """Electrical net connecting components."""

    name: str
    components: List[Tuple[str, str]] = field(default_factory=list)  # (reference, pin) tuples
    wires: List[str] = field(default_factory=list)  # Wire UUIDs
    labels: List[str] = field(default_factory=list)  # Label UUIDs

    def add_connection(self, reference: str, pin: str) -> None:
        """Add component pin to net."""
        connection = (reference, pin)
        if connection not in self.components:
            self.components.append(connection)

    def remove_connection(self, reference: str, pin: str) -> None:
        """Remove component pin from net."""
        connection = (reference, pin)
        if connection in self.components:
            self.components.remove(connection)


@dataclass
class Sheet:
    """Hierarchical sheet in schematic."""

    uuid: str
    position: Point
    size: Point  # Width, height
    name: str
    filename: str
    pins: List["SheetPin"] = field(default_factory=list)
    exclude_from_sim: bool = False
    in_bom: bool = True
    on_board: bool = True
    dnp: bool = False
    fields_autoplaced: bool = True
    stroke_width: float = 0.1524
    stroke_type: str = "solid"
    fill_color: Tuple[float, float, float, float] = (0, 0, 0, 0.0)

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())


@dataclass
class SheetPin:
    """Pin on hierarchical sheet."""

    uuid: str
    name: str
    position: Point
    pin_type: PinType = PinType.BIDIRECTIONAL
    size: float = 1.27

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())


@dataclass
class SymbolInstance:
    """Instance of a symbol from library."""

    path: str  # Hierarchical path
    reference: str
    unit: int = 1
    project: str = ""  # Project name (empty string for unnamed projects)


@dataclass
class TitleBlock:
    """Title block information."""

    title: str = ""
    company: str = ""
    rev: str = ""  # KiCAD uses "rev" not "revision"
    date: str = ""
    size: str = "A4"
    comments: Dict[int, str] = field(default_factory=dict)


@dataclass
class Schematic:
    """Complete schematic data structure."""

    version: Optional[str] = None
    generator: Optional[str] = None
    uuid: Optional[str] = None
    title_block: TitleBlock = field(default_factory=TitleBlock)
    components: List[SchematicSymbol] = field(default_factory=list)
    wires: List[Wire] = field(default_factory=list)
    junctions: List[Junction] = field(default_factory=list)
    labels: List[Label] = field(default_factory=list)
    nets: List[Net] = field(default_factory=list)
    sheets: List[Sheet] = field(default_factory=list)
    rectangles: List[SchematicRectangle] = field(default_factory=list)
    lib_symbols: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.uuid:
            self.uuid = str(uuid4())

    def get_component(self, reference: str) -> Optional[SchematicSymbol]:
        """Get component by reference."""
        for component in self.components:
            if component.reference == reference:
                return component
        return None

    def get_net(self, name: str) -> Optional[Net]:
        """Get net by name."""
        for net in self.nets:
            if net.name == name:
                return net
        return None

    def component_count(self) -> int:
        """Get total number of components."""
        return len(self.components)

    def connection_count(self) -> int:
        """Get total number of connections (wires + net connections)."""
        return len(self.wires) + sum(len(net.components) for net in self.nets)


@dataclass
class SymbolInfo:
    """
    Symbol metadata from library cache for multi-unit component introspection.

    Used by get_symbol_info() to query unit count, names, and other metadata
    before adding components programmatically.
    """

    lib_id: str  # e.g., "Amplifier_Operational:TL072"
    name: str  # Symbol name within library
    library: str  # Library name (e.g., "Amplifier_Operational")
    reference_prefix: str  # e.g., "U" for ICs, "R" for resistors
    description: str  # Symbol description
    keywords: str  # Search keywords
    datasheet: str  # Datasheet URL
    unit_count: int  # Number of units (1 for single-unit, 3 for TL072, 5 for TL074)
    unit_names: Dict[int, str]  # Maps unit number to name (e.g., {1: "A", 2: "B", 3: "C"})
    pins: List[SchematicPin]  # All pins across all units
    power_symbol: bool  # True if this is a power symbol


# Type aliases for convenience
ComponentDict = Dict[str, Any]  # Raw component data from parser
WireDict = Dict[str, Any]  # Raw wire data from parser
SchematicDict = Dict[str, Any]  # Raw schematic data from parser
