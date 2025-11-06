# Pin Connection Features - Implementation Guide with Examples

## Quick Start: How to Implement

### Phase 1: Data Models (Est. 2-3 hours)

**File 1:** `kicad_sch_api/pins/models.py` - ~200 lines

```python
"""Pin models - foundational data structures."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from ..core.types import Point

# 1. Copy PinType enum (5 lines)
class PinType(Enum):
    INPUT = "input"
    # ... (see design doc)

# 2. Copy PinShape enum (5 lines)
class PinShape(Enum):
    CIRCLE = "circle"
    # ... (see design doc)

# 3. Copy PinInfo dataclass (40 lines)
@dataclass(frozen=True)
class PinInfo:
    component_reference: str
    pin_number: str
    # ... (see design doc)

# 4. Copy PinMatchResult dataclass (10 lines)
# 5. Copy ComponentPins dataclass (20 lines)
```

**File 2:** `kicad_sch_api/routing/models.py` - ~150 lines

```python
"""Routing models - result and configuration."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from ..core.types import Point

# 1. Copy RoutingAlgorithm enum (3 lines)
# 2. Copy RoutingPath dataclass (20 lines)
# 3. Copy ConnectionResult dataclass (30 lines)
# 4. Copy RoutingOptions dataclass (20 lines)
```

**Testing Phase 1:**

```python
# tests/unit/test_models.py - Test instantiation

def test_pin_info_creation():
    """Test PinInfo can be created."""
    pin = PinInfo(
        component_reference="R1",
        pin_number="1",
        pin_name=None,
        position=Point(100, 100),
        pin_type=PinType.PASSIVE,
        pin_shape=PinShape.CIRCLE,
        lib_id="Device:R",
        # ... other required fields
    )
    assert pin.component_reference == "R1"
    assert pin.position.x == 100
```

---

### Phase 2: Pin Discovery Service (Est. 4-5 hours)

**File:** `kicad_sch_api/pins/discovery.py` - ~400 lines

**Step-by-step implementation:**

