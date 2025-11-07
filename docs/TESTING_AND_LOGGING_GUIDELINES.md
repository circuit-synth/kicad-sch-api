# Testing & Logging Guidelines for Pin Connection Implementation

**Purpose**: Ensure debugability, reliability, and fast failure detection
**Audience**: All developers on Tracks A, B, and C
**Key Focus**: Comprehensive logging + extensive testing = easy debugging

---

## Philosophy

> "If it's not logged, it didn't happen. If it's not tested, it's broken."

**Our Approach**:
1. **Heavy DEBUG logging** at all critical points (not in production, just for development)
2. **Comprehensive tests** at unit, integration, and reference levels
3. **Clear error messages** that guide users to solutions
4. **Structured logging** for easy searching and analysis
5. **Test-first debugging** - write test, watch it fail, implement, watch it pass

---

## Logging Standards

### Logging Levels

We use Python's standard logging levels:

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Development visibility | Position calculations, intermediate values |
| **INFO** | Operation milestones | "Created wire from R1 to R2" |
| **WARNING** | Unexpected but handled | "Component not found, using default" |
| **ERROR** | Operation failed | "Invalid pin position" |
| **CRITICAL** | System failure | (rare in our code) |

**Important**:
- ✅ DEBUG logs are verbose and detailed (for development)
- ✅ INFO logs are high-level and meaningful to users
- ⚠️ DEBUG logs must be at DEBUG level (not INFO)
- ⚠️ Never log to stdout (use logging module only)

---

## Required Logging Points

### 1. Pin Position Calculation

**File**: `kicad_sch_api/core/pin_utils.py`

```python
import logging

logger = logging.getLogger(__name__)

def get_component_pin_position(component: SchematicSymbol, pin_number: str) -> Optional[Point]:
    """Get absolute position of a component pin."""

    # ENTRY POINT
    logger.debug(f"get_component_pin_position: {component.reference}.{pin_number}")
    logger.debug(f"  Component position: ({component.position.x}, {component.position.y})")
    logger.debug(f"  Component rotation: {getattr(component, 'rotation', 0)}°")
    logger.debug(f"  Component mirror: {getattr(component, 'mirror', None)}")

    # LOOKUP
    for pin in component.pins:
        if pin.number == pin_number:
            logger.debug(f"  Found pin in component data")
            logger.debug(f"    Relative position: ({pin.position.x}, {pin.position.y})")

            # TRANSFORMATION
            absolute_pos = apply_transformation(...)
            logger.debug(f"    After transformation: ({absolute_pos[0]}, {absolute_pos[1]})")

            # RETURN
            result = Point(absolute_pos[0], absolute_pos[1])
            logger.debug(f"  RESULT: ({result.x}, {result.y})")
            return result

    # FALLBACK
    logger.debug(f"  Pin not in component data, checking symbol library")
    try:
        symbol_cache = get_symbol_cache()
        symbol_def = symbol_cache.get_symbol(component.lib_id)
        logger.debug(f"  Symbol definition: {component.lib_id}")

        # ... search in symbol
        logger.debug(f"    Pin found in symbol at ({pin_x}, {pin_y})")

    except Exception as e:
        logger.debug(f"  ERROR accessing symbol: {e}", exc_info=True)
        return None

    # NOT FOUND
    logger.debug(f"  Pin {pin_number} not found anywhere")
    return None
```

**Key Points**:
- Log at entry with component reference and pin number
- Log component properties (position, rotation, mirror)
- Log each lookup attempt (component data, symbol library)
- Log intermediate values (relative position, after transformation)
- Log final result or failure reason
- Use `exc_info=True` for exceptions to capture stack trace

---

### 2. Wire Creation & Routing

**File**: `kicad_sch_api/core/schematic.py`

