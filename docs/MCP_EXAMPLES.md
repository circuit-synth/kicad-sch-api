# MCP Server Usage Examples

This guide provides examples of using the kicad-sch-api MCP server for programmatic circuit generation.

## Table of Contents
- [Setup](#setup)
- [Basic Component Operations](#basic-component-operations)
- [Building Complete Circuits](#building-complete-circuits)
- [Advanced Examples](#advanced-examples)
- [Common Patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Setup

### Prerequisites
```bash
# Install kicad-sch-api
cd /path/to/kicad-sch-api
uv pip install -e .

# Verify MCP server works
uv run kicad-sch-mcp
# Press Ctrl+C to stop
```

### Claude Code Integration
The `.mcp.json` file in the project root automatically loads the MCP server:
```json
{
  "mcpServers": {
    "kicad-sch-api": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "kicad-sch-mcp"]
    }
  }
}
```

Start Claude Code normally (NOT with `--dangerously-skip-permissions`):
```bash
cd /path/to/kicad-sch-api
claude
```

Approve the MCP server when prompted, then verify:
```
"What MCP tools do you have available?"
```

You should see 15 tools across 4 categories.

## Basic Component Operations

### Example 1: Create Schematic and Add Component

**Request**:
```
Create a new schematic called "BasicTest" and add a 10k resistor at position (100, 100)
```

**MCP Tools Called**:
1. `create_schematic(name="BasicTest")`
2. `add_component(lib_id="Device:R", value="10k", reference="R1", position=(100.0, 100.0))`

**Result**:
- New schematic created
- Resistor R1 added at specified position
- Component has auto-generated UUID
- Ready to add more components or save

### Example 2: List and Filter Components

**Request**:
```
Show me all components in the schematic, then find all resistors
```

**MCP Tools Called**:
1. `list_components()` - Returns all components with metadata
2. `filter_components(lib_id="Device:R")` - Returns only resistors

**Output includes**:
- Reference (R1, R2, etc.)
- Value (10k, 100k, etc.)
- Position (x, y coordinates)
- Rotation (0, 90, 180, 270)
- Library ID (Device:R)
- Footprint (if specified)

### Example 3: Update Component Properties

**Request**:
```
Change R1's value to 20k, rotate it 90 degrees, and set footprint to R_0603_1608Metric
```

**MCP Tools Called**:
```
update_component(
    reference="R1",
    value="20k",
    rotation=90.0,
    footprint="Resistor_SMD:R_0603_1608Metric"
)
```

**Result**:
- R1 value updated: 10k → 20k
- R1 rotation updated: 0° → 90°
- R1 footprint assigned
- Component ready for PCB layout

### Example 4: Remove Component

**Request**:
```
Remove resistor R1 from the schematic
```

**MCP Tools Called**:
```
remove_component(reference="R1")
```

**Result**:
- R1 removed from schematic
- UUID freed for reuse
- Schematic modified flag set

## Building Complete Circuits

### Example 5: Voltage Divider (Verified ✅)

**Request**:
```
Create a voltage divider with R1=10k and R2=20k, fully connected with VCC and GND labels
```

**Complete MCP Tool Sequence**:
```python
# 1. Create schematic
create_schematic(name="Voltage Divider")

# 2. Add components
add_component(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(127.0, 76.2),
    rotation=0
)

add_component(
    lib_id="Device:R",
    reference="R2",
    value="20k",
    position=(127.0, 95.25),
    rotation=0
)

# 3. Get pin positions
get_component_pins("R1")
# Returns:
# {
#   "pin_count": 2,
#   "pins": [
#     {"number": "1", "position": {"x": 127.0, "y": 72.39}, "type": "passive"},
#     {"number": "2", "position": {"x": 127.0, "y": 80.01}, "type": "passive"}
#   ]
# }

get_component_pins("R2")
# Returns:
# {
#   "pin_count": 2,
#   "pins": [
#     {"number": "1", "position": {"x": 127.0, "y": 91.44}, "type": "passive"},
#     {"number": "2", "position": {"x": 127.0, "y": 99.06}, "type": "passive"}
#   ]
# }

# 4. Add wires
add_wire(start=(127.0, 72.39), end=(127.0, 66.04))   # VCC to R1 pin 1
add_wire(start=(127.0, 80.01), end=(127.0, 91.44))   # R1 pin 2 to R2 pin 1
add_wire(start=(127.0, 99.06), end=(127.0, 105.41))  # R2 pin 2 to GND

# 5. Add labels (offset from wire for visibility)
add_label(text="VCC", position=(129.54, 66.04), rotation=0.0)
add_label(text="VOUT", position=(129.54, 85.725), rotation=0.0)
add_label(text="GND", position=(129.54, 105.41), rotation=0.0)

# 6. Add junction at voltage divider tap point
add_junction(position=(127.0, 85.725), diameter=0.0)

# 7. Save schematic
save_schematic(file_path="voltage_divider.kicad_sch")
```

**Circuit Details**:
- **Input**: VCC at top
- **Output**: VOUT = VCC × (R2 / (R1 + R2)) = VCC × (20k / 30k) = 0.667 × VCC
- **Ground**: GND at bottom
- **Junction**: At R1-R2 connection point (VOUT tap)

**Result**: ✅ **VERIFIED WORKING** - Opens perfectly in KiCAD with proper connectivity!

### Example 6: LED Circuit with Current Limiting Resistor

**Request**:
```
Create an LED circuit with a 220Ω current limiting resistor, wired to VCC and GND
```

**Complete MCP Tool Sequence**:
```python
# 1. Create schematic
create_schematic(name="LED Circuit")

# 2. Add LED
add_component(
    lib_id="Device:LED",
    reference="D1",
    value="LED",
    position=(127.0, 88.9),
    rotation=0
)

# 3. Add current limiting resistor
add_component(
    lib_id="Device:R",
    reference="R1",
    value="220",
    position=(127.0, 69.85),
    rotation=0
)

# 4. Get pin positions
r1_pins = get_component_pins("R1")
# Pin 1 at (127.0, 66.04), Pin 2 at (127.0, 73.66)

d1_pins = get_component_pins("D1")
# Anode (pin 1) at (127.0, 85.09), Cathode (pin 2) at (127.0, 92.71)

# 5. Wire VCC → R1 → LED → GND
add_wire(start=(127.0, 66.04), end=(127.0, 59.69))   # VCC to R1
add_wire(start=(127.0, 73.66), end=(127.0, 85.09))   # R1 to LED anode
add_wire(start=(127.0, 92.71), end=(127.0, 99.06))   # LED cathode to GND

# 6. Add labels
add_label(text="VCC", position=(129.54, 59.69), rotation=0.0)
add_label(text="GND", position=(129.54, 99.06), rotation=0.0)

# 7. Save
save_schematic(file_path="led_circuit.kicad_sch")
```

**Circuit Details**:
- **Current Limiting**: I = (VCC - V_LED) / R1 = (5V - 2V) / 220Ω ≈ 13.6mA (safe for standard LED)
- **Polarity**: Anode to VCC (through resistor), cathode to GND
- **Components**: Standard red/green LED, 1/4W resistor

**Result**: Complete LED driver circuit ready for use!

### Example 7: RC Low-Pass Filter

**Request**:
```
Create an RC low-pass filter with R=10k, C=100nF for audio applications
```

**Complete MCP Tool Sequence**:
```python
# 1. Create schematic
create_schematic(name="RC Low-Pass Filter")

# 2. Add resistor
add_component(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(101.6, 88.9),
    rotation=90  # Horizontal orientation
)

# 3. Add capacitor
add_component(
    lib_id="Device:C",
    reference="C1",
    value="100nF",
    position=(127.0, 95.25),
    rotation=0  # Vertical orientation
)

# 4. Get pin positions
r1_pins = get_component_pins("R1")
# Pin 1 (left) at (97.79, 88.9), Pin 2 (right) at (105.41, 88.9)

c1_pins = get_component_pins("C1")
# Pin 1 (top) at (127.0, 91.44), Pin 2 (bottom) at (127.0, 99.06)

# 5. Wire input → R1 → C1 → output
add_wire(start=(97.79, 88.9), end=(88.9, 88.9))      # Input to R1
add_wire(start=(105.41, 88.9), end=(127.0, 88.9))    # R1 to horizontal bus
add_wire(start=(127.0, 88.9), end=(127.0, 91.44))    # Bus to C1 top
add_wire(start=(127.0, 88.9), end=(135.89, 88.9))    # Bus to output
add_wire(start=(127.0, 99.06), end=(127.0, 105.41))  # C1 bottom to GND

# 6. Add labels
add_label(text="INPUT", position=(86.36, 88.9), rotation=0.0)
add_label(text="OUTPUT", position=(138.43, 88.9), rotation=0.0)
add_label(text="GND", position=(129.54, 105.41), rotation=0.0)

# 7. Add junction at output tap (where R1, C1, and output meet)
add_junction(position=(127.0, 88.9), diameter=0.0)

# 8. Save
save_schematic(file_path="rc_filter.kicad_sch")
```

**Circuit Details**:
- **Cutoff Frequency**: f_c = 1 / (2π × R × C) = 1 / (2π × 10kΩ × 100nF) ≈ 159 Hz
- **Application**: Audio low-pass filter, removes high-frequency noise
- **Attenuation**: -20dB/decade above cutoff
- **Input Impedance**: 10kΩ
- **Output Impedance**: ~10kΩ at DC, decreases with frequency

**Result**: Professional audio filter circuit with proper grounding!

## Advanced Examples

### Example 8: Multi-Component Circuit Analysis

**Request**:
```
Load my schematic and analyze it:
1. List all components
2. Find all resistors
3. Find all capacitors with value 100nF
4. Show pin details for U1
```

**MCP Tool Sequence**:
```python
# 1. Load existing schematic
load_schematic(file_path="/path/to/my_circuit.kicad_sch")

# 2. List all components
all_components = list_components()
# Returns: {"success": true, "count": 15, "components": [...]}

# 3. Find all resistors
resistors = filter_components(lib_id="Device:R")
# Returns: {"success": true, "count": 5, "components": [R1, R2, R3, R4, R5]}

# 4. Find specific capacitors
caps_100nf = filter_components(lib_id="Device:C", value="100nF")
# Returns: {"success": true, "count": 2, "components": [C2, C7]}

# 5. Get detailed pin information for IC
u1_pins = get_component_pins("U1")
# Returns all 64 pins with positions, names, and types
```

**Use Cases**:
- BOM generation
- Design review
- Component inventory
- Circuit analysis

### Example 9: Pin Discovery for Complex ICs

**Request**:
```
For component U1 (STM32 microcontroller):
1. Show all pins
2. Find all clock pins
3. Find all power input pins
4. Find UART TX pin
```

**MCP Tool Sequence**:
```python
# 1. Get all pins (comprehensive view)
all_pins = get_component_pins("U1")
# Returns: 144 pins with complete metadata

# 2. Find clock pins by name pattern
clk_pins = find_pins_by_name("U1", "CLK*", case_sensitive=False)
# Returns: ["PA8", "PB0", "PC9"] - all pins with "CLK" in name

# 3. Find power pins by electrical type
power_pins = find_pins_by_type("U1", "power_in")
# Returns: ["VDD", "VDDA", "VREF+", ...] - all power input pins

# 4. Find specific UART pin
uart_tx = find_pins_by_name("U1", "*TX*", case_sensitive=False)
# Returns: ["PA9", "PB6", "PC10"] - UART TX pins
```

**Use Cases**:
- Complex IC routing
- Power distribution design
- Signal integrity analysis
- Automatic wire routing

### Example 10: Batch Component Updates

**Request**:
```
Update all resistors to 1% tolerance footprint and rotate them 90 degrees
```

**MCP Tool Sequence**:
```python
# 1. Find all resistors
resistors = filter_components(lib_id="Device:R")

# 2. Update each resistor
for resistor in resistors["components"]:
    ref = resistor["reference"]

    update_component(
        reference=ref,
        rotation=90.0,
        footprint="Resistor_SMD:R_0603_1608Metric"
    )

# Result: All resistors now have:
# - 90° rotation (horizontal orientation)
# - 0603 footprint for tight PCB layout
```

**Use Cases**:
- Design standardization
- Footprint assignment
- Layout optimization
- Design rules compliance

## Common Patterns

### Pattern 1: Component Placement with Grid Alignment

**Always use grid-aligned coordinates (1.27mm increments)**:

```python
# Good - on grid
add_component("Device:R", "R1", "10k", position=(127.0, 76.2))
add_component("Device:C", "C1", "100nF", position=(101.6, 88.9))

# Bad - off grid (causes connectivity issues!)
add_component("Device:R", "R2", "10k", position=(125.5, 75.3))
```

**Grid calculation helper**:
```python
# Convert mm to grid units (1.27mm grid)
def to_grid(mm):
    return round(mm / 1.27) * 1.27

# Examples
to_grid(100.0) → 101.6   # (80 × 1.27)
to_grid(125.0) → 124.46  # (98 × 1.27)
```

### Pattern 2: Vertical Component Stacking

**Stack components vertically with consistent spacing**:

```python
SPACING = 19.05  # 15 × 1.27mm grid units

base_x = 127.0
base_y = 76.2

# Add components with vertical stacking
add_component("Device:R", "R1", "10k", position=(base_x, base_y))
add_component("Device:R", "R2", "20k", position=(base_x, base_y + SPACING))
add_component("Device:R", "R3", "30k", position=(base_x, base_y + 2*SPACING))

# Result: Three resistors perfectly aligned vertically
```

### Pattern 3: Pin-to-Pin Wiring

**Connect components using pin positions**:

```python
# 1. Get pin positions
r1_pins = get_component_pins("R1")
r2_pins = get_component_pins("R2")

# Extract specific pins
r1_pin2 = next(p for p in r1_pins["pins"] if p["number"] == "2")
r2_pin1 = next(p for p in r2_pins["pins"] if p["number"] == "1")

# 2. Create wire
add_wire(
    start=(r1_pin2["position"]["x"], r1_pin2["position"]["y"]),
    end=(r2_pin1["position"]["x"], r2_pin1["position"]["y"])
)

# Result: Direct connection between R1 pin 2 and R2 pin 1
```

### Pattern 4: Label Placement Near Wires

**Place labels offset from wires for visibility**:

```python
# Wire coordinates
wire_x = 127.0
wire_y = 66.04

# Add wire
add_wire(start=(wire_x, wire_y), end=(wire_x, wire_y - 10.0))

# Add label offset to the right (+2.54mm)
add_label(
    text="VCC",
    position=(wire_x + 2.54, wire_y),
    rotation=0.0
)

# Result: Label appears to the right of the wire, clearly visible
```

**Note**: See issue #104 for planned improvements to automatic label placement on wires.

### Pattern 5: Junction Placement

**Add junctions where 3+ wires meet**:

```python
# Connection point coordinates
tap_x = 127.0
tap_y = 85.725

# Add three wires meeting at this point
add_wire(start=(tap_x, 80.01), end=(tap_x, tap_y))    # From above
add_wire(start=(tap_x, tap_y), end=(tap_x, 91.44))    # To below
add_wire(start=(tap_x, tap_y), end=(tap_x + 10, tap_y))  # To right

# Add junction to indicate proper connection
add_junction(position=(tap_x, tap_y), diameter=0.0)

# Result: Clear T-connection with visual junction indicator
```

## Troubleshooting

### Issue 1: Components Not Connecting

**Problem**: Wires don't connect to component pins.

**Solution**: Verify pin positions and grid alignment:

```python
# Check pin positions
pins = get_component_pins("R1")
print(pins)  # Verify exact coordinates

# Ensure wire endpoints match pin positions exactly
add_wire(
    start=(127.0, 72.39),  # Must match pin position EXACTLY
    end=(127.0, 66.04)
)
```

### Issue 2: Labels Not On Wires

**Problem**: Labels appear disconnected from wires.

**Current Workaround**: Manually calculate label offset:

```python
# Wire position
wire_pos = (127.0, 66.04)

# Place label offset to the right
label_pos = (wire_pos[0] + 2.54, wire_pos[1])

add_label(text="VCC", position=label_pos)
```

**Future**: See issue #104 for planned `add_label_on_wire()` helper method.

### Issue 3: Component Rotation

**Problem**: Component oriented incorrectly after placement.

**Solution**: Use correct rotation values:

```python
# Resistor/Capacitor orientations
rotation=0    # Vertical (default) - pins at top and bottom
rotation=90   # Horizontal - pins on left and right
rotation=180  # Vertical inverted
rotation=270  # Horizontal inverted

# Update rotation if needed
update_component(reference="R1", rotation=90.0)
```

### Issue 4: Schematic Not Saving

**Problem**: `save_schematic()` fails or produces empty file.

**Solution**: Check schematic state and file path:

```python
# Verify schematic info
info = get_schematic_info()
print(info)  # Should show component count, project name

# Save with absolute path
save_schematic(file_path="/Users/me/Desktop/my_circuit.kicad_sch")
```

### Issue 5: Component Not Found

**Problem**: `get_component_pins("R1")` returns error "Component not found".

**Solution**: Verify component exists and use correct reference:

```python
# List all components
components = list_components()
print([c["reference"] for c in components["components"]])

# Use exact reference
pins = get_component_pins("R1")  # Case-sensitive!
```

## Best Practices

1. **Always use grid-aligned coordinates** (1.27mm increments)
2. **Get pin positions before wiring** - don't guess coordinates
3. **Add junctions at T-connections** - ensures proper connectivity
4. **Place labels offset from wires** - improves readability
5. **Use consistent spacing** - improves readability and maintainability
6. **Verify component references** - use exact case-sensitive names
7. **Save frequently** - preserve work incrementally
8. **Test in KiCAD** - verify generated schematics open correctly

## Additional Resources

- **[MCP Setup Guide](../MCP_SETUP_GUIDE.md)** - Installation and configuration
- **[README](../README.md)** - Main project documentation
- **[API Reference](API_REFERENCE.md)** - Complete Python API documentation
- **[Issue #104](https://github.com/circuit-synth/kicad-sch-api/issues/104)** - Label placement improvements

---

**Questions or Issues?**

Report problems at: https://github.com/circuit-synth/kicad-sch-api/issues
