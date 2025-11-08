# Basic Examples

Essential getting-started examples for learning the kicad-sch-api.

## Overview

These examples demonstrate fundamental API usage:
- Creating schematics
- Adding components
- Setting properties
- Adding wires and labels
- Component rotation
- Pin-aligned placement

## Examples

### `example.py` - Complete Feature Demonstration ⭐

**Start here!** Comprehensive example showing all major features in one place.

**What it demonstrates:**
- **Components**: Microcontroller, voltage regulator, resistors, capacitors, LED, button, connector
- **Properties**: Power ratings, tolerances, voltage ratings, colors, part numbers
- **Wiring**: Simple wires and pin-to-pin connections
- **Labels**: Net labels (local) and hierarchical labels (inter-sheet)
- **Text annotations**: Adding documentation
- **Component search**: Filtering by lib_id, reference, value
- **Bulk operations**: Updating multiple components at once
- **Validation**: Checking for errors before saving
- **Save/Load**: Writing and reading schematic files

**Run it:**
```bash
cd examples
python basics/example.py
```

**Output:** `output/example.kicad_sch` (opens in KiCAD)

**Key code patterns:**

```python
import kicad_sch_api as ksa

# Create schematic
sch = ksa.create_schematic("Example Circuit")

# Add component with properties
resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(100, 100),
    footprint="Resistor_SMD:R_0603_1608Metric"
)
resistor.set_property("Power", "0.1W")
resistor.set_property("Tolerance", "1%")

# Add wires
sch.wires.add(start=(100, 110), end=(150, 110))

# Add labels
sch.add_label("VCC", position=(125, 110))

# Filter components
all_resistors = sch.components.filter(lib_id="Device:R")
print(f"Found {len(all_resistors)} resistors")

# Bulk update
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)

# Validate and save
errors = sch.validate()
if not errors:
    sch.save("output/example.kicad_sch")
```

---

### `component_rotation.py` - Component Rotation

Demonstrates component rotation at all standard angles: 0°, 90°, 180°, 270°.

**What it demonstrates:**
- Component rotation parameter
- How rotation affects pin positions
- Grid-aligned rotated placement
- Visual layout with different orientations

**Run it:**
```bash
python basics/component_rotation.py
```

**Output:** `output/component_rotation.kicad_sch`

**Key concept:**
```python
# Rotation affects pin positions!
r1 = sch.components.add("Device:R", "R1", "10k",
                        position=(100, 100), rotation=0)     # Vertical
r2 = sch.components.add("Device:R", "R2", "10k",
                        position=(120, 100), rotation=90)    # Horizontal
r3 = sch.components.add("Device:R", "R3", "10k",
                        position=(140, 100), rotation=180)   # Vertical (flipped)
r4 = sch.components.add("Device:R", "R4", "10k",
                        position=(160, 100), rotation=270)   # Horizontal (flipped)

# Query actual pin positions after rotation
pins_r2 = sch.list_component_pins("R2")
print(f"R2 pin 1 at: {pins_r2['1'].position}")  # Accounts for rotation!
```

**Important:** Always use `list_component_pins()` to get actual pin positions after rotation. Don't hardcode pin offsets.

---

### `pin_aligned_placement.py` - Pin-Aligned Placement

Shows how to place components aligned to specific pins for clean routing.

**What it demonstrates:**
- Pin position queries
- Component placement relative to pins
- Creating aligned circuit layouts
- Professional routing patterns

**Run it:**
```bash
python basics/pin_aligned_placement.py
```

**Output:** `output/pin_aligned.kicad_sch`

**Key technique:**
```python
# Add first component
r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

# Query its pin positions
r1_pins = sch.list_component_pins("R1")
r1_pin2_pos = r1_pins['2'].position  # Get actual pin 2 position

# Place second component aligned with first component's pin
# Align R2's pin 1 with R1's pin 2
r2_pin1_offset = 3.81  # Standard resistor pin offset (from component center)
aligned_x = r1_pin2_pos[0]
aligned_y = r1_pin2_pos[1] + 10.16  # 8 grids spacing

r2 = sch.components.add("Device:R", "R2", "10k",
                        position=(aligned_x, aligned_y))

# Now wire connects cleanly without jogs
sch.wires.add(start=r1_pin2_pos, end=(aligned_x, aligned_y - r2_pin1_offset))
```

**Benefits:**
- Clean vertical/horizontal wiring
- No unnecessary jogs or junctions
- Professional appearance
- Easier to read schematics

---

## Common Patterns

### Creating a Schematic
```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("My Circuit")
```

