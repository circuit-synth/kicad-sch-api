# GitHub Issues: MCP Pin Connection & Wire Routing

**Epic**: Enable AI Assistants to Create Accurate KiCad Schematics via MCP
**Status**: Ready for Implementation
**Target**: Phase 1 (Weeks 1-2)

---

## Epic Issue Template

```
Title: Epic: Pin Connection & Wire Routing for MCP Server
Labels: epic, mcp-server, phase-1, high-priority
Assignee: [TBD]

## Description

Pin/wire connection accuracy is the critical feature for MCP server usability.
AI assistants need simple, foolproof ways to discover pins and create accurate electrical connections.

## Goals

- [ ] Enable pin discovery programmatically
- [ ] Support semantic pin lookup by name/function
- [ ] Implement smart orthogonal wire routing
- [ ] Automatic junction detection and creation
- [ ] Comprehensive validation tools

## Related Issues

- #200 Implement get_component_pins tool
- #201 Implement find_pins_by_name tool
- #202 Enhance connect_pins with orthogonal routing
- #203 Implement auto-junction detection
- #204 Add connectivity validation tools
- #205 Create pin connection testing infrastructure
- #206 Create reference KiCAD test circuits
- #207 Implement comprehensive logging for pin operations
- #208 Create pin connection documentation

## Acceptance Criteria

- [ ] All sub-issues completed
- [ ] >95% test coverage for pin operations
- [ ] All functions have debug logging at DEBUG level
- [ ] Can connect two arbitrary components with orthogonal routing
- [ ] Validates connections before save
- [ ] Documentation examples work in Claude conversations

## Resources

- Pin positioning code: `kicad_sch_api/core/pin_utils.py`
- Schematic methods: `kicad_sch_api/core/schematic.py`
- Strategy document: `MCP_PIN_CONNECTION_STRATEGY.md`
- Test infrastructure: `tests/test_pin_*.py`
```

---

## Sub-Issues

### Group 1: Pin Discovery & Lookup (Sprint 1)

#### Issue #200: Implement `get_component_pins` Tool

```
Title: Implement get_component_pins tool - discover all pins for a component
Type: Feature
Labels: mcp-server, pin-discovery, phase-1, core-tool
Epic: #199 (Pin Connection Epic)
Priority: P0
Assigned to: [Backend Developer A]
Estimate: 3 days

## Description

Implement the `get_component_pins` tool that enables AI assistants to discover
all available pins for a component, including pin numbers, names, types, and positions.

This is CRITICAL because AI cannot make connections without knowing what pins exist.

## Implementation Details

### New Function
File: `kicad_sch_api/collections/components.py`

```python
class ComponentCollection:
    def get_pins_info(self, reference: str) -> List[PinInfo]:
        """
        Get detailed information about all pins for a component.

        Args:
            reference: Component reference (e.g., "R1")

        Returns:
            List of PinInfo objects with pin details

        Raises:
            ValueError: If component not found
        """
```

### Data Model
File: `kicad_sch_api/core/types.py`

```python
@dataclass
class PinInfo:
    """Pin information with position and metadata."""
    number: str
    name: str
    electrical_type: str  # "input", "output", "bidirectional", "power_in", "power_out", "passive"
    position: Point  # Absolute position in schematic space
    orientation: str  # "right", "left", "up", "down"
    uuid: str  # Pin unique identifier
```

### Pydantic Model for MCP
File: `mcp_server/models.py`

```python
class PinInfoOutput(BaseModel):
    number: str
    name: str
    electrical_type: str
    position: tuple[float, float]
    orientation: str
```

### MCP Tool
File: `mcp_server/tools/component_tools.py`

```python
@mcp.tool()
def get_component_pins(reference: str) -> List[PinInfoOutput]:
    """
    Get all pins for a component with detailed information.

    Enables AI to discover pins before making connections.

    Args:
        reference: Component reference (e.g., "R1")

    Returns:
        List of pin information including number, name, type, position

    Example:
        pins = get_component_pins("U1")
        for pin in pins:
            print(f"Pin {pin.number}: {pin.name} ({pin.electrical_type})")
    """