```python
"""Phase 2: Implement PinDiscovery service."""

import logging
from typing import List, Optional, Dict

from ..core.types import Point, SchematicSymbol
from ..library.cache import get_symbol_cache
from ..core.pin_utils import list_component_pins
from .models import PinInfo, PinType, PinShape, ComponentPins, PinMatchResult
from .errors import PinNotFoundError

logger = logging.getLogger(__name__)

class PinDiscovery:
    """Service for discovering pins."""

    def __init__(self, schematic: 'Schematic', cache_enabled: bool = True):
        """Initialize."""
        self._schematic = schematic
        self._cache_enabled = cache_enabled
        self._component_pins_cache: Dict[str, ComponentPins] = {}
        self._symbol_cache = get_symbol_cache()

    # STEP 1: Implement basic structure (30 mins)
    def get_pins_info(self, component_reference: str) -> ComponentPins:
        """
        Get pins for a component.

        Skeleton implementation:
        """
        # Check cache
        if component_reference in self._component_pins_cache:
            return self._component_pins_cache[component_reference]

        # Get component
        component = self._schematic.components.get(component_reference)
        if component is None:
            raise PinNotFoundError(f"Component {component_reference} not found")

        # TODO: Fill in the rest (steps 2-5)
        pass

    # STEP 2: Get pin positions (30 mins)
    # In get_pins_info(), add:
    #   component_data = component._data
    #   pin_list = list_component_pins(component_data)
    #   # Returns: [(pin_number, Point), ...]

    # STEP 3: Get symbol information (30 mins)
    # In get_pins_info(), add:
    #   symbol_def = self._get_symbol_definition(component.lib_id)
    #   # Returns: SymbolDefinition or None

    # STEP 4: Create PinInfo objects (1 hour)
    # Loop through pins, combine position + symbol info:
    #   for pin_number, position in pin_list:
    #       symbol_pin = self._find_symbol_pin(symbol_def, pin_number)
    #       pin_info = PinInfo(...)
    #       pins_by_number[pin_number] = pin_info

    # STEP 5: Return ComponentPins (15 mins)
    # result = ComponentPins(pins_by_number, pins_by_name)
    # return result

    # STEP 6: Implement helper methods (1 hour)
    def _get_symbol_definition(self, lib_id: str) -> Optional['SymbolDefinition']:
        """Get symbol from cache."""
        try:
            return self._symbol_cache.get_symbol(lib_id)
        except Exception as e:
            logger.warning(f"Failed to get symbol {lib_id}: {e}")
            return None

    def _find_symbol_pin(self, symbol_def, pin_number: str):
        """Find pin in symbol definition."""
        if not symbol_def:
            return None
        for pin in symbol_def.pins:
            if pin.number == pin_number:
                return pin
        return None

    def _parse_pin_type(self, type_str: str) -> PinType:
        """Convert string to PinType enum."""
        # Simple mapping
        type_map = {
            "input": PinType.INPUT,
            "output": PinType.OUTPUT,
            "passive": PinType.PASSIVE,
            # ... etc
        }
        return type_map.get(type_str.lower(), PinType.UNSPECIFIED)

    # STEP 7: Implement public query methods (2 hours)
    def find_pins_by_name(self, pin_name: str) -> List[PinInfo]:
        """Find all pins with a specific name."""
        results = []
        for component in self._schematic.components:
            try:
                component_pins = self.get_pins_info(component.reference)
                if pin_name in component_pins.pins_by_name:
                    results.append(component_pins.pins_by_name[pin_name])
            except PinNotFoundError:
                continue
        return results

    def match_pin(self, component_reference: str, pin_identifier: str) -> PinMatchResult:
        """Match a pin with diagnostics."""
        try:
            component_pins = self.get_pins_info(component_reference)
        except PinNotFoundError as e:
            return PinMatchResult(
                found=False,
                pin_info=None,
                candidates=[],
                error_message=str(e)
            )

        # Try to find pin
        pin = component_pins.get_pin(pin_identifier)
        if pin:
            return PinMatchResult(
                found=True,
                pin_info=pin,
                candidates=[],
                error_message=None
            )

        # Return candidates
        return PinMatchResult(
            found=False,
            pin_info=None,
            candidates=component_pins.all_pins(),
            error_message=f"Pin {pin_identifier} not found"
        )
```

**Testing Phase 2:**

```python
# tests/unit/test_pin_discovery.py

def test_get_pins_info_basic(simple_schematic):
    """Test getting pins for a resistor."""
    discovery = PinDiscovery(simple_schematic)

    # Should have R1 in schematic
    pins = discovery.get_pins_info("R1")

    # Resistors have 2 pins
    assert len(pins.pins_by_number) == 2

    # Can get by number
    pin_1 = pins.get_pin("1")
    assert pin_1 is not None
    assert pin_1.pin_number == "1"

def test_find_pins_by_name(simple_schematic):
    """Test searching for pins by name."""
    discovery = PinDiscovery(simple_schematic)

    # Search for all "GND" pins (might not exist in simple schematic)
    gnd_pins = discovery.find_pins_by_name("GND")

    # Should return list (may be empty)
    assert isinstance(gnd_pins, list)

def test_match_pin_success(simple_schematic):
    """Test successful pin matching."""
    discovery = PinDiscovery(simple_schematic)

    result = discovery.match_pin("R1", "1")

    assert result.found
    assert result.pin_info is not None

def test_match_pin_failure(simple_schematic):
    """Test pin matching failure with diagnostics."""
    discovery = PinDiscovery(simple_schematic)

    result = discovery.match_pin("R1", "99")  # Non-existent pin

    assert not result.found
    assert result.pin_info is None
    assert len(result.candidates) > 0  # Should suggest real pins
    assert result.error_message is not None
```

