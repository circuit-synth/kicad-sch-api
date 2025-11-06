# MCP Server: Pin Connection & Wire Routing Strategy

**Date**: 2025-11-06
**Issue**: Pin/wire connection accuracy is critical for MCP server usability
**Status**: Analysis & Enhancement Plan

---

## Executive Summary

You're absolutely right - **pin connection accuracy is the make-or-break feature** for the MCP server. AI assistants need simple, foolproof ways to connect components electrically. This document outlines:

1. **Current capabilities** (what exists in kicad-sch-api v0.5.0)
2. **Gaps & challenges** for AI-driven schematic creation
3. **MCP-specific enhancements** needed for production use
4. **Implementation recommendations** for Phase 1-2

---

## Current State: What Exists (v0.5.0)

### ✅ Core Pin Position Calculation

**File**: `kicad_sch_api/core/pin_utils.py`

**Functions**:
```python
# Get absolute position of a specific pin
def get_component_pin_position(component: SchematicSymbol, pin_number: str) -> Optional[Point]

# List all pins with their absolute positions
def list_component_pins(component: SchematicSymbol) -> List[Tuple[str, Point]]
```

**Features**:
- Accurate pin position calculation with **full transformation support**:
  - Component position translation
  - Rotation (0°, 90°, 180°, 270°)
  - Mirroring (x-axis, y-axis)
  - **Y-axis inversion** (symbol space → schematic space)
- Symbol library integration for pin definitions
- Comprehensive logging for debugging
- Grid-aligned positions (1.27mm KiCad grid)

**Testing**: 19 tests covering all rotations, transformations, and real KiCad references

### ✅ Schematic-Level Pin Methods

**File**: `kicad_sch_api/core/schematic.py`

**Methods**:
```python
# Get pin position by reference
sch.get_component_pin_position(reference: str, pin_number: str) -> Optional[Point]

# Wire from point to pin
sch.add_wire_to_pin(start: Point, component_ref: str, pin_number: str) -> Optional[str]

# Wire between two pins (direct connection)
sch.add_wire_between_pins(ref1: str, pin1: str, ref2: str, pin2: str) -> Optional[str]

# Alias for clarity
sch.connect_pins_with_wire(ref1: str, pin1: str, ref2: str, pin2: str) -> Optional[str]
```

**Features**:
- High-level API for pin-to-pin connections
- Automatic pin lookup and validation
- Returns `None` if component/pin not found (safe failure)
- UUID tracking for created wires

**Testing**: 18 tests for pin-to-pin wiring workflows

---

## Critical Gap Analysis for MCP Server

### ❌ Problem 1: AI Doesn't Know Pin Numbers/Names

**Issue**: AI assistants need to discover pin information programmatically

**Example**:
```
User: "Connect the output of U1 to the input of U2"

AI needs to know:
- U1 is an op-amp with pins: 1=IN+, 2=IN-, 3=OUT, 4=V-, 5=V+
- U2 is a resistor with pins: 1, 2
- "output" maps to pin 3 on U1
- "input" maps to pin 1 on U2
```

**Missing Tool**:
```python
# MCP Tool needed:
get_component_pins(reference: str) -> List[PinInfo]

# Returns:
[
    {"number": "1", "name": "IN+", "type": "input", "position": (100.0, 96.19)},
    {"number": "2", "name": "IN-", "type": "input", "position": (100.0, 103.81)},
    {"number": "3", "name": "OUT", "type": "output", "position": (115.0, 100.0)},
    ...
]
```

### ❌ Problem 2: No "Smart Routing" for Orthogonal Wires

**Issue**: Direct pin-to-pin wires create diagonal connections (not professional)

**Current behavior**:
```python
# R1 at (100, 100), R2 at (150, 120)
sch.connect_pins_with_wire("R1", "2", "R2", "1")
# Creates: diagonal wire from (103.81, 100) to (146.19, 120) ❌
```

**Expected behavior** (professional schematic):
```
R1 pin 2 → horizontal wire → vertical wire → R2 pin 1
(orthogonal routing with automatic junction)
```

