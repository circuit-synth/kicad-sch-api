# Pin Connection Features - Detailed Code Structure Design

## Executive Summary

This document provides a comprehensive design for implementing three interconnected tracks for pin connection functionality in kicad-sch-api:

- **Track A (Pin Discovery)**: Query pins from components and retrieve detailed pin information
- **Track B (Wire Routing)**: Route wires between pins with automatic junction detection and grid snapping
- **Track C (Testing)**: Comprehensive test fixtures and validation patterns

This design maintains the library's core principles:
- Exact format preservation
- High performance through caching and indexing
- Professional error handling
- Clear separation of concerns
- Testability and dependency injection

---

## Part 1: Track A - Pin Discovery

### 1.1 Module Organization

**Location**: `/kicad_sch_api/pins/` (new module)

```
pins/
├── __init__.py
├── models.py          # PinInfo dataclass and related types
├── discovery.py       # PIN_DISCOVERER service for querying pins
├── validator.py       # Pin validation logic
└── errors.py          # Pin-specific exceptions
```

### 1.2 Core Data Structures

#### File: `pins/models.py`

```python
"""Pin discovery data models and types."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Tuple
from ..core.types import Point


class PinType(Enum):
    """KiCAD pin types from symbol definitions."""
    INPUT = "input"
    OUTPUT = "output"
    BIDIR = "bidir"  # Bidirectional
    TRISTATE = "tri_state"
    PASSIVE = "passive"
    POWER = "power"
    GROUND = "ground"
    UNSPECIFIED = "unspecified"


class PinShape(Enum):
    """KiCAD pin shapes."""
    CIRCLE = "circle"
    INVERTED = "inverted"
    CLOCK = "clock"
    INVERTED_CLOCK = "inverted_clock"
    INPUT_LOW = "input_low"
    CLOCK_LOW = "clock_low"
    OUTPUT_LOW = "output_low"
    EDGE_CLOCK_HIGH = "edge_clock_high"
    NON_LOGIC = "non_logic"


@dataclass(frozen=True)
class PinInfo:
    """
    Complete information about a component pin.

    This dataclass represents both library definition and schematic placement.
    Properties are immutable for safety in cached lookups.
    """
    # Identification
    component_reference: str      # e.g., "R1"
    pin_number: str               # e.g., "1", "2", "A1"
    pin_name: Optional[str]       # e.g., "GND", "VCC" (from symbol)

    # Position (in schematic space)
    position: Point               # Absolute position where pin connects

    # Type information from symbol library
    pin_type: PinType             # INPUT, OUTPUT, etc.
    pin_shape: PinShape           # CIRCLE, INVERTED, etc.

    # Symbol definition source
    lib_id: str                   # e.g., "Device:R"

    # Symbol library position (for reference)
    symbol_relative_position: Point  # Position in symbol coordinate system

    # Component transformation applied
    component_position: Point
    component_rotation: float     # 0, 90, 180, 270
    component_mirror: Optional[str]  # "x", "y", or None

    # Connectivity information
    connected_wires: List[str]    # Wire UUIDs connected to this pin
    connected_label: Optional[str] # Label UUID if labeled

    # Metadata
    length: float = 0.0           # Pin length in mm (from symbol)

    def __str__(self) -> str:
        """String representation for logging."""
        return f"Pin({self.component_reference}.{self.pin_number} @ {self.position})"

    def __repr__(self) -> str:
        return (f"PinInfo(ref={self.component_reference}, pin={self.pin_number}, "
                f"type={self.pin_type.value}, pos=({self.position.x:.2f}, {self.position.y:.2f}))")


@dataclass
class PinMatchResult:
    """Result of searching/matching pins."""
    found: bool                      # Whether pin was found
    pin_info: Optional[PinInfo]     # The pin info if found
    candidates: List[PinInfo]       # Candidate matches if ambiguous
    error_message: Optional[str]    # Error description if not found


@dataclass
class ComponentPins:
    """All pins for a component with lookup indices."""
    component_reference: str
    lib_id: str
    pins_by_number: dict[str, PinInfo]  # Number -> PinInfo
    pins_by_name: dict[str, PinInfo]    # Name -> PinInfo (for named pins)

    def get_pin(self, identifier: str) -> Optional[PinInfo]:
        """Get pin by number or name."""
        # Try by number first
        if identifier in self.pins_by_number:
            return self.pins_by_number[identifier]
        # Try by name
        return self.pins_by_name.get(identifier)

    def all_pins(self) -> List[PinInfo]:
        """Get all pins in order of pin number."""
        return sorted(
            self.pins_by_number.values(),
            key=lambda p: int(p.pin_number) if p.pin_number.isdigit() else float('inf')
        )
```

### 1.3 Pin Discovery Service

#### File: `pins/discovery.py`