---

### Phase 3: Routing Service (Est. 5-6 hours)

**File 1:** `kicad_sch_api/routing/grid.py` - ~100 lines (EASY - start here!)

```python
"""Phase 3a: Grid snapping - simplest module."""

import logging
from ..core.types import Point

logger = logging.getLogger(__name__)

class GridSnapping:
    """Snap points to grid."""

    def __init__(self, grid_size: float = 2.54):
        """Initialize with grid size."""
        self._grid_size = grid_size

    def snap(self, point: Point) -> Point:
        """Snap point to nearest grid intersection."""
        # ALGORITHM:
        # 1. Divide by grid size
        # 2. Round to nearest integer
        # 3. Multiply back
        # 4. Return Point

        snapped_x = round(point.x / self._grid_size) * self._grid_size
        snapped_y = round(point.y / self._grid_size) * self._grid_size

        result = Point(snapped_x, snapped_y)

        if result != point:
            logger.debug(f"Snapped {point} -> {result}")

        return result

    def is_aligned(self, point: Point, tolerance: float = 0.01) -> bool:
        """Check if point is grid-aligned."""
        snapped = self.snap(point)
        distance = point.distance_to(snapped)
        return distance < tolerance

    @property
    def grid_size(self) -> float:
        """Get grid size."""
        return self._grid_size
```

**Testing Phase 3a:**

```python
# tests/unit/test_grid_snapping.py

def test_grid_snapping_basic():
    """Test basic grid snapping."""
    grid = GridSnapping(2.54)

    point = Point(100.5, 100.3)
    snapped = grid.snap(point)

    # Should snap to nearest grid
    assert snapped.x % 2.54 < 0.01 or (2.54 - snapped.x % 2.54) < 0.01
    assert snapped.y % 2.54 < 0.01 or (2.54 - snapped.y % 2.54) < 0.01

def test_grid_alignment_check():
    """Test checking if point is grid-aligned."""
    grid = GridSnapping(2.54)

    aligned_point = Point(101.6, 101.6)  # 40*2.54, 40*2.54
    assert grid.is_aligned(aligned_point)

    misaligned_point = Point(101.5, 101.5)
    assert not grid.is_aligned(misaligned_point)
```

**File 2:** `kicad_sch_api/routing/junction_detector.py` - ~200 lines

```python
"""Phase 3b: Junction detection."""

import logging
from typing import List, Optional, Tuple
from ..core.types import Point
from .models import RoutingPath

logger = logging.getLogger(__name__)

class JunctionDetector:
    """Detect where junctions are needed."""

    def __init__(self, schematic: 'Schematic', tolerance: float = 0.01):
        """Initialize."""
        self._schematic = schematic
        self._tolerance = tolerance

    def detect_required_junctions(self, path: RoutingPath) -> List[Point]:
        """
        Detect junctions for a new wire.

        ALGORITHM (simplified):
        1. Get all segments of new wire
        2. For each existing wire:
           a. Check if new wire crosses it
           b. Find crossing points
           c. Filter out endpoints
        3. Return crossing points
        """
        junctions = []
        all_points = path.all_points()

        # STEP 1: Create segments from path
        for i in range(len(all_points) - 1):
            segment_start = all_points[i]
            segment_end = all_points[i + 1]

            # STEP 2: Check against each existing wire
            for existing_wire in self._schematic.wires:
                # STEP 3: Find crossings
                crossings = self._find_segment_intersections(
                    segment_start, segment_end, existing_wire.points
                )

                # STEP 4: Filter and add
                for crossing in crossings:
                    # Skip if it's an endpoint
                    is_endpoint = (
                        crossing.distance_to(segment_start) < self._tolerance or
                        crossing.distance_to(segment_end) < self._tolerance or
                        crossing.distance_to(existing_wire.points[0]) < self._tolerance or
                        crossing.distance_to(existing_wire.points[-1]) < self._tolerance
                    )

                    if not is_endpoint:
                        # Skip duplicates
                        if not any(p.distance_to(crossing) < self._tolerance for p in junctions):
                            junctions.append(crossing)
                            logger.debug(f"Found junction at {crossing}")

        return junctions

    def _find_segment_intersections(
        self,
        seg_start: Point,
        seg_end: Point,
        wire_points: List[Point],
    ) -> List[Point]:
        """Find intersections between segment and wire."""
        intersections = []

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
    ) -> Optional[Point]:
        """Calculate intersection of two line segments."""
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if abs(denom) < 1e-10:
            return None  # Parallel

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        s = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        if 0 <= t <= 1 and 0 <= s <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return Point(x, y)

        return None
```

