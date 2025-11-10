---
name: generate-circuit
description: Expert guidance on using kicad-sch-api Python library to generate KiCAD schematics with CRUD operations for all schematic components (add, list, update, remove components, wires, labels, junctions)
---

# Generate Professional KiCAD Circuit Schematic

You are generating a professional KiCAD schematic using `kicad-sch-api` with expert-level component placement and routing.

## User's Circuit Request

**Description:** {{arg}}

Your task is to generate a complete, professional Python script that creates this circuit schematically.

---

## ⚠️ ULTRA CRITICAL: GRID ALIGNMENT (1.27mm) ⚠️

**🔴 THE MOST CRITICAL RULE: ALL POSITIONS MUST BE ON 1.27mm GRID! 🔴**

**KiCAD uses a 1.27mm (50 mil) grid for schematic components and wires.**

**EVERY position MUST be a multiple of 1.27mm:**
- ✅ Valid: 0, 1.27, 2.54, 3.81, 5.08, 6.35, 7.62, 8.89, 10.16, 11.43, 12.70...
- ✅ Valid: 100.33, 101.60, 102.87, 104.14, 105.41, 106.68, 107.95...
- ❌ Invalid: 100.5, 115.3, 129.540, 184.150 (OFF GRID!)

**Why this matters:**
- Off-grid components cause **crooked wires**
- Off-grid wires cause **connectivity issues**
- Off-grid placement looks **unprofessional**
- Can cause **ERC (Electrical Rule Check) failures**

**How to ensure grid alignment:**

```python
def snap_to_grid(value, grid=1.27):
    """Snap a value to nearest grid point."""
    return round(value / grid) * grid

# Use for ALL positions
signal_y = snap_to_grid(130.0)  # Ensures exactly on grid
r1_x = snap_to_grid(180.0)
vout_x = snap_to_grid(200.0)

# Verify grid alignment
assert signal_y % 1.27 < 0.01, f"Y position {signal_y} not on 1.27mm grid!"
```

**Pin positions and grid:**
- Component centers MUST be on grid
- Pin offsets from component center may cause pins to be off-grid
- **Use actual pin positions from `list_component_pins()` for wire endpoints** (already on correct positions)
- **Never manually calculate pin positions** - always query them!

---

## ⚠️ CRITICAL: KiCAD Y-Axis Is INVERTED ⚠️

**THE SECOND MOST IMPORTANT THING TO UNDERSTAND:**

**In KiCAD schematics, the Y-axis is INVERTED compared to normal math coordinates:**
- **LOWER Y values = HIGHER on screen (TOP of schematic)**
- **HIGHER Y values = LOWER on screen (BOTTOM of schematic)**
- **X-axis is normal** (increases to the right)

**This means:**
- Power symbol at TOP of schematic → **SMALL Y value** (e.g., Y = 100mm)
- Ground symbol at BOTTOM of schematic → **LARGE Y value** (e.g., Y = 160mm)
- Component above another → **SMALLER Y value**
- Wire going DOWN → **INCREASING Y values**

**If your circuit appears upside-down (GND at top, +5V at bottom), you have the Y-axis backwards!**

---

## Core Placement Principles

### 1. Visual Layout Conventions

**Vertical Layout:**
- **Power at TOP** (small Y values) - +5V, +3V3, VCC symbols
- **Ground at BOTTOM** (large Y values) - GND symbols
- Creates natural top-to-bottom reading direction

**Horizontal Layout:**
- **Input on LEFT** - Signal sources start on left
- **Output on RIGHT** - Signal destinations on right

**Component Orientation:**
- **Vertical components** for top-to-bottom connections (resistors, LEDs)
- **Polarized components** oriented for readability:
  - LED cathodes point toward ground (downward)
  - Capacitor negative toward ground
  - Diode cathode (bar) toward load/ground