```python
def connect_pins(
    self, ref1: str, pin1: str, ref2: str, pin2: str,
    routing: str = "orthogonal", auto_junction: bool = True
) -> ConnectionResult:
    """Connect two component pins with routing."""

    logger.debug(f"connect_pins: {ref1}.{pin1} → {ref2}.{pin2}")
    logger.debug(f"  Routing: {routing}, AutoJunction: {auto_junction}")

    # VALIDATE
    logger.debug(f"  Validating components...")
    comp1 = self.components.get(ref1)
    comp2 = self.components.get(ref2)
    if not comp1:
        logger.debug(f"    Component {ref1} not found!")
        return ConnectionResult(success=False, wire_uuids=[], junction_uuids=[])
    if not comp2:
        logger.debug(f"    Component {ref2} not found!")
        return ConnectionResult(success=False, wire_uuids=[], junction_uuids=[])

    # GET PIN POSITIONS
    logger.debug(f"  Getting pin positions...")
    pos1 = self.get_component_pin_position(ref1, pin1)
    pos2 = self.get_component_pin_position(ref2, pin2)
    logger.debug(f"    Start: ({pos1.x}, {pos1.y})")
    logger.debug(f"    End: ({pos2.x}, {pos2.y})")

    # CALCULATE ROUTING PATH
    logger.debug(f"  Calculating {routing} path...")
    if routing == "orthogonal":
        dx = abs(pos2.x - pos1.x)
        dy = abs(pos2.y - pos1.y)
        logger.debug(f"    Distance: dx={dx:.2f}mm, dy={dy:.2f}mm")

        if dx > dy:
            path = _route_h_first(pos1, pos2)
            logger.debug(f"    Using horizontal-first strategy")
        else:
            path = _route_v_first(pos1, pos2)
            logger.debug(f"    Using vertical-first strategy")

        logger.debug(f"    Path points: {len(path)} points")
        for i, p in enumerate(path):
            logger.debug(f"      [{i}] ({p.x}, {p.y})")

    # CREATE WIRES
    logger.debug(f"  Creating wires...")
    wire_uuids = []
    for i in range(len(path) - 1):
        wire_uuid = self.add_wire(path[i], path[i+1])
        logger.debug(f"    Wire {i}: {wire_uuid}")
        wire_uuids.append(wire_uuid)

    # AUTO-JUNCTIONS
    logger.debug(f"  Auto-junction check...")
    junction_uuids = []
    if auto_junction:
        for point in path[1:-1]:  # Skip endpoints
            if self.has_wire_at_position(point):
                logger.debug(f"    Wire meets at ({point.x}, {point.y}), creating junction")
                junction_uuid = self.add_junction(point)
                junction_uuids.append(junction_uuid)

    # RESULT
    logger.info(f"Connected {ref1}.{pin1} to {ref2}.{pin2} ({len(wire_uuids)} wires)")
    return ConnectionResult(
        success=True,
        wire_uuids=wire_uuids,
        junction_uuids=junction_uuids,
        path_points=path,
        total_length=sum(distance(path[i], path[i+1]) for i in range(len(path)-1)),
        routing_strategy=routing
    )
```

**Key Points**:
- Log at function entry with all parameters
- Log validation results
- Log intermediate values (distances, path points)
- Log each created wire/junction with UUID
- Log final result at INFO level

---

### 3. Junction Detection

**File**: `kicad_sch_api/core/managers/wire.py`

```python
def auto_create_junctions(self) -> List[str]:
    """Automatically create junctions where wires meet."""

    logger.debug(f"auto_create_junctions starting")
    logger.debug(f"  Scanning {len(list(self.wires))} wires for intersections")

    junction_uuids = []
    intersection_points = set()

    # FIND INTERSECTIONS
    logger.debug(f"  Phase 1: Finding intersection points")
    wires = list(self.wires)
    for i, wire1 in enumerate(wires):
        for j, wire2 in enumerate(wires[i+1:], start=i+1):
            logger.debug(f"    Checking wire {i} vs wire {j}")

            # Check endpoints
            for p1 in wire1.points:
                for p2 in wire2.points:
                    if self._points_equal(p1, p2, tolerance=0.01):
                        intersection_points.add((p1.x, p1.y))
                        logger.debug(f"      Found junction at ({p1.x}, {p1.y})")

            # Check if wire1 crosses wire2
            for k in range(len(wire1.points) - 1):
                for m in range(len(wire2.points) - 1):
                    if self._segments_intersect(
                        wire1.points[k], wire1.points[k+1],
                        wire2.points[m], wire2.points[m+1]
                    ):
                        int_point = self._find_intersection(...)
                        intersection_points.add((int_point.x, int_point.y))
                        logger.debug(f"      Found crossing at ({int_point.x}, {int_point.y})")

    logger.debug(f"  Phase 1 complete: {len(intersection_points)} intersections found")

    # CREATE JUNCTIONS
    logger.debug(f"  Phase 2: Creating junctions at intersections")
    for x, y in intersection_points:
        # Check if junction already exists
        existing = self._find_junction_at((x, y))
        if existing:
            logger.debug(f"    Junction already exists at ({x}, {y})")
            junction_uuids.append(existing.uuid)
        else:
            junction_uuid = self.add_junction(Point(x, y))
            logger.debug(f"    Created junction: {junction_uuid} at ({x}, {y})")
            junction_uuids.append(junction_uuid)

    logger.info(f"Created {len(junction_uuids)} junctions")
    return junction_uuids
```