```

## Testing Requirements

### Unit Tests
File: `tests/unit/test_get_component_pins.py`

- [ ] Test with simple 2-pin component (resistor)
- [ ] Test with multi-pin IC (8-pin op-amp)
- [ ] Test with large component (100-pin MCU)
- [ ] Test pin positions match expected values
- [ ] Test pin names from symbol library
- [ ] Test electrical types are correct
- [ ] Test non-existent component returns error
- [ ] Test 0°, 90°, 180°, 270° rotations
- [ ] Test with mirrored components
- [ ] Verify all pins are in correct order

### Integration Tests
File: `tests/integration/test_pin_discovery_workflow.py`

- [ ] Load real schematic and discover pins
- [ ] Pins match KiCAD's netlist pins
- [ ] Performance: <50ms for 100-pin component

### Logging Requirements

Add DEBUG level logging at these points:
```python
logger.debug(f"Getting pins for component {reference}")
logger.debug(f"  Component position: {comp.position}")
logger.debug(f"  Component rotation: {comp.rotation}")
logger.debug(f"  Found {len(pins)} pins")
for pin in pins:
    logger.debug(f"    Pin {pin.number} ({pin.name}): ({pin.position.x}, {pin.position.y})")
```

## Acceptance Criteria

- [ ] Function returns all pins with correct data
- [ ] Pins have accurate positions (tested against KiCAD)
- [ ] Pin names/types populated from symbol library
- [ ] All rotations/mirrors supported
- [ ] Comprehensive test coverage (>95%)
- [ ] Debug logging for all operations
- [ ] Performance <50ms
- [ ] Works with MCP tool invocation

## Documentation

- Docstring with examples
- Add to `MCP_TOOLS.md`
- Include usage example in claude conversation format

## Related Issues

- #199 (Epic)
- #201 (find_pins_by_name depends on this)
- #202 (connect_pins depends on this)
```

---

#### Issue #201: Implement `find_pins_by_name` Tool

```
Title: Implement find_pins_by_name tool - semantic pin lookup
Type: Feature
Labels: mcp-server, pin-discovery, phase-1, core-tool
Epic: #199
Priority: P0
Assigned to: [Backend Developer A or B]
Estimate: 2 days
Depends on: #200

## Description

Implement semantic pin lookup so AI can find pins by meaningful names.

Instead of: "Connect R1 pin 2 to R2 pin 1"
Enable: "Connect the output of R1 to the input of R2"

## Implementation Details

### New Function
File: `kicad_sch_api/collections/components.py`

```python
class ComponentCollection:
    def find_pins_by_name(self, reference: str, name_pattern: str) -> List[str]:
        """
        Find pin numbers matching a name pattern.

        Args:
            reference: Component reference
            name_pattern: Name to search for (e.g., "VCC", "CLK", "OUT")
                         Can include wildcards: "CLK*", "*IN*"

        Returns:
            List of matching pin numbers

        Raises:
            ValueError: If component not found
        """

    def find_pins_by_type(self, reference: str, pin_type: str) -> List[str]:
        """
        Find pin numbers by electrical type.

        Args:
            reference: Component reference
            pin_type: Electrical type filter
                     ("input", "output", "power_in", "power_out", etc.)

        Returns:
            List of matching pin numbers
        """