**Missing Feature**:
```python
# Smart routing options:
sch.connect_pins_with_wire(
    "R1", "2", "R2", "1",
    routing="orthogonal"  # or "direct", "horizontal-first", "vertical-first"
)
```

### ❌ Problem 3: No Automatic Junction Creation

**Issue**: Multiple wires meeting at a point need explicit junctions for connectivity

**Current**:
```python
sch.add_wire_between_pins("R1", "2", "R2", "1")  # Wire 1
sch.add_wire_between_pins("R1", "2", "R3", "1")  # Wire 2 from same point
# KiCad may not recognize this as electrically connected without junction!
```

**Needed**:
```python
# Automatic junction detection and creation
sch.connect_pins_with_wire("R1", "2", "R2", "1", auto_junction=True)
sch.connect_pins_with_wire("R1", "2", "R3", "1", auto_junction=True)
# Should auto-create junction at R1 pin 2 position
```

### ❌ Problem 4: No Pin Name/Function Lookup

**Issue**: AI needs to find pins by semantic meaning, not just number

**Example queries AI needs to support**:
- "Connect to the gate pin of Q1" (not "Connect to pin 1 of Q1")
- "Connect the clock input" (find the CLK pin)
- "Connect all VCC pins to power"

**Missing Functionality**:
```python
# Find pins by name/function
sch.find_component_pins_by_name(reference: str, name_pattern: str) -> List[str]
# Example: find_component_pins_by_name("U1", "VCC") → ["7", "14"]

sch.find_component_pins_by_type(reference: str, pin_type: str) -> List[str]
# Example: find_component_pins_by_type("Q1", "gate") → ["1"]
```

### ❌ Problem 5: No Visual Layout Assistance

**Issue**: AI doesn't know where to place components for clean routing

**Current**: AI must specify exact positions (hard without visual feedback)

**Needed**: Layout helpers
```python
# Auto-positioning for clean layouts
sch.auto_position_component(
    lib_id="Device:R",
    reference="R2",
    relative_to="R1",
    direction="right",  # or "below", "above", "left"
    spacing=50.0  # mm
)

# Grid-aligned positioning helpers
sch.snap_to_grid(position: Point) -> Point
sch.suggest_wire_path(from_pin: str, to_pin: str) -> List[Point]
```

### ❌ Problem 6: No Connection Validation

**Issue**: No way to verify connections are electrically valid before saving

**Needed**:
```python
# Validate connectivity
sch.validate_connections() -> ValidationResult

# Check if two points are electrically connected
sch.are_pins_connected(ref1: str, pin1: str, ref2: str, pin2: str) -> bool

# Get all components on a net
sch.get_net_components(net_name: str) -> List[str]
```

---

## Recommended MCP-Specific Enhancements

### Phase 1: Essential Pin Discovery (Week 1-2)

#### Tool 1: `get_component_pins`
```python
@mcp.tool()
def get_component_pins(reference: str) -> List[PinInfo]:
    """
    Get all pins for a component with positions and metadata.

    Essential for AI to discover what pins exist before connecting.

    Returns:
        List of pin information including number, name, type, position
    """
```

**Implementation**:
```python
from kicad_sch_api.core.pin_utils import list_component_pins

class PinInfo(BaseModel):
    number: str
    name: str
    pin_type: str  # "input", "output", "bidirectional", "power_in", etc.
    position: tuple[float, float]
    orientation: str  # "right", "left", "up", "down"

def get_component_pins(reference: str) -> List[PinInfo]:
    component = ctx.current_schematic.components.get(reference)
    if not component:
        raise ValueError(f"Component {reference} not found")

    # Get pins with positions
    pins_with_pos = list_component_pins(component)

    # Get pin metadata from symbol library
    symbol_cache = get_symbol_cache()
    symbol_def = symbol_cache.get_symbol(component.lib_id)

    result = []
    for pin_num, pos in pins_with_pos:
        # Find pin definition for metadata
        pin_def = next((p for p in symbol_def.pins if p.number == pin_num), None)

        result.append(PinInfo(
            number=pin_num,
            name=pin_def.name if pin_def else pin_num,
            pin_type=pin_def.electrical_type if pin_def else "passive",
            position=(pos.x, pos.y),
            orientation=pin_def.orientation if pin_def else "right"
        ))

    return result
```