```python
"""Pin discovery service for querying component pins."""

import logging
from typing import List, Optional, Dict
from dataclasses import asdict

from ..core.types import Point, SchematicSymbol
from ..library.cache import get_symbol_cache, SymbolDefinition
from ..core.pin_utils import list_component_pins, get_component_pin_position
from ..core.geometry import points_equal
from .models import PinInfo, PinType, PinShape, PinMatchResult, ComponentPins
from .errors import PinNotFoundError, AmbiguousPinError, SymbolLibraryError


logger = logging.getLogger(__name__)


class PinDiscovery:
    """
    Service for discovering and retrieving pin information from components.

    Integrates with symbol library cache for efficient lookups.
    Handles both component-specific pins and symbol library definitions.

    Features:
    - Get pins for a component with absolute positions
    - Search pins by number, name, or position
    - Retrieve pin type and electrical properties
    - Find connected elements (wires, labels)
    """

    def __init__(self, schematic: 'Schematic', cache_enabled: bool = True):
        """
        Initialize pin discovery service.

        Args:
            schematic: Parent schematic for context
            cache_enabled: Enable caching of pin info lookups
        """
        self._schematic = schematic
        self._cache_enabled = cache_enabled
        self._pin_cache: Dict[str, PinInfo] = {}  # UUID/reference -> PinInfo
        self._component_pins_cache: Dict[str, ComponentPins] = {}
        self._symbol_cache = get_symbol_cache()
        logger.debug(f"Initialized PinDiscovery (cache={cache_enabled})")

    def get_pins_info(self, component_reference: str) -> ComponentPins:
        """
        Get complete pin information for a component.

        This is the PRIMARY entry point for pin discovery.
        Returns all pins with absolute positions and symbol information.

        Args:
            component_reference: Component reference (e.g., "R1", "U1")

        Returns:
            ComponentPins with all pins indexed by number and name

        Raises:
            PinNotFoundError: If component not found
            SymbolLibraryError: If symbol library lookup fails

        Example:
            >>> discovery = PinDiscovery(schematic)
            >>> pins = discovery.get_pins_info("U1")
            >>> pin_1 = pins.get_pin("1")
            >>> print(pin_1.position)
            (100.5, 50.2)
        """
        # Check cache first
        if self._cache_enabled and component_reference in self._component_pins_cache:
            logger.debug(f"Cache hit for {component_reference}")
            return self._component_pins_cache[component_reference]

        # Get component from schematic
        component = self._schematic.components.get(component_reference)
        if component is None:
            raise PinNotFoundError(
                f"Component '{component_reference}' not found in schematic",
                component_ref=component_reference
            )

        logger.info(f"Getting pin info for {component_reference} ({component.lib_id})")

        # Get component's symbol data
        component_data = component._data  # Access underlying SchematicSymbol

        # Get all pins with positions
        pin_list = list_component_pins(component_data)

        # Enhance with symbol library information
        symbol_def = self._get_symbol_definition(component.lib_id)

        pins_by_number = {}
        pins_by_name = {}

        for pin_number, absolute_pos in pin_list:
            # Find corresponding symbol pin definition
            symbol_pin = self._find_symbol_pin(symbol_def, pin_number)

            pin_info = PinInfo(
                component_reference=component_reference,
                pin_number=pin_number,
                pin_name=symbol_pin.name if symbol_pin else None,
                position=absolute_pos,
                pin_type=self._parse_pin_type(symbol_pin.type if symbol_pin else "unspecified"),
                pin_shape=self._parse_pin_shape(symbol_pin.shape if symbol_pin else None),
                lib_id=component.lib_id,
                symbol_relative_position=Point(
                    symbol_pin.position.x if symbol_pin else 0,
                    symbol_pin.position.y if symbol_pin else 0
                ),
                component_position=component_data.position,
                component_rotation=getattr(component_data, 'rotation', 0),
                component_mirror=getattr(component_data, 'mirror', None),
                connected_wires=self._find_connected_wires(absolute_pos),
                connected_label=self._find_connected_label(absolute_pos),
                length=symbol_pin.length if symbol_pin else 0.0
            )

            pins_by_number[pin_number] = pin_info
            if pin_info.pin_name:
                pins_by_name[pin_info.pin_name] = pin_info

        result = ComponentPins(
            component_reference=component_reference,
            lib_id=component.lib_id,
            pins_by_number=pins_by_number,
            pins_by_name=pins_by_name
        )

        # Cache result
        if self._cache_enabled:
            self._component_pins_cache[component_reference] = result

        logger.info(f"Found {len(pins_by_number)} pins for {component_reference}")
        return result

    def find_pins_by_name(self, pin_name: str) -> List[PinInfo]:
        """
        Find all pins matching a specific name across all components.

        Useful for finding power pins (VCC, GND) or named signal pins.

        Args:
            pin_name: Pin name to search for (e.g., "GND", "VCC")

        Returns:
            List of matching PinInfo objects

        Example:
            >>> discovery = PinDiscovery(schematic)
            >>> gnd_pins = discovery.find_pins_by_name("GND")
            >>> for pin in gnd_pins:
            ...     print(f"{pin.component_reference}: {pin.position}")
        """
        logger.info(f"Searching for pins named '{pin_name}'")
        results = []

        for component in self._schematic.components:
            try:
                component_pins = self.get_pins_info(component.reference)
                if pin_name in component_pins.pins_by_name:
                    results.append(component_pins.pins_by_name[pin_name])
            except PinNotFoundError:
                # Component pins couldn't be determined, skip
                continue

        logger.info(f"Found {len(results)} pins named '{pin_name}'")
        return results

    def find_pins_by_number(self, component_reference: str, pin_numbers: List[str]) -> Dict[str, PinInfo]:
        """
        Find multiple pins by number for a component.

        Args:
            component_reference: Component to search
            pin_numbers: List of pin numbers to find

        Returns:
            Dictionary mapping pin number -> PinInfo (only includes found pins)

        Raises:
            PinNotFoundError: If component not found

        Example:
            >>> pins = discovery.find_pins_by_number("U1", ["1", "8", "14"])
            >>> pin_1 = pins["1"]  # May raise KeyError if pin not found
        """
        component_pins = self.get_pins_info(component_reference)

        found = {}
        for pin_num in pin_numbers:
            if pin_num in component_pins.pins_by_number:
                found[pin_num] = component_pins.pins_by_number[pin_num]

        return found

    def find_pin_by_position(
        self,
        position: Point,
        tolerance: float = 0.01
    ) -> Optional[PinInfo]:
        """
        Find pin at or near a position.

        Useful for finding what pin is at a wire endpoint.

        Args:
            position: Position to search
            tolerance: Distance tolerance in mm

        Returns:
            PinInfo if found, None otherwise

        Example:
            >>> pin = discovery.find_pin_by_position(Point(100.5, 50.2))
            >>> if pin:
            ...     print(f"Found pin at position: {pin}")
        """
        best_match = None
        best_distance = tolerance

        for component in self._schematic.components:
            try:
                component_pins = self.get_pins_info(component.reference)
                for pin in component_pins.all_pins():
                    distance = pin.position.distance_to(position)
                    if distance < best_distance:
                        best_match = pin
                        best_distance = distance
            except PinNotFoundError:
                continue

        return best_match

    def match_pin(self, component_reference: str, pin_identifier: str) -> PinMatchResult:
        """
        Find a pin with detailed match results and diagnostics.

        PRIMARY method for resolving pin references with error details.
        Handles both numeric and named pins with helpful error messages.

        Args:
            component_reference: Component reference (e.g., "R1")
            pin_identifier: Pin number or name (e.g., "1", "GND")

        Returns:
            PinMatchResult with found flag, pin info, and candidates

        Example:
            >>> result = discovery.match_pin("U1", "1")
            >>> if result.found:
            ...     print(f"Pin position: {result.pin_info.position}")
            >>> else:
            ...     print(f"Error: {result.error_message}")
            ...     print(f"Did you mean: {result.candidates}")
        """
        try:
            component_pins = self.get_pins_info(component_reference)
        except PinNotFoundError as e:
            return PinMatchResult(
                found=False,
                pin_info=None,
                candidates=[],
                error_message=str(e)
            )

        # Try exact match
        pin = component_pins.get_pin(pin_identifier)
        if pin:
            return PinMatchResult(
                found=True,
                pin_info=pin,
                candidates=[],
                error_message=None
            )

        # Provide helpful error with candidates
        candidates = component_pins.all_pins()
        error = f"Pin '{pin_identifier}' not found in {component_reference}"

        return PinMatchResult(
            found=False,
            pin_info=None,
            candidates=candidates,
            error_message=error
        )

    def clear_cache(self) -> None:
        """Clear all cached pin information."""
        self._pin_cache.clear()
        self._component_pins_cache.clear()
        logger.debug("Cleared pin discovery cache")

    # Private helper methods

    def _get_symbol_definition(self, lib_id: str) -> Optional[SymbolDefinition]:
        """Get symbol definition from library cache."""
        try:
            return self._symbol_cache.get_symbol(lib_id)
        except Exception as e:
            logger.warning(f"Failed to get symbol definition for {lib_id}: {e}")
            return None

    def _find_symbol_pin(
        self,
        symbol_def: Optional[SymbolDefinition],
        pin_number: str
    ) -> Optional['SchematicPin']:
        """Find a pin in symbol definition by number."""
        if not symbol_def:
            return None

        for pin in symbol_def.pins:
            if pin.number == pin_number:
                return pin

        return None

    def _parse_pin_type(self, type_str: str) -> PinType:
        """Convert symbol pin type string to PinType enum."""
        type_map = {
            "input": PinType.INPUT,
            "output": PinType.OUTPUT,
            "bidir": PinType.BIDIR,
            "tri_state": PinType.TRISTATE,
            "passive": PinType.PASSIVE,
            "power": PinType.POWER,
            "unspecified": PinType.UNSPECIFIED,
        }
        return type_map.get(type_str.lower(), PinType.UNSPECIFIED)

    def _parse_pin_shape(self, shape_str: Optional[str]) -> PinShape:
        """Convert symbol pin shape string to PinShape enum."""
        if not shape_str:
            return PinShape.CIRCLE

        shape_map = {
            "circle": PinShape.CIRCLE,
            "inverted": PinShape.INVERTED,
            "clock": PinShape.CLOCK,
            "inverted_clock": PinShape.INVERTED_CLOCK,
            "input_low": PinShape.INPUT_LOW,
            "clock_low": PinShape.CLOCK_LOW,
            "output_low": PinShape.OUTPUT_LOW,
            "edge_clock_high": PinShape.EDGE_CLOCK_HIGH,
            "non_logic": PinShape.NON_LOGIC,
        }
        return shape_map.get(shape_str.lower(), PinShape.CIRCLE)

    def _find_connected_wires(self, pin_position: Point) -> List[str]:
        """Find wires connected to a pin position."""
        connected = []
        tolerance = 0.01

        for wire in self._schematic.wires:
            # Check wire endpoints and points
            for point in wire.points:
                if point.distance_to(pin_position) < tolerance:
                    connected.append(wire.uuid)
                    break

        return connected

    def _find_connected_label(self, pin_position: Point) -> Optional[str]:
        """Find label at or near a pin position."""
        tolerance = 0.01

        for label in self._schematic.labels:
            if label.position.distance_to(pin_position) < tolerance:
                return label.uuid

        return None
```

### 1.4 Pin-Specific Errors

#### File: `pins/errors.py`