```

## Testing Requirements

### Unit Tests
File: `tests/unit/test_find_pins_by_name.py`

- [ ] Find pins by exact name match
- [ ] Find pins by wildcard pattern
- [ ] Case-insensitive matching
- [ ] No match returns empty list
- [ ] Multiple matching pins
- [ ] Special characters in names
- [ ] Find pins by electrical type
- [ ] Non-existent component raises error

### Integration Tests
- [ ] Find "VCC" pins in 100-pin MCU
- [ ] Find "DATA*" pins in bus interface
- [ ] Performance: <50ms for large components

### Logging
```python
logger.debug(f"Finding pins matching '{name_pattern}' in {reference}")
logger.debug(f"  Found {len(results)} matching pins: {results}")
```

## Acceptance Criteria

- [ ] Wildcard pattern matching works
- [ ] Case-insensitive by default
- [ ] Returns pin numbers (strings)
- [ ] Fast enough for real-time use
- [ ] >90% test coverage
- [ ] Works with MCP tool
```

---

### Group 2: Wire Routing & Connections (Sprint 1-2)

#### Issue #202: Enhance `connect_pins` with Orthogonal Routing

```
Title: Enhance connect_pins with intelligent orthogonal routing
Type: Enhancement
Labels: mcp-server, wire-routing, phase-1, core-tool
Epic: #199
Priority: P0
Assigned to: [Backend Developer B]
Estimate: 3 days
Depends on: #200

## Description

Enhance the `connect_pins` method to support smart routing:
- Orthogonal routing (L-shape): Professional-looking connections
- Automatic routing strategy selection
- Multi-segment wire paths
- Automatic junction creation

## Implementation Details

### Enhanced Schematic Method
File: `kicad_sch_api/core/schematic.py`

```python
def connect_pins(
    self,
    ref1: str,
    pin1: str,
    ref2: str,
    pin2: str,
    routing: Literal["direct", "orthogonal", "h-first", "v-first"] = "orthogonal",
    auto_junction: bool = True,
    spacing: float = 2.54
) -> ConnectionResult:
    """
    Connect two component pins with intelligent routing.

    Args:
        ref1, pin1: First component and pin
        ref2, pin2: Second component and pin
        routing: Strategy - "direct" (line), "orthogonal" (L-shape),
                 "h-first" (horizontal then vertical),
                 "v-first" (vertical then horizontal)
        auto_junction: Auto-create junctions where wires meet
        spacing: Grid spacing for corner points

    Returns:
        ConnectionResult with wire UUIDs, junction UUIDs, path info

    Raises:
        ValueError: If components or pins not found
    """
```

### Data Model
File: `kicad_sch_api/core/types.py`

```python
@dataclass
class ConnectionResult:
    success: bool
    wire_uuids: List[str]
    junction_uuids: List[str]
    path_points: List[Point]
    total_length: float
    routing_strategy: str
```

## Implementation Strategy

### Orthogonal Routing Algorithm

```python
def _route_orthogonal(start: Point, end: Point, h_first: bool = True) -> List[Point]:
    """
    Calculate orthogonal path (L-shape) between two points.

    Args:
        start, end: Start and end points
        h_first: If True, go horizontal first then vertical
                If False, go vertical first then horizontal

    Returns:
        List of points forming the path (start, corner, end)
    """
    if h_first:
        corner = Point(end.x, start.y)
    else:
        corner = Point(start.x, end.y)

    # Snap corner to grid
    corner = snap_to_grid(corner)

    return [start, corner, end]
```

### Automatic Strategy Selection

```python
def _select_routing_strategy(start: Point, end: Point) -> str:
    """Choose routing strategy based on component positions."""
    dx = abs(end.x - start.x)
    dy = abs(end.y - start.y)

    # If horizontal separation > vertical, use h-first
    if dx > dy:
        return "h-first"
    else:
        return "v-first"