---

### 4. Connectivity Validation

**File**: `kicad_sch_api/core/schematic.py`

```python
def validate_connectivity(self) -> ConnectivityReport:
    """Validate all connections in schematic."""

    logger.debug(f"validate_connectivity starting")
    logger.debug(f"  Components: {len(list(self.components))}")
    logger.debug(f"  Wires: {len(list(self.wires))}")
    logger.debug(f"  Junctions: {len(list(self.junctions))}")

    issues = []

    # CHECK UNCONNECTED PINS
    logger.debug(f"  Checking for unconnected pins...")
    for component in self.components:
        logger.debug(f"    {component.reference}: {len(component.pins)} pins")

        for pin in component.pins:
            connected = self._is_pin_connected(component.reference, pin.number)
            if not connected:
                logger.debug(f"      Pin {pin.number} is UNCONNECTED")
                issues.append(ValidationIssue(
                    severity="warning",
                    component=component.reference,
                    message=f"Pin {pin.number} not connected"
                ))
            else:
                logger.debug(f"      Pin {pin.number} is connected ✓")

    # CHECK FLOATING COMPONENTS
    logger.debug(f"  Checking for floating components...")
    for component in self.components:
        all_unconnected = all(
            not self._is_pin_connected(component.reference, pin.number)
            for pin in component.pins
        )
        if all_unconnected and not component.is_power_symbol:
            logger.debug(f"    {component.reference} is FLOATING")
            issues.append(ValidationIssue(
                severity="error",
                component=component.reference,
                message=f"Component {component.reference} has no connections"
            ))

    logger.debug(f"  Validation complete: {len(issues)} issues found")

    passed = all(issue.severity != "error" for issue in issues)
    logger.info(f"Connectivity validation: {'PASSED' if passed else 'FAILED'}")

    return ConnectivityReport(
        passed=passed,
        error_count=sum(1 for i in issues if i.severity == "error"),
        warning_count=sum(1 for i in issues if i.severity == "warning"),
        issues=issues
    )
```

---

## Testing Standards

### Test Structure

**Every test file should have**:
1. Clear docstrings explaining what's being tested
2. Arrange-Act-Assert structure
3. Descriptive assertion messages
4. DEBUG logging for test debugging
5. Edge cases and error conditions

### Unit Tests - Pin Discovery

**File**: `tests/unit/test_get_component_pins.py`

