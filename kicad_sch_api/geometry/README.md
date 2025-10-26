# Geometry Module

Advanced geometric calculations for symbol bounding boxes and font metrics.

## Overview

This module provides specialized geometric utilities for accurate symbol bounding box calculation and text sizing. This is a small, focused module - most geometry and routing code is in `core/`.

## Module Files

### Symbol Bounding Box (`symbol_bbox.py`)
- **Lines**: ~800
- **Purpose**: Calculate accurate bounding boxes for symbol components
- **Key Functions**:
  - `calculate_symbol_bbox()` - Get accurate symbol bounds
  - `get_pin_bounds()` - Calculate pin extents
  - `merge_bounds()` - Combine multiple bounding boxes
- **Features**:
  - Accurate pin position calculation
  - Symbol transformation support
  - Text label bounds
  - Multi-unit symbol support

### Font Metrics (`font_metrics.py`)
- **Lines**: ~40
- **Purpose**: Font metrics for text sizing calculations
- **Key Constants**:
  - Font sizes for different text types
  - Character width calculations
  - Line height metrics
- **Used By**:
  - Label positioning
  - Text element sizing
  - Bounding box calculations for text

## Note: Most Geometry Code is in core/

The following geometry-related modules are in `core/`, not here:

| File | Location | Purpose |
|------|----------|---------|
| `geometry.py` | `core/` | Basic geometric primitives (Point, Segment, etc.) |
| `pin_utils.py` | `core/` | Pin parsing and position calculation |
| `component_bounds.py` | `core/` | Component bounding box calculation |
| `wire_routing.py` | `core/` | Wire routing utilities |
| `simple_manhattan.py` | `core/` | Simple L-shaped routing |
| `manhattan_routing.py` | `core/` | A* pathfinding routing |

## Symbol Bounding Box Calculation

The `symbol_bbox.py` module provides accurate bounding box calculation that accounts for:

1. **Symbol Body** - The main symbol rectangle
2. **Pin Extensions** - Pins extend beyond symbol bounds
3. **Text Labels** - Reference and value text
4. **Transformations** - Rotation and mirroring
5. **Multi-Unit Components** - ICs with multiple units

### Usage Example
```python
from kicad_sch_api.geometry import symbol_bbox

# Calculate symbol bounds
bounds = symbol_bbox.calculate_symbol_bbox(symbol_def, component_position)

# Result structure
{
    'x_min': 95.0,
    'x_max': 105.0,
    'y_min': 95.0,
    'y_max': 105.0,
    'width': 10.0,
    'height': 10.0
}
```

## Font Metrics

Font metrics are used for calculating text bounds:

```python
from kicad_sch_api.geometry import font_metrics

# Get character width
width = font_metrics.get_char_width(font_size=12)

# Get line height
height = font_metrics.get_line_height(font_size=12)
```

## Integration Points

### Used By
- `core/component_bounds.py` - Uses symbol_bbox for accurate bounds
- `core/labels.py` - Uses font_metrics for label sizing
- `core/texts.py` - Uses font_metrics for text sizing
- Format preservation - Ensures bounds match KiCAD's calculations

### Related Modules
- `core/geometry.py` - Basic geometric primitives
- `core/component_bounds.py` - Component-level bounds
- `core/pin_utils.py` - Pin position calculation

## Known Issues

1. **Font Metrics Approximation** - KiCAD uses TrueType fonts, we approximate
2. **Symbol Rotation** - Complex rotations may have edge cases
3. **Multi-Unit Symbols** - Unit positioning may not be exact

## Testing

Tests located in `../../tests/`:
- `test_symbol_bbox.py` - Bounding box calculation tests
- `test_font_metrics.py` - Font metric tests
- Integration tests with real KiCAD symbols

## Performance

- **Symbol bbox calculation**: ~100µs per component
- **Font metrics lookup**: ~1µs (constant time)
- **Cached results**: Yes, bounds are cached per component

## Future Improvements

- [ ] More accurate font metrics (actual TrueType parsing)
- [ ] Better rotation and transformation support
- [ ] Caching of complex symbol bounds
- [ ] Support for custom fonts

## References

- KiCAD symbol format: https://github.com/KiCad/kicad-symbols
- Font metrics: KiCAD source code
- Bounding box calculation: See implementation in `symbol_bbox.py`
