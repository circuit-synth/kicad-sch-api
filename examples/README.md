# Examples

## Quick Start

```bash
# Run the main example
python examples/example.py

# Export to various formats (requires KiCAD CLI)
python examples/kicad_cli_exports.py
```

## Available Examples

### `example.py` - Complete Feature Demonstration

Comprehensive example showing all major features:

- **Components**: Microcontroller, voltage regulator, resistors, capacitors, LED, button, connector
- **Properties**: Setting power ratings, tolerances, voltage ratings, colors
- **Wiring**: Simple wires and pin-to-pin connections
- **Labels**: Net labels and hierarchical labels
- **Text**: Adding text annotations
- **Search**: Filtering by lib_id, reference, value
- **Bulk Operations**: Updating multiple components at once
- **Validation**: Checking for errors before saving
- **Save/Load**: Writing and reading schematic files

**Run it:**
```bash
python examples/example.py
```

**Output:** Creates `examples/output/example.kicad_sch` with all demonstrated features.

---

### `kicad_cli_exports.py` - KiCAD CLI Integration

Demonstrates integration with KiCAD command-line tools:

- Netlist export (multiple formats)
- Bill of Materials (BOM) generation
- Electrical Rules Check (ERC)
- PDF/SVG/DXF export

**Requirements:** KiCAD CLI installed or Docker available.

**Run it:**
```bash
python examples/kicad_cli_exports.py
```

---

### `stm32g431_simple.py` - Simple STM32 Development Board ⭐ START HERE!

**Beginner-friendly** hierarchical design with STM32G431RBT6 (64-pin LQFP).

**Perfect for learning!** This simplified version has:
- **STM32G431RBT6** - 64-pin LQFP (easier to solder than QFN)
- **AMS1117-3.3** - Simple voltage regulator
- **USB-C** - Power-only (no data complexity)
- **1 button** - Reset
- **1 LED** - Classic blinky on PC13
- **SWD header** - For programming
- **Only ~14 components** - Easy to understand!

**Sheet structure (5 sheets):**
- main.kicad_sch - Top-level
- power.kicad_sch - Voltage regulator
- mcu.kicad_sch - STM32G431RBT6
- usb.kicad_sch - USB-C power
- ui.kicad_sch - Button + LED + SWD

**What it demonstrates:**
- Hierarchical organization (simpler than G474)
- Essential components only
- LQFP package (hand-solderable)
- Perfect first STM32 board

**Run it:**
```bash
python examples/stm32g431_simple.py
```

**Output:** `examples/stm32g431_simple/` with 5 schematic files (~14 components, 5,127 lines).

**Why start here:**
- Half the complexity of G474 version
- Easier to understand
- Hand-solderable components
- All the basics covered

---

### `stm32g474_example.py` - Comprehensive STM32 Development Board

A production-ready example recreating the STM32G474 Black Pill development board.

**Features:**
- **STM32G474CEUx** microcontroller (48-pin QFN)
- **USB-C** connector with proper CC resistors
- **3.3V voltage regulator** (AP7343xx)
- **32Mbit SPI Flash** memory (W25Q32JVSS)
- **3 user buttons** (NRST, USER, BOOT0)
- **2 status LEDs** (red and green)
- **SWD debug header** (4-pin programming interface)
- **2x20 GPIO expansion headers**
- **Comprehensive power filtering** (decoupling caps, analog supply filtering)

**What it demonstrates:**
- Complex multi-IC schematic design
- Proper power distribution and decoupling
- USB standards compliance (CC resistors)
- Professional component organization
- Grid-aligned placement
- Complete power management circuit

**Run it:**
```bash
python examples/stm32g474_example.py
```

**Output:** Creates `examples/stm32g474_example.kicad_sch` with 34 components organized into 10 functional sections.

**Based on:** [STM32G474 Black Pill v3.0](https://github.com/nikolai2111/STM32G474_Black-Pill_v3.0) (CERN-OHL-P-2.0)

---

### `stm32g474_hierarchical.py` - Multi-Sheet Hierarchical Design

The same STM32G474 Black Pill design organized as a professional hierarchical schematic with 7 sheets.

**Sheet Structure:**
- **main.kicad_sch** - Top-level with sheet instances
- **power.kicad_sch** - Voltage regulator (AP7343xx 3.3V)
- **mcu.kicad_sch** - Microcontroller + decoupling
- **usb.kicad_sch** - USB-C connector with CC resistors
- **flash.kicad_sch** - SPI Flash memory (W25Q32JVSS)
- **ui.kicad_sch** - User interface (3 buttons + 2 LEDs)
- **headers.kicad_sch** - Connectors (SWD + GPIO headers)

**What it demonstrates:**
- Hierarchical sheet organization
- Sheet pins for inter-sheet connections
- Global labels for signal routing
- Functional separation of circuits
- Professional multi-sheet design patterns
- Clean organization for complex designs

**Run it:**
```bash
python examples/stm32g474_hierarchical.py
```

**Output:** Creates `examples/stm32g474_hierarchical/` directory with 7 schematic files (36 components total).

**Compare:** Open both flat and hierarchical versions to see different organizational approaches for the same circuit.

---

## Recommended Learning Path

**New to hierarchical design?**
1. ⭐ **Start:** `stm32g431_simple.py` - Simplified STM32 (5 sheets, ~14 components)
2. **Next:** `stm32g474_hierarchical.py` - Full-featured (7 sheets, 36 components)
3. **Compare:** `stm32g474_example.py` - Flat version of same circuit

**Complexity comparison:**
- G431 Simple: 5 sheets, ~14 components, 5,127 lines
- G474 Hierarchical: 7 sheets, 36 components, 8,282 lines
- G474 Flat: 1 sheet, 34 components, 6,663 lines

---

## Common Patterns

### Create Schematic
```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("My Circuit")
```

### Add Component
```python
resistor = sch.components.add(
    "Device:R", "R1", "10k",
    position=(100, 100),
    footprint="Resistor_SMD:R_0603_1608Metric"
)
resistor.set_property("Power", "0.1W")
```

### Add Wire
```python
# Simple wire
sch.wires.add(start=(100, 100), end=(150, 100))

# Pin-to-pin
sch.add_wire_between_pins("R1", "2", "R2", "1")
```

### Filter Components
```python
# Find all resistors
resistors = sch.components.filter(lib_id="Device:R")

# Find by reference
r1 = sch.components.get("R1")
```

### Save
```python
sch.save("my_circuit.kicad_sch")
```

## Next Steps

- Read the [API documentation](../docs/API_REFERENCE.md)
- Check the [llm.txt](../llm.txt) for comprehensive API reference
- See [main README](../README.md) for installation and setup

## MCP Server

For AI integration with Claude and other LLMs, see the separate [mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api) repository.
