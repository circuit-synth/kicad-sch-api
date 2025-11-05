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