```python
"""Pin discovery specific exceptions."""

from ..core.exceptions import KiCadSchError


class PinError(KiCadSchError):
    """Base exception for pin-related errors."""
    pass


class PinNotFoundError(PinError):
    """Raised when a pin cannot be found."""

    def __init__(
        self,
        message: str,
        component_ref: str = "",
        pin_identifier: str = "",
    ):
        self.component_ref = component_ref
        self.pin_identifier = pin_identifier
        super().__init__(message)


class AmbiguousPinError(PinError):
    """Raised when pin reference is ambiguous."""

    def __init__(self, message: str, candidates: List['PinInfo']):
        self.candidates = candidates
        super().__init__(message)


class SymbolLibraryError(PinError):
    """Raised when symbol library lookup fails."""

    def __init__(self, message: str, lib_id: str = ""):
        self.lib_id = lib_id
        super().__init__(message)
```

### 1.5 Module Init and Exports

#### File: `pins/__init__.py`

```python
"""Pin discovery and management module."""

from .models import (
    PinInfo,
    PinType,
    PinShape,
    PinMatchResult,
    ComponentPins,
)
from .discovery import PinDiscovery
from .errors import PinError, PinNotFoundError, AmbiguousPinError, SymbolLibraryError

__all__ = [
    "PinInfo",
    "PinType",
    "PinShape",
    "PinMatchResult",
    "ComponentPins",
    "PinDiscovery",
    "PinError",
    "PinNotFoundError",
    "AmbiguousPinError",
    "SymbolLibraryError",
]
```

---

## Part 2: Track B - Wire Routing

### 2.1 Module Organization

**Location**: `/kicad_sch_api/routing/` (new module)

```
routing/
├── __init__.py
├── models.py          # ConnectionResult, RoutingPath dataclasses
├── router.py          # WireRouter service for routing between pins
├── junction_detector.py  # Junction detection and creation logic
├── grid.py            # Grid snapping utilities
└── errors.py          # Routing-specific exceptions
```

### 2.2 Core Data Structures

#### File: `routing/models.py`

```python
"""Wire routing data models."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from ..core.types import Point, Wire


class RoutingAlgorithm(Enum):
    """Routing algorithm selection."""
    MANHATTAN = "manhattan"    # L-shaped routing (horizontal then vertical)
    DIRECT = "direct"          # Straight line (for validation)
    ORTHOGONAL = "orthogonal"  # Orthogonal with multiple segments


class RoutingStyle(Enum):
    """Visual routing style."""
    WIRE = "wire"              # Standard wire
    BUS = "bus"                # Bus line


@dataclass
class RoutingPath:
    """
    Path for routing a wire.

    Represents the route from start point to end point,
    including intermediate waypoints and junction points.
    """
    start_point: Point
    end_point: Point
    waypoints: List[Point] = field(default_factory=list)  # Intermediate points
    junction_points: List[Point] = field(default_factory=list)  # Points needing junctions

    def all_points(self) -> List[Point]:
        """Get all points in order: start + waypoints + end."""
        points = [self.start_point]
        points.extend(self.waypoints)
        points.append(self.end_point)
        return points

    def segment_count(self) -> int:
        """Number of line segments."""
        return len(self.all_points()) - 1


@dataclass
class ConnectionResult:
    """
    Result of a wire connection operation.

    PRIMARY data structure returned by routing operations.
    Contains complete information about the connection,
    including created wires and junctions.
    """
    # Connection status
    success: bool

    # Wire information
    wire_uuid: Optional[str] = None      # UUID of created wire
    wire_points: List[Point] = field(default_factory=list)  # Wire path points

    # Junction information
    junctions_created: List[str] = field(default_factory=list)  # Junction UUIDs
    junction_positions: List[Point] = field(default_factory=list)  # Junction positions

    # Routing details
    algorithm_used: Optional[RoutingAlgorithm] = None
    path: Optional[RoutingPath] = None

    # Connectivity
    from_pin_ref: Optional[str] = None   # Source component reference
    from_pin_num: Optional[str] = None   # Source pin number
    to_pin_ref: Optional[str] = None     # Destination component reference
    to_pin_num: Optional[str] = None     # Destination pin number

    # Diagnostics
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def __str__(self) -> str:
        """String representation."""
        if self.success:
            return f"ConnectionResult(wire={self.wire_uuid}, junctions={len(self.junctions_created)})"
        else:
            return f"ConnectionResult(FAILED: {self.error_message})"


@dataclass
class RoutingOptions:
    """Configuration options for wire routing."""

    algorithm: RoutingAlgorithm = RoutingAlgorithm.MANHATTAN
    style: RoutingStyle = RoutingStyle.WIRE
    snap_to_grid: bool = True
    grid_size: float = 2.54  # KiCAD default: 2.54mm (0.1 inch)

    # Junction creation
    auto_create_junctions: bool = True
    junction_tolerance: float = 0.01  # mm

    # Validation
    validate_connectivity: bool = True
    warn_on_crossings: bool = False

    # Performance
    use_cache: bool = True


@dataclass
class JunctionCandidate:
    """A potential junction point to create."""
    position: Point
    reason: str  # Why a junction should be created
    confidence: float  # 0.0 to 1.0
```

### 2.3 Wire Routing Service

#### File: `routing/router.py`

