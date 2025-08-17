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

    def __post_init__(self):
        # Ensure coordinates are float
        object.__setattr__(self, "x", float(self.x))
        object.__setattr__(self, "y", float(self.y))

    def distance_to(self, other: "Point") -> float:
        """Calculate distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def offset(self, dx: float, dy: float) -> "Point":
        """Create new point offset by dx, dy."""
        return Point(self.x + dx, self.y + dy)

    def __str__(self) -> str:
        return f"({self.x:.3f}, {self.y:.3f})"


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

    def __post_init__(self):
        # Ensure types are correct
        self.pin_type = PinType(self.pin_type) if isinstance(self.pin_type, str) else self.pin_type
        self.pin_shape = (
            PinShape(self.pin_shape) if isinstance(self.pin_shape, str) else self.pin_shape
        )


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
    rotation: float = 0.0
    in_bom: bool = True
    on_board: bool = True
    unit: int = 1

    def __post_init__(self):
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
        """Get absolute position of a pin."""
        pin = self.get_pin(pin_number)
        if not pin:
            return None
        # TODO: Apply rotation and symbol position transformation
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

    def __post_init__(self):
        if not self.uuid:
            self.uuid = str(uuid4())

        self.wire_type = (
            WireType(self.wire_type) if isinstance(self.wire_type, str) else self.wire_type
        )
        
        # Ensure we have at least 2 points
        if len(self.points) < 2:
            raise ValueError("Wire must have at least 2 points")

    @classmethod
    def from_start_end(cls, uuid: str, start: Point, end: Point, **kwargs) -> "Wire":
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

    def __post_init__(self):
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

    def __post_init__(self):
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
class Net:
    """Electrical net connecting components."""

    name: str
    components: List[Tuple[str, str]] = field(default_factory=list)  # (reference, pin) tuples
    wires: List[str] = field(default_factory=list)  # Wire UUIDs
    labels: List[str] = field(default_factory=list)  # Label UUIDs

    def add_connection(self, reference: str, pin: str):
        """Add component pin to net."""
        connection = (reference, pin)
        if connection not in self.components:
            self.components.append(connection)

    def remove_connection(self, reference: str, pin: str):
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

    def __post_init__(self):
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

    def __post_init__(self):
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
    revision: str = ""
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
    lib_symbols: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
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
