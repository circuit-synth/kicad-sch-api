# KiCAD Schematic API

[![Documentation Status](https://readthedocs.org/projects/kicad-sch-api/badge/?version=latest)](https://kicad-sch-api.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/kicad-sch-api.svg)](https://badge.fury.io/py/kicad-sch-api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Python library for reading and writing KiCAD schematic files**

Generates valid `.kicad_sch` files that open in KiCAD 7/8. Focus on exact format preservation and simple API design.

## Overview

Read and write KiCAD schematic files programmatically. This library parses and generates `.kicad_sch` files with exact format preservation - output matches KiCAD's native formatting byte-for-byte.

## Core Features

- **Exact format preservation** - Output matches KiCAD's native formatting byte-for-byte
- **Standalone library** - No KiCAD installation required
- **Simple API** - Object-oriented interface for components, wires, labels, and symbols
- **Tested compatibility** - 70+ tests verify format preservation against KiCAD reference files
- **KiCAD library access** - Read actual KiCAD symbol libraries for component validation
- **Connectivity analysis** - Trace electrical connections through wires, labels, and hierarchy
- **Hierarchical design** - Complete support for multi-sheet schematic projects
- **Component bounding boxes** - Calculate precise component boundaries for layout algorithms
- **Wire routing** - Manhattan-style orthogonal routing with basic obstacle avoidance
- **MCP server** - 15 tools for programmatic schematic manipulation via Model Context Protocol

## Quick Start

### Installation

```bash
# Install from PyPI
pip install kicad-sch-api

# Or install from source
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api
uv pip install -e .
```

### Basic Usage

```python
import kicad_sch_api as ksa

# Create a new schematic
sch = ksa.create_schematic("My Circuit")

# Add components with proper validation
resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(100.0, 100.0),
    footprint="Resistor_SMD:R_0603_1608Metric"
)

# Add wires for connectivity
sch.wires.add(start=(100, 110), end=(150, 110))

# Pin-to-pin wiring
wire_uuid = sch.add_wire_between_pins("R1", "2", "C1", "1")

# Add labels for nets
sch.add_label("VCC", position=(125, 110))

# Save with exact format preservation
sch.save("my_circuit.kicad_sch")
```

## ⚠️ Critical: KiCAD Coordinate System

**Understanding this is CRITICAL for working with this library.**

### The Two Coordinate Systems

KiCAD uses **two different Y-axis conventions**:

1. **Symbol Space** (library definitions): Normal Y-axis (+Y is UP, like math)
2. **Schematic Space** (placed components): Inverted Y-axis (+Y is DOWN, like graphics)

### The Transformation

When placing a symbol on a schematic, **Y coordinates are negated**:

```python
# Symbol library (normal Y, +Y up):
Pin 1: (0, +3.81)   # 3.81mm UPWARD in symbol
Pin 2: (0, -3.81)   # 3.81mm DOWNWARD in symbol

# Component placed at (100, 100) in schematic (inverted Y, +Y down):
# Y is NEGATED during transformation:
Pin 1: (100, 100 + (-3.81)) = (100, 96.52)   # LOWER Y = visually HIGHER
Pin 2: (100, 100 + (+3.81)) = (100, 103.81)  # HIGHER Y = visually LOWER
```

### Visual Interpretation

In schematic space (inverted Y-axis):
- **Lower Y values** = visually HIGHER on screen (top)
- **Higher Y values** = visually LOWER on screen (bottom)
- **X-axis is normal** (increases to the right)

### Grid Alignment

**ALL positions MUST be grid-aligned:**
- Default grid: **1.27mm (50 mil)**
- Component positions, wire endpoints, pin positions, labels must all align to grid
- Common values: 0.00, 1.27, 2.54, 3.81, 5.08, 6.35, 7.62, 8.89, 10.16...

```python
# Good - on grid
sch.components.add('Device:R', 'R1', '10k', position=(100.33, 101.60))

# Bad - off grid (will cause connectivity issues)
sch.components.add('Device:R', 'R2', '10k', position=(100.5, 101.3))
```

This coordinate system is critical for:
- Pin position calculations
- Wire routing and connectivity
- Component placement
- Hierarchical connections
- Electrical connectivity detection

## 🔧 Core Features

### Component Management

```python
# Add and manage components
resistor = sch.components.add("Device:R", "R1", "10k", (100, 100))

# Search and filter
resistors = sch.components.find(lib_id_pattern='Device:R*')

# Bulk updates
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)

# Remove components
sch.components.remove("R1")
```

**📖 See [API Reference](docs/API_REFERENCE.md) for complete component API**

### Text Effects & Styling

```python
# Read text effects from component properties
r1 = sch.components.get("R1")
effects = r1.get_property_effects("Reference")
# Returns: {'font_face': 'Arial', 'font_size': (2.0, 2.0), 'bold': True, ...}

# Modify text effects (partial updates - preserves other effects)
r1.set_property_effects("Reference", {
    "color": (0, 255, 0, 1.0),  # Green
    "bold": True,
    "font_size": (2.0, 2.0)
})

# Create components with custom styling
r2 = sch.components.add("Device:R", "R2", "10k", position=(100, 100))
r2.set_property_effects("Value", {
    "rotation": 90.0,           # Sideways
    "justify_h": "left",        # Left justified
    "color": (160, 32, 240, 1.0),  # Purple
    "italic": True
})

# Supported effects: position, rotation, font_face, font_size, font_thickness,
# bold, italic, color (RGBA), justify_h, justify_v, visible
```

**📖 See [API Reference](docs/API_REFERENCE.md#text-effects) for text effects details**

### Connectivity Analysis

```python
# Check if pins are electrically connected
if sch.are_pins_connected("R1", "2", "R2", "1"):
    print("Connected!")

# Get net information
net = sch.get_net_for_pin("R1", "2")
print(f"Net: {net.name}, Pins: {len(net.pins)}")

# Get all connected pins
connected = sch.get_connected_pins("R1", "2")
```

Connectivity analysis includes:
- Direct wire connections
- Connections through junctions
- Local and global labels
- Hierarchical labels (cross-sheet)
- Power symbols (VCC, GND)
- Sheet pins (parent/child)

**📖 See [API Reference](docs/API_REFERENCE.md#connectivity-analysis) for complete connectivity API**

### Hierarchy Management

```python
# Build hierarchy tree
tree = sch.hierarchy.build_hierarchy_tree(sch, schematic_path)

# Find reused sheets
reused = sch.hierarchy.find_reused_sheets()
for filename, instances in reused.items():
    print(f"{filename} used {len(instances)} times")

# Validate sheet connections
connections = sch.hierarchy.validate_sheet_pins()
errors = sch.hierarchy.get_validation_errors()

# Trace signals through hierarchy
paths = sch.hierarchy.trace_signal_path("VCC")

# Flatten design
flattened = sch.hierarchy.flatten_hierarchy(prefix_references=True)

# Visualize hierarchy
print(sch.hierarchy.visualize_hierarchy(include_stats=True))
```

**📖 See [Hierarchy Features Guide](docs/HIERARCHY_FEATURES.md) for complete hierarchy documentation**

### Wire Routing & Pin Connections

```python
# Direct pin-to-pin wiring
sch.add_wire_between_pins("R1", "2", "R2", "1")

# Manhattan routing with obstacle avoidance
wires = sch.auto_route_pins(
    "R1", "2", "R2", "1",
    routing_mode="manhattan",
    avoid_components=True
)

# Get pin positions
pos = sch.get_component_pin_position("R1", "1")
```

**📖 See [Recipes](docs/RECIPES.md) for routing patterns and examples**

### Component Bounding Boxes

```python
from kicad_sch_api.core.component_bounds import get_component_bounding_box

# Get bounding box
bbox = get_component_bounding_box(resistor, include_properties=False)
print(f"Size: {bbox.width:.2f}×{bbox.height:.2f}mm")

# Visualize with rectangles
sch.draw_bounding_box(bbox, stroke_color="blue")
sch.draw_component_bounding_boxes(include_properties=True)
```

**📖 See [API Reference](docs/API_REFERENCE.md#bounding-boxes) for bounding box details**

### Configuration & Customization

```python
import kicad_sch_api as ksa

# Customize property positioning
ksa.config.properties.reference_y = -2.0
ksa.config.properties.value_y = 2.0

# Tolerances
ksa.config.tolerance.position_tolerance = 0.05

# Grid settings
ksa.config.grid.component_spacing = 5.0
```

**📖 See [API Reference](docs/API_REFERENCE.md#configuration) for all configuration options**

#### Library Path Configuration

The library automatically discovers KiCAD symbol libraries from:
- **Environment variables** (`KICAD_SYMBOL_DIR`, `KICAD8_SYMBOL_DIR`, `KICAD7_SYMBOL_DIR`)
- **Standard KiCAD installations** (version-flexible detection)
- **User document directories**

**Set environment variable** (Unix/macOS):
```bash
# Single path
export KICAD_SYMBOL_DIR=/path/to/kicad/symbols

# Multiple paths (colon-separated)
export KICAD_SYMBOL_DIR=/path/to/symbols:/path/to/custom/symbols
```

**Set environment variable** (Windows):
```cmd
# Single path
set KICAD_SYMBOL_DIR=C:\KiCad\symbols

# Multiple paths (semicolon-separated)
set KICAD_SYMBOL_DIR=C:\KiCad\symbols;D:\Custom\symbols
```

**Add library paths programmatically**:
```python
import kicad_sch_api as ksa

# Get cache
cache = ksa.library.get_symbol_cache()

# Add specific library file
cache.add_library_path("/path/to/Device.kicad_sym")

# Discover all libraries in directory
cache.discover_libraries(["/path/to/custom/symbols"])
```

**📖 See [Library Configuration Guide](docs/LIBRARY_CONFIGURATION.md) for complete documentation**

## 📝 Examples

Learn by example with our polished reference circuits in the **[examples/](examples/)** directory:

### Basic Circuits
- **[voltage_divider.py](examples/voltage_divider.py)** - Simple 10k/10k voltage divider with grid-based parametric design
- **[rc_filter.py](examples/rc_filter.py)** - RC low-pass filter demonstrating wire routing and junctions
- **[power_supply.py](examples/power_supply.py)** - AMS1117-3.3 voltage regulator (5V → 3.3V) with power symbols

### Microcontroller Examples
- **[stm32_simple.py](examples/stm32_simple.py)** - STM32G030K8Tx with reset circuit, LED, and SWD debug interface

### Run All Examples
- **[COMBINED.py](examples/COMBINED.py)** - Master script that generates all example schematics at once

### Getting Started
Start with **[WALKTHROUGH.md](examples/WALKTHROUGH.md)** - a complete tutorial from basics to advanced parametric circuits.

All examples use:
- Grid-based positioning with intuitive grid units (1.27mm)
- Parametric `p(x, y)` helper for clean, readable coordinates
- Individual `add_wire()` calls with descriptive comments
- Proper wire junctions at all T-connection points
- Comprehensive inline documentation

```bash
# Run any example
uv run python examples/voltage_divider.py
uv run python examples/rc_filter.py
uv run python examples/power_supply.py
uv run python examples/stm32_simple.py

# Or run all examples at once
uv run python examples/COMBINED.py
```

## 📚 Advanced Features

For comprehensive documentation on all features:

- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[Hierarchy Features](docs/HIERARCHY_FEATURES.md)** - Multi-sheet design guide
- **[Recipes](docs/RECIPES.md)** - Common patterns and examples
- **[Getting Started](docs/GETTING_STARTED.md)** - Detailed tutorial
- **[Architecture](docs/ARCHITECTURE.md)** - Library design and internals

## MCP Server

Includes an MCP (Model Context Protocol) server with 15 tools for programmatic schematic manipulation:

```bash
# Start the MCP server
uv run kicad-sch-mcp

# Or install and run directly
pip install kicad-sch-api
kicad-sch-mcp
```

### MCP Tool Suite (15 Tools)

**Component Management (5 tools):**
- `add_component` - Add components with auto-reference/position
- `list_components` - List all components with metadata
- `update_component` - Update properties (value, position, rotation, footprint)
- `remove_component` - Remove components
- `filter_components` - Advanced filtering by lib_id, value, footprint

**Connectivity (3 tools):**
- `add_wire` - Create wire connections between points
- `add_label` - Add net labels for logical connections
- `add_junction` - Add wire junctions for T-connections

**Pin Discovery (3 tools):**
- `get_component_pins` - Complete pin information with positions
- `find_pins_by_name` - Semantic lookup with wildcards (*, CLK*, *IN*)
- `find_pins_by_type` - Filter by electrical type (passive, input, output, power_in)

**Schematic Management (4 tools):**
- `create_schematic` - Create new KiCAD schematics
- `load_schematic` - Load existing .kicad_sch files
- `save_schematic` - Save schematics to disk
- `get_schematic_info` - Query schematic metadata

### MCP Server Capabilities

The MCP server provides tools for:
- Adding components, creating connections, and labeling nets
- Creating, loading, saving, and modifying schematic files
- Listing components, filtering by criteria, and discovering pin information
- Building circuits like voltage dividers, filters, LED drivers, and power supplies

### Example: Building Complete Circuits via MCP

#### Voltage Divider (Verified Working ✅)

**Natural Language Request**:
```
"Create a voltage divider with R1=10k and R2=20k, fully wired with VCC and GND labels"
```

**The AI agent executes**:
1. `create_schematic(name="Voltage Divider")` - Create new schematic
2. `add_component(lib_id="Device:R", reference="R1", value="10k", position=(127.0, 76.2))` - Add R1
3. `add_component(lib_id="Device:R", reference="R2", value="20k", position=(127.0, 95.25))` - Add R2
4. `get_component_pins("R1")` - Get R1 pin positions
5. `get_component_pins("R2")` - Get R2 pin positions
6. `add_wire(start=(127.0, 72.39), end=(127.0, 66.04))` - VCC to R1
7. `add_wire(start=(127.0, 80.01), end=(127.0, 91.44))` - R1 to R2
8. `add_wire(start=(127.0, 99.06), end=(127.0, 105.41))` - R2 to GND
9. `add_label(text="VCC", position=(129.54, 66.04))` - Add VCC label
10. `add_label(text="VOUT", position=(129.54, 85.725))` - Add output label
11. `add_label(text="GND", position=(129.54, 105.41))` - Add GND label
12. `add_junction(position=(127.0, 85.725))` - Add junction at tap point
13. `save_schematic(file_path="voltage_divider.kicad_sch")` - Save to disk

**Result**: ✅ Fully functional KiCAD schematic verified to open perfectly in KiCAD!

#### LED Circuit with Current Limiting

**Natural Language Request**:
```
"Create an LED circuit with 220Ω current limiting resistor"
```

**The AI agent will**:
- Add LED and 220Ω resistor components
- Wire VCC → resistor → LED → GND
- Add appropriate net labels
- Save the complete circuit

**Result**: Ready-to-use LED driver circuit schematic!

#### RC Low-Pass Filter

**Natural Language Request**:
```
"Create an RC low-pass filter with R=10k, C=100nF"
```

**The AI agent will**:
- Add resistor (10k) and capacitor (100nF)
- Wire input → R → C → output
- Add GND connection to capacitor
- Label INPUT, OUTPUT, and GND nets
- Add junction at output tap
- Save filter schematic

**Result**: Complete filter circuit with proper connectivity!

### Claude Desktop Integration

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "kicad-sch-api": {
      "command": "uv",
      "args": ["run", "kicad-sch-mcp"],
      "env": {}
    }
  }
}
```

MCP tools enable programmatic creation, modification, and analysis of KiCAD schematics.

**📖 Complete Documentation**:
- **[MCP Setup Guide](docs/MCP_SETUP_GUIDE.md)** - Installation, configuration, and troubleshooting
- **[MCP Examples](docs/MCP_EXAMPLES.md)** - Comprehensive usage examples and patterns
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation

## Architecture

### Design Principles

- **Building Block First**: Designed to be the foundation for other tools
- **Exact Format Preservation**: Guaranteed byte-perfect KiCAD output
- **Comprehensive Validation**: Error handling and input validation
- **MCP Integration**: Includes MCP server for programmatic schematic manipulation
- **Performance Optimized**: Fast operations on large schematics

**📖 See [Architecture Guide](docs/ARCHITECTURE.md) for detailed design documentation**

## Testing & Quality

```bash
# Run all tests (29 tests covering all functionality)
uv run pytest tests/ -v

# Format preservation tests (critical - exact KiCAD output matching)
uv run pytest tests/reference_tests/ -v

# Code quality checks
uv run black kicad_sch_api/ tests/
uv run mypy kicad_sch_api/
```

### Test Categories

- **Format Preservation**: Byte-for-byte compatibility with KiCAD native files
- **Component Management**: Creation, modification, and removal
- **Connectivity**: Wire tracing, net analysis, hierarchical connections
- **Hierarchy**: Multi-sheet designs, sheet reuse, signal tracing
- **Integration**: Real KiCAD library compatibility

## Why This Library?

### vs. Direct KiCAD File Editing
- **High-level API**: Object-oriented interface vs low-level S-expression manipulation
- **Format Preservation**: Byte-perfect output vs manual formatting
- **Validation**: Real KiCAD library integration and component validation

### vs. Other Python KiCAD Libraries
- **Format Preservation**: Exact KiCAD compatibility vs approximate output
- **Object-Oriented Design**: Modern collection classes vs legacy patterns
- **MCP Integration**: Included MCP server vs no programmatic interface

**📖 See [Why Use This Library](docs/WHY_USE_THIS_LIBRARY.md) for detailed comparison**

## Known Limitations

### Connectivity Analysis
- **Global Labels**: Explicit global label connections not yet fully implemented (power symbols like VCC/GND work correctly)

### ERC (Electrical Rule Check)
- **Partial Implementation**: ERC validators have incomplete features
- Net tracing, pin type checking, and power net detection are in development
- Core functionality works, advanced validation features coming soon

### Performance
- Large schematics (>1000 components) may experience slower connectivity analysis
- Symbol cache helps, but first analysis can take time
- Optimization ongoing

**Report issues**: https://github.com/circuit-synth/kicad-sch-api/issues

## Documentation

Full documentation is available:

### Learning Resources
- **[Examples Walkthrough](examples/WALKTHROUGH.md)** - Start here! Complete tutorial from basics to advanced
- **[Example Circuits](examples/)** - Polished reference circuits (voltage divider, RC filter, power supply, STM32)
- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete beginner's tutorial

### API Documentation
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Hierarchy Features](docs/HIERARCHY_FEATURES.md)** - Multi-sheet design guide
- **[Recipes & Patterns](docs/RECIPES.md)** - Practical examples

### Project Information
- **[Why Use This Library](docs/WHY_USE_THIS_LIBRARY.md)** - Value proposition
- **[Architecture](docs/ARCHITECTURE.md)** - Internal design details

## 🤝 Contributing

We welcome contributions! Key areas:

- KiCAD library integration and component validation
- Performance optimizations for large schematics
- MCP server tools and AI agent capabilities
- Test coverage and format preservation validation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- **[circuit-synth](https://github.com/circuit-synth/circuit-synth)** - High-level circuit design automation
- **[Claude Code](https://claude.ai/code)** - AI development environment with MCP support
- **[KiCAD](https://kicad.org/)** - Open source electronics design automation
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Standard for AI agent tool integration

---

*Made with ❤️ for the open hardware community*