```

## Testing Requirements

### Unit Tests
File: `tests/unit/test_orthogonal_routing.py`

- [ ] Direct routing (straight line)
- [ ] Orthogonal H-first routing
- [ ] Orthogonal V-first routing
- [ ] Automatic strategy selection
- [ ] Grid snapping of corners
- [ ] Path calculation accuracy
- [ ] Multiple segment wires
- [ ] Zero-length segments handled
- [ ] Performance: <10ms per connection

### Integration Tests
File: `tests/integration/test_routing_workflows.py`

- [ ] Connect 3 resistors in series
- [ ] Voltage divider circuit
- [ ] Complex multi-component routing
- [ ] Save and load preserves routing
- [ ] KiCAD can load result without errors

### Reference Tests
File: `tests/reference_tests/test_routing_reference.py`

- [ ] Load hand-drawn KiCAD schematics
- [ ] Verify our routing matches professional standards
- [ ] Wire lengths similar to manual routing

### Logging
```python
logger.debug(f"Connecting {ref1}.{pin1} → {ref2}.{pin2}")
logger.debug(f"  Start: ({start.x}, {start.y})")
logger.debug(f"  End: ({end.x}, {end.y})")
logger.debug(f"  Routing: {routing}")
logger.debug(f"  Path points: {path_points}")
logger.debug(f"  Created wires: {wire_uuids}")
```

## Acceptance Criteria

- [ ] All routing strategies work
- [ ] Orthogonal routing creates L-shapes
- [ ] Automatic strategy selection works
- [ ] Corners snap to grid
- [ ] >95% test coverage
- [ ] Can create complete circuits (voltage divider, etc)
- [ ] Output matches professional schematics
- [ ] Performance <10ms per connection
```

---

#### Issue #203: Implement Auto-Junction Detection & Creation

```
Title: Implement automatic junction detection and creation
Type: Feature
Labels: mcp-server, connectivity, phase-1, core-tool
Epic: #199
Priority: P0
Assigned to: [Backend Developer C]
Estimate: 2 days
Depends on: #202

## Description

Automatically detect when wires meet at a point and create junctions.

Without junctions, KiCAD doesn't recognize electrical connections.

## Implementation Details

### New Methods
File: `kicad_sch_api/core/schematic.py`

```python
def has_wire_at_position(self, position: Point, tolerance: float = 0.01) -> bool:
    """Check if any wire passes through position."""

def auto_create_junctions(self) -> List[str]:
    """
    Scan all wires and create junctions where they meet.

    Returns:
        List of created junction UUIDs
    """

def add_junction(self, position: Point) -> str:
    """
    Add junction at position.

    Args:
        position: Junction position

    Returns:
        Junction UUID
    """
```

## Testing Requirements

### Unit Tests
File: `tests/unit/test_junction_detection.py`

- [ ] Detect wire crossing at T-junction
- [ ] Detect wire crossing at cross junction
- [ ] Detect wires meeting at endpoint
- [ ] Ignore near-misses (tolerance)
- [ ] Create junctions at correct positions
- [ ] No duplicate junctions
- [ ] Grid-aligned junctions

### Integration Tests
File: `tests/integration/test_junction_workflows.py`

- [ ] Create voltage divider with tap (T-junction)
- [ ] Parallel resistors (cross junction)
- [ ] Complex circuits with multiple junctions
- [ ] Validate KiCAD recognizes connections

### Logging
```python
logger.debug(f"Checking for junctions at position ({x}, {y})")
logger.debug(f"  Found {len(wires)} wires at position")
logger.debug(f"  Creating junction: {junction_uuid}")
```

## Acceptance Criteria

- [ ] All junction types detected
- [ ] Junctions created at correct positions
- [ ] No false positives
- [ ] >90% test coverage
- [ ] Can create T-junctions and crosses
```

---

### Group 3: Validation & Testing (Sprint 2)

#### Issue #204: Add Connectivity Validation Tools

```
Title: Implement connectivity validation and analysis tools
Type: Feature
Labels: mcp-server, validation, phase-1, core-tool
Epic: #199
Priority: P0
Assigned to: [Backend Developer C]
Estimate: 2 days
Depends on: #203

## Description

Implement tools to validate schematic connectivity before saving.

## Implementation Details

### New Methods
File: `kicad_sch_api/core/schematic.py`

```python
def validate_connectivity(self) -> ConnectivityReport:
    """
    Validate all connections in schematic.

    Returns:
        Report with errors, warnings, and suggestions
    """