**Priority**: P0 (critical for usability)

#### Tool 2: `find_pins_by_name`
```python
@mcp.tool()
def find_pins_by_name(reference: str, name_pattern: str) -> List[str]:
    """
    Find pin numbers by semantic name (e.g., "VCC", "CLK", "OUT").

    Enables natural language connections:
    "Connect the clock pin" instead of "Connect pin 14"
    """
```

**Priority**: P0 (enables natural language)

#### Tool 3: `connect_pins` (enhanced version)
```python
@mcp.tool()
def connect_pins(
    ref1: str,
    pin1: str,
    ref2: str,
    pin2: str,
    routing: Literal["direct", "orthogonal", "horizontal-first", "vertical-first"] = "orthogonal",
    auto_junction: bool = True
) -> ConnectionResult:
    """
    Connect two component pins with intelligent routing.

    Args:
        ref1, pin1: First component and pin
        ref2, pin2: Second component and pin
        routing: Wire routing strategy
        auto_junction: Automatically create junctions where wires meet

    Returns:
        ConnectionResult with wire UUIDs, junction UUIDs, and connection info
    """
```

**Implementation** (orthogonal routing):
```python
class ConnectionResult(BaseModel):
    success: bool
    wire_uuids: List[str]
    junction_uuids: List[str]
    total_wire_length: float
    connection_path: List[tuple[float, float]]

def connect_pins(
    ref1: str, pin1: str, ref2: str, pin2: str,
    routing: str = "orthogonal",
    auto_junction: bool = True
) -> ConnectionResult:

    # Get pin positions
    pos1 = sch.get_component_pin_position(ref1, pin1)
    pos2 = sch.get_component_pin_position(ref2, pin2)

    if not pos1 or not pos2:
        return ConnectionResult(success=False, wire_uuids=[], junction_uuids=[])

    wire_uuids = []
    junction_uuids = []

    if routing == "direct":
        # Simple direct wire
        wire_uuid = sch.add_wire(pos1, pos2)
        wire_uuids.append(wire_uuid)

    elif routing == "orthogonal":
        # Create orthogonal path (L-shape)
        # Choose horizontal-first or vertical-first based on geometry
        dx = abs(pos2.x - pos1.x)
        dy = abs(pos2.y - pos1.y)

        if dx > dy:
            # Horizontal-first (longer horizontal run)
            midpoint = Point(pos2.x, pos1.y)
        else:
            # Vertical-first (longer vertical run)
            midpoint = Point(pos1.x, pos2.y)

        # Add two wire segments
        wire1_uuid = sch.add_wire(pos1, midpoint)
        wire2_uuid = sch.add_wire(midpoint, pos2)
        wire_uuids.extend([wire1_uuid, wire2_uuid])

        # Check if junction needed at midpoint
        if auto_junction:
            # Check if other wires exist at midpoint
            if sch.has_wire_at_position(midpoint):
                junction_uuid = sch.add_junction(midpoint)
                junction_uuids.append(junction_uuid)

    return ConnectionResult(
        success=True,
        wire_uuids=wire_uuids,
        junction_uuids=junction_uuids,
        total_wire_length=calculate_path_length([pos1, midpoint, pos2]),
        connection_path=[(pos1.x, pos1.y), (midpoint.x, midpoint.y), (pos2.x, pos2.y)]
    )
```

**Priority**: P0 (core functionality upgrade)

---

### Phase 2: Smart Layout & Validation (Week 3-4)

#### Tool 4: `auto_position_component`
```python
@mcp.tool()
def auto_position_component(
    lib_id: str,
    reference: str,
    value: str,
    relative_to: str,
    direction: Literal["right", "left", "above", "below"],
    spacing: float = 50.0
) -> ComponentInfo:
    """
    Add component with automatic positioning relative to existing component.

    Enables AI to build circuits without calculating exact coordinates.
    """
```