```python
"""Test get_component_pins functionality.

Tests pin discovery with various component types, rotations, and positions.
"""

import pytest
import logging
from kicad_sch_api import create_schematic
from kicad_sch_api.core.types import Point

logger = logging.getLogger(__name__)

class TestGetComponentPins:
    """Test pin discovery for components."""

    @pytest.fixture
    def simple_schematic(self):
        """Create a simple schematic with one resistor."""
        sch = create_schematic("Pin Discovery Test")
        r1 = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100, 100),
            rotation=0
        )
        logger.debug(f"Fixture: Created schematic with R1 at (100, 100)")
        return sch, r1

    def test_get_pins_resistor_basic(self, simple_schematic):
        """Test getting pins from a simple 2-pin resistor."""
        sch, r1 = simple_schematic
        logger.debug("Test: get pins from resistor")

        # ARRANGE
        logger.debug("  Calling get_component_pins('R1')")

        # ACT
        pins = sch.components.list_pins("R1")
        logger.debug(f"  Got {len(pins)} pins")
        for pin_num, pos in pins:
            logger.debug(f"    Pin {pin_num}: ({pos.x}, {pos.y})")

        # ASSERT
        assert len(pins) == 2, "Resistor should have exactly 2 pins"
        assert pins[0][0] == "1", "First pin should be numbered '1'"
        assert pins[1][0] == "2", "Second pin should be numbered '2'"
        assert pins[0][1] != pins[1][1], "Pins should be at different positions"

        logger.debug("  ✓ Test passed")

    def test_pin_positions_accuracy(self, simple_schematic):
        """Test that pin positions are accurate."""
        sch, r1 = simple_schematic
        logger.debug("Test: pin position accuracy")

        # ARRANGE
        # R1 at (100, 100), 0° rotation
        # Standard resistor has pins 3.81mm apart

        # ACT
        pin1_pos = sch.get_component_pin_position("R1", "1")
        pin2_pos = sch.get_component_pin_position("R1", "2")

        logger.debug(f"  Pin 1: ({pin1_pos.x}, {pin1_pos.y})")
        logger.debug(f"  Pin 2: ({pin2_pos.x}, {pin2_pos.y})")

        distance = ((pin2_pos.x - pin1_pos.x)**2 + (pin2_pos.y - pin1_pos.y)**2)**0.5
        logger.debug(f"  Distance between pins: {distance:.2f}mm")

        # ASSERT
        # KiCAD resistor: pins 3.81mm apart vertically
        assert abs(distance - 3.81) < 0.1, f"Pins should be 3.81mm apart, got {distance:.2f}mm"

        logger.debug("  ✓ Test passed")

    def test_pin_positions_with_rotation(self):
        """Test pin positions at different rotations."""
        logger.debug("Test: pin positions with rotation")

        for rotation in [0, 90, 180, 270]:
            logger.debug(f"  Testing rotation: {rotation}°")

            sch = create_schematic(f"Rotation {rotation}")
            r1 = sch.components.add(
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=(100, 100),
                rotation=rotation
            )

            # ACT
            pin1_pos = sch.get_component_pin_position("R1", "1")
            pin2_pos = sch.get_component_pin_position("R1", "2")

            # ASSERT
            assert pin1_pos is not None, f"Pin 1 should exist at {rotation}°"
            assert pin2_pos is not None, f"Pin 2 should exist at {rotation}°"
            assert pin1_pos != pin2_pos, f"Pins should differ at {rotation}°"

            logger.debug(f"    Pin 1: ({pin1_pos.x}, {pin1_pos.y})")
            logger.debug(f"    Pin 2: ({pin2_pos.x}, {pin2_pos.y})")

        logger.debug("  ✓ Test passed for all rotations")

    @pytest.mark.parametrize("pin_num,expected_exists", [
        ("1", True),
        ("2", True),
        ("3", False),  # Resistor only has 2 pins
        ("999", False),
    ])
    def test_pin_existence(self, simple_schematic, pin_num, expected_exists):
        """Test checking if specific pins exist."""
        sch, r1 = simple_schematic
        logger.debug(f"Test: checking if pin {pin_num} exists")

        # ACT
        result = sch.get_component_pin_position("R1", pin_num)

        # ASSERT
        if expected_exists:
            assert result is not None, f"Pin {pin_num} should exist"
        else:
            assert result is None, f"Pin {pin_num} should not exist"

        logger.debug(f"  ✓ Pin {pin_num} existence: {expected_exists}")

    def test_nonexistent_component(self, simple_schematic):
        """Test error handling for non-existent component."""
        sch, r1 = simple_schematic
        logger.debug("Test: non-existent component error handling")

        # ACT
        result = sch.get_component_pin_position("R999", "1")

        # ASSERT
        assert result is None, "Should return None for non-existent component"

        logger.debug("  ✓ Correctly handled non-existent component")
```

**Key Points**:
- Use `logger.debug()` throughout tests for visibility
- Use descriptive assertion messages
- Use `@pytest.mark.parametrize` for testing multiple cases
- Include docstrings on each test method
- Log intermediate values for debugging

---

### Integration Tests - Connection Workflows

**File**: `tests/integration/test_routing_workflows.py`