**File 3:** `kicad_sch_api/routing/router.py` - ~400 lines

```python
"""Phase 3c: Wire routing service."""

import logging
from typing import Optional

from ..core.types import Point, WireType
from ..pins.discovery import PinDiscovery
from .models import (
    ConnectionResult,
    RoutingPath,
    RoutingAlgorithm,
    RoutingOptions,
)
from .junction_detector import JunctionDetector
from .grid import GridSnapping

logger = logging.getLogger(__name__)

class WireRouter:
    """Route wires between pins."""

    def __init__(
        self,
        schematic: 'Schematic',
        pin_discovery: Optional[PinDiscovery] = None,
        options: Optional[RoutingOptions] = None,
    ):
        """Initialize."""
        self._schematic = schematic
        self._pin_discovery = pin_discovery or PinDiscovery(schematic)
        self._options = options or RoutingOptions()
        self._junction_detector = JunctionDetector(schematic)
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

        STEP 1: Resolve pins (30 mins to implement)
        STEP 2: Calculate path (1 hour)
        STEP 3: Create wire (15 mins)
        STEP 4: Detect junctions (15 mins)
        STEP 5: Return result (5 mins)
        """
        options = options or self._options

        logger.info(f"Connecting {from_component}.{from_pin} -> {to_component}.{to_pin}")

        # STEP 1: Resolve pins
        from_result = self._pin_discovery.match_pin(from_component, from_pin)
        if not from_result.found:
            return ConnectionResult(
                success=False,
                error_message=f"Cannot find pin: {from_result.error_message}",
            )

        to_result = self._pin_discovery.match_pin(to_component, to_pin)
        if not to_result.found:
            return ConnectionResult(
                success=False,
                error_message=f"Cannot find pin: {to_result.error_message}",
            )

        from_pos = from_result.pin_info.position
        to_pos = to_result.pin_info.position

        # STEP 2: Calculate path
        try:
            path = self._calculate_path(from_pos, to_pos, options)
        except Exception as e:
            return ConnectionResult(
                success=False,
                error_message=f"Failed to calculate path: {e}",
            )

        # STEP 3: Create wire
        try:
            wire_uuid = self._schematic.wires.add(
                points=path.all_points(),
                wire_type=WireType.WIRE,
            )
        except Exception as e:
            return ConnectionResult(
                success=False,
                error_message=f"Failed to create wire: {e}",
            )

        # STEP 4: Detect junctions
        junction_uuids = []
        if options.auto_create_junctions:
            try:
                junctions = self._junction_detector.detect_required_junctions(path)
                for junction_pos in junctions:
                    junc_uuid = self._schematic.junctions.add(junction_pos)
                    junction_uuids.append(junc_uuid)
            except Exception as e:
                logger.warning(f"Failed to create junctions: {e}")

        # STEP 5: Return result
        return ConnectionResult(
            success=True,
            wire_uuid=wire_uuid,
            wire_points=path.all_points(),
            junctions_created=junction_uuids,
            algorithm_used=options.algorithm,
            path=path,
            from_pin_ref=from_component,
            from_pin_num=from_pin,
            to_pin_ref=to_component,
            to_pin_num=to_pin,
        )

    def _calculate_path(
        self,
        start: Point,
        end: Point,
        options: RoutingOptions,
    ) -> RoutingPath:
        """Calculate routing path."""
        # Snap to grid
        if options.snap_to_grid:
            start = self._grid.snap(start)
            end = self._grid.snap(end)

        # Select algorithm
        if options.algorithm == RoutingAlgorithm.MANHATTAN:
            return self._route_manhattan(start, end)
        else:
            raise ValueError(f"Unknown algorithm: {options.algorithm}")

    def _route_manhattan(self, start: Point, end: Point) -> RoutingPath:
        """Create L-shaped path."""
        # Go horizontal first, then vertical
        h_point = Point(end.x, start.y)

        waypoints = []
        if h_point != end:
            waypoints.append(h_point)

        return RoutingPath(
            start_point=start,
            end_point=end,
            waypoints=waypoints,
        )
```