def are_pins_connected(self, ref1: str, pin1: str, ref2: str, pin2: str) -> bool:
    """Check if two pins are electrically connected."""

def get_connection_info(self, ref: str, pin: str) -> PinConnectionInfo:
    """Get all connections to a specific pin."""
```

### Data Models
```python
@dataclass
class ValidationIssue:
    severity: Literal["error", "warning", "info"]
    component: Optional[str]
    message: str

@dataclass
class ConnectivityReport:
    passed: bool
    error_count: int
    warning_count: int
    issues: List[ValidationIssue]
```

## Testing Requirements

### Unit Tests
File: `tests/unit/test_connectivity_validation.py`

- [ ] Detect unconnected pins
- [ ] Detect floating components
- [ ] Detect missing junctions
- [ ] Detect overlapping wires
- [ ] Verify connected pins
- [ ] Check net continuity

### Logging
```python
logger.debug(f"Validating connectivity for {len(self.components)} components")
logger.debug(f"  Issues found: {len(report.issues)}")
for issue in report.issues:
    logger.debug(f"    [{issue.severity}] {issue.message}")
```

## Acceptance Criteria

- [ ] Detects common connection errors
- [ ] Clear error messages
- [ ] >90% test coverage
```

---

#### Issue #205: Create Pin Connection Testing Infrastructure

```
Title: Build comprehensive testing infrastructure for pin operations
Type: Infrastructure
Labels: testing, phase-1, core-tools
Epic: #199
Priority: P0
Assigned to: [QA/Test Engineer]
Estimate: 2 days

## Description

Create testing utilities and fixtures for pin operations.

## Implementation Details

### Test Fixtures
File: `tests/mcp_server/conftest.py`

```python
@pytest.fixture
def simple_schematic():
    """Schematic with 2 resistors for basic connection testing."""

@pytest.fixture
def complex_schematic():
    """Complex schematic with multiple component types."""

@pytest.fixture
def test_component_positions():
    """Common test component positions for consistent testing."""
```

### Helper Functions
File: `tests/helpers/pin_helpers.py`

```python
def assert_pin_exists(sch, reference: str, pin_number: str):
    """Assert a specific pin exists."""

def assert_pins_connected(sch, ref1: str, pin1: str, ref2: str, pin2: str):
    """Assert two pins are electrically connected."""

def get_pin_position(sch, reference: str, pin_number: str) -> Point:
    """Get pin position for assertions."""

def count_wires_at_position(sch, position: Point) -> int:
    """Count wires at a specific position."""
```

### Reference Test Fixtures
File: `tests/reference_kicad_projects/pin_connection_tests/`

Create several reference schematics:
- `voltage_divider/` - 2 resistors with labeled output
- `led_circuit/` - LED with series resistor
- `parallel_resistors/` - Multiple parallel paths
- `junction_test/` - T-junction and cross-junction
- `large_ic_test/` - Multi-pin IC connections

## Acceptance Criteria

- [ ] Comprehensive fixture library
- [ ] Helper functions for common assertions
- [ ] Reference test circuits created
- [ ] Fixtures easy to use and extend
```

---

#### Issue #206: Create Reference KiCAD Test Circuits

