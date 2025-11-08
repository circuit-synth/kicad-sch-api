# Advanced Examples

Complex features and professional design patterns for kicad-sch-api.

## Overview

These examples demonstrate advanced techniques:
- Multi-sheet hierarchical design
- Complex microcontroller circuits
- Wire routing strategies
- Professional design organization

## Examples

### `stm32g431_simple.py` - Simple STM32 Development Board ⭐

**Perfect for learning hierarchical design!**

Beginner-friendly hierarchical design with STM32G431RBT6 (64-pin LQFP).

**Why this example:**
- Simplified version (vs G474) - easier to understand
- Complete working development board design
- Professional hierarchical organization
- Hand-solderable components (LQFP vs QFN)
- Essential features only (~14 components)

**Features:**
- **STM32G431RBT6** microcontroller (64-pin LQFP)
- **AMS1117-3.3** voltage regulator
- **USB-C** power connector
- **Reset button** + **Status LED**
- **SWD programming header**
- **Proper power filtering** (decoupling capacitors)

**Sheet Structure (5 sheets):**
```
stm32g431_simple/
├── main.kicad_sch              # Top-level sheet with hierarchical blocks
├── power.kicad_sch             # AMS1117-3.3 voltage regulator
├── mcu.kicad_sch               # STM32G431RBT6 + decoupling
├── usb.kicad_sch               # USB-C power connector
└── ui.kicad_sch                # Button + LED + SWD header
```

**Run it:**
```bash
python advanced/stm32g431_simple.py
```

**Output:** `stm32g431_simple/` directory with 5 schematic files

**What it demonstrates:**

1. **Hierarchical Organization:**
   ```python
   # Create parent schematic
   main_sch = ksa.create_schematic("STM32G431_Simple")
   parent_uuid = main_sch.uuid

   # Add hierarchical sheet
   power_sheet_uuid = main_sch.sheets.add_sheet(
       name="Power Supply",
       filename="power.kicad_sch",
       position=(50, 50),
       size=(100, 100),
       project_name="STM32G431_Simple"
   )

   # Create child schematic with hierarchy context
   power_sch = ksa.create_schematic("STM32G431_Simple")
   power_sch.set_hierarchy_context(parent_uuid, power_sheet_uuid)
   ```

2. **Sheet Pins (Inter-sheet Connections):**
   ```python
   # Add sheet pin for power output
   main_sch.sheets.add_sheet_pin(
       sheet_uuid=power_sheet_uuid,
       name="+3V3",
       position=(150, 60),
       shape="output"
   )
   ```

3. **Global Labels (Signal Routing):**
   ```python
   # In parent sheet
   main_sch.add_global_label("+3V3", position=(160, 60), shape="input")

   # In child sheet - connects automatically
   power_sch.add_global_label("+3V3", position=(200, 80), shape="output")
   ```

4. **Functional Separation:**
   - Power generation in one sheet
   - MCU core in another
   - User interface separate
   - Clean, modular organization

**Complexity Comparison:**
- G431 Simple: 5 sheets, ~14 components, 5,127 lines
- G474 Hierarchical: 7 sheets, 36 components, 8,282 lines
- G474 Flat: 1 sheet, 34 components, 6,663 lines

**Start here if:** You want to learn hierarchical design with a simple, complete example.

---

### `hierarchy_example.py` - Hierarchical Design Patterns

Comprehensive guide to hierarchical schematic organization.

**What it demonstrates:**
- Creating parent and child sheets
- Setting hierarchy context (`set_hierarchy_context()`)
- Sheet pins for inter-sheet connections
- Global labels for signal routing
- Hierarchical label shapes (input, output, bidirectional, passive)
- Project name consistency requirements

**Key concepts:**

**1. Hierarchy Context (CRITICAL):**
```python
# Parent schematic
main = ksa.create_schematic("MyProject")
parent_uuid = main.uuid

# Add sheet to parent
sheet_uuid = main.sheets.add_sheet(
    name="Power",
    filename="power.kicad_sch",
    position=(50, 50),
    size=(100, 100),
    project_name="MyProject"  # MUST match parent!
)

# Create child with hierarchy context
child = ksa.create_schematic("MyProject")  # Same name!
child.set_hierarchy_context(parent_uuid, sheet_uuid)  # CRITICAL!

# Now components get correct hierarchical paths
vreg = child.components.add(...)  # Path: /parent_uuid/sheet_uuid ✓
```