```python
"""Wire routing service for creating connections between pins."""

import logging
from typing import Optional, List, Tuple

from ..core.types import Point, Wire, WireType, Junction
from ..pins.models import PinInfo
from ..pins.discovery import PinDiscovery
from .models import (
    ConnectionResult,
    RoutingPath,
    RoutingAlgorithm,
    RoutingOptions,
    JunctionCandidate,
)
from .junction_detector import JunctionDetector
from .grid import GridSnapping
from .errors import RoutingError, NoPathError, PinConnectionError


logger = logging.getLogger(__name__)


class WireRouter:
    """
    Service for routing wires between pins.

    Handles:
    - Path calculation (Manhattan, orthogonal, direct)
    - Grid snapping
    - Junction detection and creation
    - Validation

    Features:
    - Automatic junction detection at intersections
    - Grid alignment for professional schematics
    - Comprehensive routing options
    - Detailed result reporting
    """

    def __init__(
        self,
        schematic: 'Schematic',
        pin_discovery: Optional[PinDiscovery] = None,
        options: Optional[RoutingOptions] = None,
    ):
        """
        Initialize wire router.

        Args:
            schematic: Parent schematic
            pin_discovery: Pin discovery service (created if not provided)
            options: Routing options (uses defaults if not provided)
        """
        self._schematic = schematic
        self._pin_discovery = pin_discovery or PinDiscovery(schematic)
        self._options = options or RoutingOptions()
        self._junction_detector = JunctionDetector(schematic, self._options.junction_tolerance)
        self._grid = GridSnapping(self._options.grid_size)

        logger.debug(f"Initialized WireRouter (algorithm={self._options.algorithm.value})")

    def connect_pins(
        self,
        from_component: str,
        from_pin: str,
        to_component: str,
        to_pin: str,
        options: Optional[RoutingOptions] = None,
    ) -> ConnectionResult:
        """
        Connect two pins with a wire.

        PRIMARY entry point for creating wired connections.
        Handles all routing, junction creation, and connectivity.

        Args:
            from_component: Source component reference (e.g., "R1")
            from_pin: Source pin number (e.g., "1")
            to_component: Destination component reference (e.g., "R2")
            to_pin: Destination pin number (e.g., "2")
            options: Override routing options for this connection

        Returns:
            ConnectionResult with wire and junction UUIDs

        Raises:
            PinConnectionError: If pins cannot be connected

        Example:
            >>> router = WireRouter(schematic)
            >>> result = router.connect_pins("R1", "2", "R2", "1")
            >>> if result.success:
            ...     print(f"Connected with wire {result.wire_uuid}")
            ...     for junction in result.junctions_created:
            ...         print(f"  Junction: {junction}")
        """
        options = options or self._options

        logger.info(f"Connecting {from_component}.{from_pin} -> {to_component}.{to_pin}")

        # Resolve pin references
        from_pin_result = self._pin_discovery.match_pin(from_component, from_pin)
        if not from_pin_result.found:
            error_msg = f"Cannot find source pin: {from_pin_result.error_message}"
            logger.error(error_msg)
            return ConnectionResult(
                success=False,
                error_message=error_msg,
                from_pin_ref=from_component,
                from_pin_num=from_pin,
            )

        to_pin_result = self._pin_discovery.match_pin(to_component, to_pin)
        if not to_pin_result.found:
            error_msg = f"Cannot find destination pin: {to_pin_result.error_message}"
            logger.error(error_msg)
            return ConnectionResult(
                success=False,
                error_message=error_msg,
                to_pin_ref=to_component,
                to_pin_num=to_pin,
            )

        from_pin_info = from_pin_result.pin_info
        to_pin_info = to_pin_result.pin_info

        # Calculate routing path
        try:
            path = self._calculate_path(from_pin_info.position, to_pin_info.position, options)
        except NoPathError as e:
            error_msg = f"Cannot calculate route: {str(e)}"
            logger.error(error_msg)
            return ConnectionResult(
                success=False,
                error_message=error_msg,
                from_pin_ref=from_component,
                from_pin_num=from_pin,
                to_pin_ref=to_component,
                to_pin_num=to_pin,
            )

        logger.debug(f"Calculated path with {path.segment_count()} segments")

        # Create wire in schematic
        try:
            wire_uuid = self._schematic.wires.add(
                points=path.all_points(),
                wire_type=WireType.WIRE,
            )
            logger.info(f"Created wire {wire_uuid}")
        except Exception as e:
            error_msg = f"Failed to create wire: {str(e)}"
            logger.error(error_msg)
            return ConnectionResult(
                success=False,
                error_message=error_msg,
                path=path,
            )

        # Detect and create junctions
        junction_uuids = []
        if options.auto_create_junctions:
            try:
                junctions = self._junction_detector.detect_required_junctions(path)
                for junction_pos in junctions:
                    junc_uuid = self._schematic.junctions.add(junction_pos)
                    junction_uuids.append(junc_uuid)
                logger.info(f"Created {len(junction_uuids)} junctions")
            except Exception as e:
                logger.warning(f"Failed to create junctions: {e}")
                # Don't fail the whole operation

        logger.info(f"Connection complete: wire={wire_uuid}, junctions={len(junction_uuids)}")

        return ConnectionResult(
            success=True,
            wire_uuid=wire_uuid,
            wire_points=path.all_points(),
            junctions_created=junction_uuids,
            junction_positions=junctions,
            algorithm_used=options.algorithm,
            path=path,
            from_pin_ref=from_component,
            from_pin_num=from_pin,
            to_pin_ref=to_component,
            to_pin_num=to_pin,
        )

    def connect_pin_to_point(
        self,
        component: str,
        pin: str,
        target_point: Point,
        options: Optional[RoutingOptions] = None,
    ) -> ConnectionResult:
        """
        Connect a pin to an arbitrary point.

        Useful for:
        - Connecting to labels
        - Connecting to existing wires
        - Connecting to junctions

        Args:
            component: Component reference
            pin: Pin number
            target_point: Target point (should be grid-aligned)
            options: Routing options

        Returns:
            ConnectionResult

        Example:
            >>> result = router.connect_pin_to_point("R1", "2", Point(150, 100))
            >>> if result.success:
            ...     print(f"Connected to point")
        """
        options = options or self._options

        # Resolve pin
        pin_result = self._pin_discovery.match_pin(component, pin)
        if not pin_result.found:
            return ConnectionResult(
                success=False,
                error_message=pin_result.error_message,
            )

        pin_info = pin_result.pin_info

        # Snap target point to grid
        if options.snap_to_grid:
            target_point = self._grid.snap(target_point)

        # Calculate path
        path = self._calculate_path(pin_info.position, target_point, options)

        # Create wire
        wire_uuid = self._schematic.wires.add(points=path.all_points())

        # Create junctions
        junction_uuids = []
        if options.auto_create_junctions:
            junctions = self._junction_detector.detect_required_junctions(path)
            for junction_pos in junctions:
                junc_uuid = self._schematic.junctions.add(junction_pos)
                junction_uuids.append(junc_uuid)

        return ConnectionResult(
            success=True,
            wire_uuid=wire_uuid,
            wire_points=path.all_points(),
            junctions_created=junction_uuids,
            algorithm_used=options.algorithm,
            path=path,
        )

    def reconnect_wire(
        self,
        wire_uuid: str,
        new_start: Optional[Point] = None,
        new_end: Optional[Point] = None,
    ) -> ConnectionResult:
        """
        Modify an existing wire's endpoints.

        Args:
            wire_uuid: Wire to modify
            new_start: New start point (None to keep current)
            new_end: New end point (None to keep current)

        Returns:
            ConnectionResult
        """
        # Get wire
        wire = self._schematic.wires.get(wire_uuid)
        if wire is None:
            return ConnectionResult(
                success=False,
                error_message=f"Wire {wire_uuid} not found",
            )

        # Use current endpoints if not specified
        start = new_start or wire.points[0]
        end = new_end or wire.points[-1]

        # Calculate new path
        path = self._calculate_path(start, end, self._options)

        # Update wire points
        wire.points = path.all_points()

        return ConnectionResult(
            success=True,
            wire_uuid=wire_uuid,
            wire_points=path.all_points(),
            path=path,
        )

    # Private path calculation methods

    def _calculate_path(
        self,
        start: Point,
        end: Point,
        options: RoutingOptions,
    ) -> RoutingPath:
        """
        Calculate routing path between two points.

        Implements different routing algorithms.
        """
        # Snap points to grid
        if options.snap_to_grid:
            start = self._grid.snap(start)
            end = self._grid.snap(end)

        if options.algorithm == RoutingAlgorithm.DIRECT:
            return self._route_direct(start, end)
        elif options.algorithm == RoutingAlgorithm.MANHATTAN:
            return self._route_manhattan(start, end)
        elif options.algorithm == RoutingAlgorithm.ORTHOGONAL:
            return self._route_orthogonal(start, end)
        else:
            raise RoutingError(f"Unknown routing algorithm: {options.algorithm}")

    def _route_direct(self, start: Point, end: Point) -> RoutingPath:
        """
        Direct line routing (minimal waypoints).

        PSEUDOCODE:
        1. Create straight path from start to end
        2. No intermediate waypoints
        3. Identify segments that cross existing wires
        4. Mark crossing points as junction candidates
        """
        return RoutingPath(start_point=start, end_point=end, waypoints=[])

    def _route_manhattan(self, start: Point, end: Point) -> RoutingPath:
        """
        Manhattan/L-shaped routing.

        PSEUDOCODE:
        1. Create path that goes horizontal then vertical
        2. Start X direction: add waypoint at (end.x, start.y)
        3. Then Y direction to (end.x, end.y)
        4. Detect crossings with existing wires at waypoints
        5. Mark crossing points for junction creation

        Why this order:
        - Generally creates cleaner schematics
        - Minimizes backtracking
        - Works well for left-to-right wiring
        """
        # Horizontal segment
        h_point = Point(end.x, start.y)

        waypoints = [h_point] if h_point != end else []

        path = RoutingPath(
            start_point=start,
            end_point=end,
            waypoints=waypoints,
            junction_points=self._junction_detector.detect_crossing_points(start, end),
        )

        return path

    def _route_orthogonal(self, start: Point, end: Point) -> RoutingPath:
        """
        Orthogonal routing with multiple segments.

        More sophisticated algorithm for complex layouts.
        """
        # For now, use Manhattan as fallback
        return self._route_manhattan(start, end)
```

### 2.4 Junction Detection

#### File: `routing/junction_detector.py`

