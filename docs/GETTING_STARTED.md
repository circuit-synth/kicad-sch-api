# Getting Started with kicad-sch-api

Welcome! This guide will help you understand and use kicad-sch-api in 15 minutes.

## What is kicad-sch-api?

**kicad-sch-api** is a Python library that lets you create, read, and modify KiCAD schematic files programmatically. Think of it as "code that writes circuit schematics" - instead of manually clicking and dragging in KiCAD's schematic editor, you write Python code to build circuits.

## Why Would You Use This?

### 1. **Automate Repetitive Circuit Design**
Have you ever needed to create 50 similar circuits with slight variations? Or generate test schematics for every combination of component values? This library makes that trivial:

```python
import kicad_sch_api as ksa

# Generate 10 RC filter circuits with different values
for i, (r_val, c_val) in enumerate([(1000, 100e-9), (2200, 47e-9), ...]):
    sch = ksa.create_schematic(f"RC_Filter_{i+1}")
    sch.components.add("Device:R", f"R{i+1}", f"{r_val}", (100, 100))
    sch.components.add("Device:C", f"C{i+1}", f"{c_val*1e9:.0f}nF", (150, 100))
    sch.save(f"filter_{i+1}.kicad_sch")
```

### 2. **Build Circuit Generation Tools**
Create tools that generate circuits from specifications:
- Convert truth tables to logic circuits
- Generate power distribution networks automatically
- Create test circuits from component datasheets

### 3. **AI-Powered Circuit Design**
Integrate with AI agents (like Claude) to design circuits through natural language. The library works perfectly with MCP (Model Context Protocol) for AI agent integration.

### 4. **Circuit Analysis & Validation**
Read existing schematics, analyze them, and generate reports:
```python
sch = ksa.load_schematic("existing_design.kicad_sch")

# Count components by type
resistors = sch.components.filter(lib_id="Device:R")
print(f"Found {len(resistors)} resistors")

# Find potential issues
for r in resistors:
    if "k" in r.value and float(r.value.replace("k", "")) > 100:
        print(f"Warning: {r.reference} has unusually high value")
```

## Installation

```bash
# From PyPI (recommended)
pip install kicad-sch-api

# From source (for development)
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api
uv pip install -e .
```

## Your First Circuit (5 Minutes)

Let's create a simple LED circuit with a resistor.

### Step 1: Create a New Schematic

```python
import kicad_sch_api as ksa

# Create a blank schematic
sch = ksa.create_schematic("LED Circuit")
```

That's it! You now have a valid KiCAD schematic in memory.

### Step 2: Add Components

```python
# Add an LED
led = sch.components.add(
    lib_id="Device:LED",          # KiCAD library and component
    reference="D1",               # Component reference (shown on schematic)
    value="RED",                  # Component value (shown on schematic)
    position=(100, 100),          # X, Y position in mm
    footprint="LED_SMD:LED_0805_2012Metric"  # PCB footprint
)

# Add a current-limiting resistor
resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="330",                  # 330 ohms
    position=(100, 80),           # Above the LED
    footprint="Resistor_SMD:R_0805_2012Metric"
)
```

### Step 3: Connect Components with Wires

```python
# Connect resistor pin 2 to LED pin 1 (anode)
sch.add_wire_between_pins("R1", "2", "D1", "1")

# Add power and ground connections
sch.add_wire_to_pin((80, 80), "R1", "1")  # VCC to resistor
sch.add_wire_to_pin((100, 110), "D1", "2")  # LED to ground

# Add labels to show what connects where
sch.add_label("VCC", position=(80, 80))
sch.add_label("GND", position=(100, 115))
```

### Step 4: Save Your Circuit

```python
sch.save("led_circuit.kicad_sch")
print("Circuit saved! Open it in KiCAD to see your work.")
```

### Open it in KiCAD!

Now open `led_circuit.kicad_sch` in KiCAD's schematic editor. You'll see:
- An LED (D1) with value "RED"
- A resistor (R1) with value "330"
- Wires connecting them properly
- Labels showing VCC and GND
- Perfect formatting that looks hand-drawn

**The library preserves KiCAD's exact format** - your generated schematic is indistinguishable from one created manually.

## Common Patterns

### Pattern 1: Parameterized Circuits

Create a reusable function to generate circuits:

```python
def create_voltage_divider(sch, name, r1_value, r2_value, position):
    """Create a voltage divider at the specified position."""
    x, y = position

    # Top resistor
    r1 = sch.components.add(
        "Device:R", f"R_{name}_1", f"{r1_value}", (x, y)
    )

    # Bottom resistor
    r2 = sch.components.add(
        "Device:R", f"R_{name}_2", f"{r2_value}", (x, y + 20)
    )

    # Connect them
    sch.add_wire_between_pins(f"R_{name}_1", "2", f"R_{name}_2", "1")

    # Add labels
    sch.add_label(f"V_{name}_IN", (x, y - 10))
    sch.add_label(f"V_{name}_OUT", (x, y + 10))
    sch.add_label("GND", (x, y + 30))

    return r1, r2

# Use it multiple times
sch = ksa.create_schematic("Multi-Divider")
create_voltage_divider(sch, "3V3", "10k", "5k", (100, 100))
create_voltage_divider(sch, "1V8", "22k", "10k", (150, 100))
sch.save("dividers.kicad_sch")
```