**Without `set_hierarchy_context()`:**
- Components show as "?" in KiCAD
- Annotation doesn't work
- Netlist is broken

**With `set_hierarchy_context()`:**
- Components show proper references (U1, R1, etc.)
- Annotation works correctly
- Netlist is correct

**2. Sheet Pins:**
```python
# Connect sheet to parent schematic
main.sheets.add_sheet_pin(
    sheet_uuid=sheet_uuid,
    name="VCC_OUT",
    position=(150, 60),  # Position on sheet rectangle
    shape="output"       # Electrical direction
)
```

**3. Global Labels:**
```python
# Labels with same name connect across sheets
child.add_global_label("VCC", position=(100, 100), shape="output")
main.add_global_label("VCC", position=(200, 100), shape="input")
# These connect automatically!
```

**Run it:**
```bash
python advanced/hierarchy_example.py
```

---

### Routing Demonstrations

**Location:** `routing/`

Wire routing examples showing different strategies for clean schematics.

#### `create_routing_demo.py` - Basic Wire Routing

**What it demonstrates:**
- Direct wire connections
- Orthogonal (Manhattan) routing
- Using junctions for T-connections
- Wire segment management

**Key patterns:**
```python
# Direct connection
sch.wires.add(start=(100, 100), end=(150, 100))

# L-shaped routing (horizontal then vertical)
sch.wires.add(start=(100, 100), end=(150, 100))  # Horizontal
sch.wires.add(start=(150, 100), end=(150, 150))  # Vertical

# T-connection with junction
sch.wires.add(start=(100, 100), end=(200, 100))
sch.wires.add(start=(150, 100), end=(150, 150))
sch.add_junction(position=(150, 100))  # Junction at T
```

**Run it:**
```bash
python advanced/routing/create_routing_demo.py
```

#### `orthogonal_routing_demo.py` - Manhattan Routing

**What it demonstrates:**
- Automatic orthogonal routing between pins
- Horizontal-first vs vertical-first routing
- Junction placement at corners
- Label placement on routes

**Key technique:**
```python
# Automatic routing with library function
sch.connect_components(
    from_component="R1",
    from_pin="2",
    to_component="R2",
    to_pin="1",
    corner_direction="horizontal_first",  # Route horizontally first
    add_label="VCC",                      # Optional label on route
    add_junction=True                     # Add junction at corner
)
```

**Routing Strategies:**

1. **Horizontal First:**
   ```
   R1 ----+
          |
          +---- R2
   ```
   Good for: Left-to-right layouts

2. **Vertical First:**
   ```
   R1
   |
   +---- R2
   ```
   Good for: Top-to-bottom layouts

3. **Auto (Default):**
   - Chooses based on distance
   - If dx >= dy: horizontal first
   - If dy > dx: vertical first

**Run it:**
```bash
python advanced/routing/orthogonal_routing_demo.py
```

---

## Design Patterns

### Pattern 1: Functional Hierarchy

Organize by circuit function:
```
main.kicad_sch          # Top level
├── power.kicad_sch     # Power generation/regulation
├── mcu.kicad_sch       # Microcontroller core
├── peripherals.kicad_sch  # External devices
└── connectors.kicad_sch   # Headers/connectors
```

**Benefits:**
- Easy to understand
- Simple navigation
- Clear functional boundaries
- Reusable blocks

### Pattern 2: Signal Flow Hierarchy

Organize by signal flow:
```
main.kicad_sch
├── input.kicad_sch     # Input stage
├── processing.kicad_sch # Signal processing
├── output.kicad_sch    # Output stage
└── power.kicad_sch     # Power supply
```

**Benefits:**
- Follows circuit flow
- Easier debugging
- Natural organization
- Clear data path

### Pattern 3: Module-Based Hierarchy

Organize by reusable modules:
```
main.kicad_sch
├── module_sensor.kicad_sch    # Sensor interface
├── module_adc.kicad_sch       # ADC + filtering
├── module_mcu.kicad_sch       # MCU core
└── module_output.kicad_sch    # Output drivers
```

**Benefits:**
- Reusable modules
- Clear interfaces
- Easy testing
- Scalable design

## Best Practices

### Hierarchical Design

1. **Consistent Project Names:**
   ```python
   # All schematics MUST use same project name
   main = ksa.create_schematic("MyProject")
   child = ksa.create_schematic("MyProject")  # Same!
   ```