```python
"""Junction detection and creation logic."""

import logging
from typing import List, Set, Tuple

from ..core.types import Point
from ..core.geometry import points_equal
from .models import JunctionCandidate, RoutingPath


logger = logging.getLogger(__name__)


class JunctionDetector:
    """
    Detects where junctions should be created.

    A junction is needed when:
    1. A wire crosses another wire (not at endpoints)
    2. Multiple wires meet at a point
    3. A wire connects to a junction explicitly marked

    ALGORITHM:
    - Check new wire endpoints against existing wires
    - For each existing wire, find crossing points
    - Mark crossings where the new wire passes THROUGH
    - Exclude endpoints (where wires intentionally meet)
    """

    def __init__(self, schematic: 'Schematic', tolerance: float = 0.01):
        """
        Initialize junction detector.

        Args:
            schematic: Parent schematic for wire access
            tolerance: Position matching tolerance in mm
        """
        self._schematic = schematic
        self._tolerance = tolerance
        logger.debug(f"Initialized JunctionDetector (tolerance={tolerance}mm)")

    def detect_required_junctions(self, path: RoutingPath) -> List[Point]:
        """
        Detect where junctions are required for a new wire.

        PRIMARY entry point for junction detection.

        Returns points where junctions should be created.

        ALGORITHM:
        1. For each existing wire in schematic
        2. Check if new path crosses it
        3. Find crossing point(s)
        4. Exclude endpoints of existing wire
        5. Exclude endpoints of new wire
        6. Return remaining crossing points

        Args:
            path: RoutingPath for new wire

        Returns:
            List of positions where junctions should be created

        Example:
            >>> path = RoutingPath(Point(0, 0), Point(100, 100))
            >>> crossings = detector.detect_required_junctions(path)
            >>> for pt in crossings:
            ...     print(f"Junction at {pt}")
        """
        junction_points = []

        logger.debug(f"Detecting junctions for path with {path.segment_count()} segments")

        # Get all segments of the new wire
        all_points = path.all_points()

        for existing_wire in self._schematic.wires:
            # Don't cross with own wire (if updating)

            # Check each segment of the new wire against the existing wire
            for i in range(len(all_points) - 1):
                segment_start = all_points[i]
                segment_end = all_points[i + 1]

                # Find intersections with existing wire
                crossings = self._find_segment_intersections(
                    segment_start, segment_end, existing_wire.points
                )

                for crossing_point in crossings:
                    # Exclude endpoints
                    is_new_endpoint = (
                        crossing_point.distance_to(segment_start) < self._tolerance or
                        crossing_point.distance_to(segment_end) < self._tolerance
                    )

                    is_existing_endpoint = (
                        crossing_point.distance_to(existing_wire.points[0]) < self._tolerance or
                        crossing_point.distance_to(existing_wire.points[-1]) < self._tolerance
                    )

                    if not is_new_endpoint and not is_existing_endpoint:
                        # Avoid duplicates
                        if not any(p.distance_to(crossing_point) < self._tolerance for p in junction_points):
                            junction_points.append(crossing_point)
                            logger.debug(f"Found junction at {crossing_point}")

        logger.info(f"Detected {len(junction_points)} required junctions")
        return junction_points

    def detect_crossing_points(self, start: Point, end: Point) -> List[Point]:
        """
        Simple crossing detection for a line segment.

        PSEUDOCODE:
        1. Create virtual line from start to end
        2. Test intersection with all existing wires
        3. Return crossing points (excluding endpoints)
        """
        crossings = []

        for existing_wire in self._schematic.wires:
            crossings.extend(
                self._find_segment_intersections(start, end, existing_wire.points)
            )

        return crossings

    def _find_segment_intersections(
        self,
        seg_start: Point,
        seg_end: Point,
        wire_points: List[Point],
    ) -> List[Point]:
        """
        Find intersection points between a line segment and wire.

        PSEUDOCODE:
        1. For each segment of the wire
        2. Check intersection with the line segment
        3. Calculate exact intersection point
        4. Return all intersections

        Args:
            seg_start: Segment start point
            seg_end: Segment end point
            wire_points: Points defining existing wire

        Returns:
            List of intersection points
        """
        intersections = []

        # Check segment against each wire segment
        for i in range(len(wire_points) - 1):
            wire_seg_start = wire_points[i]
            wire_seg_end = wire_points[i + 1]

            intersection = self._line_segment_intersection(
                seg_start, seg_end,
                wire_seg_start, wire_seg_end
            )

            if intersection:
                intersections.append(intersection)

        return intersections

    def _line_segment_intersection(
        self,
        p1: Point, p2: Point,
        p3: Point, p4: Point,
    ) -> Tuple[Point, None]:
        """
        Calculate intersection point of two line segments.

        ALGORITHM (from computational geometry):
        1. Parametric form: P = P1 + t(P2 - P1) and Q = P3 + s(P4 - P3)
        2. Set P = Q and solve for t and s
        3. Check if 0 <= t <= 1 and 0 <= s <= 1
        4. If yes, segments intersect; calculate exact point

        Args:
            p1, p2: First segment endpoints
            p3, p4: Second segment endpoints

        Returns:
            Intersection Point if segments cross, None otherwise
        """
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if abs(denom) < 1e-10:
            return None  # Parallel or collinear

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        s = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        if 0 <= t <= 1 and 0 <= s <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return Point(x, y)

        return None

    def has_junction_at(self, position: Point) -> bool:
        """Check if junction already exists at position."""
        for junction in self._schematic.junctions:
            if junction.position.distance_to(position) < self._tolerance:
                return True
        return False
```

### 2.5 Grid Snapping

#### File: `routing/grid.py`

```python
"""Grid snapping utilities for wire routing."""

import logging
from ..core.types import Point


logger = logging.getLogger(__name__)


class GridSnapping:
    """
    Grid alignment for professional schematic appearance.

    KiCAD uses grid alignment for:
    - Electrical connectivity detection
    - Visual cleanliness
    - Professional appearance

    Default grid: 2.54mm (0.1 inch, 50 mil)
    Common grids: 2.54mm, 1.27mm (50mil, 50mil)
    """

    def __init__(self, grid_size: float = 2.54):
        """
        Initialize grid snapping.

        Args:
            grid_size: Grid size in mm (default 2.54mm)
        """
        self._grid_size = grid_size
        logger.debug(f"Initialized GridSnapping (grid_size={grid_size}mm)")

    def snap(self, point: Point) -> Point:
        """
        Snap a point to the nearest grid intersection.

        ALGORITHM:
        1. Divide coordinates by grid size
        2. Round to nearest integer
        3. Multiply by grid size
        4. Return snapped point

        Args:
            point: Point to snap

        Returns:
            Grid-aligned point

        Example:
            >>> grid = GridSnapping(2.54)
            >>> snapped = grid.snap(Point(100.5, 50.3))
            >>> print(snapped)  # (101.6, 50.8) or similar
        """
        snapped_x = round(point.x / self._grid_size) * self._grid_size
        snapped_y = round(point.y / self._grid_size) * self._grid_size

        result = Point(snapped_x, snapped_y)

        if result != point:
            logger.debug(f"Snapped {point} -> {result}")

        return result

    def is_aligned(self, point: Point, tolerance: float = 0.01) -> bool:
        """
        Check if point is grid-aligned.

        Args:
            point: Point to check
            tolerance: How close to grid counts as aligned

        Returns:
            True if point is on or very near a grid intersection
        """
        snapped = self.snap(point)
        distance = point.distance_to(snapped)
        return distance < tolerance

    @property
    def grid_size(self) -> float:
        """Get current grid size."""
        return self._grid_size
```

### 2.6 Routing Errors

#### File: `routing/errors.py`

```python
"""Routing-specific exceptions."""

from ..core.exceptions import KiCadSchError


class RoutingError(KiCadSchError):
    """Base exception for routing errors."""
    pass


class NoPathError(RoutingError):
    """Raised when no valid path can be calculated."""
    pass


class PinConnectionError(RoutingError):
    """Raised when pins cannot be connected."""
    pass


class GridAlignmentError(RoutingError):
    """Raised when routing cannot be grid-aligned."""
    pass
```

### 2.7 Routing Module Init

#### File: `routing/__init__.py`

```python
"""Wire routing and junction detection module."""

from .models import (
    ConnectionResult,
    RoutingPath,
    RoutingAlgorithm,
    RoutingOptions,
    JunctionCandidate,
)
from .router import WireRouter
from .junction_detector import JunctionDetector
from .grid import GridSnapping
from .errors import RoutingError, NoPathError, PinConnectionError

__all__ = [
    "ConnectionResult",
    "RoutingPath",
    "RoutingAlgorithm",
    "RoutingOptions",
    "JunctionCandidate",
    "WireRouter",
    "JunctionDetector",
    "GridSnapping",
    "RoutingError",
    "NoPathError",
    "PinConnectionError",
]
```

---

## Part 3: Track C - Testing

### 3.1 Test Fixture Structure

#### File: `tests/conftest.py` (Create if doesn't exist)

