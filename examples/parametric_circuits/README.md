# Parametric Circuits

Reusable circuit patterns that can be placed anywhere on a schematic with configurable positioning.

## What are Parametric Circuits?

Parametric circuits are **Python functions** that generate circuit subsections with:
- **Position offsets**: Place the circuit anywhere on the schematic
- **Instance numbers**: Create multiple copies with unique component references
- **Configurable parameters**: Customize component values, labels, etc.

This is the **core pattern** for building complex schematics from modular building blocks.

## Directory Structure

```
parametric_circuits/
├── grid_based/           # ⭐ RECOMMENDED: Integer grid positioning
│   ├── demo_all_circuits.py
│   ├── create_stm32_parametric_grid.py
│   └── GRID_CONVERSION_NOTES.md
└── mm_based/            # Traditional millimeter positioning
    ├── test_circuit_1_voltage_divider.py
    ├── test_circuit_2_power_supply.py
    ├── test_circuit_3_rc_filter.py
    ├── test_circuit_5_stm32_microprocessor.py
    └── create_stm32_parametric.py
```

## Grid-Based vs MM-Based

### Grid-Based (RECOMMENDED) 🎯

**Benefits:**
- Clean integer coordinates: `pos(6, 10)` instead of `pos(7.62, 12.7)`
- Easy mental model: Think in grid squares
- Simple adjustments: Move 1 grid = just +/-1
- No floating point errors

**Grid System:**
- 1 grid unit = 1.27mm (50 mil - KiCAD standard)
- All positions are integers
- Automatic conversion to mm

**Example:**
```python
def create_voltage_divider(sch, x_offset_grids: int, y_offset_grids: int, instance: int = 1):
    GRID = 1.27

    def pos(x_grid, y_grid):
        return ((x_offset_grids + x_grid) * GRID, (y_offset_grids + y_grid) * GRID)

    # Clean integer positions!
    r1 = sch.components.add("Device:R", "R1", "10k", position=pos(6, 10))
    r2 = sch.components.add("Device:R", "R2", "10k", position=pos(6, 19))
```

### MM-Based (Traditional)

**When to use:**
- Converting existing designs with mm coordinates
- Precise positioning requirements
- Legacy compatibility

**Example:**
```python
def snap_to_grid(value, grid=1.27):
    return round(value / grid) * grid

def create_power_supply(sch, x_offset=0, y_offset=0, instance=1):
    ORIGIN_X = 45.72
    ORIGIN_Y = 31.75

    def pos(abs_x, abs_y):
        rel_x = abs_x - ORIGIN_X
        rel_y = abs_y - ORIGIN_Y
        return (snap_to_grid(x_offset + rel_x), snap_to_grid(y_offset + rel_y))

    # MM coordinates
    vreg = sch.components.add("Regulator_Linear:LM7805_TO220", "U1", "LM7805",
                              position=pos(91.44, 68.58))
```

## Parametric Circuit Pattern

All parametric circuits follow this standard pattern:

```python
import kicad_sch_api as ksa

def create_my_circuit(sch, x_offset_grids: int, y_offset_grids: int, instance: int = 1):
    """
    Create a reusable circuit block

    Args:
        sch: Schematic object to add components to
        x_offset_grids: X offset in grid units
        y_offset_grids: Y offset in grid units
        instance: Instance number for unique component references
    """
    GRID = 1.27  # mm per grid unit

    # Position helper
    def pos(x_grid, y_grid):
        """Convert grid position to mm with offset"""
        return ((x_offset_grids + x_grid) * GRID,
                (y_offset_grids + y_grid) * GRID)

    # Component references with instance number
    r1_ref = f'R{instance*10+1}'
    r2_ref = f'R{instance*10+2}'

    # Add components at grid positions
    r1 = sch.components.add("Device:R", r1_ref, "10k", position=pos(6, 10))
    r2 = sch.components.add("Device:R", r2_ref, "10k", position=pos(6, 19))

    # Add wiring using pin queries
    r1_pins = sch.list_component_pins(r1_ref)
    r2_pins = sch.list_component_pins(r2_ref)

    sch.wires.add(start=r1_pins['2'].position, end=r2_pins['1'].position)

    # Add labels
    sch.add_label("VCC", position=pos(6, 6))
    sch.add_label("GND", position=pos(6, 23))

    # Add graphical elements
    sch.add_rectangle(start=pos(0, 0), end=pos(24, 36))
    sch.add_text("MY CIRCUIT", position=pos(8, 2), size=2.0)

# Use it
sch = ksa.create_schematic("Demo")
create_my_circuit(sch, x_offset_grids=16, y_offset_grids=16, instance=1)
create_my_circuit(sch, x_offset_grids=63, y_offset_grids=16, instance=2)
sch.save("demo.kicad_sch")
```

## Key Concepts

### 1. Position Transformation

The `pos()` helper converts local circuit coordinates to global schematic coordinates:

```python
def pos(x_grid, y_grid):
    """
    Local grid coords (0, 0) to (24, 36)
    → Global schematic coords with offset
    """
    return ((x_offset_grids + x_grid) * GRID,
            (y_offset_grids + y_grid) * GRID)
```

This allows you to design circuits in a local coordinate system (starting at 0, 0) and place them anywhere on the schematic.

### 2. Instance-Based References

Use instance numbers to create unique component references:

```python
# Instance 1: R11, R12, C11, C12
r1_ref = f'R{instance*10+1}'  # instance=1 → R11
r2_ref = f'R{instance*10+2}'  # instance=1 → R12

# Instance 2: R21, R22, C21, C22
r1_ref = f'R{instance*10+1}'  # instance=2 → R21
r2_ref = f'R{instance*10+2}'  # instance=2 → R22
```

This prevents reference conflicts when placing multiple instances.

### 3. Pin Position Queries

Use `list_component_pins()` to get actual pin positions for wiring:

```python
# Add components
r1 = sch.components.add("Device:R", "R1", "10k", position=pos(6, 10))

# Query pin positions (accounts for rotation!)
pins = sch.list_component_pins("R1")
pin1_pos = pins['1'].position  # Actual position in mm
pin2_pos = pins['2'].position

# Add wire between pins
sch.wires.add(start=pin2_pos, end=some_other_position)
```

This ensures wires connect to the correct pin positions regardless of component rotation.

### 4. Grid Alignment

All positions MUST be grid-aligned (1.27mm increments):

```python
# Good - on grid
pos(6, 10)   # → (6*1.27, 10*1.27) = (7.62, 12.7) ✓

# Bad - off grid
(7.5, 12.8)  # Not aligned to 1.27mm grid ✗
```

Grid alignment ensures:
- Proper electrical connectivity
- Professional appearance
- No floating-point errors
- Matches KiCAD's internal connection detection

## Available Circuits

### Grid-Based Circuits

#### `demo_all_circuits.py` - Complete Demo
Combined demo showing:
- Voltage divider (grid-based)
- Power supply (LM7805) (converted to grid)
- RC filter (converted to grid)
- STM32 microprocessor (grid-based)

**Run it:**
```bash
python parametric_circuits/grid_based/demo_all_circuits.py
```

#### `create_stm32_parametric_grid.py` - STM32 Microprocessor
Complete STM32G030K8Tx circuit with:
- Microcontroller
- Decoupling capacitors
- Reset resistor
- LED indicator
- Debug connector
- Power symbols

### MM-Based Circuits

#### `test_circuit_1_voltage_divider.py`
Simple voltage divider with two resistors and labels.

#### `test_circuit_2_power_supply.py`
LM7805 5V regulator with input/output capacitors.

#### `test_circuit_3_rc_filter.py`
RC low-pass filter circuit.

#### `test_circuit_5_stm32_microprocessor.py`
STM32G030K8Tx microprocessor (same as grid version, in mm).

## Conversion Guide

Converting from MM-based to grid-based:

### 1. Change function signature
```python
# Before (mm-based)
def create_circuit(sch, x_offset=0, y_offset=0, instance=1):

# After (grid-based)
def create_circuit(sch, x_offset_grids: int, y_offset_grids: int, instance: int = 1):
```

### 2. Update pos() helper
```python
# Before (mm-based)
ORIGIN_X = 45.72
ORIGIN_Y = 31.75

def pos(abs_x, abs_y):
    rel_x = abs_x - ORIGIN_X
    rel_y = abs_y - ORIGIN_Y
    return (snap_to_grid(x_offset + rel_x), snap_to_grid(y_offset + rel_y))

# After (grid-based)
GRID = 1.27

def pos(x_grid, y_grid):
    return ((x_offset_grids + x_grid) * GRID, (y_offset_grids + y_grid) * GRID)
```

### 3. Convert coordinates to grid units
```python
# Before (mm-based)
r1 = sch.components.add("Device:R", "R1", "10k", position=pos(91.44, 68.58))

# Calculate grid coordinates: 91.44mm ÷ 1.27 = 72 grids
# After (grid-based)
r1 = sch.components.add("Device:R", "R1", "10k", position=pos(72, 54))
```

See `grid_based/GRID_CONVERSION_NOTES.md` for detailed conversion guide.

## Best Practices

1. **Start with grid-based** for new circuits
2. **Use integer grid positions** for all components
3. **Query pin positions** for wiring (don't hardcode)
4. **Use instance numbers** for unique references
5. **Add graphical boundaries** (rectangles + text) for visual organization
6. **Test placement** at multiple positions to verify offset logic
7. **Document** the circuit's origin point and size

## Quick Reference

```python
# Grid-based parametric circuit template
import kicad_sch_api as ksa

def create_my_circuit(sch, x_offset_grids: int, y_offset_grids: int, instance: int = 1):
    GRID = 1.27

    def pos(x_grid, y_grid):
        return ((x_offset_grids + x_grid) * GRID, (y_offset_grids + y_grid) * GRID)

    # Components with instance-based references
    comp_ref = f'R{instance*10+1}'
    comp = sch.components.add("Device:R", comp_ref, "10k", position=pos(6, 10))

    # Labels
    sch.add_label("LABEL", position=pos(10, 10))

    # Wiring with pin queries
    pins = sch.list_component_pins(comp_ref)
    sch.wires.add(start=pins['2'].position, end=pos(6, 15))

    # Graphics
    sch.add_rectangle(start=pos(0, 0), end=pos(24, 36))
    sch.add_text("CIRCUIT NAME", position=pos(8, 2), size=2.0)
```

## See Also

- [Main Examples README](../README.md) - Complete examples documentation
- [GRID_CONVERSION_NOTES.md](grid_based/GRID_CONVERSION_NOTES.md) - Detailed grid positioning guide
- [CLAUDE.md](../../CLAUDE.md) - Grid alignment requirements