2. **Always Set Hierarchy Context:**
   ```python
   child.set_hierarchy_context(parent_uuid, sheet_uuid)
   # Do this BEFORE adding components!
   ```

3. **Use Descriptive Sheet Names:**
   ```python
   # Good
   main.sheets.add_sheet(name="USB Power Supply", ...)

   # Less clear
   main.sheets.add_sheet(name="Sheet1", ...)
   ```

4. **Logical Sheet Sizes:**
   ```python
   # Typical sheet sizes (in mm)
   small = (76.2, 50.8)    # ~60 grids × 40 grids
   medium = (127, 101.6)   # 100 grids × 80 grids
   large = (177.8, 127)    # 140 grids × 100 grids
   ```

### Wire Routing

1. **Use Grid-Aligned Positions:**
   ```python
   # Good - grid aligned
   sch.wires.add(start=(100.33, 101.60), end=(127.00, 101.60))

   # Bad - off grid
   sch.wires.add(start=(100.5, 101.8), end=(127.2, 101.8))
   ```

2. **Query Pin Positions:**
   ```python
   # Good - query actual positions
   pins = sch.list_component_pins("R1")
   sch.wires.add(start=pins['2'].position, end=(150, 100))

   # Bad - hardcoded offset
   sch.wires.add(start=(100, 103.81), end=(150, 100))  # Breaks with rotation!
   ```

3. **Use Junctions for T-Connections:**
   ```python
   # Three wires meet at (150, 100)
   sch.wires.add(start=(100, 100), end=(200, 100))
   sch.wires.add(start=(150, 100), end=(150, 150))
   sch.add_junction(position=(150, 100))  # Required!
   ```

4. **Prefer Orthogonal Routing:**
   ```python
   # Good - orthogonal (Manhattan)
   sch.wires.add(start=(100, 100), end=(150, 100))  # Horizontal
   sch.wires.add(start=(150, 100), end=(150, 150))  # Vertical

   # Avoid - diagonal wiring
   sch.wires.add(start=(100, 100), end=(150, 150))  # Harder to read
   ```

## Common Patterns

### Create Hierarchical Schematic
```python
import kicad_sch_api as ksa

# Parent
main = ksa.create_schematic("MyProject")
parent_uuid = main.uuid

# Add sheet
sheet_uuid = main.sheets.add_sheet(
    name="Power Supply",
    filename="power.kicad_sch",
    position=(50, 50),
    size=(100, 100),
    project_name="MyProject"
)

# Child
child = ksa.create_schematic("MyProject")
child.set_hierarchy_context(parent_uuid, sheet_uuid)

# Add components to child
child.components.add("Regulator_Linear:LM7805_TO220", "U1", "LM7805",
                     position=(100, 100))

# Save both
main.save("main.kicad_sch")
child.save("power.kicad_sch")
```

### Add Sheet Pins
```python
# Output from child sheet
main.sheets.add_sheet_pin(
    sheet_uuid=sheet_uuid,
    name="VCC_OUT",
    position=(150, 60),
    shape="output"
)

# Connect in parent
main.add_global_label("VCC_OUT", position=(160, 60), shape="input")
```

### Automatic Routing
```python
# Route between components
sch.connect_components(
    from_component="R1",
    from_pin="2",
    to_component="C1",
    to_pin="1",
    corner_direction="auto",
    add_junction=True
)
```

## Troubleshooting

**Components show as "?" in KiCAD:**
- Missing `set_hierarchy_context()` call
- Project names don't match between parent and child
- Sheet not added to parent before creating child

**Wires don't connect:**
- Positions not grid-aligned
- Missing junction at T-connection
- Pin positions not queried correctly

**Hierarchy broken:**
- `set_hierarchy_context()` called after adding components
- Parent UUID or sheet UUID incorrect
- Files not saved in same directory

## Performance Tips

For large hierarchical designs:

1. **Use sheet-level organization** (not all components in main sheet)
2. **Reuse child sheets** when possible
3. **Query pins once** and cache positions for multiple wires
4. **Batch wire creation** instead of one-by-one

## See Also

- [Parametric Circuits](../parametric_circuits/) - Reusable circuit patterns
- [Basics](../basics/) - Getting started examples
- [Hierarchy Features](../../docs/HIERARCHY_FEATURES.md) - Complete hierarchy documentation
- [CLAUDE.md](../../CLAUDE.md) - Hierarchy requirements and grid alignment