**⚠️ CRITICAL ALIGNMENT RULE:**
- **Vertical circuits**: All components in a stack MUST have the **SAME X coordinate**
- **Horizontal circuits**: All components in a chain MUST have the **SAME Y coordinate**
- **If you see diagonal wires, your component placement is WRONG!**

---

### 2. Horizontal Signal Flow Circuits (CRITICAL!)

**For left-to-right signal paths (filters, amplifiers, signal chains):**

**🔴 CRITICAL: Use `add_with_pin_at()` for perfect horizontal alignment!**

**🎉 NEW API (v0.6.0+): Pin-Aligned Placement - Eliminates Manual Calculations!**

The library now provides `add_with_pin_at()` which places components by specifying WHERE A SPECIFIC PIN should be, rather than where the component center should be. This **eliminates all manual pin offset calculations and verification loops!**

```python
# SIMPLE: Connection PINS must be at signal_y
signal_y = rect_center_y  # Choose one Y coordinate for entire signal path

# NEW WAY: Direct pin positioning (RECOMMENDED!)
# Place resistor with output pin (pin 2) on signal line
r1 = sch.components.add_with_pin_at(
    lib_id='Device:R',
    pin_number='2',  # Which pin to position
    pin_position=(r1_x, signal_y),  # Where that pin should be
    value='1k',
    reference='R1'
)

# Place capacitor with input pin (pin 1) on signal line
c1 = sch.components.add_with_pin_at(
    lib_id='Device:C',
    pin_number='1',  # Which pin to position
    pin_position=(c1_x, signal_y),  # Where that pin should be
    value='100nF',
    reference='C1'
)

# ✅ GUARANTEED: R1 pin 2 and C1 pin 1 are now EXACTLY at signal_y!
# ✅ NO verification needed - alignment is automatic!
# ✅ Works with ANY rotation!

# Ground BELOW the signal path
gnd_y = signal_y + 30  # 30mm below signal line
gnd = sch.components.add('power:GND', '#PWR01', value='GND', position=(c1_x, gnd_y))
```

**Benefits of `add_with_pin_at()`:**
- ✅ **No manual pin offset calculations** - just specify where the pin should be
- ✅ **No verification loops needed** - alignment is guaranteed
- ✅ **Code is 66% shorter** - clean and readable
- ✅ **Works with any rotation** - handles transformations automatically
- ✅ **Intent is clear** - code says exactly what it does

**Alternative: Align existing components**

If you already have components placed, use `align_pin()` to fix alignment:

```python
# Component already exists but not aligned
r1 = sch.components.get('R1')

# Move it so pin 2 is at the signal line
r1.align_pin('2', (r1_x, signal_y))
```

**Common mistakes (OLD WAY):**
- ❌ Manual calculation: "capacitor pin 1 at Y=96.19, so center at Y=103.81"
- ❌ Verification loops checking if pins are on signal line
- ❌ Remove/recreate cycle when alignment is wrong

**Rule:** Horizontal signal flow = Use `add_with_pin_at()` with CONNECTION PINS at same Y coordinate!

**Why this matters:**
- Before: 30+ lines of complex verification and repositioning code
- After: 3 lines per component with guaranteed alignment
- Result: Cleaner code, fewer bugs, faster development

---

### 3. Circuit Centering Strategy (CRITICAL!)

**Always calculate rectangle center FIRST, then work backwards:**