### Adding Components
```python
# Minimal
resistor = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

# With all options
resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(100, 100),
    rotation=0,
    footprint="Resistor_SMD:R_0603_1608Metric"
)

# Set additional properties
resistor.set_property("Power", "0.1W")
resistor.set_property("Tolerance", "1%")
resistor.set_property("MPN", "RC0603FR-0710KL")
```

### Adding Wires
```python
# Simple wire
sch.wires.add(start=(100, 100), end=(150, 100))

# Between component pins (uses pin queries internally)
sch.add_wire_between_pins("R1", "2", "R2", "1")

# Manual pin query + wire
pins = sch.list_component_pins("R1")
sch.wires.add(start=pins['2'].position, end=(150, 100))
```

### Adding Labels
```python
# Net label (local to sheet)
sch.add_label("VCC", position=(100, 95))

# Hierarchical label (connects between sheets)
sch.add_hierarchical_label("SPI_MOSI", position=(200, 100), shape="output")
```

### Finding Components
```python
# Get by reference
r1 = sch.components.get("R1")

# Filter by library ID
all_resistors = sch.components.filter(lib_id="Device:R")

# Filter by value
ten_k_resistors = sch.components.filter(value="10k")

# Multiple criteria
smd_resistors = sch.components.filter(
    lib_id="Device:R",
    footprint_pattern="*SMD*"
)
```

### Updating Components
```python
# Update single component
r1 = sch.components.get("R1")
r1.value = "4.7k"
r1.footprint = "Resistor_SMD:R_0805_2012Metric"

# Bulk update
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={
        'properties': {'Tolerance': '1%'},
        'footprint': 'Resistor_SMD:R_0603_1608Metric'
    }
)
```

### Validation and Saving
```python
# Validate before saving
errors = sch.validate()
if errors:
    for error in errors:
        print(f"Error: {error}")
else:
    sch.save("my_circuit.kicad_sch")
    print("Saved successfully!")
```

## Grid Alignment

**All positions must be grid-aligned** to KiCAD's 1.27mm (50 mil) grid:

```python
# Good positions (grid-aligned)
position=(100.33, 101.60)  # Exact multiples of 1.27mm
position=(127.00, 254.00)

# Bad positions (off-grid)
position=(100.5, 101.3)    # Will cause connectivity issues!
position=(127.1, 254.2)

# Use grid-based coordinates (from parametric examples)
GRID = 1.27
position=(10 * GRID, 20 * GRID)  # Always grid-aligned!
```

**Why it matters:**
- Ensures proper electrical connectivity
- Prevents floating-point errors
- Matches KiCAD's connection detection
- Professional appearance

## Next Steps

After mastering these basics:

1. **Parametric Circuits** - Learn to build reusable circuit blocks
   - See `parametric_circuits/grid_based/` for the recommended approach
   - Read `parametric_circuits/README.md` for comprehensive guide

2. **Advanced Examples** - Complex features
   - Hierarchical designs: `advanced/stm32g431_simple.py`
   - Wire routing: `advanced/routing/`

3. **API Reference**
   - Full documentation: `docs/API_REFERENCE.md`
   - LLM reference: `llm.txt`

## Tips

1. **Start simple** - Begin with `example.py` to understand the core API
2. **Use grid coordinates** - Always think in 1.27mm increments
3. **Query pin positions** - Don't hardcode pin offsets; use `list_component_pins()`
4. **Validate before saving** - Catch errors early with `sch.validate()`
5. **Open in KiCAD** - Visually verify your generated schematics
6. **Read the output** - Use `Read` tool to inspect generated `.kicad_sch` files

## Common Pitfalls

**Off-grid positioning:**
```python
# ❌ Bad - off grid
sch.components.add("Device:R", "R1", "10k", position=(100.5, 101.3))

# ✅ Good - grid aligned
sch.components.add("Device:R", "R1", "10k", position=(100.33, 101.60))
```

**Hardcoded pin offsets:**
```python
# ❌ Bad - assumes pin offset
r1_pos = (100, 100)
wire_start = (100, 103.81)  # Assumes 3.81mm pin offset

# ✅ Good - query actual pin position
r1_pins = sch.list_component_pins("R1")
wire_start = r1_pins['2'].position  # Works with any rotation!
```

**Missing validation:**
```python
# ❌ Bad - no validation
sch.save("circuit.kicad_sch")

# ✅ Good - validate first
errors = sch.validate()
if not errors:
    sch.save("circuit.kicad_sch")
```

## Getting Help

- Read [main README](../README.md)
- Check [API reference](../../docs/API_REFERENCE.md)
- Review [CLAUDE.md](../../CLAUDE.md) for development guidelines
- See [parametric circuits](../parametric_circuits/) for advanced patterns