**Testing Phase 3:**

```python
# tests/unit/test_wire_router.py

def test_connect_pins_basic(simple_schematic):
    """Test basic pin connection."""
    router = WireRouter(simple_schematic)

    result = router.connect_pins("R1", "2", "R2", "1")

    assert result.success
    assert result.wire_uuid is not None
    assert len(result.wire_points) >= 2

def test_connect_pins_invalid_source(simple_schematic):
    """Test connecting to non-existent source pin."""
    router = WireRouter(simple_schematic)

    result = router.connect_pins("R1", "99", "R2", "1")

    assert not result.success
    assert result.error_message is not None

def test_junction_detection(simple_schematic):
    """Test junction detection."""
    router = WireRouter(simple_schematic)

    # First connection: R1.2 -> R2.1
    result1 = router.connect_pins("R1", "2", "R2", "1")
    assert result1.success

    # Second connection that might cross first
    # (depends on component positions)
    result2 = router.connect_pins("R1", "1", "R2", "2")
    assert result2.success
```

---

### Phase 4: Integration (Est. 2 hours)

**File:** `kicad_sch_api/core/schematic.py` - Modify existing class

```python
"""Phase 4: Integrate services into Schematic class."""

class Schematic:
    def __init__(self, ...):
        # Existing code
        # ...

        # Add lazy-initialized services
        self._pin_discovery = None
        self._wire_router = None

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
    def get_component_pins(self, reference: str):
        """Get all pins for a component."""
        return self.pin_discovery.get_pins_info(reference)

    def connect_pins(self, from_comp, from_pin, to_comp, to_pin, options=None):
        """Connect two pins with a wire."""
        return self.wire_router.connect_pins(
            from_comp, from_pin, to_comp, to_pin, options
        )
```

**Create module init files:**

```python
# kicad_sch_api/pins/__init__.py
"""Pin discovery module."""

from .models import (
    PinInfo,
    PinType,
    PinShape,
    PinMatchResult,
    ComponentPins,
)
from .discovery import PinDiscovery
from .errors import PinError, PinNotFoundError

__all__ = [
    "PinInfo",
    "PinType",
    "PinShape",
    "PinMatchResult",
    "ComponentPins",
    "PinDiscovery",
    "PinError",
    "PinNotFoundError",
]
```

```python
# kicad_sch_api/routing/__init__.py
"""Wire routing module."""

from .models import (
    ConnectionResult,
    RoutingPath,
    RoutingAlgorithm,
    RoutingOptions,
)
from .router import WireRouter
from .junction_detector import JunctionDetector
from .grid import GridSnapping

__all__ = [
    "ConnectionResult",
    "RoutingPath",
    "RoutingAlgorithm",
    "RoutingOptions",
    "WireRouter",
    "JunctionDetector",
    "GridSnapping",
]
```

---

### Phase 5: Comprehensive Testing (Est. 4-5 hours)

**File:** `tests/conftest.py` - Create new