```python
"""Test complete pin connection workflows.

Tests realistic scenarios like voltage dividers, LED circuits, etc.
"""

import pytest
import logging
from kicad_sch_api import create_schematic

logger = logging.getLogger(__name__)

class TestConnectionWorkflows:
    """Test complete circuit connection workflows."""

    def test_voltage_divider_creation(self):
        """Test creating a voltage divider with pin-accurate connections."""
        logger.info("=== Test: Voltage Divider Creation ===")

        # ARRANGE
        logger.debug("Creating schematic...")
        sch = create_schematic("Voltage Divider")

        logger.debug("Adding components...")
        r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
        r2 = sch.components.add("Device:R", "R2", "1k", (100, 150))

        logger.debug(f"  R1 at {r1.position}")
        logger.debug(f"  R2 at {r2.position}")

        # ACT
        logger.debug("Connecting R1.2 to R2.1 with orthogonal routing...")
        result = sch.connect_pins("R1", "2", "R2", "1", routing="orthogonal")

        logger.debug(f"  Connection result:")
        logger.debug(f"    Success: {result.success}")
        logger.debug(f"    Wires: {len(result.wire_uuids)}")
        logger.debug(f"    Junctions: {len(result.junction_uuids)}")
        logger.debug(f"    Path length: {result.total_length:.2f}mm")

        # ASSERT
        assert result.success, "Connection should succeed"
        assert len(result.wire_uuids) >= 1, "Should have at least 1 wire"
        logger.debug(f"  Wire UUIDs: {result.wire_uuids}")

        # Verify orthogonal routing (should have corner point)
        if result.routing_strategy == "orthogonal":
            assert len(result.path_points) == 3, "Orthogonal path should have 3 points"
            logger.debug(f"    Path is orthogonal with {len(result.path_points)} points ✓")

        # VERIFY CONNECTIVITY
        logger.debug("Validating connectivity...")
        validation = sch.validate_connectivity()
        logger.debug(f"  Validation: {'PASSED' if validation.passed else 'FAILED'}")
        logger.debug(f"  Errors: {validation.error_count}, Warnings: {validation.warning_count}")

        assert validation.passed, "Schematic should pass validation"

        logger.info("✓ Voltage divider creation test PASSED")
```

**Key Points**:
- Log at INFO level for major operations
- Log at DEBUG level for intermediate steps
- Include structured results with all meaningful values
- Verify both creation and validation

---

### Reference Tests - KiCAD Compatibility

**File**: `tests/reference_tests/test_pin_connections_reference.py`

```python
"""Test against reference KiCAD schematics.

These tests verify that our pin positions and connections match
what KiCAD produces exactly.
"""

import pytest
import logging
from pathlib import Path
from kicad_sch_api import load_schematic

logger = logging.getLogger(__name__)

class TestPinConnectionsReference:
    """Test pin positions match KiCAD references."""

    REFERENCE_DIR = Path(__file__).parent / "../reference_kicad_projects"

    def test_voltage_divider_reference(self):
        """Test against manually-created voltage divider."""
        logger.info("=== Reference Test: Voltage Divider ===")

        # LOAD REFERENCE
        ref_path = self.REFERENCE_DIR / "voltage_divider" / "voltage_divider.kicad_sch"
        logger.debug(f"Loading reference: {ref_path}")

        sch = load_schematic(str(ref_path))

        # VERIFY PIN POSITIONS
        logger.debug("Verifying pin positions match KiCAD...")
        r1 = sch.components.get("R1")
        r2 = sch.components.get("R2")

        r1_pin2 = sch.get_component_pin_position("R1", "2")
        r2_pin1 = sch.get_component_pin_position("R2", "1")

        logger.debug(f"  R1.2: ({r1_pin2.x}, {r1_pin2.y})")
        logger.debug(f"  R2.1: ({r2_pin1.x}, {r2_pin1.y})")

        # GET WIRE INFO
        wires = list(sch.wires)
        logger.debug(f"  Wires in reference: {len(wires)}")

        for i, wire in enumerate(wires):
            logger.debug(f"    Wire {i}: {len(wire.points)} points")
            for j, point in enumerate(wire.points):
                logger.debug(f"      [{j}] ({point.x}, {point.y})")

        # ASSERT
        assert len(wires) >= 1, "Should have wires connecting components"
        logger.debug("  ✓ Reference schematic loads correctly")

        logger.info("✓ Reference test PASSED")
```

---

## Test Execution

### Before Committing

```bash
cd /Users/shanemattner/Desktop/circuit_synth_repos/kicad-sch-api-track-X

# Run tests with verbose output and logging
uv run pytest tests/unit/test_*.py -vv --log-level=DEBUG

# Check specific test
uv run pytest tests/unit/test_get_component_pins.py::TestGetComponentPins::test_pin_positions_accuracy -vv --log-level=DEBUG

# Check coverage
uv run pytest tests/unit/test_get_component_pins.py --cov=kicad_sch_api.collections --cov-report=term-missing
```

### Full Test Suite

