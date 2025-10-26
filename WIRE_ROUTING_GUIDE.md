# Wire Routing Algorithms Guide

## Overview

The kicad-sch-api provides two complementary wire routing algorithms for different use cases:

1. **Simple Manhattan** - Fast, simple L-shaped routing
2. **Manhattan A\* Routing** - Advanced pathfinding with obstacle avoidance

## Algorithm Comparison

| Feature | Simple Manhattan | A* Manhattan |
|---------|------------------|--------------|
| **Speed** | Very Fast (~1ms) | Moderate (10-100ms) |
| **Obstacle Avoidance** | ❌ No | ✅ Yes |
| **Path Optimization** | Basic | Advanced |
| **Memory Usage** | Minimal | Moderate |
| **Best For** | Quick routing, simple layouts | Complex designs, multiple obstacles |
| **Complexity** | Low | High |

## Algorithm Details

### 1. Simple Manhattan Routing

**Location**: `kicad_sch_api/core/simple_manhattan.py` (~150 lines)

**How It Works**:
```
Start Point → Horizontal to X → Vertical to Y → End Point
       ↓
Simple L-shaped path (or 3-segment with middle bend)
```

**Example Path**:
```
Start (100, 100)
  ├─ Move right to X=200
  │  └─ (100,100) → (200,100)
  └─ Move down to Y=150
     └─ (200,100) → (200,150)
```

**Use Cases**:
- Simple point-to-point connections
- Empty schematics with no component obstacles
- Quick wiring without optimization needs
- Educational purposes

**Pros**:
- ✅ Extremely fast
- ✅ Minimal memory usage
- ✅ Predictable results
- ✅ Easy to understand and debug

**Cons**:
- ❌ Cannot avoid components
- ❌ Will cross other wires
- ❌ No path optimization
- ❌ May create very long routes

### 2. Manhattan A* Routing

**Location**: `kicad_sch_api/core/manhattan_routing.py` (~430 lines)

**How It Works**:
```
Converts schematic to grid
  ↓
Marks obstacles (components, existing wires)
  ↓
Uses A* pathfinding on grid
  ↓
Returns shortest path avoiding obstacles
```

**Algorithm**:
- Grid-based pathfinding on Manhattan distance metric
- A* heuristic optimization for performance
- Obstacle detection from component bounding boxes
- Diagonal movement prevented (Manhattan constraint)

**Example Path with Obstacles**:
```
Grid with obstacles marked as X:

Start (S) → End (E) with component obstacles
S . . . .
. X X X .
. X E . .
. . . . .

Route: S → up → left → down → E
```

**Use Cases**:
- Complex schematics with many components
- Avoiding component placements
- Production schematics
- Designs with existing wires to route around

**Pros**:
- ✅ Avoids all obstacles
- ✅ Finds near-optimal paths
- ✅ Professional routing quality
- ✅ Suitable for complex designs

**Cons**:
- ❌ Slower (10-100ms per route)
- ❌ More memory usage
- ❌ Grid conversion overhead
- ❌ Complex codebase

## Usage Guide

### Simple Manhattan - Quick Routing

```python
import kicad_sch_api as ksa
from kicad_sch_api.core.simple_manhattan import simple_manhattan_route

sch = ksa.create_schematic("Simple Routing")

# Add two components
r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
r2 = sch.components.add("Device:C", "C1", "100nF", (200, 100))

# Simple L-shaped routing
from kicad_sch_api.core.types import Point
start = Point(110, 100)  # R1 pin
end = Point(200, 110)    # C1 pin

path = simple_manhattan_route(start, end)
# Returns: [Point(110, 100), Point(200, 100), Point(200, 110)]

# Draw wire along path
for i in range(len(path) - 1):
    sch.wires.add(start=path[i], end=path[i + 1])
```

### A* Manhattan - Smart Routing with Obstacles

```python
import kicad_sch_api as ksa
from kicad_sch_api.core.manhattan_routing import ManhattanRouter
from kicad_sch_api.core.component_bounds import get_component_bounding_box

sch = ksa.create_schematic("Smart Routing")

# Add components with obstacles
r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
obstacle = sch.components.add("Device:C", "C1", "100nF", (150, 100))
r2 = sch.components.add("Device:R", "R2", "20k", (200, 100))

# Setup router
router = ManhattanRouter()

# Get obstacle bounding boxes
obstacle_bbox = get_component_bounding_box(obstacle, include_properties=False)

# Route around obstacle
from kicad_sch_api.core.types import Point
start = Point(110, 100)
end = Point(190, 100)

path = router.route_between_points(
    start,
    end,
    [obstacle_bbox],  # Obstacles to avoid
    clearance=2.0     # 2mm clearance from obstacles
)
# Returns: [Point(110, 100), Point(110, 85), Point(200, 85), Point(200, 100), Point(190, 100)]
# Route goes around the obstacle!

# Draw wire along path
for i in range(len(path) - 1):
    sch.wires.add(start=path[i], end=path[i + 1])
```