```
Title: Create reference KiCAD circuits for pin connection validation
Type: Research/Reference
Labels: testing, reference-data, phase-1
Epic: #199
Priority: P0
Assigned to: [User + Developer pair]
Estimate: 1 day (with user interaction)

## Description

Create manually-drawn KiCAD circuits to serve as reference standards.

These are CRITICAL for validating that our generated circuits match KiCAD exactly.

## Circuits to Create

1. **voltage_divider/**
   - R1: 10k, R2: 1k
   - Connected with wire
   - VCC, GND labels
   - Expected: Professional orthogonal routing

2. **led_circuit/**
   - LED with 220Ω current limiting resistor
   - Power and ground connections
   - Proper LED polarity
   - Expected: Clear routing, no crossing wires

3. **parallel_resistors/**
   - Two resistors in parallel
   - T-junctions at both ends
   - Multiple wires meeting at points
   - Expected: Junctions created, proper connectivity

4. **complex_circuit/**
   - Op-amp circuit with resistors/capacitors
   - Multiple interconnections
   - Power pins routed separately
   - Expected: Professional layout with no crossing wires

5. **ic_connections/**
   - 8-pin or 14-pin IC
   - All pins connected to various nodes
   - Multi-pin power connections
   - Expected: Pin positions accurate to symbol definition

## Creation Process

1. Open KiCAD Schematic Editor
2. Add components from standard libraries
3. Route connections professionally
4. Save to reference directory
5. Extract expected values:
   - Wire endpoints (must match pin positions)
   - Junction positions
   - Wire counts

## Testing with References

After creation, tests will:
- Load reference circuit
- Verify our pin positions match KiCAD
- Compare generated routing with reference
- Ensure electrical connectivity

## Acceptance Criteria

- [ ] All 5 reference circuits created
- [ ] Saved to `tests/reference_kicad_projects/`
- [ ] Documentation with expected values
- [ ] Tests validate against these references
```

---

#### Issue #207: Implement Comprehensive Logging for Pin Operations

```
Title: Add comprehensive debug logging to all pin operations
Type: Enhancement
Labels: logging, debugging, phase-1
Epic: #199
Priority: P0
Assigned to: [Backend Developer A]
Estimate: 1 day

## Description

Add structured debug logging at all critical points in pin operations.

Critical for debugability when users report issues.

## Logging Points

### Pin Position Calculation
```python
logger.debug(f"get_component_pin_position: {reference}.{pin_number}")
logger.debug(f"  Component position: ({x}, {y})")
logger.debug(f"  Component rotation: {rotation}°")
logger.debug(f"  Component mirror: {mirror}")
logger.debug(f"  Pin relative position: ({rel_x}, {rel_y})")
logger.debug(f"  After transformation: ({abs_x}, {abs_y})")
```

### Wire Creation
```python
logger.debug(f"Creating wire from ({start.x}, {start.y}) to ({end.x}, {end.y})")
logger.debug(f"  Wire UUID: {wire_uuid}")
logger.debug(f"  Grid aligned: {is_grid_aligned}")
```

### Connection Operations
```python
logger.debug(f"Connecting pins: {ref1}.{pin1} → {ref2}.{pin2}")
logger.debug(f"  Routing strategy: {strategy}")
logger.debug(f"  Path points: {path}")
logger.debug(f"  Wires created: {len(wire_uuids)}")
logger.debug(f"  Junctions created: {len(junction_uuids)}")
```

### Junction Detection
```python
logger.debug(f"Scanning for junctions...")
logger.debug(f"  Found {n} potential junction points")
logger.debug(f"  Created {m} junctions")
```

## Logging Configuration
File: `mcp_server/utils/logging.py`

```python
def configure_logging(level: str = "INFO"):
    """Configure structured logging with JSON output."""
    # Use structlog for JSON output
    # Log to file: logs/mcp_server.log
    # Console output for errors only
```

## Acceptance Criteria

- [ ] All critical operations have DEBUG logs
- [ ] Logs are structured and queryable
- [ ] Performance impact minimal (<5%)
- [ ] Log levels appropriate (DEBUG for detail, INFO for operations)
```

---

#### Issue #208: Create Pin Connection Documentation

```
Title: Create comprehensive documentation for pin connection tools
Type: Documentation
Labels: documentation, phase-1
Epic: #199
Priority: P0
Assigned to: [Documentation Writer]
Estimate: 2 days

## Documentation to Create

### 1. MCP_PIN_CONNECTION_USER_GUIDE.md

**Audience**: MCP users (AI assistants using the server)

**Sections**:
- Overview of pin connection capabilities
- Pin discovery workflow
- Semantic pin lookup examples
- Connection routing strategies
- Common patterns and examples
- Troubleshooting guide

**Examples**:
```markdown
## Connecting Components