```python
"""Pytest fixtures for pin connection testing."""

import pytest
from pathlib import Path
import tempfile
import shutil

import kicad_sch_api as ksa
from kicad_sch_api.pins import PinDiscovery
from kicad_sch_api.routing import WireRouter, RoutingOptions, RoutingAlgorithm
from kicad_sch_api.core.types import Point


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture
def simple_schematic():
    """
    Create a simple 2-component schematic for basic testing.

    Layout:
    - R1 at (100, 100) - 10k resistor
    - R2 at (150, 100) - 10k resistor

    Both resistors are side-by-side for easy wiring tests.
    """
    sch = ksa.create_schematic("Test")

    # Add two resistors
    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(100, 100),
        rotation=0,
    )

    r2 = sch.components.add(
        lib_id="Device:R",
        reference="R2",
        value="10k",
        position=(150, 100),
        rotation=0,
    )

    return sch


@pytest.fixture
def ic_schematic():
    """
    Create schematic with IC for testing multi-pin components.

    Uses common 14-pin DIP IC (like 7400 NAND gates):
    - U1: TL072 (8-pin op-amp)
    - Supply decoupling capacitors
    """
    sch = ksa.create_schematic("IC Test")

    u1 = sch.components.add(
        lib_id="Amplifier_Operational:TL072",
        reference="U1",
        value="TL072",
        position=(100, 100),
        rotation=0,
    )

    # Add bypass capacitors
    c1 = sch.components.add(
        lib_id="Device:C",
        reference="C1",
        value="100n",
        position=(75, 85),
        rotation=0,
    )

    c2 = sch.components.add(
        lib_id="Device:C",
        reference="C2",
        value="100n",
        position=(75, 115),
        rotation=0,
    )

    return sch


@pytest.fixture
def hierarchical_schematic(temp_dir):
    """
    Create parent + child schematic for hierarchical testing.

    Parent has:
    - Sheet instance referencing Power.kicad_sch

    Child has:
    - Power regulation components
    """
    # Parent schematic
    parent = ksa.create_schematic("HierarchyTest")

    # Add sheet (but don't create actual file)
    sheet_uuid = parent.sheets.add_sheet(
        name="Power Supply",
        filename="power.kicad_sch",
        position=(50, 50),
        size=(100, 100),
        project_name="HierarchyTest",
    )

    return parent, sheet_uuid


@pytest.fixture
def pin_discovery(simple_schematic):
    """Create PinDiscovery service for testing."""
    return PinDiscovery(simple_schematic)


@pytest.fixture
def wire_router(simple_schematic):
    """Create WireRouter service for testing."""
    return WireRouter(simple_schematic)


@pytest.fixture
def routing_options():
    """Create default routing options."""
    return RoutingOptions(
        algorithm=RoutingAlgorithm.MANHATTAN,
        snap_to_grid=True,
        grid_size=2.54,
        auto_create_junctions=True,
    )


# Parametrized fixtures for multiple test inputs

@pytest.fixture(
    params=[
        (0, "No rotation"),
        (90, "90° clockwise"),
        (180, "180° flip"),
        (270, "270° counter-clockwise"),
    ],
    ids=["0°", "90°", "180°", "270°"]
)
def rotation_variant(request):
    """
    Parametrized fixture for testing all rotations.

    Usage:
        def test_pins_at_rotation(rotation_variant):
            rotation, desc = rotation_variant
            # Test with this rotation
    """
    rotation, description = request.param
    return rotation, description


@pytest.fixture(
    params=[
        ("Device:R", "Resistor"),
        ("Device:C", "Capacitor"),
        ("Device:L", "Inductor"),
        ("Connector:Conn_01x02_Pin", "2-pin connector"),
    ],
    ids=["R", "C", "L", "Connector"]
)
def component_variants(request):
    """
    Parametrized fixture for testing different component types.
    """
    lib_id, name = request.param
    return lib_id, name
```

### 3.2 Test Helper Functions

#### File: `tests/helpers.py`

```python
"""Helper functions for pin connection testing."""

from typing import List, Tuple, Optional
from kicad_sch_api import Schematic
from kicad_sch_api.core.types import Point, Wire


class SchematicTestHelper:
    """Helper class for schematic testing utilities."""

    @staticmethod
    def find_wire_endpoints(schematic: Schematic, wire_uuid: str) -> Tuple[Point, Point]:
        """
        Get start and end points of a wire.

        Args:
            schematic: Schematic to search
            wire_uuid: Wire UUID

        Returns:
            (start_point, end_point) tuple

        Raises:
            ValueError: If wire not found
        """
        wire = schematic.wires.get(wire_uuid)
        if not wire:
            raise ValueError(f"Wire {wire_uuid} not found")

        return wire.points[0], wire.points[-1]

    @staticmethod
    def count_wires_at_position(schematic: Schematic, position: Point, tolerance: float = 0.01) -> int:
        """
        Count how many wires pass through a position.

        Args:
            schematic: Schematic to search
            position: Position to check
            tolerance: Distance tolerance

        Returns:
            Number of wires at position
        """
        count = 0
        for wire in schematic.wires:
            for point in wire.points:
                if point.distance_to(position) < tolerance:
                    count += 1
                    break
        return count

    @staticmethod
    def get_connected_components(schematic: Schematic, wire_uuid: str) -> List[str]:
        """
        Get component references connected by a wire.

        Args:
            schematic: Schematic to analyze
            wire_uuid: Wire UUID

        Returns:
            List of component references connected to this wire
        """
        # Get wire
        wire = schematic.wires.get(wire_uuid)
        if not wire:
            return []

        # Find pins at wire endpoints
        connected = []

        for endpoint in [wire.points[0], wire.points[-1]]:
            # Search all components for pins at this position
            for component in schematic.components:
                # This requires pin discovery to be implemented
                # Placeholder for now
                pass

        return connected

    @staticmethod
    def assert_pin_connected(
        schematic: Schematic,
        component_ref: str,
        pin_num: str,
        tolerance: float = 0.01
    ) -> bool:
        """
        Assert that a pin is connected to a wire.

        Args:
            schematic: Schematic to check
            component_ref: Component reference
            pin_num: Pin number
            tolerance: Distance tolerance

        Returns:
            True if connected, False otherwise
        """
        # Requires pin discovery
        # Placeholder
        return False

    @staticmethod
    def verify_grid_alignment(schematic: Schematic, grid_size: float = 2.54) -> List[str]:
        """
        Verify all wire points are grid-aligned.

        Args:
            schematic: Schematic to check
            grid_size: Grid size in mm

        Returns:
            List of issues found (empty = OK)
        """
        issues = []
        tolerance = 0.01

        for wire in schematic.wires:
            for point in wire.points:
                snapped_x = round(point.x / grid_size) * grid_size
                snapped_y = round(point.y / grid_size) * grid_size

                x_error = abs(point.x - snapped_x)
                y_error = abs(point.y - snapped_y)

                if x_error > tolerance or y_error > tolerance:
                    issues.append(
                        f"Wire {wire.uuid} point {point} not grid-aligned "
                        f"(errors: x={x_error:.3f}, y={y_error:.3f})"
                    )

        return issues


# Module-level helper functions

def create_test_schematic_with_components(component_specs: List[dict]) -> Schematic:
    """
    Create schematic with specified components.

    Args:
        component_specs: List of dicts with keys:
            - lib_id: Library ID
            - reference: Component reference
            - value: Component value
            - position: (x, y) tuple or Point
            - rotation: Rotation in degrees (optional)

    Returns:
        Populated Schematic

    Example:
        >>> specs = [
        ...     {"lib_id": "Device:R", "reference": "R1", "value": "10k", "position": (100, 100)},
        ...     {"lib_id": "Device:C", "reference": "C1", "value": "100n", "position": (150, 100)},
        ... ]
        >>> sch = create_test_schematic_with_components(specs)
    """
    import kicad_sch_api as ksa

    sch = ksa.create_schematic("Test")

    for spec in component_specs:
        position = spec.get("position", (0, 0))
        rotation = spec.get("rotation", 0)

        if isinstance(position, tuple):
            position = Point(*position)

        sch.components.add(
            lib_id=spec["lib_id"],
            reference=spec["reference"],
            value=spec["value"],
            position=position,
            rotation=rotation,
        )

    return sch


def assert_pin_info_valid(pin_info: 'PinInfo') -> None:
    """
    Assert that a PinInfo object has valid data.

    Args:
        pin_info: PinInfo to validate

    Raises:
        AssertionError: If any field is invalid
    """
    assert pin_info.component_reference, "Component reference missing"
    assert pin_info.pin_number, "Pin number missing"
    assert pin_info.position is not None, "Position missing"
    assert pin_info.lib_id, "Library ID missing"
    assert pin_info.pin_type is not None, "Pin type missing"
```