**Priority**: P1 (major UX improvement)

#### Tool 5: `validate_connectivity`
```python
@mcp.tool()
def validate_connectivity() -> ConnectivityReport:
    """
    Validate all connections in the schematic.

    Returns:
        - Unconnected pins
        - Missing junctions
        - Overlapping wires without junctions
        - Floating components
    """
```

**Priority**: P1 (ensures schematic quality)

#### Tool 6: `get_connection_info`
```python
@mcp.tool()
def get_connection_info(reference: str, pin_number: str) -> ConnectionInfo:
    """
    Get all connections to a specific pin.

    Returns:
        - Connected components and pins
        - Net name (if labeled)
        - Wire paths
        - Junctions
    """
```

**Priority**: P1 (debugging aid)

---

### Phase 3: Advanced Features (Week 5-6)

#### Tool 7: `suggest_wire_path`
```python
@mcp.tool()
def suggest_wire_path(
    from_ref: str, from_pin: str,
    to_ref: str, to_pin: str
) -> SuggestedPath:
    """
    Suggest optimal wire routing path between pins.

    Uses heuristics:
    - Prefer orthogonal routing
    - Avoid crossing existing wires
    - Minimize total wire length
    - Respect grid alignment
    """
```

**Priority**: P2 (nice to have)

#### Tool 8: `connect_bus`
```python
@mcp.tool()
def connect_bus(
    component1: str,
    pins1: List[str],
    component2: str,
    pins2: List[str],
    spacing: float = 2.54
) -> BusConnectionResult:
    """
    Connect multiple pins as a bus with uniform spacing.

    Example: Connect 8-bit data bus between microcontroller and RAM.
    """
```

**Priority**: P2 (advanced use case)

---

## Implementation Recommendations

### Immediate Actions (Phase 1 - Week 1-2)

1. **Expose `list_component_pins` in ComponentCollection**
   ```python
   # Add to kicad_sch_api/collections/components.py
   def list_pins(self, reference: str) -> List[Tuple[str, Point]]:
       """List all pins for a component."""
       component = self.get(reference)
       return list_component_pins(component)
   ```

2. **Add `get_component_pins` MCP tool** (returns structured pin info)

3. **Add `find_pins_by_name` MCP tool** (semantic pin lookup)

4. **Enhance `connect_pins` with routing options**:
   - Direct routing (current behavior)
   - Orthogonal routing (L-shape)
   - Auto-junction detection

5. **Add comprehensive MCP tool examples** in docs:
   ```markdown
   # Example: Connecting components

   User: "Connect R1 pin 2 to R2 pin 1"

   AI:
   1. get_component_pins("R1") → find pin 2 position
   2. get_component_pins("R2") → find pin 1 position
   3. connect_pins("R1", "2", "R2", "1", routing="orthogonal")
   ```

### Medium-Term (Phase 2 - Week 3-4)

1. **Smart positioning helpers** for component layout
2. **Connectivity validation** before save
3. **Net tracing** for debugging
4. **Junction management** (detect + auto-create)

### Long-Term (Phase 3+)

1. **Wire routing optimization** (avoid crossings)
2. **Bus connections** (multi-pin parallel routing)
3. **Differential pair routing** (controlled spacing)
4. **PCB-style autorouting** (advanced path finding)

---

## Testing Strategy

### Unit Tests (per MCP tool)
```python
def test_get_component_pins():
    """Test pin discovery returns all pin info."""
    result = get_component_pins("U1")
    assert len(result) > 0
    assert all(isinstance(p, PinInfo) for p in result)
    assert all(p.number and p.position for p in result)

def test_connect_pins_orthogonal():
    """Test orthogonal routing creates L-shape."""
    result = connect_pins("R1", "2", "R2", "1", routing="orthogonal")
    assert result.success
    assert len(result.wire_uuids) == 2  # Two segments
    assert result.connection_path has three points  # start, corner, end
```

