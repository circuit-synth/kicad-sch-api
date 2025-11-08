# kicad-sch-api Examples

Comprehensive examples demonstrating KiCAD schematic generation using Python.

## Directory Structure

```
examples/
├── parametric_circuits/     # Reusable circuit patterns
│   ├── grid_based/         # ⭐ NEW: Integer grid positioning (RECOMMENDED)
│   └── mm_based/           # Traditional millimeter positioning
├── basics/                 # Getting started examples
├── advanced/               # Complex features
│   └── routing/           # Wire routing demonstrations
└── utilities/             # Helper tools and logging
```

## Quick Start

```bash
# Grid-based parametric demo (RECOMMENDED approach)
python parametric_circuits/grid_based/demo_all_circuits.py

# Basic getting started
python basics/example.py

# Advanced hierarchical design
python advanced/stm32g431_simple.py
```

---

## Parametric Circuits - The Core Pattern ⭐

Parametric circuits are **reusable circuit functions** that can be placed anywhere on a schematic. This is the **recommended approach** for building complex schematics from modular building blocks.

### Grid-Based Positioning (NEW - RECOMMENDED) 🎯

**Location:** `parametric_circuits/grid_based/`

The grid-based approach uses **integer grid units** instead of millimeters, making positioning intuitive and adjustments easy.

**Key Benefits:**
- Clean integer coordinates: `pos(6, 10)` instead of `pos(7.62, 12.7)`
- Easy adjustments: Move 1 grid = just +/-1 (not calculating 1.27mm multiples)
- No floating point errors
- Mental model: Think in grid squares, not millimeters

**Grid System:**
- 1 grid unit = 1.27mm (50 mil - KiCAD standard grid)
- All positions use integer grid coordinates
- Automatic conversion to mm coordinates

#### Example: Grid-Based Voltage Divider

```python
import kicad_sch_api as ksa

def create_voltage_divider(sch, x_offset_grids: int, y_offset_grids: int, instance: int = 1):
    """Create voltage divider using GRID-BASED positioning"""
    GRID = 1.27  # mm per grid unit

    def pos(x_grid, y_grid):
        """Convert grid position to mm"""
        return ((x_offset_grids + x_grid) * GRID, (y_offset_grids + y_grid) * GRID)

    # Component references
    r1_ref = f'R{instance*10+1}'
    r2_ref = f'R{instance*10+2}'

    # Add components at GRID positions (clean integers!)
    r1 = sch.components.add("Device:R", r1_ref, "10k", position=pos(6, 10))
    r2 = sch.components.add("Device:R", r2_ref, "10k", position=pos(6, 19))

    # Add labels at grid positions
    sch.add_label("VCC", position=pos(6, 6))
    sch.add_label("VOUT", position=pos(10, 15))
    sch.add_label("GND", position=pos(6, 23))

    # Rectangle boundary in grid units
    sch.add_rectangle(start=pos(0, 0), end=pos(24, 36))
    sch.add_text("VOLTAGE DIVIDER", position=pos(11, 2), size=2.0)

# Use it - positions in GRID UNITS
sch = ksa.create_schematic("Demo")
create_voltage_divider(sch, x_offset_grids=16, y_offset_grids=16, instance=1)
sch.save("voltage_divider_grid.kicad_sch")
```

**Files in grid_based/:**
- `demo_all_circuits.py` - Complete demo with multiple grid-based circuits
- `create_stm32_parametric_grid.py` - STM32 microcontroller circuit (grid-based)
- `GRID_CONVERSION_NOTES.md` - Detailed grid positioning guide

### MM-Based Positioning (Traditional)

**Location:** `parametric_circuits/mm_based/`

Traditional approach using millimeter coordinates with snap-to-grid helper.

**When to use:**
- Converting existing designs with mm coordinates
- Precise positioning requirements
- Legacy compatibility

#### Example: MM-Based Power Supply

```python
import kicad_sch_api as ksa

def snap_to_grid(value, grid=1.27):
    """Snap value to KiCAD grid (1.27mm)"""
    return round(value / grid) * grid

def create_power_supply(sch, x_offset=0, y_offset=0, instance=1):
    """Create LM7805 power supply using MM positioning"""
    ORIGIN_X = 45.72
    ORIGIN_Y = 31.75

    def pos(abs_x, abs_y):
        """Convert absolute mm position to offset position"""
        rel_x = abs_x - ORIGIN_X
        rel_y = abs_y - ORIGIN_Y
        return (snap_to_grid(x_offset + rel_x), snap_to_grid(y_offset + rel_y))

    # Component references
    u_ref = f'U{instance}'

    # Add components at MM positions
    vreg = sch.components.add(
        'Regulator_Linear:LM7805_TO220',
        u_ref, 'LM7805',
        position=pos(91.44, 68.58)
    )

    # ... rest of circuit
```

**Files in mm_based/:**
- `test_circuit_1_voltage_divider.py` - Voltage divider (mm)
- `test_circuit_2_power_supply.py` - LM7805 power supply (mm)
- `test_circuit_3_rc_filter.py` - RC filter (mm)
- `test_circuit_5_stm32_microprocessor.py` - STM32 circuit (mm)
- `create_stm32_parametric.py` - Standalone STM32 test (mm)

### Which Approach to Use?

| Approach | Use When | Benefits |
|----------|----------|----------|
| **Grid-based** | New designs, learning, prototyping | Intuitive, easy adjustments, clean integers |
| **MM-based** | Converting existing designs, precise control | Exact positioning, legacy compatibility |

