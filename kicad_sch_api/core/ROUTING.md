# Wire Routing Implementations

This document describes the three routing implementations available in the core module and guidance on when to use each.

## Overview

The kicad-sch-api provides three wire routing modules:

1. **`wire_routing.py`** - Basic utilities and grid snapping
2. **`simple_manhattan.py`** - Simple L-shaped routing (fast)
3. **`manhattan_routing.py`** - A* pathfinding routing (complex)

## Module Descriptions

### wire_routing.py (~380 lines)
**Purpose**: Core routing utilities and grid snapping

**Key Functions**:
- `snap_to_grid()` - Snap coordinates to KiCAD grid (1.27mm standard)
- `normalize_segment()` - Normalize wire segments
- `merge_collinear_segments()` - Simplify wire paths
- `distance_to_segment()` - Point-to-line distance calculations

**Use When**: You need basic grid snapping or wire utilities

### simple_manhattan.py (~228 lines)
**Purpose**: Fast L-shaped wire routing for simple connections

**Algorithm**: Two-segment (horizontal-then-vertical or vertical-then-horizontal) routing

**Advantages**:
- ✅ Fast O(1) performance
- ✅ Simple, predictable paths
- ✅ No memory overhead
- ✅ Works for 90% of use cases

**Limitations**:
- ❌ Cannot route around obstacles
- ❌ Limited to L-shaped paths
- ❌ No pathfinding

**Use When**:
- Simple point-to-point connections
- No obstacles in the path
- Speed is priority
- Predictable routing is preferred

### manhattan_routing.py (~430 lines)
**Purpose**: Advanced A* pathfinding routing for complex scenarios

**Algorithm**: A* pathfinding on Manhattan grid with obstacle avoidance

**Advantages**:
- ✅ Routes around obstacles
- ✅ Finds optimal paths
- ✅ Handles complex scenarios
- ✅ Configurable clearance

**Limitations**:
- ❌ Slower O(n log n) performance
- ❌ More memory overhead
- ❌ Complexity may be overkill for simple cases

**Use When**:
- Must route around components
- Complex multi-segment paths needed
- Obstacle avoidance is required
- Path quality matters more than speed

## Recommendation: Routing Strategy

### Default Strategy
Use **`simple_manhattan.py`** as the default for most cases:

```python
from kicad_sch_api.core.simple_manhattan import route_manhattan_simple

# Simple L-shaped routing (recommended default)
path = route_manhattan_simple(start, end)
```

### Fallback to Advanced
Only use **`manhattan_routing.py`** when obstacles detected:

```python
from kicad_sch_api.core.manhattan_routing import route_manhattan_astar
from kicad_sch_api.core.component_bounds import check_path_collision

# Check if simple path would collide
if check_path_collision(start, end, component_bboxes):
    # Use advanced routing
    path = route_manhattan_astar(start, end, obstacles=component_bboxes)
else:
    # Use simple routing
    path = route_manhattan_simple(start, end)
```

## Performance Comparison

| Operation | simple_manhattan | manhattan_routing |
|-----------|------------------|-------------------|
| 10 simple wires | ~1ms | ~10ms |
| 10 wires w/ obstacles | Not supported | ~50ms |
| Memory usage | ~1KB | ~100KB |
| Code complexity | Simple | Complex |

## Future Consolidation

**Recommendation**: Create a unified routing API that:
1. Attempts simple routing first
2. Falls back to A* if collision detected
3. Provides single interface for users

**Example Future API**:
```python
# Unified routing API (future)
from kicad_sch_api.core.routing import route_wire

# Automatically selects best algorithm
path = route_wire(start, end, obstacles=component_bboxes, strategy='auto')
```

## Current Status

- ✅ Both implementations work correctly
- ✅ Both are tested and validated
- ⚠️ No unified API (users must choose)
- ⚠️ Documentation could be clearer about when to use each

## See Also

- `component_bounds.py` - Bounding box calculations for obstacle detection
- `pin_utils.py` - Pin position calculations for routing endpoints
- Wire manager (`managers/wire.py`) - High-level wire operations