### Integration Tests (real workflows)
```python
def test_voltage_divider_workflow():
    """Test complete voltage divider creation with pin connections."""
    # Create schematic
    create_schematic("Test")

    # Add components
    add_component("Device:R", "R1", "10k", position=(100, 100))
    add_component("Device:R", "R2", "1k", position=(100, 120))

    # Connect with orthogonal routing
    result = connect_pins("R1", "2", "R2", "1", routing="orthogonal")
    assert result.success

    # Validate connectivity
    validation = validate_connectivity()
    assert validation.error_count == 0
```

### Reference Tests (against KiCad)
- Load manually created KiCad schematics
- Verify our pin positions match KiCad's netlist
- Ensure wire routing produces valid KiCad files

---

## Documentation Requirements

### MCP Server User Guide Updates

Add comprehensive section: **"Connecting Components"**

```markdown
## Connecting Components

### Discovering Pins

Before connecting components, discover available pins:

User: "What pins does U1 have?"

Claude uses: get_component_pins("U1")
Returns: List of all pins with numbers, names, types, positions

### Connecting by Pin Number

User: "Connect R1 pin 2 to R2 pin 1"

Claude uses: connect_pins("R1", "2", "R2", "1")
Creates: Orthogonal wire connection (default)

### Connecting by Pin Name

User: "Connect the clock output of U1 to the clock input of U2"

Claude uses:
1. find_pins_by_name("U1", "CLK_OUT") → "14"
2. find_pins_by_name("U2", "CLK_IN") → "3"
3. connect_pins("U1", "14", "U2", "3")

### Routing Options

Specify routing strategy for different layout needs:

- **orthogonal** (default): Professional L-shape routing
- **direct**: Straight line (quick but may look messy)
- **horizontal-first**: Go horizontal then vertical
- **vertical-first**: Go vertical then horizontal
```

### Tool Reference Documentation

Document each new tool with:
- Purpose and use case
- Input parameters with types
- Output structure with examples
- Common error cases
- Claude conversation examples

---

## Success Metrics

### Usability Metrics
- **Pin discovery success rate**: >99% (AI finds correct pins)
- **Connection accuracy**: 100% (wires connect to exact pin positions)
- **Routing quality**: >90% orthogonal connections by default
- **User satisfaction**: "Just works" - minimal debugging needed

### Technical Metrics
- **Pin position accuracy**: <0.1mm error vs KiCad
- **Junction detection**: 100% of T-junctions detected
- **Grid alignment**: 100% of wire endpoints on grid
- **Performance**: <50ms to connect two pins

### Quality Metrics
- **KiCad compatibility**: 100% of schematics open without errors
- **ERC clean**: >95% of AI-generated circuits pass basic ERC
- **Visual quality**: Orthogonal routing matches hand-drawn schematics

---

## Risk Mitigation

### Risk 1: Pin Position Errors
**Mitigation**: Extensive testing against KiCad references (already done in v0.5.0)

### Risk 2: AI Chooses Wrong Pins
**Mitigation**: Rich pin metadata (names, types) + examples in prompts

### Risk 3: Complex Routing Failures
**Mitigation**: Fallback to direct routing if orthogonal fails

### Risk 4: Junction Detection False Positives
**Mitigation**: Configurable tolerance + validation tool

---

## Conclusion

**Pin connection accuracy is THE critical feature for MCP server success.**

**Current State**: Strong foundation with accurate pin positioning (v0.5.0)

**Immediate Needs** (Phase 1):
1. ✅ Pin discovery tool (`get_component_pins`)
2. ✅ Semantic pin lookup (`find_pins_by_name`)
3. ✅ Enhanced connection tool with routing options
4. ✅ Comprehensive documentation with examples

**Future Enhancements** (Phase 2-3):
- Smart component positioning
- Connectivity validation
- Advanced routing algorithms
- Bus connections

**With these enhancements, AI assistants can create professional-quality KiCad schematics through natural language.**

---

**Next Steps**:
1. Review this strategy with core team
2. Prioritize Phase 1 tools for MCP v1.0
3. Implement and test with real Claude conversations
4. Iterate based on user feedback