```python
"""Pytest fixtures for all tests."""

import pytest
import kicad_sch_api as ksa
from kicad_sch_api.pins import PinDiscovery
from kicad_sch_api.routing import WireRouter, RoutingOptions, RoutingAlgorithm
from kicad_sch_api.core.types import Point


@pytest.fixture
def simple_schematic():
    """Create 2-component schematic for testing."""
    sch = ksa.create_schematic("Test")

    r1 = sch.components.add(
        lib_id="Device:R",
        reference="R1",
        value="10k",
        position=(100, 100),
    )

    r2 = sch.components.add(
        lib_id="Device:R",
        reference="R2",
        value="10k",
        position=(150, 100),
    )

    return sch


@pytest.fixture
def pin_discovery(simple_schematic):
    """Create PinDiscovery service."""
    return PinDiscovery(simple_schematic)


@pytest.fixture
def wire_router(simple_schematic):
    """Create WireRouter service."""
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
```

**File:** `tests/unit/test_pin_discovery.py` - Create new

```python
"""Unit tests for pin discovery."""

import pytest
from kicad_sch_api.pins import PinDiscovery, PinNotFoundError


class TestPinDiscovery:
    """Test PinDiscovery service."""

    def test_get_pins_info_basic(self, pin_discovery, simple_schematic):
        """Test getting pins for a resistor."""
        pins = pin_discovery.get_pins_info("R1")

        assert len(pins.pins_by_number) == 2
        assert "1" in pins.pins_by_number
        assert "2" in pins.pins_by_number

    def test_get_pin_by_number(self, pin_discovery):
        """Test getting specific pin by number."""
        pins = pin_discovery.get_pins_info("R1")
        pin_1 = pins.get_pin("1")

        assert pin_1 is not None
        assert pin_1.pin_number == "1"
        assert pin_1.component_reference == "R1"

    def test_pin_not_found_error(self, pin_discovery):
        """Test error when component doesn't exist."""
        with pytest.raises(PinNotFoundError):
            pin_discovery.get_pins_info("R99")

    def test_match_pin_success(self, pin_discovery):
        """Test successful pin matching."""
        result = pin_discovery.match_pin("R1", "1")

        assert result.found
        assert result.pin_info is not None

    def test_match_pin_failure(self, pin_discovery):
        """Test pin matching with candidates."""
        result = pin_discovery.match_pin("R1", "99")

        assert not result.found
        assert len(result.candidates) > 0
```

**File:** `tests/unit/test_wire_router.py` - Create new

```python
"""Unit tests for wire routing."""

import pytest
from kicad_sch_api.routing import WireRouter, ConnectionResult


class TestWireRouter:
    """Test WireRouter service."""

    def test_connect_pins_basic(self, wire_router):
        """Test connecting two pins."""
        result = wire_router.connect_pins("R1", "2", "R2", "1")

        assert isinstance(result, ConnectionResult)
        assert result.success
        assert result.wire_uuid is not None

    def test_connect_pins_invalid_source(self, wire_router):
        """Test connecting with invalid source pin."""
        result = wire_router.connect_pins("R1", "99", "R2", "1")

        assert not result.success
        assert result.error_message is not None

    def test_Manhattan_routing(self, wire_router, routing_options):
        """Test Manhattan routing algorithm."""
        routing_options.algorithm = RoutingAlgorithm.MANHATTAN

        result = wire_router.connect_pins(
            "R1", "2", "R2", "1",
            options=routing_options
        )

        assert result.success
        # Manhattan should have 2-3 points (start, waypoint, end)
        assert len(result.wire_points) >= 2
```

---

## Implementation Order Summary

1. **Data Models (2h)** ✓
   - pins/models.py
   - routing/models.py
   - Create error modules

2. **Pin Discovery (4h)** ✓
   - Implement get_pins_info()
   - Implement helper methods
   - Add caching

3. **Routing Basics (5h)** ✓
   - GridSnapping (easy first)
   - JunctionDetector
   - WireRouter