```python
# 1. Define desired rectangle location and size
rect_x1 = 140
rect_y1 = 90
rect_x2 = 240
rect_y2 = 170

# 2. Calculate rectangle center
rect_center_x = (rect_x1 + rect_x2) / 2  # 190
rect_center_y = (rect_y1 + rect_y2) / 2  # 130

# 3. Calculate circuit dimensions (how much space it needs)
branch_spacing = 50  # Distance between left and right branches
circuit_height = 60  # Distance from top power to bottom GND

# 4. Calculate starting position to CENTER the circuit
base_x = rect_center_x - (branch_spacing / 2)  # 190 - 25 = 165
base_y = rect_center_y - (circuit_height / 2)  # 130 - 30 = 100

# 5. Now place components relative to base position
left_x = base_x              # 165 (left branch)
right_x = base_x + branch_spacing  # 215 (right branch)
power_y = base_y             # 100 (TOP - small Y!)
resistor_y = base_y + 20
led_y = base_y + 40
gnd_y = base_y + 60          # 160 (BOTTOM - large Y!)

# 6. VERIFY CENTERING (important check!)
circuit_actual_center_x = (left_x + right_x) / 2  # Should equal rect_center_x
circuit_actual_center_y = (power_y + gnd_y) / 2   # Should equal rect_center_y
assert abs(circuit_actual_center_x - rect_center_x) < 1.0, "Circuit not centered horizontally!"
assert abs(circuit_actual_center_y - rect_center_y) < 1.0, "Circuit not centered vertically!"
```

---

### 3. Component Spacing Guidelines

**Horizontal spacing between parallel branches:**
- Use **40-60mm** between branches (50mm is ideal)
- NOT 80mm+ (too sparse)

**Vertical spacing between components:**
- **15-20mm** between component centers
- Power to resistor: 20mm
- Resistor to LED: 20mm
- LED to ground: 20mm

**Total dimensions:**
- Circuit width (2 branches): **100-130mm**
- Circuit height (4 stages): **70-85mm**

---

### 4. Component Rotation and Pin Verification (CRITICAL!)

**⚠️ WARNING: After rotating components, ALWAYS verify pin positions!**

Different components behave differently with rotation. Pin locations change based on rotation angle.

**CRITICAL: Resistor Rotation in KiCAD**

Resistor orientation is counter-intuitive:
- **`rotation=0`**: Vertical resistor (pins top/bottom)
- **`rotation=90`**: Horizontal resistor (pins left/right) ← Use this for horizontal signal paths!

**When rotation changes, pin order MAY change - ALWAYS query actual positions!**

**Best practice workflow for horizontal components:**

```python
# 1. Place component with rotation for horizontal orientation
r1 = sch.components.add('Device:R', 'R1', '1k', position=(r_x, signal_y), rotation=90)

# 2. Query ACTUAL pin positions (returns Point objects)
r_pins = sch.list_component_pins('R1')
r_pin1_pos = r_pins[0][1]  # Point object with .x and .y
r_pin2_pos = r_pins[1][1]  # Point object with .x and .y

# 3. CRITICAL: Determine left/right based on actual X coordinates (NOT pin numbers!)
if r_pin1_pos.x < r_pin2_pos.x:
    r_left_pin = r_pin1_pos
    r_right_pin = r_pin2_pos
else:
    r_left_pin = r_pin2_pos
    r_right_pin = r_pin1_pos

# 4. Wire based on actual positions (prevents crossed wires!)
sch.add_wire(start=(in_x, signal_y), end=r_left_pin)
sch.add_wire(start=r_right_pin, end=(out_x, signal_y))
```

**Common rotation issues:**
- ❌ Assuming pin 1 is always left after rotation (WRONG - it depends on rotation!)
- ❌ Using rotation=0 for horizontal resistors (creates vertical resistor)
- ❌ Not querying actual pin positions → crossed wires over component body

**LED Rotation Guide (vertical orientation with cathode pointing DOWN):**

```python
# CORRECT - cathode points down (toward higher Y)
d1 = sch.components.add(
    'Device:LED',
    reference='D1',
    value='GREEN',
    position=(x, y),
    rotation=270  # 90° CCW from 0° - cathode points DOWN
)
```

**LED rotation guide:**
- `rotation=0`: Cathode points RIGHT (horizontal)
- `rotation=90`: Cathode points UP (WRONG for vertical)
- `rotation=180`: Cathode points LEFT (horizontal)
- `rotation=270`: **Cathode points DOWN (CORRECT for vertical circuits)**

**Rule:** Don't assume pin positions after rotation. Always query with `list_component_pins()` and determine left/right by X coordinate!

