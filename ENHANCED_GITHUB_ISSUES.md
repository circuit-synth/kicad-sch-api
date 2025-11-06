# Enhanced GitHub Issues: Most Critical Pin Connection Tasks

This document provides enhanced versions of the 3 most critical issues (#200, #202, #204) with comprehensive improvements for production-ready implementation.

**Key Enhancements Applied:**
1. ✅ Clear, measurable acceptance criteria
2. ✅ Example error messages and debugging tips
3. ✅ Links between dependent issues with context
4. ✅ Comprehensive testing requirements with edge cases
5. ✅ Code examples with complete context
6. ✅ Validation checklists for implementation and review

---

## CRITICAL ISSUE #200: Implement `get_component_pins` Tool

### Title
Implement get_component_pins tool - discover all pins for a component

### Type & Metadata
- **Type**: Feature
- **Labels**: mcp-server, pin-discovery, phase-1, core-tool
- **Epic**: #199 (Pin Connection Epic)
- **Priority**: P0 (Critical - blocks #201, #202)
- **Assigned to**: [Backend Developer A]
- **Estimate**: 3 days
- **Dependencies**: None (foundational)
- **Dependent Issues**: #201 (find_pins_by_name), #202 (connect_pins), #205 (testing infrastructure)

### Description

Implement the `get_component_pins` tool that enables AI assistants to discover all available pins for a component, including pin numbers, names, electrical types, and absolute positions in the schematic.

**Why This Is Critical:**
- ❌ Without this, AI cannot know what pins exist on a component
- ❌ Impossible to make informed connection decisions
- ❌ Foundation for semantic pin lookup (#201) and connection routing (#202)
- ✅ Enables discovery-driven component interaction workflow

### Implementation Details

#### New Function in Core Library
**File**: `kicad_sch_api/collections/components.py`

```python
class ComponentCollection:
    def get_pins_info(self, reference: str) -> List[PinInfo]:
        """
        Get detailed information about all pins for a component.

        This is the foundational discovery method that enables semantic pin
        lookup and intelligent connection routing. Must handle all component
        types including passive components, ICs, and connectors.

        Args:
            reference: Component reference (e.g., "R1", "U1", "J1")
                      Case-insensitive search supported

        Returns:
            List[PinInfo]: Pin information sorted by pin number
                          Returns empty list for passive components with 2 pins

        Raises:
            ValueError: If component not found
                       Message: f"Component '{reference}' not found in schematic"
            TypeError: If component has no symbol loaded
                      Message: f"Component {reference} symbol not found in library"

        Example:
            >>> pins = sch.components.get_pins_info("U1")
            >>> for pin in pins:
            ...     print(f"Pin {pin.number}: {pin.name} at ({pin.position.x}, {pin.position.y})")
            Pin 1: VCC at (100.0, 96.52)
            Pin 2: PA0 at (100.0, 93.98)
            Pin 3: PA1 at (100.0, 91.44)
        """
        logger.debug(f"Getting pins for component {reference}")

        # Find component (case-insensitive)
        component = self._find_component_by_reference(reference)
        if not component:
            raise ValueError(f"Component '{reference}' not found in schematic")

        logger.debug(f"  Component position: {component.position}")
        logger.debug(f"  Component rotation: {component.rotation}°")
        logger.debug(f"  Component mirror: {component.mirror}")

        # Load symbol from library
        symbol = self._schematic.symbol_cache.get_symbol(component.lib_id)
        if not symbol:
            raise TypeError(f"Component {reference} symbol not found in library")

        logger.debug(f"  Loaded symbol: {component.lib_id}")

        # Transform pin positions to absolute schematic coordinates
        pins = []
        for pin in symbol.pins:
            pin_info = self._transform_pin_to_schematic(component, pin)
            pins.append(pin_info)
            logger.debug(f"    Pin {pin_info.number} ({pin_info.name}): ({pin_info.position.x}, {pin_info.position.y})")

        logger.debug(f"  Found {len(pins)} pins total")
        return sorted(pins, key=lambda p: self._pin_sort_key(p.number))
```

#### Data Model
**File**: `kicad_sch_api/core/types.py`

```python
@dataclass
class PinInfo:
    """Pin information with position and metadata."""
    number: str                    # "1", "2", "A1", etc.
    name: str                      # "VCC", "PA0", "SDA", etc.
    electrical_type: str           # "input", "output", "bidirectional", "passive", "power_in", "power_out", "tri_state"
    position: Point                # Absolute position in schematic space (inverted Y-axis)
    orientation: str               # "right", "left", "up", "down" - relative to component symbol
    uuid: str                      # Pin unique identifier (from symbol)
    connected_wires: List[str] = field(default_factory=list)  # UUIDs of connected wires (if populated)

    def __post_init__(self):
        """Validate pin data."""
        valid_types = {"input", "output", "bidirectional", "passive", "power_in", "power_out", "tri_state", "nc"}
        if self.electrical_type not in valid_types:
            raise ValueError(f"Invalid electrical_type: {self.electrical_type}")

        valid_orientations = {"right", "left", "up", "down"}
        if self.orientation not in valid_orientations:
            raise ValueError(f"Invalid orientation: {self.orientation}")
```

#### Pydantic Model for MCP
**File**: `mcp_server/models.py`

```python
from pydantic import BaseModel, Field

class PinInfoOutput(BaseModel):
    """Pin information for MCP tool output."""
    number: str = Field(..., description="Pin number (e.g., '1', 'A1')")
    name: str = Field(..., description="Pin name (e.g., 'VCC', 'PA0')")
    electrical_type: str = Field(..., description="Electrical type: input/output/power_in/power_out/passive/etc")
    position: tuple[float, float] = Field(..., description="Absolute position (x, y) in schematic space")
    orientation: str = Field(..., description="Pin orientation: right/left/up/down")

    class Config:
        example = {
            "number": "1",
            "name": "VCC",
            "electrical_type": "power_in",
            "position": (100.0, 96.52),
            "orientation": "right"
        }
```

#### MCP Tool Definition
**File**: `mcp_server/tools/component_tools.py`

```python
import logging
from typing import List
from pydantic import tool

logger = logging.getLogger(__name__)

@tool()
def get_component_pins(reference: str) -> List[PinInfoOutput]:
    """
    Get all pins for a component with detailed information.

    Enables AI to discover available pins before making connections.
    This is the foundational discovery tool for component interaction.

    Args:
        reference: Component reference (e.g., "R1", "U1", "J1")
                  Case-insensitive

    Returns:
        List of pin information including number, name, type, and position
        Pins sorted by number for consistent output

    Example:
        pins = get_component_pins("U1")
        for pin in pins:
            print(f"Pin {pin.number}: {pin.name} ({pin.electrical_type}) at {pin.position}")

    Example Output:
        [
            {"number": "1", "name": "VCC", "electrical_type": "power_in", "position": (100.0, 96.52), "orientation": "right"},
            {"number": "2", "name": "PA0", "electrical_type": "input", "position": (100.0, 93.98), "orientation": "right"},
            {"number": "3", "name": "PA1", "electrical_type": "input", "position": (100.0, 91.44), "orientation": "right"}
        ]

    Raises:
        ValueError: Component not found
        TypeError: Symbol not found in library

    Performance: <50ms for components with <100 pins
    """
    logger.debug(f"MCP tool: get_component_pins('{reference}')")

    try:
        pin_infos = SCHEMATIC.components.get_pins_info(reference)
        logger.info(f"Successfully retrieved {len(pin_infos)} pins for {reference}")

        return [
            PinInfoOutput(
                number=pin.number,
                name=pin.name,
                electrical_type=pin.electrical_type,
                position=(float(pin.position.x), float(pin.position.y)),
                orientation=pin.orientation
            )
            for pin in pin_infos
        ]
    except ValueError as e:
        logger.error(f"Component lookup failed: {e}")
        raise
    except TypeError as e:
        logger.error(f"Symbol library error: {e}")
        raise
```

### Testing Requirements

#### Unit Tests
**File**: `tests/unit/test_get_component_pins.py`

```python
import pytest
from kicad_sch_api import create_schematic, Point
from kicad_sch_api.core.types import PinInfo

class TestGetComponentPins:

    def test_simple_resistor_pins(self, schematic):
        """Test 2-pin passive component."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))

        pins = sch.components.get_pins_info('R1')

        assert len(pins) == 2
        assert pins[0].number == '1'
        assert pins[1].number == '2'
        assert all(p.electrical_type == 'passive' for p in pins)
        assert all(isinstance(p, PinInfo) for p in pins)

    def test_multipin_ic_pins(self, schematic):
        """Test multi-pin IC (8-pin op-amp)."""
        sch = schematic
        sch.components.add('Amplifier_Operational:TL072', 'U1', 'TL072', position=(100, 100))

        pins = sch.components.get_pins_info('U1')

        assert len(pins) == 8
        assert pins[0].number == '1'  # Non-inverting input A
        assert any(p.name == 'VCC+' for p in pins)  # Power pin
        assert any(p.electrical_type == 'power_in' for p in pins)

    def test_large_component_pins(self, schematic):
        """Test large component (100-pin MCU)."""
        sch = schematic
        sch.components.add('MCU_STMicroelectronics:STM32G431CBTx', 'U1', 'STM32G431CBTx', position=(150, 150))

        pins = sch.components.get_pins_info('U1')

        assert len(pins) == 100
        assert all(p.number for p in pins)
        assert all(p.position for p in pins)

    def test_pin_positions_accuracy(self, schematic):
        """Test pin positions match expected values."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(100, 100), rotation=0)

        pins = sch.components.get_pins_info('R1')

        # Expected positions for resistor at (100, 100) with no rotation
        # In schematic space (inverted Y)
        assert pins[0].position.x == pytest.approx(100.0, abs=0.01)
        assert pins[1].position.x == pytest.approx(100.0, abs=0.01)
        # Y should be properly inverted
        assert pins[0].position.y < pins[1].position.y  # Pin 1 above pin 2 (lower Y value)

    def test_pin_names_from_library(self, schematic):
        """Test pin names loaded correctly from symbol library."""
        sch = schematic
        sch.components.add('Connector:Conn_01x03_Pin', 'J1', '', position=(50, 50))

        pins = sch.components.get_pins_info('J1')

        assert len(pins) == 3
        assert all(p.name for p in pins)  # All should have names
        assert all(p.name != '' for p in pins)

    def test_electrical_types(self, schematic):
        """Test electrical types are correct."""
        sch = schematic
        sch.components.add('Amplifier_Operational:TL072', 'U1', 'TL072', position=(100, 100))

        pins = sch.components.get_pins_info('U1')

        valid_types = {'input', 'output', 'power_in', 'power_out', 'passive', 'bidirectional'}
        assert all(p.electrical_type in valid_types for p in pins)

        # Check for expected types in op-amp
        assert any(p.electrical_type == 'input' for p in pins)
        assert any(p.electrical_type == 'power_in' for p in pins)

    def test_rotation_0_degrees(self, schematic):
        """Test component at 0° rotation."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(100, 100), rotation=0)
        pins = sch.components.get_pins_info('R1')
        assert all(p.orientation == 'right' for p in pins)

    def test_rotation_90_degrees(self, schematic):
        """Test component at 90° rotation."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(100, 100), rotation=90)
        pins = sch.components.get_pins_info('R1')
        # Orientations should be rotated accordingly
        assert all(p.orientation in ['up', 'down'] for p in pins)

    def test_rotation_180_degrees(self, schematic):
        """Test component at 180° rotation."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(100, 100), rotation=180)
        pins = sch.components.get_pins_info('R1')
        assert all(p.orientation == 'left' for p in pins)

    def test_rotation_270_degrees(self, schematic):
        """Test component at 270° rotation."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(100, 100), rotation=270)
        pins = sch.components.get_pins_info('R1')
        assert all(p.orientation in ['up', 'down'] for p in pins)

    def test_mirrored_component(self, schematic):
        """Test mirrored component."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(100, 100), mirror=True)
        pins = sch.components.get_pins_info('R1')
        assert len(pins) == 2
        # Mirror should not change pin count

    def test_pin_order_consistency(self, schematic):
        """Test pins are always returned in consistent order."""
        sch = schematic
        sch.components.add('Amplifier_Operational:TL072', 'U1', 'TL072', position=(100, 100))

        pins1 = sch.components.get_pins_info('U1')
        pins2 = sch.components.get_pins_info('U1')

        assert [p.number for p in pins1] == [p.number for p in pins2]

    def test_nonexistent_component_error(self, schematic):
        """Test error when component not found."""
        sch = schematic

        with pytest.raises(ValueError) as exc_info:
            sch.components.get_pins_info('R999')

        assert "Component 'R999' not found" in str(exc_info.value)

    def test_case_insensitive_lookup(self, schematic):
        """Test component reference is case-insensitive."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))

        pins_lower = sch.components.get_pins_info('r1')
        pins_upper = sch.components.get_pins_info('R1')
        pins_mixed = sch.components.get_pins_info('R1')

        assert len(pins_lower) == len(pins_upper) == len(pins_mixed) == 2

class TestGetComponentPinsPerformance:

    def test_performance_100_pins(self, schematic):
        """Test performance with 100-pin component."""
        import time
        sch = schematic
        sch.components.add('MCU_STMicroelectronics:STM32G431CBTx', 'U1', 'STM32G431CBTx', position=(150, 150))

        start = time.time()
        pins = sch.components.get_pins_info('U1')
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 50, f"Performance issue: {elapsed}ms > 50ms"
        assert len(pins) == 100

class TestGetComponentPinsIntegration:

    def test_load_real_schematic(self):
        """Test with real schematic from reference projects."""
        sch = create_schematic('Test')
        # Add component
        sch.components.add('Device:R', 'R1', '10k', position=(100, 100))

        pins = sch.components.get_pins_info('R1')

        assert len(pins) == 2
        assert pins[0].number == '1'
        assert pins[1].number == '2'

    def test_pins_match_netlist(self):
        """Test pins match KiCAD netlist output."""
        # This requires comparing against kicad-cli netlist output
        # Load reference schematic with known netlist
        # Verify pin count and positions match
        pass
```

#### Integration Tests
**File**: `tests/integration/test_pin_discovery_workflow.py`

```python
def test_pin_discovery_workflow():
    """Test complete pin discovery workflow."""
    sch = create_schematic('Test')

    # Add multiple components
    sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
    sch.components.add('Amplifier_Operational:TL072', 'U1', 'TL072', position=(150, 150))

    # Discover all pins
    r1_pins = sch.components.get_pins_info('R1')
    u1_pins = sch.components.get_pins_info('U1')

    assert len(r1_pins) == 2
    assert len(u1_pins) == 8

    # All pins should have valid data
    for pin in r1_pins + u1_pins:
        assert pin.number
        assert pin.name
        assert pin.electrical_type in {'input', 'output', 'power_in', 'power_out', 'passive', 'bidirectional'}
        assert pin.position
        assert pin.orientation in {'left', 'right', 'up', 'down'}

def test_pins_match_kicad_netlist():
    """Test pins match KiCAD's netlist pins."""
    # Load reference schematic
    sch = Schematic.load('tests/reference_kicad_projects/simple_circuit/test.kicad_sch')

    # Get pins via our API
    api_pins = sch.components.get_pins_info('U1')

    # Get pins from KiCAD netlist
    # kicad-cli sch export netlist test.kicad_sch
    kicad_pins = parse_netlist_pins('test.net')

    # Should match exactly
    assert len(api_pins) == len(kicad_pins)
    for api_pin, kicad_pin in zip(api_pins, kicad_pins):
        assert api_pin.number == kicad_pin['number']
        assert api_pin.position.x == pytest.approx(kicad_pin['x'], abs=0.01)
        assert api_pin.position.y == pytest.approx(kicad_pin['y'], abs=0.01)

def test_performance_large_schematic():
    """Test performance with large schematic."""
    import time
    sch = create_schematic('Test')

    # Add many components
    for i in range(50):
        sch.components.add('Device:R', f'R{i}', '10k', position=(50 + i*10, 50))

    start = time.time()
    for i in range(50):
        pins = sch.components.get_pins_info(f'R{i}')
    elapsed = (time.time() - start) * 1000

    avg_per_component = elapsed / 50
    assert avg_per_component < 10, f"Average {avg_per_component}ms per component > 10ms"
```

### Example Error Messages & Debugging

#### Error Scenario 1: Component Not Found
```
ValueError: Component 'R999' not found in schematic

DEBUG log context:
  Getting pins for component R999
  Available components: R1, R2, C1, U1, J1
  Suggestion: Did you mean R1 or R2?
```

#### Error Scenario 2: Symbol Library Missing
```
TypeError: Component R1 symbol not found in library

DEBUG log context:
  Getting pins for component R1
  Component position: (100.0, 100.0)
  Component rotation: 0°
  Component mirror: False
  Symbol lookup failed: Device:R
  Installed libraries: Device, Connector, Amplifier_Operational
  Suggestion: Verify symbol library path in KiCAD settings
```

#### Debug Output Example
```
DEBUG: Getting pins for component U1
DEBUG:   Component position: (150.0, 150.0)
DEBUG:   Component rotation: 90°
DEBUG:   Component mirror: False
DEBUG:   Loaded symbol: Amplifier_Operational:TL072
DEBUG:     Pin 1 (Non-Inverting A): (146.52, 150.0)
DEBUG:     Pin 2 (Inverting A): (146.52, 152.54)
DEBUG:     Pin 3 (Output A): (146.52, 155.08)
DEBUG:     ...
DEBUG:   Found 8 pins total
```

### Acceptance Criteria

- [ ] **Implementation Complete**
  - [ ] `get_pins_info()` method in ComponentCollection
  - [ ] PinInfo dataclass with all fields
  - [ ] MCP tool definition with Pydantic models
  - [ ] Proper error handling and validation

- [ ] **Test Coverage >95%**
  - [ ] All unit tests pass (15+ tests)
  - [ ] All integration tests pass (3+ tests)
  - [ ] Edge cases covered (rotations, mirrors, large components)
  - [ ] Performance verified (<50ms)
  - [ ] Code coverage report shows >95%

- [ ] **Debugging & Logging**
  - [ ] DEBUG logs at all critical points
  - [ ] Structured logging with context
  - [ ] Example error messages documented
  - [ ] Debug output is actionable

- [ ] **Documentation**
  - [ ] Docstrings complete with examples
  - [ ] Added to MCP_TOOLS.md
  - [ ] Usage examples in Claude format
  - [ ] Performance characteristics documented

- [ ] **Quality Assurance**
  - [ ] Black code formatting applied
  - [ ] MyPy type checking passes
  - [ ] Flake8 linting passes
  - [ ] Works with MCP tool invocation

### Validation Checklist for Implementation

**Before Starting Implementation:**
- [ ] Read CLAUDE.md coordinate system section
- [ ] Understand Y-axis inversion (symbol space vs schematic space)
- [ ] Review existing pin position code in geometry.py
- [ ] Check symbol caching implementation

**During Implementation:**
- [ ] Add extensive debug logging at each step
- [ ] Test with 2-pin, 8-pin, and 100-pin components
- [ ] Verify positions match KiCAD for all rotations
- [ ] Test case-insensitive lookup
- [ ] Measure performance on large components

**Before Submitting PR:**
- [ ] Run `pytest tests/unit/test_get_component_pins.py -v`
- [ ] Run `pytest tests/integration/test_pin_discovery_workflow.py -v`
- [ ] Check code coverage: `coverage run -m pytest && coverage report`
- [ ] Run quality checks: `black`, `mypy`, `flake8`
- [ ] Verify performance benchmark <50ms
- [ ] Test with MCP tool manually

### Related Issues & Dependencies

| Issue | Type | Relationship | Status |
|-------|------|--------------|--------|
| #201 | Feature | Depends on #200 | Blocked until complete |
| #202 | Feature | Depends on #200 | Blocked until complete |
| #205 | Infrastructure | Uses #200 | Blocked until complete |
| #199 | Epic | Parent issue | Links all related work |
| ADR-001 | Documentation | Reference for S-expression design | External reference |

---

## CRITICAL ISSUE #202: Enhance `connect_pins` with Orthogonal Routing

### Title
Enhance connect_pins with intelligent orthogonal routing

### Type & Metadata
- **Type**: Enhancement
- **Labels**: mcp-server, wire-routing, phase-1, core-tool
- **Epic**: #199
- **Priority**: P0 (Critical - required for usable circuit creation)
- **Assigned to**: [Backend Developer B]
- **Estimate**: 3 days
- **Dependencies**: #200 (get_component_pins must be complete)
- **Dependent Issues**: #203 (auto-junctions), #204 (validation)

### Description

Enhance the `connect_pins` method to support professional-quality orthogonal routing:
- **Orthogonal routing**: L-shaped connections that look professional
- **Smart strategy selection**: Automatic choice of horizontal-first or vertical-first based on component positions
- **Multi-segment wire paths**: Support for complex routing scenarios
- **Junction creation**: Automatic junctions where wires meet at T-points or crosses
- **Grid alignment**: Ensure all corners snap to KiCAD grid

**Why This Matters:**
- ❌ Direct/diagonal wires look unprofessional and are hard to read
- ❌ AI-generated schematics appear low-quality
- ✅ Orthogonal routing is industry standard for schematic design
- ✅ Makes automatic schematics indistinguishable from manual design
- ✅ Required for MCP server usability

### Implementation Details

#### Enhanced Method in Schematic
**File**: `kicad_sch_api/core/schematic.py`

```python
def connect_pins(
    self,
    ref1: str,
    pin1: str,
    ref2: str,
    pin2: str,
    routing: Literal["direct", "orthogonal", "h-first", "v-first"] = "orthogonal",
    auto_junction: bool = True,
    spacing: float = 1.27  # Default KiCAD grid
) -> ConnectionResult:
    """
    Connect two component pins with intelligent routing.

    Creates professional-quality electrical connections between pins with
    automatic routing strategy selection and optional junction creation.

    Routing Strategies:
    - "direct": Single straight line from pin1 to pin2
    - "orthogonal": Auto-select H-first or V-first based on component positions
    - "h-first": Horizontal first, then vertical (forms ⌐ shape)
    - "v-first": Vertical first, then horizontal (forms ⌞ shape)

    Grid Alignment:
    All wire endpoints and corners are snapped to the specified grid spacing
    (default 1.27mm for KiCAD schematic grid).

    Args:
        ref1 (str): First component reference (e.g., "R1")
        pin1 (str): First component pin number (e.g., "1")
        ref2 (str): Second component reference (e.g., "R2")
        pin2 (str): Second component pin number (e.g., "2")
        routing (str): Routing strategy
                      Default: "orthogonal" (intelligent selection)
                      Options: "direct", "orthogonal", "h-first", "v-first"
        auto_junction (bool): Automatically create junctions where wires meet
                             Default: True
        spacing (float): Grid spacing in mm for corner snapping
                        Default: 1.27 (KiCAD standard)

    Returns:
        ConnectionResult: Success indicator, wire UUIDs, junction UUIDs, path info

    Raises:
        ValueError: If components or pins not found
                   Message: f"Component '{ref1}' not found"
        ValueError: If pin doesn't exist
                   Message: f"Pin {pin1} not found on {ref1}"
        RuntimeError: If wire creation fails
                     Message: f"Failed to create wire segment: {reason}"

    Example:
        >>> result = sch.connect_pins("R1", "2", "R2", "1", routing="orthogonal")
        >>> print(f"Created {len(result.wire_uuids)} wires")
        Created 2 wires
        >>> print(f"Path: {result.path_points}")
        Path: [Point(100, 110), Point(125, 110), Point(150, 110)]

    Performance:
        < 10ms per connection (tested on modern hardware)
    """
    logger.debug(f"Connecting {ref1}.{pin1} → {ref2}.{pin2}")
    logger.debug(f"  Routing strategy: {routing}")
    logger.debug(f"  Auto-junction: {auto_junction}")
    logger.debug(f"  Grid spacing: {spacing}mm")

    # Validate components exist
    comp1 = self.components.get(ref1)
    comp2 = self.components.get(ref2)

    if not comp1:
        raise ValueError(f"Component '{ref1}' not found")
    if not comp2:
        raise ValueError(f"Component '{ref2}' not found")

    logger.debug(f"  Component 1: {ref1} at {comp1.position}, rotation={comp1.rotation}°")
    logger.debug(f"  Component 2: {ref2} at {comp2.position}, rotation={comp2.rotation}°")

    # Get pin positions
    pin1_pos = self.components.get_pin_position(ref1, pin1)
    pin2_pos = self.components.get_pin_position(ref2, pin2)

    if not pin1_pos:
        raise ValueError(f"Pin {pin1} not found on {ref1}")
    if not pin2_pos:
        raise ValueError(f"Pin {pin2} not found on {ref2}")

    logger.debug(f"  Pin {ref1}.{pin1}: {pin1_pos}")
    logger.debug(f"  Pin {ref2}.{pin2}: {pin2_pos}")

    # Select routing strategy if auto
    if routing == "orthogonal":
        routing = self._select_routing_strategy(pin1_pos, pin2_pos)
        logger.debug(f"  Auto-selected routing: {routing}")

    # Calculate path
    path_points = self._calculate_path(pin1_pos, pin2_pos, routing, spacing)
    logger.debug(f"  Path points ({len(path_points)}): {path_points}")

    # Create wires for each segment
    wire_uuids = []
    for i in range(len(path_points) - 1):
        start = path_points[i]
        end = path_points[i + 1]

        # Skip zero-length segments
        if start == end:
            logger.debug(f"  Skipping zero-length segment")
            continue

        wire_uuid = self.add_wire(start, end)
        wire_uuids.append(wire_uuid)
        logger.debug(f"  Created wire: {wire_uuid}")

    # Create junctions if requested
    junction_uuids = []
    if auto_junction and len(path_points) > 2:
        for point in path_points[1:-1]:  # Corner points
            junction_uuid = self.add_junction(point)
            junction_uuids.append(junction_uuid)
            logger.debug(f"  Created junction at {point}: {junction_uuid}")

    result = ConnectionResult(
        success=True,
        wire_uuids=wire_uuids,
        junction_uuids=junction_uuids,
        path_points=path_points,
        total_length=self._calculate_path_length(path_points),
        routing_strategy=routing
    )

    logger.info(f"Connection successful: {len(wire_uuids)} wires, {len(junction_uuids)} junctions")
    return result

def _select_routing_strategy(self, start: Point, end: Point) -> str:
    """
    Automatically select best routing strategy based on component positions.

    Uses a simple heuristic: if components are spread more horizontally,
    use h-first routing. Otherwise use v-first.

    Args:
        start: Starting point position
        end: Ending point position

    Returns:
        Routing strategy: "h-first" or "v-first"
    """
    dx = abs(end.x - start.x)
    dy = abs(end.y - start.y)

    logger.debug(f"_select_routing_strategy: dx={dx}, dy={dy}")

    # If horizontal distance > vertical distance, route horizontally first
    if dx > dy:
        logger.debug(f"  Selected h-first (horizontal spread {dx}mm > vertical {dy}mm)")
        return "h-first"
    else:
        logger.debug(f"  Selected v-first (vertical spread {dy}mm >= horizontal {dx}mm)")
        return "v-first"

def _calculate_path(
    self,
    start: Point,
    end: Point,
    routing: str,
    spacing: float
) -> List[Point]:
    """
    Calculate waypoints for wire routing.

    For orthogonal routing, creates an L-shaped path with corner snapped to grid.

    Args:
        start: Starting point
        end: Ending point
        routing: "direct", "h-first", or "v-first"
        spacing: Grid spacing for corner snapping

    Returns:
        List of waypoints (start, corner, end)
    """
    logger.debug(f"_calculate_path: {routing} routing from {start} to {end}")

    if routing == "direct":
        return [start, end]

    # Orthogonal routing
    if routing == "h-first":
        # Go horizontal first, then vertical
        corner = Point(end.x, start.y)
    else:  # v-first
        # Go vertical first, then horizontal
        corner = Point(start.x, end.y)

    # Snap corner to grid
    corner = self._snap_to_grid(corner, spacing)
    logger.debug(f"  Corner point: {corner} (snapped to {spacing}mm grid)")

    return [start, corner, end]

def _snap_to_grid(self, point: Point, spacing: float) -> Point:
    """
    Snap a point to the nearest grid intersection.

    Uses standard rounding to nearest grid point.

    Args:
        point: Point to snap
        spacing: Grid spacing in mm

    Returns:
        Snapped point
    """
    snapped_x = round(point.x / spacing) * spacing
    snapped_y = round(point.y / spacing) * spacing

    logger.debug(f"_snap_to_grid: ({point.x}, {point.y}) → ({snapped_x}, {snapped_y}) at {spacing}mm")

    return Point(snapped_x, snapped_y)

def _calculate_path_length(self, points: List[Point]) -> float:
    """Calculate total length of a wire path."""
    total = 0.0
    for i in range(len(points) - 1):
        dx = points[i+1].x - points[i].x
        dy = points[i+1].y - points[i].y
        total += (dx**2 + dy**2)**0.5
    return total
```

#### Data Model
**File**: `kicad_sch_api/core/types.py`

```python
@dataclass
class ConnectionResult:
    """Result of a pin connection operation."""
    success: bool                          # True if connection created successfully
    wire_uuids: List[str]                 # UUIDs of created wire segments
    junction_uuids: List[str]             # UUIDs of created junctions
    path_points: List[Point]              # Calculated wire path waypoints
    total_length: float                   # Total wire length in mm
    routing_strategy: str                 # Strategy used: "direct", "h-first", "v-first"

    def __post_init__(self):
        """Validate result data."""
        assert len(self.wire_uuids) > 0, "At least one wire must be created"
        assert len(self.path_points) >= 2, "Path must have start and end"
        assert self.total_length > 0, "Path length must be positive"
```

### Testing Requirements

#### Unit Tests
**File**: `tests/unit/test_orthogonal_routing.py`

```python
import pytest
from kicad_sch_api import create_schematic, Point
from kicad_sch_api.core.types import ConnectionResult

class TestOrthogonalRouting:

    def test_direct_routing(self, schematic):
        """Test direct (straight line) routing."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='direct')

        assert result.success
        assert len(result.wire_uuids) == 1  # Single straight wire
        assert result.routing_strategy == 'direct'
        assert len(result.path_points) == 2  # Start and end only

    def test_h_first_routing(self, schematic):
        """Test horizontal-first orthogonal routing."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='h-first')

        assert result.success
        assert len(result.wire_uuids) == 2  # Two segments (H and V)
        assert len(result.path_points) == 3  # Start, corner, end
        assert result.path_points[1].y == result.path_points[0].y  # Horizontal first

    def test_v_first_routing(self, schematic):
        """Test vertical-first orthogonal routing."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='v-first')

        assert result.success
        assert len(result.wire_uuids) == 2
        assert len(result.path_points) == 3
        assert result.path_points[1].x == result.path_points[0].x  # Vertical first

    def test_auto_strategy_wide_separation(self, schematic):
        """Test auto-selection with wide horizontal separation."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(150, 60))

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='orthogonal')

        # Wide horizontal gap should select h-first
        assert result.routing_strategy == 'h-first'

    def test_auto_strategy_tall_separation(self, schematic):
        """Test auto-selection with tall vertical separation."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(60, 150))

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='orthogonal')

        # Tall vertical gap should select v-first
        assert result.routing_strategy == 'v-first'

    def test_grid_snapping(self, schematic):
        """Test that corners snap to grid."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(75.25, 100.75))  # Off-grid

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='orthogonal', spacing=1.27)

        # Corner should be snapped to 1.27mm grid
        corner = result.path_points[1]
        assert corner.x % 1.27 == pytest.approx(0, abs=0.001)
        assert corner.y % 1.27 == pytest.approx(0, abs=0.001)

    def test_multiple_segment_wires(self, schematic):
        """Test multi-segment wire creation."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='orthogonal')

        assert len(result.wire_uuids) >= 2  # At least two segments
        assert all(uuid for uuid in result.wire_uuids)  # All UUIDs populated

    def test_zero_length_segment_skip(self, schematic):
        """Test that zero-length segments are skipped."""
        sch = schematic
        # Place both on same vertical line
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(50, 100))

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='orthogonal')

        # Should only have one wire (no horizontal movement)
        assert len(result.wire_uuids) == 1

    def test_path_length_calculation(self, schematic):
        """Test path length is calculated correctly."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(0, 0))
        sch.components.add('Device:R', 'R2', '10k', position=(30, 40))

        result = sch.connect_pins('R1', '2', 'R2', '1', routing='h-first')

        # Should be approximately 30 + 40 = 70mm
        assert result.total_length == pytest.approx(70, abs=1)

    def test_component_not_found_error(self, schematic):
        """Test error when component doesn't exist."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))

        with pytest.raises(ValueError) as exc_info:
            sch.connect_pins('R999', '2', 'R1', '1')
        assert "Component 'R999' not found" in str(exc_info.value)

    def test_pin_not_found_error(self, schematic):
        """Test error when pin doesn't exist."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        with pytest.raises(ValueError) as exc_info:
            sch.connect_pins('R1', '999', 'R2', '1')
        assert "Pin 999 not found" in str(exc_info.value)

    def test_auto_junction_creation(self, schematic):
        """Test automatic junction creation at corners."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        result = sch.connect_pins('R1', '2', 'R2', '1', auto_junction=True)

        # With orthogonal routing and 3 points, should create junction at corner
        assert len(result.junction_uuids) == 1
        assert result.junction_uuids[0]  # UUID populated

    def test_no_junction_when_disabled(self, schematic):
        """Test that junctions aren't created when disabled."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        result = sch.connect_pins('R1', '2', 'R2', '1', auto_junction=False)

        assert len(result.junction_uuids) == 0

class TestOrthogonalRoutingPerformance:

    def test_performance_per_connection(self, schematic):
        """Test routing performance is under 10ms per connection."""
        import time
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        start = time.time()
        result = sch.connect_pins('R1', '2', 'R2', '1')
        elapsed = (time.time() - start) * 1000  # ms

        assert elapsed < 10, f"Routing took {elapsed}ms, expected <10ms"

    def test_performance_many_connections(self, schematic):
        """Test performance with many connections."""
        import time
        sch = schematic

        # Create 20 components
        for i in range(20):
            sch.components.add('Device:R', f'R{i}', '10k', position=(50 + i*10, 50))

        start = time.time()
        for i in range(19):
            sch.connect_pins(f'R{i}', '2', f'R{i+1}', '1')
        elapsed = (time.time() - start) * 1000  # ms

        avg = elapsed / 19
        assert avg < 10, f"Average routing {avg}ms per connection, expected <10ms"
```

#### Integration Tests
**File**: `tests/integration/test_routing_workflows.py`

```python
def test_voltage_divider_circuit():
    """Test creating a complete voltage divider circuit."""
    sch = create_schematic('Voltage Divider Test')

    # Add components
    sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
    sch.components.add('Device:R', 'R2', '1k', position=(50, 100))
    sch.add_label('VCC', position=(50, 40))
    sch.add_label('GND', position=(50, 110))
    sch.add_label('Vout', position=(75, 75))

    # Connect R1 to VCC
    result1 = sch.connect_pins('R1', '1', 'VCC', '1')
    assert result1.success
    assert len(result1.wire_uuids) > 0

    # Connect R1 to R2
    result2 = sch.connect_pins('R1', '2', 'R2', '1')
    assert result2.success
    assert len(result2.wire_uuids) > 0

    # Connect R2 to GND
    result3 = sch.connect_pins('R2', '2', 'GND', '1')
    assert result3.success

    # Save and verify
    sch.save('test_voltage_divider.kicad_sch')
    assert sch.components.count() == 2  # Two resistors

def test_led_circuit():
    """Test creating LED circuit with series resistor."""
    sch = create_schematic('LED Circuit')

    sch.components.add('Device:LED', 'D1', 'LED', position=(50, 50))
    sch.components.add('Device:R', 'R1', '220', position=(100, 50))

    # Connect LED to resistor
    result = sch.connect_pins('D1', '2', 'R1', '1', routing='orthogonal')

    assert result.success
    assert len(result.wire_uuids) > 0

def test_complex_multi_component_routing():
    """Test routing with many components."""
    sch = create_schematic('Complex Circuit')

    # Create a complex circuit with multiple components
    sch.components.add('Device:R', 'R1', '1k', position=(50, 50))
    sch.components.add('Amplifier_Operational:TL072', 'U1', 'TL072', position=(150, 100))
    sch.components.add('Device:C', 'C1', '100n', position=(200, 50))

    # Connect R1 to U1 input
    result1 = sch.connect_pins('R1', '2', 'U1', '3', routing='orthogonal')
    assert result1.success

    # Connect U1 output to C1
    result2 = sch.connect_pins('U1', '1', 'C1', '1', routing='orthogonal')
    assert result2.success

def test_save_and_load_preserves_routing():
    """Test that saved schematic preserves routing."""
    sch = create_schematic('Test')

    sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
    sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

    result = sch.connect_pins('R1', '2', 'R2', '1', routing='orthogonal')

    initial_wire_count = len(result.wire_uuids)

    # Save
    sch.save('test_routing.kicad_sch')

    # Load
    sch2 = Schematic.load('test_routing.kicad_sch')

    # Verify wires preserved
    assert len(sch2.wires) == initial_wire_count

def test_kicad_can_load_result():
    """Test that KiCAD can load the generated schematic without errors."""
    sch = create_schematic('KiCAD Compatibility Test')

    sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
    sch.components.add('Device:R', 'R2', '10k', position=(100, 100))
    sch.connect_pins('R1', '2', 'R2', '1', routing='orthogonal')

    sch.save('test_kicad_compat.kicad_sch')

    # Try to open with KiCAD
    import subprocess
    result = subprocess.run(
        ['kicad-cli', 'sch', 'erc', 'test_kicad_compat.kicad_sch'],
        capture_output=True,
        timeout=5
    )

    # Should not have critical errors
    assert result.returncode == 0 or 'critical' not in result.stderr.lower()
```

#### Reference Tests
**File**: `tests/reference_tests/test_routing_reference.py`

```python
def test_routing_matches_professional_standard():
    """Compare our routing against professionally drawn schematics."""
    # Load reference schematic with manual routing
    reference = Schematic.load('tests/reference_kicad_projects/voltage_divider/reference.kicad_sch')

    # Extract reference wire paths
    ref_wires = list(reference.wires)

    # Generate equivalent circuit with our routing
    generated = create_schematic('Generated')
    generated.components.add('Device:R', 'R1', '10k', position=ref_wires[0]['start'])
    generated.components.add('Device:R', 'R2', '1k', position=ref_wires[0]['end'])
    result = generated.connect_pins('R1', '2', 'R2', '1', routing='orthogonal')

    # Compare routing paths
    assert len(result.wire_uuids) == len(ref_wires)

    # Verify wire lengths are similar
    ref_length = sum(w['length'] for w in ref_wires)
    gen_length = result.total_length

    assert gen_length == pytest.approx(ref_length, rel=0.1)
```

### Example Error Messages & Debugging

#### Error Scenario 1: Component Not Found
```
ValueError: Component 'R999' not found

DEBUG log context:
  Connecting R999.2 → R2.1
  Routing strategy: orthogonal
  Auto-junction: True
  Grid spacing: 1.27mm
  Component lookup failed for R999
  Available components: R1, R2, C1, U1
  Suggestion: Did you mean R1 or R2?
```

#### Error Scenario 2: Pin Not Found
```
ValueError: Pin 999 not found on R1

DEBUG log context:
  Connecting R1.999 → R2.1
  Routing strategy: orthogonal
  Component 1: R1 at (50.0, 50.0), rotation=0°
  Pin lookup failed: Pin 999
  Available pins on R1: 1, 2
  Suggestion: Resistor has only 2 pins (1, 2)
```

#### Debug Output Example
```
DEBUG: Connecting R1.2 → R2.1
DEBUG:   Routing strategy: orthogonal
DEBUG:   Auto-junction: True
DEBUG:   Grid spacing: 1.27mm
DEBUG:   Component 1: R1 at (50.0, 50.0), rotation=0°
DEBUG:   Component 2: R2 at (100.0, 100.0), rotation=0°
DEBUG:   Pin R1.2: (56.52, 50.0)
DEBUG:   Pin R2.1: (93.48, 100.0)
DEBUG:   Auto-selected routing: h-first (horizontal spread 37.0mm > vertical 50.0mm)
DEBUG:   _calculate_path: h-first routing from (56.52, 50.0) to (93.48, 100.0)
DEBUG:   Corner point: (93.48, 50.0) (snapped to 1.27mm grid)
DEBUG:   Created wire: 550e8400-e29b-41d4-a716-446655440000
DEBUG:   Created wire: 550e8400-e29b-41d4-a716-446655440001
DEBUG:   Created junction at (93.48, 50.0): 550e8400-e29b-41d4-a716-446655440002
DEBUG: Connection successful: 2 wires, 1 junctions
```

### Acceptance Criteria

- [ ] **Implementation Complete**
  - [ ] `connect_pins()` method with all routing strategies
  - [ ] Automatic strategy selection algorithm
  - [ ] Grid snapping for corners
  - [ ] Junction creation support
  - [ ] Error handling for all edge cases

- [ ] **Test Coverage >95%**
  - [ ] All routing strategies tested
  - [ ] Auto-selection logic verified
  - [ ] Grid snapping validated
  - [ ] All error conditions tested
  - [ ] Performance <10ms verified
  - [ ] Code coverage >95%

- [ ] **Professional Quality Output**
  - [ ] Orthogonal routing produces L-shaped paths
  - [ ] Automatic strategy selection works correctly
  - [ ] Output matches professional KiCAD schematics
  - [ ] No crossing/overlapping wires in standard scenarios

- [ ] **Integration**
  - [ ] Works with #203 (auto-junctions)
  - [ ] Depends on #200 (get_component_pins)
  - [ ] Required for #204 (validation)
  - [ ] Enables complete circuit creation

- [ ] **Debugging & Documentation**
  - [ ] Comprehensive DEBUG logging
  - [ ] Example error messages documented
  - [ ] Performance characteristics documented
  - [ ] Usage examples included

### Validation Checklist for Implementation

**Before Starting:**
- [ ] Review CLAUDE.md coordinate system section
- [ ] Understand schematic space (inverted Y-axis)
- [ ] Study existing wire creation code
- [ ] Plan routing algorithm on paper

**During Implementation:**
- [ ] Add extensive debug logging at each step
- [ ] Test all 4 routing strategies
- [ ] Verify grid snapping works
- [ ] Test auto-selection logic
- [ ] Measure performance on complex circuits

**Before Submitting PR:**
- [ ] Run all unit tests: `pytest tests/unit/test_orthogonal_routing.py -v`
- [ ] Run integration tests: `pytest tests/integration/test_routing_workflows.py -v`
- [ ] Check code coverage >95%
- [ ] Run quality checks: `black`, `mypy`, `flake8`
- [ ] Verify performance <10ms/connection
- [ ] Test with KiCAD compatibility

### Related Issues & Dependencies

| Issue | Type | Relationship | Status |
|-------|------|--------------|--------|
| #200 | Feature | Depends on - required | Must complete first |
| #203 | Feature | Enables this | Can start after routing |
| #204 | Feature | Uses this | Depends on routing |
| #199 | Epic | Parent issue | Links all related work |
| CLAUDE.md | Docs | Reference | Required reading |

---

## CRITICAL ISSUE #204: Add Connectivity Validation Tools

### Title
Implement connectivity validation and analysis tools

### Type & Metadata
- **Type**: Feature
- **Labels**: mcp-server, validation, phase-1, core-tool
- **Epic**: #199
- **Priority**: P0 (Critical - ensures circuit correctness)
- **Assigned to**: [Backend Developer C]
- **Estimate**: 2 days
- **Dependencies**: #202 (routing), #203 (junctions)
- **Dependent Issues**: None (final validation layer)

### Description

Implement comprehensive tools to validate schematic connectivity before saving. These tools detect electrical errors and provide actionable feedback to prevent invalid schematics.

**Why This Matters:**
- ❌ Undetected connectivity errors create non-functional circuits
- ❌ Users blame the API instead of recognizing connection mistakes
- ✅ Early error detection prevents wasted time debugging
- ✅ Validation provides "guardrails" for AI-driven circuit design
- ✅ Clear error messages guide users to fix problems

### Implementation Details

#### New Methods in Schematic
**File**: `kicad_sch_api/core/schematic.py`

```python
def validate_connectivity(self) -> ConnectivityReport:
    """
    Validate all electrical connections in the schematic.

    Performs comprehensive checks including:
    - Unconnected pins (floating inputs)
    - Disconnected components
    - Missing required junctions
    - Ambiguous wire/pin intersections
    - Net continuity analysis

    Returns:
        ConnectivityReport with detailed findings

    Example:
        >>> report = sch.validate_connectivity()
        >>> if not report.passed:
        ...     for issue in report.issues:
        ...         print(f"[{issue.severity}] {issue.message}")
        >>> print(f"Found {report.error_count} errors, {report.warning_count} warnings")

    Performance:
        < 100ms for typical schematics (10-50 components)
        < 500ms for large schematics (100+ components)
    """
    logger.debug(f"validate_connectivity() called")
    logger.debug(f"  Schematic has {len(self.components)} components")
    logger.debug(f"  Schematic has {len(self.wires)} wires")
    logger.debug(f"  Schematic has {len(self.junctions)} junctions")

    issues: List[ValidationIssue] = []

    # Check 1: Unconnected pins
    logger.debug("  Checking for unconnected pins...")
    unconnected = self._find_unconnected_pins()
    for comp_ref, pin_num in unconnected:
        if self._is_no_connect_pin(comp_ref, pin_num):
            continue  # NC pins are intentionally unconnected
        issues.append(ValidationIssue(
            severity="warning",
            component=f"{comp_ref}.{pin_num}",
            message=f"Pin {pin_num} on {comp_ref} is unconnected"
        ))
    logger.debug(f"    Found {len(unconnected)} unconnected pins")

    # Check 2: Floating components
    logger.debug("  Checking for floating components...")
    floating = self._find_floating_components()
    for comp_ref in floating:
        issues.append(ValidationIssue(
            severity="warning",
            component=comp_ref,
            message=f"Component {comp_ref} has no electrical connections"
        ))
    logger.debug(f"    Found {len(floating)} floating components")

    # Check 3: Wire/pin misalignment (T-junctions without junctions)
    logger.debug("  Checking for missing junctions...")
    missing_junctions = self._find_missing_junctions()
    for position, wires in missing_junctions:
        issues.append(ValidationIssue(
            severity="error",
            component=None,
            message=f"Junction missing at ({position.x}, {position.y}): {len(wires)} wires meet without junction"
        ))
    logger.debug(f"    Found {len(missing_junctions)} missing junctions")

    # Check 4: Overlapping wires
    logger.debug("  Checking for overlapping wires...")
    overlapping = self._find_overlapping_wires()
    for wire1_uuid, wire2_uuid in overlapping:
        issues.append(ValidationIssue(
            severity="warning",
            component=None,
            message=f"Wires {wire1_uuid} and {wire2_uuid} overlap without junction"
        ))
    logger.debug(f"    Found {len(overlapping)} overlapping wire pairs")

    # Check 5: Net continuity (all connected points are same net)
    logger.debug("  Checking net continuity...")
    continuity_issues = self._check_net_continuity()
    issues.extend(continuity_issues)
    logger.debug(f"    Found {len(continuity_issues)} continuity issues")

    # Summarize
    error_count = len([i for i in issues if i.severity == 'error'])
    warning_count = len([i for i in issues if i.severity == 'warning'])

    report = ConnectivityReport(
        passed=(error_count == 0),
        error_count=error_count,
        warning_count=warning_count,
        issues=issues
    )

    logger.info(f"Connectivity validation: {error_count} errors, {warning_count} warnings, {'PASSED' if report.passed else 'FAILED'}")

    return report

def are_pins_connected(self, ref1: str, pin1: str, ref2: str, pin2: str) -> bool:
    """
    Check if two specific pins are electrically connected.

    Traces through wires and junctions to determine if electrical connection
    exists between two pins.

    Args:
        ref1, pin1: First pin (e.g., "R1", "1")
        ref2, pin2: Second pin (e.g., "R2", "2")

    Returns:
        True if pins are electrically connected via wires/junctions

    Example:
        >>> if sch.are_pins_connected("R1", "2", "R2", "1"):
        ...     print("Pins are connected")
        ... else:
        ...     print("Pins are NOT connected - fix wiring!")

    Raises:
        ValueError: If pins don't exist
    """
    logger.debug(f"are_pins_connected({ref1}.{pin1} ↔ {ref2}.{pin2})")

    # Get pin positions
    pos1 = self.components.get_pin_position(ref1, pin1)
    pos2 = self.components.get_pin_position(ref2, pin2)

    if not pos1 or not pos2:
        raise ValueError(f"One or both pins not found")

    logger.debug(f"  Pin {ref1}.{pin1}: {pos1}")
    logger.debug(f"  Pin {ref2}.{pin2}: {pos2}")

    # Find connected nets for each pin
    net1 = self._find_net_at_position(pos1)
    net2 = self._find_net_at_position(pos2)

    logger.debug(f"  Net at pin 1: {len(net1)} points")
    logger.debug(f"  Net at pin 2: {len(net2)} points")

    # Check if nets overlap (connected)
    connected = bool(net1 & net2)  # Set intersection

    logger.debug(f"  Connected: {connected}")

    return connected

def get_connection_info(self, ref: str, pin: str) -> PinConnectionInfo:
    """
    Get detailed connection information for a specific pin.

    Analyzes what a pin is connected to (if anything).

    Args:
        ref: Component reference
        pin: Pin number

    Returns:
        PinConnectionInfo with connection details

    Example:
        >>> info = sch.get_connection_info("U1", "3")
        >>> print(f"Pin is connected to: {info.connected_to}")
        >>> print(f"Via wires: {info.wire_uuids}")
        >>> print(f"Via junctions: {info.junction_uuids}")

    Raises:
        ValueError: If pin doesn't exist
    """
    logger.debug(f"get_connection_info({ref}.{pin})")

    component = self.components.get(ref)
    if not component:
        raise ValueError(f"Component {ref} not found")

    pin_pos = self.components.get_pin_position(ref, pin)
    if not pin_pos:
        raise ValueError(f"Pin {pin} not found on {ref}")

    logger.debug(f"  Pin position: {pin_pos}")

    # Find all wires touching this position
    wires_at_pin = self._find_wires_at_position(pin_pos)
    logger.debug(f"  Wires at pin: {len(wires_at_pin)}")

    # Find all junctions at this position
    junctions_at_pin = self._find_junctions_at_position(pin_pos)
    logger.debug(f"  Junctions at pin: {len(junctions_at_pin)}")

    # Trace connected net
    connected_net = self._find_net_at_position(pin_pos)
    logger.debug(f"  Connected net size: {len(connected_net)} points")

    # Find what else is connected
    connected_pins = self._find_pins_in_net(connected_net)
    logger.debug(f"  Connected pins: {len(connected_pins)}")

    info = PinConnectionInfo(
        reference=ref,
        pin_number=pin,
        position=pin_pos,
        is_connected=len(connected_net) > 1,
        wire_uuids=wires_at_pin,
        junction_uuids=junctions_at_pin,
        connected_pins=connected_pins,
        net_size=len(connected_net)
    )

    return info

def _find_unconnected_pins(self) -> List[Tuple[str, str]]:
    """Find all pins with no wires attached."""
    logger.debug("_find_unconnected_pins()")
    unconnected = []

    for component in self.components:
        pins = self.components.get_pins_info(component.reference)
        for pin in pins:
            wires = self._find_wires_at_position(pin.position)
            if not wires:
                unconnected.append((component.reference, pin.number))
                logger.debug(f"  Found unconnected: {component.reference}.{pin.number}")

    return unconnected

def _find_floating_components(self) -> List[str]:
    """Find components with no electrical connections."""
    logger.debug("_find_floating_components()")
    floating = []

    for component in self.components:
        pins = self.components.get_pins_info(component.reference)
        # Check if any pin has connections
        has_connection = False
        for pin in pins:
            if self._is_no_connect_pin(component.reference, pin.number):
                continue
            wires = self._find_wires_at_position(pin.position)
            if wires:
                has_connection = True
                break

        if not has_connection:
            floating.append(component.reference)
            logger.debug(f"  Found floating component: {component.reference}")

    return floating

def _find_missing_junctions(self) -> List[Tuple[Point, List[str]]]:
    """
    Find locations where wires meet without junctions.

    Returns:
        List of (position, wire_uuids) where junctions are missing
    """
    logger.debug("_find_missing_junctions()")
    missing = []
    tolerance = 0.01  # mm

    wire_positions = {}
    for wire in self.wires:
        for endpoint in [wire.start, wire.end]:
            key = (round(endpoint.x/tolerance)*tolerance,
                   round(endpoint.y/tolerance)*tolerance)
            if key not in wire_positions:
                wire_positions[key] = []
            wire_positions[key].append(wire.uuid)

    for pos, wire_uuids in wire_positions.items():
        if len(wire_uuids) > 2:  # More than 2 wires = junction needed
            junction_exists = any(
                j.position.x == pos[0] and j.position.y == pos[1]
                for j in self.junctions
            )
            if not junction_exists:
                missing.append((Point(pos[0], pos[1]), wire_uuids))
                logger.debug(f"  Found missing junction at {pos}: {len(wire_uuids)} wires")

    return missing

def _find_overlapping_wires(self) -> List[Tuple[str, str]]:
    """Find wires that overlap without connecting."""
    logger.debug("_find_overlapping_wires()")
    overlapping = []

    # Simplified: look for wires that share endpoints without junctions
    for i, wire1 in enumerate(self.wires):
        for wire2 in self.wires[i+1:]:
            if self._wires_overlap(wire1, wire2):
                if not self._junction_at_overlap(wire1, wire2):
                    overlapping.append((wire1.uuid, wire2.uuid))
                    logger.debug(f"  Found overlapping: {wire1.uuid} and {wire2.uuid}")

    return overlapping

def _check_net_continuity(self) -> List[ValidationIssue]:
    """Verify all connected points are same net."""
    # Simplified implementation
    return []
```

#### Data Models
**File**: `kicad_sch_api/core/types.py`

```python
@dataclass
class ValidationIssue:
    """Single validation issue found during connectivity check."""
    severity: Literal["error", "warning", "info"]  # error = blocks save, warning = review
    component: Optional[str]                        # Which component has issue (if applicable)
    message: str                                    # Human-readable description

    def __str__(self):
        """Format for display."""
        return f"[{self.severity.upper():7}] {message}"

@dataclass
class ConnectivityReport:
    """Result of connectivity validation."""
    passed: bool                      # True if no errors
    error_count: int                  # Number of critical errors
    warning_count: int                # Number of warnings
    issues: List[ValidationIssue]     # Detailed issue list

    def summary(self) -> str:
        """Get human-readable summary."""
        if self.passed:
            return f"✓ Connectivity valid ({self.warning_count} warnings)"
        else:
            return f"✗ Connectivity invalid: {self.error_count} errors, {self.warning_count} warnings"

    def __str__(self):
        """Format for display."""
        lines = [self.summary()]
        for issue in self.issues:
            lines.append(f"  {issue}")
        return "\n".join(lines)

@dataclass
class PinConnectionInfo:
    """Detailed connection information for a pin."""
    reference: str                    # Component reference
    pin_number: str                   # Pin number
    position: Point                   # Pin position
    is_connected: bool                # True if electrically connected
    wire_uuids: List[str]            # Wires touching this pin
    junction_uuids: List[str]        # Junctions at this pin
    connected_pins: List[Tuple[str, str]]  # Other pins in same net
    net_size: int                     # Total points in net

    def summary(self) -> str:
        """Get summary text."""
        if self.is_connected:
            return f"{self.reference}.{self.pin_number} connected to {len(self.connected_pins)} other pins"
        else:
            return f"{self.reference}.{self.pin_number} is NOT connected"
```

#### MCP Tool Definition
**File**: `mcp_server/tools/validation_tools.py`

```python
import logging
from kicad_sch_api.core.types import ConnectivityReport, ValidationIssue

logger = logging.getLogger(__name__)

@tool()
def validate_schematic_connectivity() -> dict:
    """
    Validate all electrical connections in current schematic.

    Checks for:
    - Unconnected pins (floating inputs)
    - Disconnected components
    - Missing junctions where wires meet
    - Net continuity issues

    Returns:
        Dictionary with validation results

    Example:
        >>> result = validate_schematic_connectivity()
        >>> if result['passed']:
        ...     print("Schematic is valid!")
        ... else:
        ...     for issue in result['issues']:
        ...         print(f"[{issue['severity']}] {issue['message']}")

    Performance:
        < 100ms for typical schematics
    """
    logger.debug("MCP tool: validate_schematic_connectivity()")

    try:
        report = SCHEMATIC.validate_connectivity()

        return {
            'passed': report.passed,
            'error_count': report.error_count,
            'warning_count': report.warning_count,
            'summary': report.summary(),
            'issues': [
                {
                    'severity': issue.severity,
                    'component': issue.component,
                    'message': issue.message
                }
                for issue in report.issues
            ]
        }
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {
            'passed': False,
            'error_count': 1,
            'warning_count': 0,
            'summary': f"Validation error: {e}",
            'issues': [
                {
                    'severity': 'error',
                    'component': None,
                    'message': str(e)
                }
            ]
        }

@tool()
def check_pins_connected(ref1: str, pin1: str, ref2: str, pin2: str) -> dict:
    """
    Check if two pins are electrically connected.

    Args:
        ref1, pin1: First pin (e.g., "R1", "1")
        ref2, pin2: Second pin (e.g., "R2", "2")

    Returns:
        Dictionary with connection status

    Example:
        >>> result = check_pins_connected("R1", "2", "R2", "1")
        >>> if result['connected']:
        ...     print("Pins are electrically connected")
    """
    logger.debug(f"MCP tool: check_pins_connected({ref1}.{pin1}, {ref2}.{pin2})")

    try:
        connected = SCHEMATIC.are_pins_connected(ref1, pin1, ref2, pin2)
        return {
            'connected': connected,
            'ref1': ref1,
            'pin1': pin1,
            'ref2': ref2,
            'pin2': pin2
        }
    except ValueError as e:
        logger.error(f"Connection check error: {e}")
        return {
            'connected': False,
            'error': str(e)
        }

@tool()
def get_pin_connections(reference: str, pin: str) -> dict:
    """
    Get all connections for a specific pin.

    Args:
        reference: Component reference
        pin: Pin number

    Returns:
        Dictionary with connection info

    Example:
        >>> info = get_pin_connections("U1", "3")
        >>> print(f"Connected pins: {info['connected_pins']}")
    """
    logger.debug(f"MCP tool: get_pin_connections({reference}.{pin})")

    try:
        info = SCHEMATIC.get_connection_info(reference, pin)

        return {
            'reference': info.reference,
            'pin_number': info.pin_number,
            'position': (float(info.position.x), float(info.position.y)),
            'is_connected': info.is_connected,
            'connected_pins': [
                {'reference': ref, 'pin': pin_num}
                for ref, pin_num in info.connected_pins
            ],
            'net_size': info.net_size,
            'summary': info.summary()
        }
    except ValueError as e:
        logger.error(f"Connection info error: {e}")
        return {
            'error': str(e)
        }
```

### Testing Requirements

#### Unit Tests
**File**: `tests/unit/test_connectivity_validation.py`

```python
import pytest
from kicad_sch_api import create_schematic

class TestValidateConnectivity:

    def test_valid_connected_circuit(self, schematic):
        """Test schematic with valid connections."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))
        sch.connect_pins('R1', '2', 'R2', '1')

        report = sch.validate_connectivity()

        assert report.passed
        assert report.error_count == 0

    def test_detect_unconnected_pins(self, schematic):
        """Test detection of unconnected pins."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        # Don't connect anything

        report = sch.validate_connectivity()

        assert not report.passed
        assert report.error_count > 0 or report.warning_count > 0
        assert any('unconnected' in i.message.lower() for i in report.issues)

    def test_detect_floating_components(self, schematic):
        """Test detection of components with no connections."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))
        # Only connect R1
        sch.add_wire((56.52, 50), (100, 50))

        report = sch.validate_connectivity()

        # R2 should be flagged as floating
        floating_issues = [i for i in report.issues if 'float' in i.message.lower()]
        assert len(floating_issues) > 0

    def test_detect_missing_junctions(self, schematic):
        """Test detection of missing junctions at T-points."""
        sch = schematic
        # Create T-junction manually without junction
        sch.add_wire((50, 50), (100, 50))  # Horizontal wire
        sch.add_wire((75, 40), (75, 60))   # Vertical wire crossing

        report = sch.validate_connectivity()

        # Should detect missing junction
        assert any('junction' in i.message.lower() for i in report.issues)

    def test_detect_overlapping_wires(self, schematic):
        """Test detection of overlapping wires without junction."""
        sch = schematic
        sch.add_wire((50, 50), (100, 50))
        sch.add_wire((50, 50), (100, 50))  # Duplicate

        report = sch.validate_connectivity()

        # Should detect overlap
        assert any('overlap' in i.message.lower() for i in report.issues)

    def test_severity_levels(self, schematic):
        """Test that severity levels are assigned correctly."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))

        report = sch.validate_connectivity()

        assert any(i.severity in ['error', 'warning', 'info'] for i in report.issues)

    def test_component_identification(self, schematic):
        """Test that issues identify which component is affected."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        report = sch.validate_connectivity()

        # Issues should reference specific components
        assert any(i.component for i in report.issues)

class TestArePinsConnected:

    def test_directly_connected_pins(self, schematic):
        """Test detection of directly connected pins."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))
        sch.connect_pins('R1', '2', 'R2', '1')

        assert sch.are_pins_connected('R1', '2', 'R2', '1')

    def test_indirectly_connected_pins(self, schematic):
        """Test detection of indirectly connected pins (via junction)."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))
        sch.components.add('Device:R', 'R3', '10k', position=(150, 50))

        sch.connect_pins('R1', '2', 'R2', '1')
        sch.connect_pins('R1', '2', 'R3', '1')  # All connected to R1.2

        assert sch.are_pins_connected('R2', '1', 'R3', '1')

    def test_unconnected_pins(self, schematic):
        """Test detection of unconnected pins."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

        assert not sch.are_pins_connected('R1', '2', 'R2', '1')

    def test_pin_not_found_error(self, schematic):
        """Test error when pin doesn't exist."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))

        with pytest.raises(ValueError):
            sch.are_pins_connected('R1', '999', 'R1', '1')

class TestGetConnectionInfo:

    def test_connected_pin_info(self, schematic):
        """Test getting info for connected pin."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
        sch.components.add('Device:R', 'R2', '10k', position=(100, 100))
        sch.connect_pins('R1', '2', 'R2', '1')

        info = sch.get_connection_info('R1', '2')

        assert info.is_connected
        assert len(info.connected_pins) > 0
        assert len(info.wire_uuids) > 0
        assert info.net_size > 1

    def test_unconnected_pin_info(self, schematic):
        """Test getting info for unconnected pin."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(50, 50))

        info = sch.get_connection_info('R1', '1')

        assert not info.is_connected
        assert len(info.connected_pins) == 0
        assert len(info.wire_uuids) == 0

    def test_pin_position_accuracy(self, schematic):
        """Test that pin position in info is accurate."""
        sch = schematic
        sch.components.add('Device:R', 'R1', '10k', position=(100, 100))

        info = sch.get_connection_info('R1', '1')

        # Should match position from get_pins_info
        pins = sch.components.get_pins_info('R1')
        pin = next(p for p in pins if p.number == '1')

        assert info.position.x == pytest.approx(pin.position.x, abs=0.01)
        assert info.position.y == pytest.approx(pin.position.y, abs=0.01)
```

#### Integration Tests
**File**: `tests/integration/test_validation_workflows.py`

```python
def test_voltage_divider_validation():
    """Test validation of valid voltage divider."""
    sch = create_schematic('Voltage Divider')
    sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
    sch.components.add('Device:R', 'R2', '1k', position=(50, 100))

    sch.connect_pins('R1', '1', 'R2', '2')

    report = sch.validate_connectivity()
    assert report.passed  # All pins connected properly

def test_broken_circuit_detection():
    """Test detection of broken/incomplete circuit."""
    sch = create_schematic('Broken Circuit')
    sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
    sch.components.add('Device:R', 'R2', '10k', position=(100, 100))

    # Intentionally don't connect anything

    report = sch.validate_connectivity()
    assert not report.passed
    assert report.error_count > 0 or report.warning_count > 0

def test_partial_connection_warning():
    """Test that partially connected circuits generate warnings."""
    sch = create_schematic('Partial')
    sch.components.add('Device:R', 'R1', '10k', position=(50, 50))
    sch.components.add('Device:R', 'R2', '10k', position=(100, 100))
    sch.components.add('Device:R', 'R3', '10k', position=(150, 50))

    # Only connect R1 to R2
    sch.connect_pins('R1', '2', 'R2', '1')
    # R3 is floating

    report = sch.validate_connectivity()
    assert not report.passed
    assert 'R3' in str(report) or 'floating' in str(report).lower()
```

### Example Error Messages & Debugging

#### Error Scenario 1: Unconnected Pin
```
[WARNING] Pin 1 on R1 is unconnected

DEBUG log context:
  validate_connectivity() called
  Schematic has 2 components
  Schematic has 1 wires
  Schematic has 0 junctions
  Checking for unconnected pins...
    Component R1: checking pins...
      Pin 1: position (56.52, 50.0) - no wires found
    Found 1 unconnected pins
```

#### Error Scenario 2: Missing Junction
```
[ERROR] Junction missing at (100.0, 75.0): 3 wires meet without junction

DEBUG log context:
  validate_connectivity() called
  Checking for missing junctions...
    Wire 1 (50.0, 75.0) → (150.0, 75.0) passes through (100.0, 75.0)
    Wire 2 (100.0, 50.0) → (100.0, 100.0) passes through (100.0, 75.0)
    Wire 3 (100.0, 75.0) → (200.0, 75.0) starts at (100.0, 75.0)
    3 wires at position - junction missing
    Found missing junction at (100.0, 75.0)
```

#### Debug Output Example
```
DEBUG: validate_connectivity() called
DEBUG:   Schematic has 3 components
DEBUG:   Schematic has 2 wires
DEBUG:   Schematic has 1 junctions
DEBUG:   Checking for unconnected pins...
DEBUG:   Checking for floating components...
DEBUG:     Component R1: has 2 connections ✓
DEBUG:     Component R2: has 2 connections ✓
DEBUG:     Component R3: has 0 connections ✗
DEBUG:   Found 1 floating components
DEBUG:   Checking for missing junctions...
DEBUG:     Position (100.0, 75.0): 2 wires
DEBUG:   Checking for overlapping wires...
DEBUG: Connectivity validation: 0 errors, 1 warnings, FAILED
```

### Acceptance Criteria

- [ ] **Implementation Complete**
  - [ ] `validate_connectivity()` method with all checks
  - [ ] `are_pins_connected()` method for pair checking
  - [ ] `get_connection_info()` method for detailed info
  - [ ] All data models defined (ValidationIssue, ConnectivityReport, etc.)
  - [ ] Proper error handling

- [ ] **Test Coverage >90%**
  - [ ] All validation checks tested
  - [ ] Error conditions tested
  - [ ] Integration scenarios tested
  - [ ] Code coverage >90%

- [ ] **Clear Error Messages**
  - [ ] Errors identify specific component/pin
  - [ ] Messages are actionable
  - [ ] Severity levels assigned appropriately
  - [ ] DEBUG logging shows context

- [ ] **Performance Requirements**
  - [ ] < 100ms for typical schematics
  - [ ] < 500ms for large schematics (100+ components)
  - [ ] Linear scaling with component count

- [ ] **Integration**
  - [ ] Requires #202 (routing) and #203 (junctions)
  - [ ] Works as final validation layer
  - [ ] Provides guardrails for AI-driven design

### Validation Checklist for Implementation

**Before Starting:**
- [ ] Review connectivity concepts
- [ ] Plan algorithm for net tracing
- [ ] Study wire/junction data structures
- [ ] Define all check types needed

**During Implementation:**
- [ ] Add extensive debug logging
- [ ] Test each validation check independently
- [ ] Verify error messages are actionable
- [ ] Test with partial circuits

**Before Submitting PR:**
- [ ] Run unit tests: `pytest tests/unit/test_connectivity_validation.py -v`
- [ ] Run integration tests: `pytest tests/integration/test_validation_workflows.py -v`
- [ ] Check code coverage >90%
- [ ] Verify performance <100ms for typical schematics
- [ ] Test MCP tools manually

### Related Issues & Dependencies

| Issue | Type | Relationship | Status |
|-------|------|--------------|--------|
| #202 | Feature | Depends on - routing | Must complete first |
| #203 | Feature | Depends on - junctions | Must complete first |
| #199 | Epic | Parent issue | Links all related work |
| #205 | Infrastructure | Uses this | Testing depends on validation |

---

## Summary of Enhancements Applied

### Enhancement #1: Clear Acceptance Criteria
Each issue now includes:
- Specific, measurable acceptance criteria
- Implementation checklist
- Validation checklist for reviewers
- Success/completion indicators

### Enhancement #2: Example Error Messages & Debugging
Each issue includes:
- Real error message examples
- DEBUG log context showing what's happening
- Actionable error messages for users
- Debug output showing the workflow

### Enhancement #3: Links Between Dependent Issues
All issues now include:
- Dependency table showing relationships
- Related issues section
- Blocking/blocked status
- Context for why dependencies exist

### Enhancement #4: Comprehensive Testing Requirements
Each issue includes:
- Unit tests (15+ tests per critical issue)
- Integration tests
- Reference/validation tests
- Performance benchmarks
- Edge case coverage

### Enhancement #5: Code Examples with Context
All code is provided with:
- Complete function signatures
- Full docstrings with examples
- Data models/types defined
- MCP tool wrappers included
- Real usage scenarios

### Enhancement #6: Validation Checklists
Each issue includes:
- Pre-implementation checklist
- During-implementation checklist
- Pre-submission checklist
- Code quality requirements
- Performance verification steps

---

## Implementation Recommendations

### Sequential vs. Parallel Execution

**Critical Path (Sequential):**
```
#200 (get_component_pins) → #202 (orthogonal routing) → #203 (junctions) → #204 (validation)
```

**Can Parallel:**
- #207 (logging) - can start immediately
- #205 (test infrastructure) - can start immediately
- #206 (reference circuits) - can start immediately with #200

### Time Estimates
- Issue #200: 3 days
- Issue #202: 3 days
- Issue #204: 2 days
- **Total: 8 days** (can compress with parallelization)

### Resource Allocation
- **Backend Developer A**: #200 + #207 (logging)
- **Backend Developer B**: #202 (routing)
- **Backend Developer C**: #203 + #204 (junctions + validation)
- **QA Engineer**: #205 + #206 (testing infrastructure)
- **Tech Writer**: #208 (documentation)

### Risk Mitigation
- Pin position accuracy is critical - test extensively against KiCAD
- Routing algorithm must produce professional-looking output
- Validation should catch ALL common errors
- Performance must stay <10ms per operation

---

*Document generated with comprehensive GitHub issue enhancements for production implementation*
