# kicad-sch-api Examples

Polished examples demonstrating KiCAD schematic generation using Python.

## Quick Start

Start with the walkthrough:

```bash
cd examples
cat WALKTHROUGH.md   # Read the tutorial
python voltage_divider.py
python rc_filter.py
python power_supply.py
```

## Directory Structure

```
examples/
├── WALKTHROUGH.md          # Start here! Complete tutorial
├── voltage_divider.py      # Basic voltage divider circuit
├── rc_filter.py            # RC low-pass filter
├── power_supply.py         # AMS1117-3.3 voltage regulator
├── stm32_simple.py         # STM32 microcontroller example
└── COMBINED.py             # Run all examples at once
```

---

## Examples Overview

### Basic Circuits (Start Here!)

**`WALKTHROUGH.md`** - Complete tutorial from basics to advanced
Start here to learn the library step-by-step.

**`voltage_divider.py`** - Simple 10k/10k voltage divider
Demonstrates:
- Grid-based parametric design
- Component placement with `p()` helper
- Auto-routing between pins
- Junctions and labels

**`rc_filter.py`** - RC low-pass filter (1.59 kHz)
Demonstrates:
- Vertical component layout
- Auto-routing between components
- Simple junction and labels

**`power_supply.py`** - AMS1117-3.3 voltage regulator
Demonstrates:
- Power symbols (VCC, GND)
- Multiple junction points
- Polarized capacitor placement
- Voltage regulator circuit patterns

**`stm32_simple.py`** - STM32 Microcontroller Example
Demonstrates:
- STM32G030K8Tx microcontroller
- Reset circuit with button and capacitor
- LED indicator circuit
- SWD debug interface connections

---

## Common Patterns

All examples use these patterns:

### Enable Grid Units
```python
import kicad_sch_api as ksa

# Enable grid units globally (1 unit = 1.27mm)
ksa.use_grid_units(True)
```

### Parametric Position Helper
```python
def my_circuit(sch, x_grid, y_grid):
    """Reusable circuit at any position"""

    # Position helper for parametric placement
    def p(dx, dy):
        return (x_grid + dx, y_grid + dy)

    # Now use p() for all positions
    sch.components.add('Device:R', 'R1', '10k', position=p(0, 0))
    sch.components.add('Device:C', 'C1', '100nF', position=p(0, 7))
```

### Create and Save
```python
sch = ksa.create_schematic("MyCircuit")
my_circuit(sch, 20, 20)  # Place at grid (20, 20)
sch.save("output.kicad_sch")
```

---

## Key Concepts

### Grid Units
- 1 grid unit = 1.27mm (50 mil - KiCAD standard)
- Use integer coordinates: `(20, 20)` instead of `(25.4, 25.4)`
- Enable with `ksa.use_grid_units(True)`

### Parametric Circuits
- Reusable circuit functions
- Place anywhere using `x_grid`, `y_grid` parameters
- Use `p(dx, dy)` helper for relative positioning
- Each circuit is self-contained

### Auto-Routing
- Automatically connects component pins
- `sch.auto_route_pins('R1', '2', 'C1', '1', routing_strategy='direct')`
- No need to calculate pin positions manually

---

## Learning Path

1. **Read `WALKTHROUGH.md`** - Complete tutorial (start here!)
2. **Run `voltage_divider.py`** - Understand basic patterns
3. **Run `rc_filter.py`** - See auto-routing
4. **Run `power_supply.py`** - Learn power symbols
5. **Run `stm32_simple.py`** - See microcontroller integration
6. **Run `COMBINED.py`** - Generate all examples at once

---

## Next Steps

- Read the [API documentation](../docs/API_REFERENCE.md)
- Check the [llm.txt](../llm.txt) for comprehensive API reference
- See [main README](../README.md) for installation and setup
- Review [CLAUDE.md](../CLAUDE.md) for development guidelines

## MCP Server

For AI integration with Claude and other LLMs, see the separate [mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api) repository.
