# Orthogonal Routing Guide

Comprehensive guide to automatic wire routing in kicad-sch-api using Manhattan-style (orthogonal) routing algorithms.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [API Reference](#api-reference)
- [Direction Modes](#direction-modes)
- [KiCAD Y-Axis Inversion](#kicad-y-axis-inversion)
- [Practical Examples](#practical-examples)
- [Best Practices](#best-practices)
- [Integration with MCP Server](#integration-with-mcp-server)
- [Troubleshooting](#troubleshooting)

## Overview

The orthogonal routing module provides automatic Manhattan-style wire routing between points in KiCAD schematics. Instead of manually calculating wire paths and junction points, you can use the routing algorithm to generate professional L-shaped or direct wire routes.

### What is Orthogonal Routing?

Orthogonal routing (also called Manhattan routing) creates wire paths that only use horizontal and vertical segments - never diagonal. This is the standard approach in electronic schematics and PCB design.

```
Point A ----→----+
                 |
                 ↓
                 Point B

Instead of: A ╱ B (diagonal)
```

### When to Use This

- **Automatic circuit generation**: Let the algorithm handle wire routing
- **Component-to-component connections**: Connect pins with proper L-shaped routes
- **Voltage dividers and T-junctions**: Route with correct corner positions
- **MCP server integration**: Enable AI agents to create properly routed circuits

## Quick Start

### Basic Usage

```python
from kicad_sch_api.core.types import Point
from kicad_sch_api.geometry import create_orthogonal_routing

# Create routing between two points
result = create_orthogonal_routing(
    Point(100.0, 100.0),  # From position
    Point(150.0, 125.0)   # To position
)

print(f"Segments: {len(result.segments)}")  # 2 (L-shaped)
print(f"Corner: {result.corner}")           # Point(150.0, 100.0)
print(f"Is direct: {result.is_direct}")     # False
```

### With Real Components

```python
import kicad_sch_api as ksa
from kicad_sch_api.geometry import create_orthogonal_routing

# Create schematic and add components
sch = ksa.create_schematic("Auto Routing Demo")
r1 = sch.components.add("Device:R", "R1", "10k", position=(100.0, 100.0))
r2 = sch.components.add("Device:R", "R2", "10k", position=(150.0, 125.0))

# Get pin positions
r1_pins = sch.components.get_pins_info("R1")
r2_pins = sch.components.get_pins_info("R2")
r1_pin2 = next(p for p in r1_pins if p.number == "2")
r2_pin1 = next(p for p in r2_pins if p.number == "1")

# Create routing
result = create_orthogonal_routing(r1_pin2.position, r2_pin1.position)

# Add wires to schematic
for start, end in result.segments:
    sch.wires.add(start=start, end=end)

sch.save("auto_routed.kicad_sch")
```

## Core Concepts

### RoutingResult

The routing algorithm returns a `RoutingResult` object with three key attributes:

```python
@dataclass
class RoutingResult:
    segments: List[Tuple[Point, Point]]  # Wire segments
    corner: Optional[Point]               # Corner junction point
    is_direct: bool                       # True if single straight line
```

### Direct vs L-Shaped Routing

**Direct Routing** (when points are aligned):
```python
# Horizontal alignment (same Y)
result = create_orthogonal_routing(
    Point(100.0, 100.0),
    Point(150.0, 100.0)
)
assert result.is_direct == True
assert len(result.segments) == 1
assert result.corner is None
```

**L-Shaped Routing** (when points are not aligned):
```python
# Not aligned - needs corner
result = create_orthogonal_routing(
    Point(100.0, 100.0),
    Point(150.0, 125.0)
)
assert result.is_direct == False
assert len(result.segments) == 2
assert result.corner is not None  # Point(150.0, 100.0)
```

### Segments

Each routing result contains a list of wire segments:

```python
for start, end in result.segments:
    print(f"Wire from ({start.x}, {start.y}) to ({end.x}, {end.y})")

# Output for L-shaped routing:
# Wire from (100.0, 100.0) to (150.0, 100.0)  # Horizontal
# Wire from (150.0, 100.0) to (150.0, 125.0)  # Vertical
```

## API Reference

### create_orthogonal_routing()

```python
def create_orthogonal_routing(
    from_pos: Point,
    to_pos: Point,
    corner_direction: CornerDirection = CornerDirection.AUTO
) -> RoutingResult:
    """
    Create orthogonal (Manhattan) routing between two points.

    Args:
        from_pos: Starting point
        to_pos: Ending point
        corner_direction: Direction preference for L-shaped corner
            - AUTO: Choose based on distance heuristic
            - HORIZONTAL_FIRST: Route horizontally, then vertically
            - VERTICAL_FIRST: Route vertically, then horizontally

    Returns:
        RoutingResult with segments list, corner point, and direct flag
    """
```

### validate_routing_result()

```python
def validate_routing_result(result: RoutingResult) -> bool:
    """
    Validate that routing result is correct.

    Checks:
    - All segments are orthogonal (horizontal or vertical)
    - Segments connect end-to-end
    - Corner point matches segment endpoints if present

    Raises:
        ValueError: If routing is invalid

    Returns:
        True if routing is valid
    """
```

## Direction Modes

The routing algorithm supports three direction modes via the `corner_direction` parameter.

### AUTO (Default)

Automatically chooses direction based on distance heuristic:
- If `dx >= dy`: Route horizontally first
- If `dy > dx`: Route vertically first

```python
from kicad_sch_api.geometry import CornerDirection

# Horizontal distance (50) > vertical distance (25)
result = create_orthogonal_routing(
    Point(100.0, 100.0),
    Point(150.0, 125.0),
    corner_direction=CornerDirection.AUTO
)
# Result: Horizontal first → corner at (150.0, 100.0)
```

**When to use:** Most cases - provides sensible routing automatically.

### HORIZONTAL_FIRST

Always routes horizontally first, then vertically:

```python
result = create_orthogonal_routing(
    Point(100.0, 100.0),
    Point(150.0, 125.0),
    corner_direction=CornerDirection.HORIZONTAL_FIRST
)
# Corner at (150.0, 100.0) - destination X, source Y
```

**Visual:**
```
Start ----→----+
               |
               ↓
               End
```

**When to use:**
- Routing to power rails (horizontal buses)
- Connecting to horizontal connectors
- Aesthetic preference for horizontal-first routing

### VERTICAL_FIRST

Always routes vertically first, then horizontally:

```python
result = create_orthogonal_routing(
    Point(100.0, 100.0),
    Point(150.0, 125.0),
    corner_direction=CornerDirection.VERTICAL_FIRST
)
# Corner at (100.0, 125.0) - source X, destination Y
```

**Visual:**
```
Start
  |
  ↓
  +----→---- End
```

**When to use:**
- Routing to ground planes (vertical connections)
- Connecting to vertical connectors
- Avoiding horizontal obstacles

### Comparison Example

```python
from_pos = Point(100.0, 100.0)
to_pos = Point(150.0, 125.0)

# All three modes
auto_result = create_orthogonal_routing(from_pos, to_pos, CornerDirection.AUTO)
h_first_result = create_orthogonal_routing(from_pos, to_pos, CornerDirection.HORIZONTAL_FIRST)
v_first_result = create_orthogonal_routing(from_pos, to_pos, CornerDirection.VERTICAL_FIRST)

print(f"AUTO corner: {auto_result.corner}")        # (150.0, 100.0) - horizontal first
print(f"H_FIRST corner: {h_first_result.corner}")  # (150.0, 100.0)
print(f"V_FIRST corner: {v_first_result.corner}")  # (100.0, 125.0)
```

## KiCAD Y-Axis Inversion

### Critical Concept

**KiCAD uses an inverted Y-axis** in schematic space. This is CRITICAL for understanding routing:

```
Normal (Math):        KiCAD (Graphics):
    +Y ↑                   +X →
       |                        ↓ +Y
  -----+----→ +X
       |
```

### What This Means

- **Lower Y values** = visually **HIGHER** on screen (top)
- **Higher Y values** = visually **LOWER** on screen (bottom)
- **X-axis is normal** (increases to the right)

### Practical Example

```python
# Component at top of screen
top_component = Point(100.0, 80.0)    # Lower Y = higher position

# Component at bottom of screen
bottom_component = Point(100.0, 120.0)  # Higher Y = lower position

# Routing "downward" on screen
result = create_orthogonal_routing(
    top_component,      # Y = 80 (visually higher)
    bottom_component    # Y = 120 (visually lower)
)
# Vertical segment goes from Y=80 to Y=120 (increasing Y = moving down)
```

### Why This Matters

The routing algorithm handles this automatically, but you need to understand it when:
- Interpreting pin positions
- Debugging routing issues
- Understanding corner positions
- Reasoning about "above" vs "below" in schematics

### Testing Y-Axis Awareness

```python
# Routing "upward" on screen (to lower Y)
result = create_orthogonal_routing(
    Point(100.0, 125.0),  # Start (visually lower)
    Point(150.0, 100.0),  # End (visually higher - lower Y!)
    corner_direction=CornerDirection.HORIZONTAL_FIRST
)

# Second segment should have decreasing Y (moving "up")
seg2_start, seg2_end = result.segments[1]
assert seg2_end.y < seg2_start.y  # End Y < Start Y means "upward"
```

## Practical Examples

### Example 1: Voltage Divider

```python
import kicad_sch_api as ksa
from kicad_sch_api.geometry import create_orthogonal_routing

# Create voltage divider circuit
sch = ksa.create_schematic("Voltage Divider")

# Add resistors in series
r1 = sch.components.add("Device:R", "R1", "10k", position=(127.0, 88.9))
r2 = sch.components.add("Device:R", "R2", "10k", position=(127.0, 114.3))

# Get pin positions
r1_pins = sch.components.get_pins_info("R1")
r2_pins = sch.components.get_pins_info("R2")
r1_pin2 = next(p for p in r1_pins if p.number == "2")
r2_pin1 = next(p for p in r2_pins if p.number == "1")

# Route R1 to R2 (direct vertical - they're aligned)
result = create_orthogonal_routing(r1_pin2.position, r2_pin1.position)
for start, end in result.segments:
    sch.wires.add(start=start, end=end)

# Add output tap at midpoint
midpoint_y = (r1_pin2.position.y + r2_pin1.position.y) / 2
midpoint = Point(127.0, midpoint_y)
output = Point(160.0, midpoint_y)

result2 = create_orthogonal_routing(midpoint, output)
for start, end in result2.segments:
    sch.wires.add(start=start, end=end)

sch.save("voltage_divider.kicad_sch")
```

### Example 2: Filter Chain

```python
import kicad_sch_api as ksa
from kicad_sch_api.geometry import create_orthogonal_routing, CornerDirection

sch = ksa.create_schematic("Filter Chain")

# Add a chain of filters with alternating positions
filters = []
for i in range(5):
    x = 100.0 + i * 50.0
    y = 100.0 + (i % 2) * 25.0  # Zigzag pattern
    r = sch.components.add("Device:R", f"R{i+1}", "1k", position=(x, y))
    filters.append(r)

# Route between consecutive filters
for i in range(len(filters) - 1):
    r1_pins = sch.components.get_pins_info(filters[i].reference)
    r2_pins = sch.components.get_pins_info(filters[i+1].reference)

    r1_pin2 = next(p for p in r1_pins if p.number == "2")
    r2_pin1 = next(p for p in r2_pins if p.number == "1")

    # Use AUTO direction for natural routing
    result = create_orthogonal_routing(
        r1_pin2.position,
        r2_pin1.position,
        corner_direction=CornerDirection.AUTO
    )

    for start, end in result.segments:
        sch.wires.add(start=start, end=end)

sch.save("filter_chain.kicad_sch")
```

### Example 3: Power Distribution

```python
import kicad_sch_api as ksa
from kicad_sch_api.geometry import create_orthogonal_routing, CornerDirection

sch = ksa.create_schematic("Power Distribution")

# VCC rail position
vcc_rail = Point(50.0, 50.0)

# Add multiple components that need VCC
components = []
positions = [(100.0, 80.0), (150.0, 100.0), (120.0, 120.0)]
for i, pos in enumerate(positions):
    ic = sch.components.add(
        "Device:C",  # Using capacitors as example
        f"C{i+1}",
        "100nF",
        position=pos
    )
    components.append((ic, pos))

# Route VCC to each component
for ic, pos in components:
    # Use HORIZONTAL_FIRST to connect to horizontal VCC rail
    result = create_orthogonal_routing(
        vcc_rail,
        Point(pos[0], pos[1] - 10.0),  # Above component
        corner_direction=CornerDirection.HORIZONTAL_FIRST
    )

    for start, end in result.segments:
        sch.wires.add(start=start, end=end)

sch.save("power_distribution.kicad_sch")
```

## Best Practices

### 1. Validate All Routing Results

Always validate routing results to catch errors early:

```python
from kicad_sch_api.geometry import create_orthogonal_routing, validate_routing_result

result = create_orthogonal_routing(from_pos, to_pos)
validate_routing_result(result)  # Raises ValueError if invalid
```

### 2. Use AUTO Direction for General Routing

Unless you have a specific reason, use `AUTO` direction:

```python
# Good - natural routing
result = create_orthogonal_routing(from_pos, to_pos)  # AUTO is default

# Only use specific directions when needed
result = create_orthogonal_routing(
    from_pos, to_pos,
    corner_direction=CornerDirection.HORIZONTAL_FIRST  # Specific requirement
)
```

### 3. Check for Direct Routing

Optimize by checking if routing is direct:

```python
result = create_orthogonal_routing(from_pos, to_pos)

if result.is_direct:
    print("Simple connection - single wire")
else:
    print(f"L-shaped connection with corner at {result.corner}")
```

### 4. Grid Alignment

Ensure all positions are grid-aligned (1.27mm = 50mil):

```python
from kicad_sch_api.core.geometry import snap_to_grid

# Snap positions to KiCAD grid before routing
from_pos = Point(*snap_to_grid((100.5, 100.3), grid_size=1.27))
to_pos = Point(*snap_to_grid((150.7, 125.2), grid_size=1.27))

result = create_orthogonal_routing(from_pos, to_pos)
```

### 5. Add Junction Markers

For L-shaped routing, mark the corner with a junction (future Phase 2 feature):

```python
result = create_orthogonal_routing(from_pos, to_pos)

# Add wires
for start, end in result.segments:
    sch.wires.add(start=start, end=end)

# Mark corner (Phase 2 - junction API)
if result.corner:
    # Future: sch.junctions.add(position=result.corner)
    pass
```

### 6. Use Type Hints

Leverage type hints for better code quality:

```python
from kicad_sch_api.core.types import Point
from kicad_sch_api.geometry import RoutingResult, create_orthogonal_routing

def route_component_pins(from_pin: Point, to_pin: Point) -> RoutingResult:
    """Route between two pin positions."""
    result = create_orthogonal_routing(from_pin, to_pin)
    validate_routing_result(result)
    return result
```

## Integration with MCP Server

The routing functionality is designed to integrate with MCP servers for AI-powered circuit design. Here's the planned integration (Phase 2):

### MCP Tool: connect_components()

```python
# Future MCP server tool
@server.call_tool()
async def connect_components(
    from_component: str,
    from_pin: str,
    to_component: str,
    to_pin: str,
    routing_style: str = "orthogonal",
    corner_direction: str = "auto"
) -> dict:
    """Connect component pins with automatic orthogonal routing."""

    # Get pin positions
    from_pos = get_pin_position(from_component, from_pin)
    to_pos = get_pin_position(to_component, to_pin)

    # Create routing
    direction = CornerDirection[corner_direction.upper()]
    result = create_orthogonal_routing(from_pos, to_pos, direction)

    # Add wires
    for start, end in result.segments:
        sch.wires.add(start=start, end=end)

    return {
        "success": True,
        "segments": len(result.segments),
        "corner": result.corner,
        "is_direct": result.is_direct
    }
```

### Example Usage with AI

```
User: "Connect R1 pin 2 to R2 pin 1 with a label VCC"

AI: connect_components("R1", "2", "R2", "1", corner_direction="auto")
```

## Troubleshooting

### Problem: Diagonal Wire Segments

**Symptom:** `ValueError: Segment is not orthogonal`

**Cause:** Routing result contains diagonal (non-orthogonal) segments.

**Solution:** This should never happen with `create_orthogonal_routing()`. If it does, it's a bug - please report it.

### Problem: Disconnected Segments

**Symptom:** `ValueError: Segments not connected`

**Cause:** Segments don't connect end-to-end.

**Solution:** Again, this is a bug if it happens. Validate your routing:

```python
result = create_orthogonal_routing(from_pos, to_pos)
validate_routing_result(result)  # Will raise ValueError with details
```

### Problem: Unexpected Corner Position

**Symptom:** Corner is not where you expect it.

**Cause:** Using wrong direction mode or misunderstanding Y-axis inversion.

**Solution:**
1. Check which direction mode you're using
2. Remember: lower Y = visually higher on screen
3. Try different direction modes:

```python
# Try all modes to see the difference
for mode in [CornerDirection.AUTO, CornerDirection.HORIZONTAL_FIRST, CornerDirection.VERTICAL_FIRST]:
    result = create_orthogonal_routing(from_pos, to_pos, corner_direction=mode)
    print(f"{mode}: corner at {result.corner}")
```

### Problem: Wire Doesn't Appear in KiCAD

**Symptom:** Wire segments added but not visible in KiCAD.

**Cause:** Position mismatch or grid misalignment.

**Solutions:**
1. Verify positions are in schematic coordinate space (mm)
2. Check Y-axis inversion (lower Y = higher on screen)
3. Ensure positions are grid-aligned (1.27mm increments)
4. Save and reload schematic to verify

```python
# Debug: Print wire positions
result = create_orthogonal_routing(from_pos, to_pos)
for i, (start, end) in enumerate(result.segments):
    print(f"Segment {i}: ({start.x:.2f}, {start.y:.2f}) → ({end.x:.2f}, {end.y:.2f})")
```

### Problem: Routing Through Obstacles

**Symptom:** Routed wire passes through other components.

**Cause:** Phase 1 has no collision detection.

**Solution:** This is expected behavior for Phase 1 (MVP). Collision detection is planned for Phase 2. Current workaround:
- Manually adjust component positions
- Use different direction modes to route around
- Wait for Phase 2 waypoint routing

## Further Reading

- [Getting Started Guide](GETTING_STARTED.md)
- [API Reference](API_REFERENCE.md)
- [MCP Server Integration](MCP_EXAMPLES.md)
- [GitHub Issue #109](https://github.com/circuit-synth/kicad-sch-api/issues/109)

## Contributing

Found a bug or have a feature request? Please open an issue on GitHub:
https://github.com/circuit-synth/kicad-sch-api/issues

---

*This feature was implemented in Phase 1 (MVP) - Issue #109*