**Recommendation:** Start with grid-based for new designs. It's easier to understand and work with.

---

## Basic Examples

**Location:** `basics/`

Essential getting-started examples for learning the API.

### `example.py` - Complete Feature Demonstration

Comprehensive example showing all major features:
- Components (resistors, capacitors, ICs, connectors, LED, button)
- Properties (power ratings, tolerances, voltage ratings, colors)
- Wiring (simple wires and pin-to-pin connections)
- Labels (net labels and hierarchical labels)
- Text annotations
- Component search and filtering
- Bulk operations
- Validation
- Save/load

**Run it:**
```bash
python basics/example.py
```

**Output:** `output/example.kicad_sch`

### `component_rotation.py` - Component Rotation

Demonstrates component rotation at 0°, 90°, 180°, 270° with proper pin alignment.

### `pin_aligned_placement.py` - Pin-Aligned Placement

Shows how to place components aligned to specific pins for clean routing.

---

## Advanced Examples

**Location:** `advanced/`

Complex features and professional design patterns.

### `stm32g431_simple.py` - Simple STM32 Development Board ⭐

**Perfect for learning hierarchical design!**

Beginner-friendly hierarchical design with STM32G431RBT6 (64-pin LQFP).

**Features:**
- STM32G431RBT6 (64-pin LQFP - easier to solder)
- AMS1117-3.3 voltage regulator
- USB-C power
- Reset button + LED
- SWD programming header
- Only ~14 components

**Sheet structure (5 sheets):**
- main.kicad_sch - Top-level
- power.kicad_sch - Voltage regulator
- mcu.kicad_sch - STM32G431RBT6
- usb.kicad_sch - USB-C power
- ui.kicad_sch - Button + LED + SWD

**Run it:**
```bash
python advanced/stm32g431_simple.py
```

**Output:** `stm32g431_simple/` with 5 schematic files

### `hierarchy_example.py` - Hierarchical Design Patterns

Demonstrates hierarchical sheet organization, sheet pins, and inter-sheet connections.

### Routing Demonstrations

**Location:** `advanced/routing/`

Wire routing examples showing different routing strategies.

**Files:**
- `create_routing_demo.py` - Basic wire routing patterns
- `orthogonal_routing_demo.py` - Manhattan-style routing

---

## Utilities

**Location:** `utilities/`

Helper tools and documentation.

### `kicad_cli_exports.py` - KiCAD CLI Integration

Integration with KiCAD command-line tools:
- Netlist export
- Bill of Materials (BOM)
- Electrical Rules Check (ERC)
- PDF/SVG/DXF export

**Requirements:** KiCAD CLI installed or Docker available.

### `logging_framework_guide.py` - Logging Framework

Comprehensive guide to the library's logging system with examples.

### Documentation Files

- `LOGGING_QUICK_REFERENCE.md` - Quick logging reference
- `example_logging_sample_output.md` - Sample logging output

---

## Recommended Learning Path

### New Users - Start Here:

1. **Basic API** - `basics/example.py`
   - Learn component creation, wiring, labels
   - Understand the core API

2. **Grid-Based Parametric** - `parametric_circuits/grid_based/demo_all_circuits.py`
   - Learn the recommended positioning approach
   - Understand parametric circuit patterns
   - See how to build modular circuits

3. **Hierarchical Design** - `advanced/stm32g431_simple.py`
   - Learn multi-sheet organization
   - Understand sheet pins and connections
   - See professional design patterns

### Parametric Circuit Development:

1. **Grid-Based Approach** (RECOMMENDED):
   - Start with `parametric_circuits/grid_based/demo_all_circuits.py`
   - Read `parametric_circuits/grid_based/GRID_CONVERSION_NOTES.md`
   - Study the voltage divider example

2. **MM-Based Approach** (if needed):
   - Review `parametric_circuits/mm_based/test_circuit_2_power_supply.py`
   - Understand the `pos()` helper pattern
   - Use `snap_to_grid()` for alignment

### Advanced Topics:

1. **Routing** - `advanced/routing/`
2. **Hierarchical Design** - `advanced/hierarchy_example.py`
3. **Logging** - `utilities/logging_framework_guide.py`

---

## Common Patterns

### Create Schematic
```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("My Circuit")
```

### Add Component (Grid-Based)
```python
GRID = 1.27

def pos(x_grid, y_grid):
    return (x_grid * GRID, y_grid * GRID)

resistor = sch.components.add(
    "Device:R", "R1", "10k",
    position=pos(10, 10),  # Grid coordinates
    footprint="Resistor_SMD:R_0603_1608Metric"
)
```

### Add Wire
```python
# Simple wire (grid-based)
sch.wires.add(start=pos(10, 12), end=pos(15, 12))

# Pin-to-pin connection
sch.add_wire_between_pins("R1", "2", "R2", "1")
```

### Filter Components
```python
# Find all resistors
resistors = sch.components.filter(lib_id="Device:R")

# Get specific component
r1 = sch.components.get("R1")
```

### Save
```python
sch.save("my_circuit.kicad_sch")
```

---

## Next Steps

- Read the [API documentation](../docs/API_REFERENCE.md)
- Check the [llm.txt](../llm.txt) for comprehensive API reference
- See [main README](../README.md) for installation and setup
- Review [CLAUDE.md](../CLAUDE.md) for development guidelines

## MCP Server

For AI integration with Claude and other LLMs, see the separate [mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api) repository.