### Discover Pins First

User: "What pins does U1 have?"

Claude uses: get_component_pins("U1")

### Connect by Pin Name

User: "Connect the clock output of U1 to the clock input of U2"

Claude:
1. find_pins_by_name("U1", "CLK*OUT") → ["14"]
2. find_pins_by_name("U2", "CLK*IN") → ["3"]
3. connect_pins("U1", "14", "U2", "3")
```

### 2. API_REFERENCE_PIN_TOOLS.md

**Audience**: Developers implementing MCP server

**Sections per tool**:
- Purpose and use case
- Function signature
- Parameters and types
- Return values with examples
- Error handling
- Performance characteristics
- Testing coverage

### 3. PIN_CONNECTION_ARCHITECTURE.md

**Audience**: Developers contributing to library

**Sections**:
- Design patterns for pin operations
- Coordinate system explanation
- Transformation pipeline (with diagrams)
- Routing algorithms
- Junction detection strategy
- Grid alignment requirements

### 4. TROUBLESHOOTING_PIN_ISSUES.md

**Audience**: Everyone

**Common Issues**:
- Pins not connecting electrically
- Wire routing looks wrong
- Missing junctions
- Position calculation errors
- KiCAD doesn't load schematic

**For each**:
- Symptoms
- Likely causes
- Debug steps
- Solutions

## Acceptance Criteria

- [ ] 4 documentation files created
- [ ] All examples work in Claude
- [ ] Code examples match actual implementation
- [ ] Clear, accessible language
- [ ] Comprehensive but not overwhelming
```

---

## Implementation Tracking

### Timeline

**Week 1 (Days 1-5)**:
- Day 1: #200 (get_component_pins) + #207 (logging)
- Day 1-2: #201 (find_pins_by_name)
- Day 2-3: #202 (orthogonal routing)
- Day 3-4: #203 (auto-junctions) + #205 (testing infra)
- Day 4-5: #204 (validation)

**Week 2 (Days 6-10)**:
- Day 6: #206 (reference circuits - collaborative with user)
- Day 6-7: #208 (documentation)
- Day 7-10: Integration testing, bug fixes, polish

### Parallel Development

**Track A (Pin Discovery)**: Issues #200, #201, #207
**Track B (Wire Routing)**: Issues #202, #203, #204
**Track C (Testing & Docs)**: Issues #205, #206, #208

These tracks can run in parallel with minimal conflicts.

### Dependencies

```
#200 (get_component_pins) → #201, #202, #205
#202 (routing) → #203 (junctions)
#203 (junctions) → #204 (validation)
#207 (logging) → independent, can start immediately
#205 (test infra) → supports all testing
#206 (reference circuits) → independent, can start anytime
#208 (docs) → independent, can start after implementations
```

---

## GitHub Integration

### Labels to Create

```
epic
mcp-server
phase-1
pin-discovery
wire-routing
connectivity
testing
reference-data
high-priority
```

### Milestones

- **Pin Connection v1.0**: All issues in this epic
- **Phase 1 Complete**: All Phase 1 epics finished

### Automation

Add these to GitHub:
- [ ] Assign issues to track owners
- [ ] Link all issues to epic #199
- [ ] Add to project board "Phase 1"
- [ ] Set up automated testing on PR
- [ ] Require test coverage >90%

---

## Success Criteria

✅ All issues completed
✅ >95% test coverage
✅ All operations have DEBUG logging
✅ Reference circuits created and validated
✅ Documentation complete
✅ Can create complete circuits (voltage divider, LED, etc)
✅ Output matches professional KiCAD schematics
✅ Works flawlessly in Claude conversations