---

### 5. Power Symbol Values (CRITICAL!)

**Power symbols MUST have voltage as value, NOT reference:**

```python
# CORRECT - shows "+3V3" in schematic
pwr = sch.components.add('power:+3V3', reference='#PWR01', value='+3V3')

# CORRECT - shows "+5V" in schematic
pwr = sch.components.add('power:+5V', reference='#PWR02', value='+5V')

# CORRECT - shows "GND" in schematic
gnd = sch.components.add('power:GND', reference='#PWR03', value='GND')

# WRONG - creates BLANK symbol
pwr = sch.components.add('power:+3V3', reference='#PWR01', value='#PWR01')  # ❌
```

**Rule:**
- Reference: Always `#PWRxx` format (e.g., #PWR01, #PWR02)
- **Value: MUST be the voltage string** (e.g., '+3V3', '+5V', 'GND')

---

### 6. Wire Routing with list_component_pins() (CRITICAL!)

**ALWAYS use `list_component_pins()` for accurate wire connections:**

```python
# list_component_pins returns: [(pin_number, (x, y)), ...]
r1_pins = sch.list_component_pins("R1")
d1_pins = sch.list_component_pins("D1")

# r1_pins = [('1', (165.0, 116.19)), ('2', (165.0, 123.81))]
# d1_pins = [('1', (165.0, 136.19)), ('2', (165.0, 143.81))]

# Get pin positions (tuples, not dicts!)
r1_pin2_pos = r1_pins[1][1]  # [1]=second pin, [1]=position tuple
d1_pin1_pos = d1_pins[0][1]  # [0]=first pin, [1]=position tuple

# Wire them together with exact pin positions
sch.add_wire(start=r1_pin2_pos, end=d1_pin1_pos)
```

**Benefits:**
- ✅ No guessing pin offsets
- ✅ Accounts for component rotation automatically
- ✅ Works for any component type
- ✅ Exact positions, no gaps

**WRONG approach:**
```python
# Don't guess offsets!
sch.add_wire(start=(x, y - 1.905), end=(x, y + 1.905))  # ❌
```

---

### 7. Text Positioning (CRITICAL!)

**Title (above rectangle):**
```python
title_y = rect_y1 - 10  # Above rectangle top
title_x = rect_center_x  # Centered

sch.add_text(
    "CIRCUIT TITLE",
    position=(title_x, title_y),
    size=2.0  # Larger than annotations
)
```

**Annotation (INSIDE rectangle bottom):**
```python
# CRITICAL: annotation_y MUST be < rect_y2 (inside rectangle)
annotation_y = rect_y2 - 10  # 10mm from bottom, safely INSIDE
annotation_x = rect_center_x  # Centered

sch.add_text(
    "Circuit description",
    position=(annotation_x, annotation_y),
    size=1.27  # Standard KiCAD size
)

# VERIFY: annotation_y < rect_y2
assert annotation_y < rect_y2, "Text outside rectangle!"
```

**Text length limits:**
- Single line: **max 50 characters**
- Use abbreviations (L/R instead of Left/Right)
- Split into multiple lines if needed

---

### 8. Label Connection Requirements (CRITICAL!)

**⚠️ Labels MUST be placed AT wire endpoints, not near them!**

```python
# WRONG - label offset from wire (floating label, not connected!)
wire_start = (160, 115)
sch.add_wire(start=wire_start, end=(180, 115))
sch.add_label("Vin", position=(150, 115))  # ❌ Offset by 10mm - NOT CONNECTED!

# CORRECT - label exactly at wire endpoint (connected!)
wire_start = (160, 115)
sch.add_wire(start=wire_start, end=(180, 115))
sch.add_label("Vin", position=wire_start)  # ✅ At wire endpoint - CONNECTED!
```

**Rule for signal labels:**
1. Place wire first
2. Save wire endpoint coordinates
3. Place label at EXACT same coordinates as wire endpoint
4. Verify label touches the wire visually

**Common mistake:** Offsetting labels for "readability" creates floating labels that aren't electrically connected

**Exception:** Component value/reference labels can be offset (handled automatically)

---

### 9. Junction Placement

**Junctions required at ALL T-junction points (3+ wires meeting):**

```python
# Add junction at power rail branch point
sch.junctions.add(position=(x, power_y))
```

**Rule:** Junction position must be EXACTLY at wire intersection

---

### 10. Rectangle Placement

**Add rectangle with exact bounds:**

```python
sch.add_rectangle(start=(rect_x1, rect_y1), end=(rect_x2, rect_y2))
```

---

## Verification Checklist

Before generating the final script, mentally verify:

- [ ] **🔴 GRID ALIGNMENT**: ALL positions are multiples of 1.27mm (use snap_to_grid function!)
- [ ] **Y-axis correct**: Power at small Y (TOP), GND at large Y (BOTTOM)
- [ ] **Circuit centered**: Calculations verified, center matches rectangle center
- [ ] **🎉 NEW: Use `add_with_pin_at()`**: For horizontal signal flows - eliminates manual alignment!
- [ ] **Component alignment**: Same X for vertical, same Y for horizontal (NO DIAGONALS!)
- [ ] **LED rotation**: `rotation=270` for vertical circuits (cathode down)
- [ ] **Power symbol values**: Voltage strings ('+3V3', '+5V', 'GND'), not references
- [ ] **Wire routing**: All wires use `list_component_pins()` tuples (pins already grid-aligned)
- [ ] **Labels connected**: Labels at exact wire endpoints, not offset
- [ ] **Text inside bounds**: `annotation_y < rect_y2`
- [ ] **Spacing balanced**: 40-60mm horizontal, 15-20mm vertical
- [ ] **Junctions added**: At all T-connection points

---

## Output Requirements

Generate a complete Python script that:

1. **Imports kicad-sch-api**: `import kicad_sch_api as ksa`
2. **Creates schematic**: `sch = ksa.create_schematic("Circuit Name")`
3. **Uses exact centering calculations** as shown above
4. **Adds all components** with proper positions and rotations
5. **Routes all wires** using `list_component_pins()`
6. **Adds junctions** at T-connections
7. **Adds text** (title above, annotation inside bottom)
8. **Adds rectangle** with calculated bounds
9. **Saves schematic**: `sch.save('output_name.kicad_sch')`
10. **Includes verification** assertions for centering
11. **Adds helpful comments** explaining positioning calculations

**Script should be complete, executable, and generate a professional schematic on first run.**

---

## Example Template Structure

```python
#!/usr/bin/env python3
"""
[Circuit Description]
"""

import kicad_sch_api as ksa

# Create schematic
sch = ksa.create_schematic("Circuit Name")

# Rectangle bounds and centering calculations
# Default: center circuit around (100, 100) for upper-left placement
rect_x1, rect_y1 = 50, 50
rect_x2, rect_y2 = 150, 150
rect_center_x = (rect_x1 + rect_x2) / 2  # 100
rect_center_y = (rect_y1 + rect_y2) / 2  # 100

# Circuit dimensions
branch_spacing = 50
circuit_height = 60

# Base position (centered)
base_x = rect_center_x - (branch_spacing / 2)
base_y = rect_center_y - (circuit_height / 2)

# Component positions
# ... (calculate all positions)

# Add components
# ... (use proper API calls)

# Get pin positions
# ... (use list_component_pins)

# Wire connections
# ... (use pin positions)

# Add junctions
# ... (at T-connections)

# Add text
# ... (title above, annotation inside)

# Add rectangle
sch.add_rectangle(start=(rect_x1, rect_y1), end=(rect_x2, rect_y2))

# Verify centering
# ... (assertions)

# Save
sch.save('output.kicad_sch')

print("Circuit created successfully!")
```

---

**Now generate the complete Python script for the user's circuit request!**