### 3.3 Reference Test Pattern

#### File: `tests/reference_tests/test_pin_discovery_reference.py`

```python
"""
Reference tests for pin discovery against manually created schematics.

Pattern for testing pin functionality with real KiCAD schematics.
"""

import pytest
from pathlib import Path

import kicad_sch_api as ksa
from kicad_sch_api.pins import PinDiscovery
from kicad_sch_api.core.types import Point


class TestPinDiscoveryReference:
    """
    Test pin discovery against reference schematics.

    Reference schematics in tests/reference_kicad_projects/:
    - single_resistor/              - 1x R
    - ic_8pin/                      - 1x 8-pin IC
    - mixed_components/             - Multiple component types
    """

    @pytest.fixture
    def single_resistor_sch(self):
        """Load reference schematic: single resistor."""
        path = Path("tests/reference_kicad_projects/single_resistor/schematic.kicad_sch")
        if not path.exists():
            pytest.skip(f"Reference schematic not found: {path}")
        return ksa.load_schematic(path)

    def test_pin_discovery_single_resistor(self, single_resistor_sch):
        """
        Test pin discovery on reference resistor schematic.

        Verifies:
        - Correct pin count
        - Accurate pin positions
        - Correct pin names
        """
        discovery = PinDiscovery(single_resistor_sch)

        # Get pins for resistor
        pins = discovery.get_pins_info("R1")

        # Resistors have 2 pins
        assert len(pins.pins_by_number) == 2, "Resistor should have 2 pins"

        # Get individual pins
        pin1 = pins.get_pin("1")
        pin2 = pins.get_pin("2")

        assert pin1 is not None, "Pin 1 should exist"
        assert pin2 is not None, "Pin 2 should exist"

        # Verify pin positions are valid Points
        assert isinstance(pin1.position, Point), "Pin 1 position should be Point"
        assert isinstance(pin2.position, Point), "Pin 2 position should be Point"

        # Positions should be different
        assert pin1.position != pin2.position, "Pin positions should differ"

        # Verify position is within schematic bounds
        assert -500 < pin1.position.x < 500, "Pin X within reasonable bounds"
        assert -500 < pin1.position.y < 500, "Pin Y within reasonable bounds"


    def test_pin_discovery_ic_8pin(self):
        """
        Test pin discovery on 8-pin IC reference schematic.

        Verifies:
        - All 8 pins found
        - Pin types correct (power, ground, signal)
        - Pin names present
        """
        # Load IC reference schematic
        path = Path("tests/reference_kicad_projects/ic_8pin/schematic.kicad_sch")
        if not path.exists():
            pytest.skip(f"Reference schematic not found: {path}")

        sch = ksa.load_schematic(path)
        discovery = PinDiscovery(sch)

        # Get IC pins
        pins = discovery.get_pins_info("U1")

        # Should have 8 pins
        assert len(pins.pins_by_number) == 8, "IC should have 8 pins"

        # Verify pin numbering
        for i in range(1, 9):
            pin = pins.get_pin(str(i))
            assert pin is not None, f"Pin {i} should exist"

    def test_pin_matching_with_diagnostics(self, single_resistor_sch):
        """
        Test match_pin() with detailed diagnostics.

        Verifies:
        - Successful matches return found=True
        - Failed matches return found=False with candidates
        - Error messages are helpful
        """
        discovery = PinDiscovery(single_resistor_sch)

        # Successful match
        result = discovery.match_pin("R1", "1")
        assert result.found, "Pin 1 should be found"
        assert result.pin_info is not None
        assert result.error_message is None

        # Failed match with candidates
        result = discovery.match_pin("R1", "99")
        assert not result.found, "Pin 99 should not exist"
        assert len(result.candidates) > 0, "Should suggest candidates"
        assert result.error_message is not None
```

---

## Part 4: Module Organization and Integration

### 4.1 Complete Module Structure

```
kicad_sch_api/
├── pins/                           # NEW: Pin discovery module
│   ├── __init__.py
│   ├── models.py                   # PinInfo, ComponentPins
│   ├── discovery.py                # PinDiscovery service
│   ├── validator.py                # Pin validation
│   └── errors.py                   # Pin exceptions
│
├── routing/                        # NEW: Wire routing module
│   ├── __init__.py
│   ├── models.py                   # ConnectionResult, RoutingPath
│   ├── router.py                   # WireRouter service
│   ├── junction_detector.py        # JunctionDetector service
│   ├── grid.py                     # GridSnapping utility
│   └── errors.py                   # Routing exceptions
│
├── core/
│   ├── geometry.py                 # EXISTING: Already has point/distance calcs
│   ├── pin_utils.py                # EXISTING: list_component_pins()
│   ├── connectivity.py             # EXISTING: Connectivity analysis
│   ├── schematic.py                # MODIFY: Add router and discovery properties
│   └── types.py                    # EXISTING: Point, Wire, etc.
│
├── library/
│   └── cache.py                    # EXISTING: Symbol caching
│
└── collections/
    ├── components.py               # EXISTING: ComponentCollection
    ├── wires.py                    # EXISTING: WireCollection
    └── junctions.py                # EXISTING: JunctionCollection

tests/
├── conftest.py                     # NEW: Comprehensive fixtures
├── helpers.py                      # NEW: Test helper functions
├── unit/
│   ├── test_pin_discovery.py       # Unit tests for PinDiscovery
│   ├── test_wire_router.py         # Unit tests for WireRouter
│   └── test_junction_detection.py  # Unit tests for JunctionDetector
├── reference_tests/
│   ├── test_pin_discovery_reference.py       # Reference-based tests
│   └── test_wire_routing_reference.py        # Reference-based tests
└── integration/
    └── test_pin_to_wire_flow.py    # End-to-end integration tests
```

### 4.2 Integration Points

#### 4.2.1 Schematic Class Integration

**File to modify**: `/kicad_sch_api/core/schematic.py`

```python
# Add to Schematic.__init__():

class Schematic:
    def __init__(self, ...):
        # ... existing initialization ...

        # Lazy-initialize pin discovery and routing services
        self._pin_discovery: Optional[PinDiscovery] = None
        self._wire_router: Optional[WireRouter] = None

    @property
    def pin_discovery(self) -> 'PinDiscovery':
        """Get or create pin discovery service."""
        if self._pin_discovery is None:
            from ..pins import PinDiscovery
            self._pin_discovery = PinDiscovery(self)
        return self._pin_discovery

    @property
    def wire_router(self) -> 'WireRouter':
        """Get or create wire router service."""
        if self._wire_router is None:
            from ..routing import WireRouter
            self._wire_router = WireRouter(self, self.pin_discovery)
        return self._wire_router

    # Convenience methods

    def get_component_pins(self, component_reference: str) -> 'ComponentPins':
        """
        Get all pins for a component with positions.

        Convenience method wrapping pin_discovery.get_pins_info().
        """
        return self.pin_discovery.get_pins_info(component_reference)

    def find_pin_by_name(self, pin_name: str) -> List['PinInfo']:
        """Find all pins with a specific name."""
        return self.pin_discovery.find_pins_by_name(pin_name)

    def connect_pins(
        self,
        from_component: str,
        from_pin: str,
        to_component: str,
        to_pin: str,
        options: Optional['RoutingOptions'] = None,
    ) -> 'ConnectionResult':
        """
        Connect two pins with a wire.

        Convenience method wrapping wire_router.connect_pins().
        """
        return self.wire_router.connect_pins(
            from_component, from_pin, to_component, to_pin, options
        )
```

### 4.3 Import Hierarchy

```
schematic.py (top level)
├── imports pin_discovery.py
│   ├── imports pins/models.py (PinInfo, ComponentPins)
│   ├── imports pins/errors.py
│   ├── imports library/cache.py (symbol definitions)
│   ├── imports core/pin_utils.py (list_component_pins)
│   ├── imports core/geometry.py (points_equal)
│   └── imports core/types.py (Point, SchematicSymbol)
│
├── imports wire_router.py
│   ├── imports routing/models.py (ConnectionResult, RoutingPath)
│   ├── imports routing/junction_detector.py
│   ├── imports routing/grid.py
│   ├── imports routing/errors.py
│   ├── imports pins/discovery.py (for pin resolution)
│   └── imports core/types.py (Wire, Junction, Point)
│
└── uses core/schematic.py (circular, but safe via lazy init)
```