### Pattern 2: Reading and Analyzing Existing Schematics

```python
# Load an existing schematic
sch = ksa.load_schematic("existing_design.kicad_sch")

# Find all capacitors and check their values
caps = sch.components.filter(lib_id="Device:C")
for cap in caps:
    value = cap.value
    # Check if value is reasonable
    if "p" in value.lower():  # picofarad values
        print(f"Warning: {cap.reference} has very small value: {value}")

# Generate a bill of materials
bom = {}
for comp in sch.components:
    part_type = comp.lib_id.split(":")[-1]
    bom[part_type] = bom.get(part_type, 0) + 1

print("Bill of Materials:")
for part, count in sorted(bom.items()):
    print(f"  {part}: {count}")
```

### Pattern 3: Circuit Transformations

```python
# Load a schematic
sch = ksa.load_schematic("design_v1.kicad_sch")

# Update all resistor footprints to 0805 package
resistors = sch.components.filter(lib_id="Device:R")
for r in resistors:
    r.footprint = "Resistor_SMD:R_0805_2012Metric"

# Update all capacitors to have 10% tolerance property
caps = sch.components.filter(lib_id="Device:C")
for c in caps:
    c.set_property("Tolerance", "10%")

# Save as new version
sch.save("design_v2.kicad_sch")
```

### Pattern 4: Component Property Management

```python
# Add custom properties to components
resistor = sch.components.add("Device:R", "R1", "10k", (100, 100))

# Set manufacturer part number
resistor.set_property("MPN", "RC0603FR-0710KL")

# Set tolerance
resistor.set_property("Tolerance", "1%")

# Set power rating
resistor.set_property("Power", "0.1W")

# Read properties later
if resistor.has_property("MPN"):
    mpn = resistor.get_property("MPN")
    print(f"Order part number: {mpn}")
```

## Understanding Positions and Coordinates

KiCAD uses millimeter coordinates with origin at top-left:
- X increases to the right
- Y increases downward
- Grid is typically 2.54mm (0.1 inch)

```python
# Good practice: use KiCAD's grid (2.54mm increments)
sch.components.add("Device:R", "R1", "10k", (25.4, 50.8))  # 1" x, 2" y

# Components automatically snap to grid
r = sch.components.add("Device:R", "R2", "1k", (100.3, 100.7))
print(f"Actual position: {r.position}")  # Snapped to grid: (101.6, 101.6)
```

## Working with Pins

Components have numbered pins. To connect them, use pin numbers from the KiCAD library:

```python
# Resistor has pins "1" and "2"
# LED has pins "1" (anode) and "2" (cathode)
# Op-amp might have pins "1", "2", "3", "4", "5", "6", "7", "8"

# Connect R1 pin 2 to LED pin 1
sch.add_wire_between_pins("R1", "2", "LED1", "1")

# Get pin position if you need it
pin_pos = sch.get_component_pin_position("R1", "1")
if pin_pos:
    print(f"R1 pin 1 is at ({pin_pos.x}, {pin_pos.y})")
```

## Next Steps

Now that you understand the basics:

1. **Explore Examples**: Check out `examples/` directory for more complex circuits
2. **API Reference**: See `docs/API_REFERENCE.md` for all available methods
3. **Common Recipes**: See `docs/RECIPES.md` for solutions to common tasks
4. **Architecture**: See `docs/ARCHITECTURE.md` to understand how the library works

## Getting Help

- **GitHub Issues**: https://github.com/circuit-synth/kicad-sch-api/issues
- **Examples**: Check the `examples/` directory
- **API Docs**: See `docs/API_REFERENCE.md`

## Common Questions

### Q: Can I modify existing KiCAD schematics?
**A:** Yes! Load with `ksa.load_schematic()`, modify, and save.

### Q: Does this replace KiCAD?
**A:** No - it generates files that you open in KiCAD. It's for *programmatic* circuit creation, not interactive design.

### Q: What KiCAD versions are supported?
**A:** KiCAD 7 and 8 (latest stable versions). File format is backward compatible.

### Q: Can I use this with AI agents?
**A:** Yes! Use the [mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api) MCP server for AI integration.

### Q: Is the output guaranteed to be valid?
**A:** Yes - the library uses exact KiCAD format preservation and validates against real KiCAD libraries.

---

**Ready to build circuits with code? Start with the LED example above, then explore the examples directory!** 🚀