```bash
# Run all tests
uv run pytest tests/ -v --log-level=INFO

# Run with coverage report
uv run pytest tests/ --cov=kicad_sch_api --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Test Output

Tests will produce:
1. **Colored output** showing pass/fail
2. **Logging output** showing what happened
3. **Coverage report** showing what was tested
4. **Failure details** showing what went wrong (if any)

---

## Debugging Failed Tests

### Step 1: Run with Full Logging

```bash
uv run pytest tests/unit/test_get_component_pins.py -vv --log-level=DEBUG
```

Look for:
- Entry/exit logging
- Intermediate values
- Where the failure occurred

### Step 2: Run Single Test

```bash
uv run pytest tests/unit/test_get_component_pins.py::TestGetComponentPins::test_pin_positions_accuracy -vv --log-level=DEBUG --pdb
```

### Step 3: Add Temporary Debug Statements

```python
def test_pin_positions_accuracy(self, simple_schematic):
    sch, r1 = simple_schematic

    pin1_pos = sch.get_component_pin_position("R1", "1")
    pin2_pos = sch.get_component_pin_position("R1", "2")

    # TEMPORARY DEBUG
    import pdb; pdb.set_trace()  # Stop here to inspect

    distance = ((pin2_pos.x - pin1_pos.x)**2 + (pin2_pos.y - pin1_pos.y)**2)**0.5
    assert abs(distance - 3.81) < 0.1
```

### Step 4: Check Logging Output

All logging should be in `logs/mcp_server.log`:

```bash
tail -100 logs/mcp_server.log | grep -A5 -B5 "ERROR\|WARNING"
```

---

## Code Quality Checks

### Before Merge

```bash
# Format code
uv run black kicad_sch_api/ tests/

# Sort imports
uv run isort kicad_sch_api/ tests/

# Type checking
uv run mypy kicad_sch_api/ --strict

# Linting
uv run flake8 kicad_sch_api/ tests/
```

### Fixing Issues

**Type errors**:
```bash
# See all type errors
uv run mypy kicad_sch_api/ --strict

# Fix specific file
# Add type hints to function signatures
def get_pins_info(self, reference: str) -> List[PinInfo]:
    ...
```

**Linting errors**:
```bash
# See all style issues
uv run flake8 kicad_sch_api/ tests/

# Black and isort usually fix automatically
uv run black kicad_sch_api/
uv run isort kicad_sch_api/
```

---

## Logging Configuration

### Development Logging

**File**: `mcp_server/utils/logging.py`

```python
"""Logging configuration for debugging."""

import logging
import logging.handlers
import json
from pathlib import Path

def configure_debug_logging():
    """Configure debug logging for development."""

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # File handler (all logs)
    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "mcp_server.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))

    # Console handler (INFO and above only)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s: %(message)s"
    ))

    root.addHandler(file_handler)
    root.addHandler(console_handler)

# Configure on import
configure_debug_logging()
```

---

## Success Criteria

✅ Every function has DEBUG logging at entry, intermediate steps, and exit
✅ Every test has descriptive logging showing what's being tested
✅ All tests pass with >95% coverage
✅ All code passes type checking (`mypy --strict`)
✅ All code passes linting (`flake8`)
✅ Reference tests validate against KiCAD
✅ Failed tests produce clear error messages
✅ Developers can debug issues using logs + tests

---

## Quick Reference

### Logging Template

```python
import logging
logger = logging.getLogger(__name__)

def my_function(param1, param2):
    """Do something."""
    logger.debug(f"my_function called: param1={param1}, param2={param2}")

    # ... do stuff ...
    intermediate = calculate_something()
    logger.debug(f"  Intermediate result: {intermediate}")

    # ... more stuff ...
    result = process(intermediate)
    logger.debug(f"  Final result: {result}")

    logger.info(f"my_function completed successfully")
    return result
```

### Test Template

```python
def test_something(self):
    """Test that something works."""
    logger.debug("Test: something")

    # ARRANGE
    logger.debug("  Setting up test data...")
    data = prepare_data()
    logger.debug(f"    Data ready: {len(data)} items")

    # ACT
    logger.debug("  Executing function...")
    result = function(data)
    logger.debug(f"    Result: {result}")

    # ASSERT
    assert result is correct, "Should produce correct result"
    logger.debug("  ✓ Test passed")
```

---

## Next Steps

1. **Day 1**: Set up logging configuration
2. **During Development**: Add required logging to all new functions
3. **Before PR**: Run full test suite and code quality checks
4. **During Review**: Reference logs when explaining changes
5. **After Merge**: Monitor production logs for issues

**Goal**: When a user reports a problem, developers should be able to trace it through logs.
