# KiCAD Schematic API - Examples Walkthrough

This walkthrough guides you from basic circuit generation to advanced parametric designs.

## Table of Contents

1. [Getting Started - Your First Component](#1-getting-started---your-first-component)
2. [Adding Wires and Connections](#2-adding-wires-and-connections)
3. [Working with Labels and Text](#3-working-with-labels-and-text)
4. [Grid Units for Cleaner Code](#4-grid-units-for-cleaner-code)
5. [Parametric Circuits](#5-parametric-circuits)
6. [Auto-Routing Between Pins](#6-auto-routing-between-pins)
7. [Complete Example - Voltage Divider](#7-complete-example---voltage-divider)

---

## 1. Getting Started - Your First Component

The simplest possible schematic - just one resistor:

```python
import kicad_sch_api as ksa

# Create a new schematic
sch = ksa.create_schematic("MyFirstCircuit")

# Add a resistor at position (100mm, 100mm)
sch.components.add(
    lib_id='Device:R',
    reference='R1',
    value='10k',
    position=(100.0, 100.0)
)

# Save the schematic
sch.save("first_circuit.kicad_sch")
```

**Key concepts:**
- `lib_id` - KiCAD library and component name (e.g., "Device:R")
- `reference` - Component designator (e.g., "R1", "C2", "U3")
- `value` - Component value (e.g., "10k", "100nF")
- `position` - Placement in millimeters (x, y)

---

## 2. Adding Wires and Connections

Let's connect two resistors - first manually, then with auto-routing:

**Manual wiring (you calculate pin positions):**

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("ManualWiring")

# Add two resistors
r1 = sch.components.add('Device:R', 'R1', '10k', position=(100.0, 100.0))
r2 = sch.components.add('Device:R', 'R2', '10k', position=(100.0, 120.0))

# Add a wire between them (manually calculate pin positions)
sch.add_wire(
    start=(100.0, 106.35),  # Bottom of R1
    end=(100.0, 113.65)     # Top of R2
)

sch.save("manual_wiring.kicad_sch")
```

**Auto-routing (library calculates pin positions for you):**

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("AutoWiring")

# Add two resistors
r1 = sch.components.add('Device:R', 'R1', '10k', position=(100.0, 100.0))
r2 = sch.components.add('Device:R', 'R2', '10k', position=(100.0, 120.0))

# Auto-route between pins - no position calculation needed!
sch.auto_route_pins('R1', '2', 'R2', '1', routing_strategy='direct')

sch.save("auto_wiring.kicad_sch")
```

**Key concepts:**
- `add_wire()` - Manual wiring, you specify exact start/end positions
- `auto_route_pins()` - Automatic wiring between component pins
- Auto-routing is easier and handles component rotations automatically
- Wire endpoints must align with component pins for proper electrical connection

> **⚠️ Important: KiCAD Y-Axis Convention**
> KiCAD uses an **inverted Y-axis** (like computer graphics):
> - **Higher Y values = lower on screen** (e.g., Y=120 is *below* Y=100)
> - **Lower Y values = higher on screen** (e.g., Y=100 is *above* Y=120)
>
> This is opposite from standard math/physics where +Y goes up!
> In our example above, R2 at Y=120.0 appears *below* R1 at Y=100.0.

---

## 3. Working with Labels and Text

Add labels to identify nets and text for documentation:

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("LabeledCircuit")

# Add components
sch.components.add('Device:R', 'R1', '10k', position=(100.0, 100.0))
sch.add_wire(start=(100.0, 106.35), end=(100.0, 115.0))

# Add a net label
sch.add_label('SIGNAL', position=(100.0, 115.0))

# Add annotation text
sch.add_text("Pull-up resistor", position=(110.0, 100.0), size=1.27)

sch.save("labeled_circuit.kicad_sch")
```

**Key concepts:**
- `add_label()` - Creates net labels for electrical connections
- `add_text()` - Adds documentation/annotations
- Labels connect nets with the same name across the schematic

---

## 4. Grid Units for Cleaner Code

KiCAD uses a 1.27mm (50 mil) grid. Enable grid units for easier positioning:

```python
import kicad_sch_api as ksa

# Enable grid units globally
ksa.use_grid_units(True)

sch = ksa.create_schematic("GridExample")

# Now positions are in grid units (1 unit = 1.27mm)
sch.components.add('Device:R', 'R1', '10k', position=(20, 20))  # 25.4mm, 25.4mm
sch.components.add('Device:R', 'R2', '10k', position=(20, 30))  # 25.4mm, 38.1mm

# Wires also use grid units
sch.add_wire(start=(20, 25), end=(20, 27))

sch.save("grid_example.kicad_sch")
```

**Key concepts:**
- `use_grid_units(True)` - Enable grid mode globally
- Positions in whole numbers align perfectly to KiCAD grid
- 1 grid unit = 1.27mm (50 mil)
- Much easier to reason about placement

---

## 5. Parametric Circuits

Create reusable circuit blocks that can be placed anywhere:

```python
import kicad_sch_api as ksa

ksa.use_grid_units(True)

def rc_filter(sch, x, y, r_value, c_value):
    """Reusable RC low-pass filter circuit"""

    # Position helper for this circuit block
    def p(dx, dy):
        return (x + dx, y + dy)

    # Build the circuit relative to (0, 0)
    sch.components.add('Device:R', 'R1', r_value, position=p(0, 0))
    sch.components.add('Device:C', 'C1', c_value, position=p(0, 7))
    sch.components.add('power:GND', '#PWR01', 'GND', position=p(0, 11))

    # Junction at output node
    sch.junctions.add(position=p(0, 4))

    # Wiring
    sch.auto_route_pins('R1', '2', 'C1', '1', routing_strategy='direct')
    sch.add_wire(start=p(0, 4), end=p(3, 4))  # Tap to label
    sch.add_wire(start=p(0, 10), end=p(0, 11))  # C1 to GND

    sch.add_label('OUT', position=p(3, 4))

# Create schematic and place the filter at different locations
sch = ksa.create_schematic("ParametricExample")

rc_filter(sch, x=20, y=20, r_value='1k', c_value='100nF')   # First filter
rc_filter(sch, x=50, y=20, r_value='10k', c_value='10nF')   # Second filter

sch.save("parametric_example.kicad_sch")
```

**Key concepts:**
- `p(dx, dy)` helper - Offsets positions relative to circuit origin
- Reusable circuit functions - Design once, place many times
- Each circuit block is self-contained and portable

---

## 6. Auto-Routing Between Pins

Let the library automatically route wires between component pins:

```python
import kicad_sch_api as ksa

ksa.use_grid_units(True)

sch = ksa.create_schematic("AutoRouteExample")

# Add components
sch.components.add('Device:R', 'R1', '10k', position=(20, 20))
sch.components.add('Device:R', 'R2', '10k', position=(20, 30))

# Auto-route between R1 pin 2 and R2 pin 1
sch.auto_route_pins('R1', '2', 'R2', '1', routing_strategy='direct')

sch.save("auto_route_example.kicad_sch")
```

**Key concepts:**
- `auto_route_pins()` - Automatically connects component pins
- No need to calculate pin positions manually
- Handles component rotations automatically
- `routing_strategy` options: "direct", "orthogonal", "manhattan"

---

## 7. Complete Example - Voltage Divider

A complete circuit showing all the techniques together:

```python
import kicad_sch_api as ksa

# Enable grid units globally for cleaner code
ksa.use_grid_units(True)

def voltage_divider(sch, x_grid, y_grid):
    """
    Create a parametric voltage divider circuit.

    Circuit: VCC -> R1 (10k) -> VOUT -> R2 (10k) -> GND
    Output: VOUT = VCC / 2
    """

    # Position helper for parametric placement
    def p(dx, dy):
        return (x_grid + dx, y_grid + dy)

    # Power symbols
    sch.components.add('power:VCC', '#PWR01', 'VCC', position=p(0, 0))
    sch.components.add('power:GND', '#PWR02', 'GND', position=p(0, 21))

    # Resistors
    sch.components.add('Device:R', 'R1', '10k', position=p(0, 5))
    sch.components.add('Device:R', 'R2', '10k', position=p(0, 15))

    # Junction at output node
    sch.junctions.add(position=p(0, 11))

    # Manual wiring for power
    sch.add_wire(start=p(0, 0), end=p(0, 2))       # VCC to R1
    sch.add_wire(start=p(0, 18), end=p(0, 21))     # R2 to GND

    # Auto-route between resistors
    sch.auto_route_pins('R1', '2', 'R2', '1', routing_strategy='direct')

    # Output tap
    sch.add_wire(start=p(0, 11), end=p(3, 11))
    sch.add_label('VOUT', position=p(3, 11))

    # Visual grouping
    sch.add_rectangle(start=p(-10, -10), end=p(10, 26))
    sch.add_text("Voltage Divider", position=p(-2, -8), size=1.27)

# Create schematic and place voltage divider at grid (20, 20)
sch = ksa.create_schematic("VoltageDiv")
voltage_divider(sch, 20, 20)
sch.save("voltage_divider.kicad_sch")
```

**See `voltage_divider.py` for the complete working example!**

---

## More Example Circuits

This folder contains polished example circuits:

- **`voltage_divider.py`** - Basic 10k/10k voltage divider (covered above)
- **`rc_filter.py`** - RC low-pass filter with horizontal resistor rotation
- **`power_supply.py`** - LM7805 5V regulator with input/output filtering

Each example demonstrates:
- Grid-based parametric design with `p()` helper
- Clean API using `ksa.use_grid_units(True)`
- Proper component placement and wiring
- Text annotations and decorative elements

---

## Next Steps

- **`../basics/`** - Simple single-component examples
- **`../parametric_circuits/`** - Reusable circuit blocks
- **`../advanced/`** - Hierarchical designs, multi-sheet projects
- **`../utilities/`** - Helper tools and analysis scripts

## Key API Reference

```python
# Schematic creation
sch = ksa.create_schematic("Name")
sch.save("output.kicad_sch")

# Configuration
ksa.use_grid_units(True)
ksa.config.positioning.grid_size = 1.27  # mm

# Components
sch.components.add(lib_id, reference, value, position, footprint=None)

# Wiring
sch.add_wire(start, end)
sch.auto_route_pins(comp1_ref, pin1, comp2_ref, pin2)

# Labels & Text
sch.add_label(text, position)
sch.add_text(text, position, size=1.27)

# Graphics
sch.add_rectangle(start, end)
sch.junctions.add(position)
```

Happy circuit building! 🔌⚡
