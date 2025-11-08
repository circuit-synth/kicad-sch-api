# Grid-Based Circuit Conversion - Breakthrough!

## Why Grid-Based is Better

Using integer grid units instead of mm provides:
- **Intuitive positioning**: `pos(6, 10)` instead of `pos(7.62, 12.7)`
- **Easy adjustments**: Move 1 grid = just +/-1, not calculating 1.27mm multiples  
- **No floating point**: Clean integer math
- **Mental model**: Think in grid squares, not millimeters

## Grid System

- **1 grid unit = 1.27mm** (50 mil - KiCAD standard grid)
- **All positions**: Integer grid coordinates
- **Conversion helper**: `pos(x_grid, y_grid)` converts to mm automatically

## Conversion Status

✅ **Voltage Divider** - CONVERTED to grid-based
✅ **STM32 Microprocessor** - Already has grid version (create_stm32_parametric_grid.py)
⏳ **Power Supply (LM7805)** - TODO
⏳ **RC Filter** - TODO

## Pattern

```python
def create_circuit(sch, x_offset_grids: int, y_offset_grids: int, instance: int = 1):
    GRID = 1.27  # mm per grid
    
    def pos(x_grid, y_grid):
        """Convert grid position to mm"""
        return ((x_offset_grids + x_grid) * GRID, (y_offset_grids + y_grid) * GRID)
    
    # All positions in GRID UNITS (integers!)
    component_pos = pos(10, 15)  # Super clear!
    
    # Wiring, labels, rectangles all use pos() helper
```

## Demo Updates

Main demo now uses:
- Grid units for offsets: `START_X = 16` (grid units)
- Grid spacing: `CIRCUIT_GRID = 47` (grid units ≈60mm)
- Voltage divider: Fully grid-based
- Others: Still need conversion
