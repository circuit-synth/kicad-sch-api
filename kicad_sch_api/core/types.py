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
    position: Union[Point, Dict[str, float], Tuple[float, float], List[float], Any]
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
class PropertyEffects:
    """
    Font and formatting effects for a component property.

    Represents the (effects ...) section of a KiCad property S-expression.
    """

    font_size: Tuple[float, float] = (1.27, 1.27)  # (width, height)
    justification: Optional[str] = None  # "left"|"right"|"center"|None
    hide: bool = False

    def to_sexp(self) -> List:
        """
        Convert to S-expression: (effects ...)

        Returns:
            S-expression list representing the effects
        """
        import sexpdata

        effects = [sexpdata.Symbol("effects")]

        # Font
        effects.append([
            sexpdata.Symbol("font"),
            [sexpdata.Symbol("size"), self.font_size[0], self.font_size[1]]
        ])

        # Justification (optional)
        if self.justification:
            effects.append([
                sexpdata.Symbol("justify"),
                sexpdata.Symbol(self.justification)
            ])

        # Hide flag (optional)
        if self.hide:
            effects.append([
                sexpdata.Symbol("hide"),
                sexpdata.Symbol("yes")
            ])

        return effects


@dataclass
class ComponentProperty:
    """
    A component property with complete formatting data.

    Represents a complete property S-expression:
    (property "Name" "Value" (at x y rotation) (effects ...))

    This captures all KiCad property attributes including position, rotation,
    font size, justification, and visibility flags.
    """

    name: str
    value: str
    position: Optional[Tuple[float, float]] = None  # (x, y) - None = use defaults
    rotation: float = 0.0  # degrees
    effects: PropertyEffects = field(default_factory=PropertyEffects)

    def to_sexp(self) -> List:
        """
        Convert to complete S-expression.

        Returns:
            S-expression list representing the complete property
        """
        import sexpdata

        sexp = [
            sexpdata.Symbol("property"),
            self.name,
            self.value,
        ]

        # Position (required in KiCad files)
        if self.position:
            x, y = self.position
            # Format as int if whole number
            x = int(x) if x == int(x) else x
            y = int(y) if y == int(y) else y
            r = int(self.rotation) if self.rotation == int(self.rotation) else self.rotation
            sexp.append([sexpdata.Symbol("at"), x, y, r])

        # Effects
        sexp.append(self.effects.to_sexp())

        return sexp


class SchematicSymbol:
    """
    Component symbol in a schematic.

    Note: This class provides backward compatibility for old-style initialization
    with reference/value/footprint as strings, while internally using property objects.
    """

    def __init__(
        self,
        uuid: str,
        lib_id: str,
        position: Point,
        reference_property: Optional[ComponentProperty] = None,
        value_property: Optional[ComponentProperty] = None,
        footprint_property: Optional[ComponentProperty] = None,
        custom_properties: Optional[Dict[str, ComponentProperty]] = None,
        pins: Optional[List[SchematicPin]] = None,
        rotation: float = 0.0,
        in_bom: bool = True,
        on_board: bool = True,
        unit: int = 1,
        # Backward compatibility: accept old-style string parameters
        reference: Optional[str] = None,
        value: Optional[str] = None,
        footprint: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
    ):
        """Initialize SchematicSymbol with property objects or legacy strings."""
        self.uuid = uuid or str(uuid4())
        self.lib_id = lib_id
        self.position = position
        self.pins = pins or []
        self.rotation = rotation
        self.in_bom = in_bom
        self.on_board = on_board
        self.unit = unit

        # Handle property objects vs legacy strings
        # Priority: property objects > legacy string parameters

        # Reference
        if reference_property:
            self.reference_property = reference_property
        elif reference:
            self.reference_property = ComponentProperty("Reference", reference)
        else:
            self.reference_property = None

        # Value
        if value_property:
            self.value_property = value_property
        elif value:
            self.value_property = ComponentProperty("Value", value)
        else:
            self.value_property = None

        # Footprint
        if footprint_property:
            self.footprint_property = footprint_property
        elif footprint:
            self.footprint_property = ComponentProperty(
                "Footprint", footprint, effects=PropertyEffects(hide=True)
            )
        else:
            self.footprint_property = None

        # Custom properties
        if custom_properties:
            self.custom_properties = custom_properties
        elif properties:
            # Convert legacy properties dict to ComponentProperty objects
            self.custom_properties = {
                name: ComponentProperty(name, val, effects=PropertyEffects(hide=True))
                for name, val in properties.items()
            }
        else:
            self.custom_properties = {}

    @property
    def reference(self) -> str:
        """Get reference value (backward compatible)."""
        return self.reference_property.value if self.reference_property else ""

    @reference.setter
    def reference(self, value: str) -> None:
        """Set reference value, preserving formatting."""
        if self.reference_property:
            self.reference_property.value = value
        else:
            # Create new property with defaults
            self.reference_property = ComponentProperty("Reference", value)

    @property
    def value(self) -> str:
        """Get value (backward compatible)."""
        return self.value_property.value if self.value_property else ""

    @value.setter
    def value(self, value: str) -> None:
        """Set value, preserving formatting."""
        if self.value_property:
            self.value_property.value = value
        else:
            self.value_property = ComponentProperty("Value", value)

    @property
    def footprint(self) -> Optional[str]:
        """Get footprint value (backward compatible)."""
        return self.footprint_property.value if self.footprint_property else None

    @footprint.setter
    def footprint(self, value: Optional[str]) -> None:
        """Set footprint value, preserving formatting."""
        if value is None:
            self.footprint_property = None
        elif self.footprint_property:
            self.footprint_property.value = value
        else:
            # Footprint defaults to hidden
            self.footprint_property = ComponentProperty(
                "Footprint",
                value,
                effects=PropertyEffects(hide=True)
            )

    @property
    def properties(self) -> Dict[str, str]:
        """Get custom property values (backward compatible)."""
        return {name: prop.value for name, prop in self.custom_properties.items()}

    def set_property(self, name: str, value: str) -> None:
        """Set a custom property value (backward compatible)."""
        if name in self.custom_properties:
            self.custom_properties[name].value = value
        else:
            self.custom_properties[name] = ComponentProperty(
                name, value, effects=PropertyEffects(hide=True)
            )

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
        """Get absolute position of a pin."""
        pin = self.get_pin(pin_number)
        if not pin:
            return None
        # TODO: Apply rotation and symbol position transformation
        # NOTE: Currently assumes 0° rotation. For rotated components, pin positions
        # would need to be transformed using rotation matrix before adding to component position.
        # This affects pin-to-pin wiring accuracy for rotated components.
        # Priority: MEDIUM - Would improve wiring accuracy for rotated components
        return Point(self.position.x + pin.position.x, self.position.y + pin.position.y)


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


# Type aliases for convenience
ComponentDict = Dict[str, Any]  # Raw component data from parser
WireDict = Dict[str, Any]  # Raw wire data from parser
SchematicDict = Dict[str, Any]  # Raw schematic data from parser