## Configuration

### Wire Manager Default Routing

The `WireManager` class handles high-level wire operations. Currently defaults to simple routing.

```python
# In kicad_sch_api/core/managers/wire.py

class WireManager:
    def auto_route_wire(self, from_point, to_point, avoid_components=False):
        if avoid_components:
            # Use A* routing
            router = ManhattanRouter()
            obstacles = self._get_component_obstacles()
            path = router.route_between_points(from_point, to_point, obstacles)
        else:
            # Use simple routing
            path = simple_manhattan_route(from_point, to_point)

        return self._create_wire_segments(path)
```

### Tuning Parameters

**Simple Manhattan** - No parameters, fully deterministic

**A* Manhattan**:
```python
from kicad_sch_api.core.manhattan_routing import ManhattanRouter

router = ManhattanRouter(
    grid_size=1.27,      # Grid cell size (mm) - smaller = finer routing
    heuristic_weight=1.0 # A* heuristic weight (1.0 = optimal balance)
)

path = router.route_between_points(
    start,
    end,
    obstacles,
    clearance=2.0,       # Distance to keep from obstacles (mm)
)
```

## When to Use Each Algorithm

### Use Simple Manhattan When:
- ✓ Components are sparse or far apart
- ✓ Quick prototyping and testing
- ✓ Educational purposes
- ✓ Performance is critical
- ✓ Simple point-to-point connections

### Use A* Manhattan When:
- ✓ Many components in layout
- ✓ Need professional routing quality
- ✓ Avoiding component collisions is important
- ✓ Schematic is dense with connections
- ✓ Production-ready designs

## Advanced Usage

### Pin-to-Pin Routing

For automatic routing between component pins, see `core/schematic.py`:

```python
# Auto-route between pins with obstacle avoidance
wire_uuid = sch.add_wire_between_pins(
    "R1", "2",           # From R1 pin 2
    "C1", "1",           # To C1 pin 1
    routing_mode="manhattan"  # Use A* routing
)
```

### Custom Routing Strategy

Implement custom routing by extending `ManhattanRouter`:

```python
class CustomRouter(ManhattanRouter):
    def route_between_points(self, start, end, obstacles, clearance):
        # Custom routing logic
        # Could add diagonal routing, spiral patterns, etc.
        return custom_path
```

## Performance Benchmarks

### Typical Performance (on modern hardware)

```
Simple Manhattan:
  Empty schematic:     ~0.5ms per route
  10 components:       ~0.5ms per route

A* Manhattan:
  Empty schematic:     ~5ms per route
  10 components:       ~20ms per route
  50 components:       ~100ms per route
  100 components:      ~300ms per route
```

### Optimization Tips

1. **For Simple Routing**:
   - No optimization needed - already optimal

2. **For A* Routing**:
   - Increase grid_size for faster (less precise) routing
   - Reduce heuristic_weight for faster pathfinding (less optimal)
   - Pre-compute component obstacles once
   - Cache routing results for repeated paths

## Known Issues and Limitations

### Simple Manhattan
1. **No Obstacle Avoidance**: Routes through components
2. **Long Paths**: May create unnecessarily long routes
3. **No Optimization**: Doesn't minimize wire length

### A* Manhattan
1. **Grid Conversion**: Overhead for converting continuous coordinates to grid
2. **Diagonal Prevention**: Only horizontal/vertical movement (by design)
3. **Clearance Calculation**: May over-estimate obstacle size slightly
4. **Performance**: Slower for very complex designs

## Future Enhancements

1. **Hybrid Routing**: Use simple routing first, upgrade to A* only when needed
2. **Diagonal Routing**: Support 45° diagonal segments for more natural routing
3. **Multi-Layer Routing**: Support routing on multiple schematic "layers"
4. **Constraint-Based Routing**: Consider electrical constraints (impedance, length matching)
5. **Route Optimization**: Post-process routes to minimize length and bends
6. **Parallel Routing**: Route multiple wires simultaneously

## Related Files

- **Simple Algorithm**: `kicad_sch_api/core/simple_manhattan.py`
- **A* Algorithm**: `kicad_sch_api/core/manhattan_routing.py`
- **High-Level Interface**: `kicad_sch_api/core/managers/wire.py`
- **Types**: `kicad_sch_api/core/types.py` (Point, Rectangle)
- **Bounds Calculation**: `kicad_sch_api/core/component_bounds.py`

## See Also

- [TEST_COVERAGE_GAPS.md](TEST_COVERAGE_GAPS.md) - Wire routing test coverage
- [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) - Known routing limitations
- [README.md](README.md#advanced-features) - Usage examples

## Testing

Current test coverage:
- Simple Manhattan: ~14% (78 lines untested)
- A* Manhattan: ~91% (18 lines untested)

To improve coverage, add tests for:
- Performance benchmarks
- Edge cases (start=end, straight lines)
- Complex obstacle configurations
- Clearance validation
- Grid conversion accuracy