4. **Integration (2h)** ✓
   - Add to Schematic class
   - Create module __init__.py files
   - Update main package

5. **Testing (4h)** ✓
   - Create conftest.py
   - Write unit tests
   - Write integration tests

**Total: ~17 hours of implementation work**

---

## Common Pitfalls and Solutions

### Pitfall 1: Circular Imports

**Problem:**
```python
# kicad_sch_api/routing/router.py
from ..core.schematic import Schematic  # ERROR: Schematic not defined yet

class WireRouter:
    def __init__(self, schematic: Schematic):
        self._schematic = schematic
```

**Solution:** Use string type hints and lazy imports
```python
# kicad_sch_api/routing/router.py
class WireRouter:
    def __init__(self, schematic: 'Schematic'):  # String type hint!
        self._schematic = schematic
```

### Pitfall 2: Missing Symbol Data

**Problem:**
```python
# Symbol library doesn't have the component
symbol_def = symbol_cache.get_symbol("CustomComponent:X1")  # Returns None
pin = symbol_def.pins[0]  # ERROR: NoneType has no pins
```

**Solution:** Always check before accessing
```python
symbol_def = symbol_cache.get_symbol(lib_id)
if symbol_def:
    for pin in symbol_def.pins:
        # Safe to access
else:
    # Use default values
    pin_type = PinType.UNSPECIFIED
```

### Pitfall 3: Grid Alignment Floating Point Errors

**Problem:**
```python
point = Point(100.0000001, 100.0000001)
grid.snap(point)  # Small errors accumulate

is_aligned = (x % grid_size == 0)  # Fails due to float precision
```

**Solution:** Always use tolerance for comparisons
```python
def is_aligned(self, point: Point, tolerance: float = 0.01) -> bool:
    snapped = self.snap(point)
    distance = point.distance_to(snapped)
    return distance < tolerance  # Tolerance-based
```

### Pitfall 4: Performance - Searching Without Indices

**Problem:**
```python
# O(n) search every time
for component in schematic.components:
    if component.reference == "R1":
        return component
```

**Solution:** Use built-in get() method which has index
```python
# O(1) lookup
component = schematic.components.get("R1")
```

### Pitfall 5: Cache Invalidation

**Problem:**
```python
pins = discovery.get_pins_info("R1")  # Cached
# ... user moves component ...
pins = discovery.get_pins_info("R1")  # Still returns old positions!
```

**Solution:** Clear cache when needed or document assumptions
```python
# Document that pin positions are based on component position at query time
# Or invalidate cache when component moves
def _on_component_moved(self, component_ref):
    if component_ref in self._component_pins_cache:
        del self._component_pins_cache[component_ref]
```

---

## Testing Quick Reference

```bash
# Run all unit tests
uv run pytest tests/unit/ -v

# Run specific test file
uv run pytest tests/unit/test_pin_discovery.py -v

# Run with coverage
uv run pytest tests/unit/ --cov=kicad_sch_api/pins --cov=kicad_sch_api/routing

# Run and stop on first failure
uv run pytest tests/unit/ -x

# Run with detailed output
uv run pytest tests/unit/ -vv -s
```

---

## Next Steps After Implementation

1. **Create Reference Test Schematics**
   - Use interactive pattern from CLAUDE.md
   - Create tests/reference_kicad_projects/pin_discovery/
   - Create tests/reference_kicad_projects/wire_routing/

2. **Add Integration Tests**
   - Test full workflows (create → place components → wire them)
   - Test round-trip (load → modify → save → load again)

3. **Update Documentation**
   - Add examples to CLAUDE.md
   - Create examples/pin_connection_example.py
   - Document in API docs

4. **Performance Optimization**
   - Profile with larger schematics
   - Optimize hot paths if needed
   - Benchmark against manual KiCAD

5. **Feature Additions**
   - Support for bus routing
   - Auto-routed connections
   - Connection validation rules