### 4.4 Dependency Injection Points

**No direct instantiation - lazy initialization:**

```python
# Constructor: No dependencies injected
router = WireRouter(schematic)

# Services created on first use
discovery = router._pin_discovery  # Created if None

# Or explicit injection
discovery = PinDiscovery(schematic)
router = WireRouter(schematic, pin_discovery=discovery)

# Testing: Can inject mocks
class MockPinDiscovery:
    def get_pins_info(self, ref):
        # Return test data
        ...

router = WireRouter(schematic, pin_discovery=MockPinDiscovery())
```

### 4.5 Circular Dependency Prevention

**Pattern used throughout:**

1. **Lazy initialization**: Services created on first use, not in `__init__`
2. **Type hints with quotes**: `'Schematic'` instead of importing
3. **Module-level imports only**: No circular imports at top level
4. **Services stored as private attributes**: `self._pin_discovery`
5. **Public properties for access**: `@property def pin_discovery(self)`

---

## Part 5: Pseudocode and Algorithms

### 5.1 Pin Discovery Algorithm

```
FUNCTION get_pins_info(component_reference):
    // Check cache
    IF component_reference IN pin_cache:
        RETURN pin_cache[component_reference]

    // Get component
    component = schematic.components.get(component_reference)
    IF component IS NULL:
        THROW PinNotFoundError

    // Get symbol definition
    symbol_def = symbol_cache.get_symbol(component.lib_id)

    // Get pin positions
    pin_positions = list_component_pins(component)
    // Returns List<(pin_number, absolute_position)>

    // Enhance each pin with symbol info
    FOR EACH (pin_number, position) IN pin_positions:
        symbol_pin = find_in_symbol(symbol_def, pin_number)

        pin_info = PinInfo(
            component_reference = component_reference,
            pin_number = pin_number,
            position = position,
            pin_type = parse_pin_type(symbol_pin.type),
            lib_id = component.lib_id,
            // ... other fields
        )

        pins_by_number[pin_number] = pin_info
        IF symbol_pin.name:
            pins_by_name[symbol_pin.name] = pin_info

    // Cache and return
    result = ComponentPins(pins_by_number, pins_by_name)
    pin_cache[component_reference] = result
    RETURN result
```

### 5.2 Manhattan Routing Algorithm

```
FUNCTION route_manhattan(start, end):
    // Create L-shaped path
    waypoint_1 = Point(end.x, start.y)  // Go horizontal first
    waypoint_2 = end                    // Then vertical

    IF waypoint_1 == end:
        RETURN RoutingPath(start, end, [])  // Already aligned
    ELSE:
        waypoints = [waypoint_1]

    // Detect crossings for junctions
    junction_points = []

    FOR EACH existing_wire IN schematic.wires:
        // Check horizontal segment: start -> waypoint_1
        crossings = find_intersections(start, waypoint_1, existing_wire)
        junction_points += crossings

        // Check vertical segment: waypoint_1 -> end
        crossings = find_intersections(waypoint_1, end, existing_wire)
        junction_points += crossings

    RETURN RoutingPath(start, end, waypoints, junction_points)
```

### 5.3 Junction Detection Algorithm

```
FUNCTION detect_required_junctions(path):
    junctions = []

    // Get all segments of new wire
    segments = get_segments(path.all_points())

    // Check each segment against existing wires
    FOR EACH segment IN segments:
        FOR EACH existing_wire IN schematic.wires:
            FOR EACH existing_segment IN get_segments(existing_wire.points):
                // Calculate intersection
                intersection = line_intersection(segment, existing_segment)

                IF intersection IS NOT NULL:
                    // Check if it's an endpoint (should not create junction)
                    is_new_endpoint = (
                        distance(intersection, segment.start) < tolerance OR
                        distance(intersection, segment.end) < tolerance
                    )

                    is_existing_endpoint = (
                        distance(intersection, existing_segment.start) < tolerance OR
                        distance(intersection, existing_segment.end) < tolerance
                    )

                    IF NOT is_new_endpoint AND NOT is_existing_endpoint:
                        // Remove duplicates
                        IF NOT contains_point(junctions, intersection, tolerance):
                            junctions.add(intersection)

    RETURN junctions
```

### 5.4 Line Intersection Algorithm

```
FUNCTION line_segment_intersection(p1, p2, p3, p4):
    // Parametric line equations:
    // Line 1: P = p1 + t(p2 - p1)
    // Line 2: Q = p3 + s(p4 - p3)
    // Solve P = Q for t and s

    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y
    x3, y3 = p3.x, p3.y
    x4, y4 = p4.x, p4.y

    // Denominator: determinant of coefficient matrix
    denom = (x1 - x2)(y3 - y4) - (y1 - y2)(x3 - x4)

    IF abs(denom) < EPSILON:
        RETURN NULL  // Lines are parallel or collinear

    // Calculate parameters
    t = ((x1 - x3)(y3 - y4) - (y1 - y3)(x3 - x4)) / denom
    s = -((x1 - x2)(y1 - y3) - (y1 - y2)(x1 - x3)) / denom

    // Check if intersection is within both segments
    IF 0 <= t <= 1 AND 0 <= s <= 1:
        // Calculate exact intersection point
        x = x1 + t(x2 - x1)
        y = y1 + t(y2 - y1)
        RETURN Point(x, y)

    RETURN NULL  // Lines intersect but not within segment bounds
```

---

## Part 6: Key Design Principles

### 6.1 Separation of Concerns

| Module | Responsibility | Dependencies |
|--------|----------------|---|
| `pins/models.py` | Data structures | core/types only |
| `pins/discovery.py` | Pin queries | models, library cache, geometry |
| `routing/models.py` | Route data | core/types |
| `routing/router.py` | Path calculation | pin discovery, junction detector |
| `routing/junction_detector.py` | Crossing detection | geometry, grid |
| `routing/grid.py` | Grid alignment | core/types |

### 6.2 Testability

- **No file I/O in core logic**: All services accept schematic as parameter
- **Dependency injection**: Services accept dependencies in constructor
- **Clear interfaces**: Each service has single responsibility
- **Mock-friendly**: All dependencies are replaceable

### 6.3 Performance

- **Caching**: Pin info cached after first lookup
- **Lazy initialization**: Services created only when used
- **Indexed lookups**: Pins indexed by number and name
- **Batch operations**: Support multiple pin operations at once

### 6.4 Error Handling

- **Specific exceptions**: PinNotFoundError, RoutingError, etc.
- **Detailed diagnostics**: PinMatchResult provides candidates and error messages
- **Warnings preserved**: RoutingResult collects non-fatal warnings
- **Graceful degradation**: Missing symbol info doesn't crash

---

## Part 7: Testing Patterns Summary

### Unit Test Pattern
```python
def test_feature_basic():
    sch = create_simple_schematic()
    service = ServiceClass(sch)
    result = service.method()
    assert result.success
    assert result.value == expected
```

### Reference Test Pattern
```python
def test_feature_against_kicad():
    # Load manually created KiCAD schematic
    sch = load_reference_schematic()
    service = ServiceClass(sch)

    # Compare against known KiCAD behavior
    assert service.method() == kicad_expected_output
```

### Integration Test Pattern
```python
def test_feature_full_workflow():
    # Create schematic
    sch = create_schematic()

    # Use Track A (discovery)
    pins = sch.pin_discovery.get_pins_info("R1")

    # Use Track B (routing)
    result = sch.wire_router.connect_pins("R1", "1", "R2", "2")

    # Verify end-to-end result
    assert schematic_is_valid(sch)
```

---

## Summary

This design provides:

1. **Complete data structures** for pins, routing, and results
2. **Clear service interfaces** for discovery and routing
3. **Comprehensive testing fixtures** for all test levels
4. **Detailed algorithms** with pseudocode
5. **No circular dependencies** through lazy initialization
6. **Professional error handling** with diagnostics
7. **Performance optimization** through caching and indexing
8. **Exact format preservation** maintained throughout

The implementation can proceed in stages:
- Phase 1: Core models (pins/models.py, routing/models.py)
- Phase 2: Services (discovery.py, router.py)
- Phase 3: Supporting utilities (grid.py, junction_detector.py)
- Phase 4: Integration into Schematic class
- Phase 5: Comprehensive test suite
