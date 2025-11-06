# KiCAD Schematic API

[![Documentation Status](https://readthedocs.org/projects/kicad-sch-api/badge/?version=latest)](https://kicad-sch-api.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/kicad-sch-api.svg)](https://badge.fury.io/py/kicad-sch-api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Professional Python library for KiCAD schematic file manipulation with exact format preservation**

## Overview

Create and manipulate KiCAD schematic files programmatically with guaranteed exact format preservation. This library serves as the foundation for EDA automation tools and AI agents that need reliable, professional-grade schematic manipulation capabilities.

## 🎯 Core Features

- **📋 Exact Format Preservation**: Byte-perfect KiCAD output that matches native formatting
- **🏗️ Professional Component Management**: Object-oriented collections with search and validation
- **⚡ High Performance**: Optimized for large schematics with intelligent caching
- **🔍 Real KiCAD Library Integration**: Access to actual KiCAD symbol libraries and validation
- **🔌 Connectivity Analysis**: Trace electrical connections through wires, labels, and hierarchy
- **📐 Component Bounding Boxes**: Precise component boundary calculation and visualization
- **🛣️ Manhattan Routing**: Intelligent wire routing with obstacle avoidance
- **🗂️ Hierarchical Design**: Complete support for multi-sheet schematic projects
- **🤖 AI Agent Ready**: MCP server for seamless integration with AI development tools

## 🚀 Quick Start

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

## 📚 Advanced Features

For comprehensive documentation on all features:

- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation with examples
- **[Hierarchy Features](docs/HIERARCHY_FEATURES.md)** - Multi-sheet design guide
- **[Recipes](docs/RECIPES.md)** - Common patterns and examples
- **[Getting Started](docs/GETTING_STARTED.md)** - Detailed tutorial
- **[Architecture](docs/ARCHITECTURE.md)** - Library design and internals

## 🤖 AI Agent Integration

This library serves as the foundation for AI agent integration. For Claude Code or other AI agents, use the **[mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api)** MCP server.

## 🏗️ Architecture

### Design Principles

- **Building Block First**: Designed to be the foundation for other tools
- **Exact Format Preservation**: Guaranteed byte-perfect KiCAD output
- **Professional Quality**: Comprehensive error handling and validation
- **MCP Foundation**: Designed as a stable foundation for MCP servers and AI agents
- **Performance Optimized**: Fast operations on large schematics

**📖 See [Architecture Guide](docs/ARCHITECTURE.md) for detailed design documentation**

## 🧪 Testing & Quality

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

## 🆚 Why This Library?

### vs. Direct KiCAD File Editing
- **Professional API**: High-level operations vs low-level S-expression manipulation
- **Guaranteed Format**: Byte-perfect output vs manual formatting
- **Validation**: Real KiCAD library integration and component validation

### vs. Other Python KiCAD Libraries
- **Format Preservation**: Exact KiCAD compatibility vs approximate output
- **Modern Design**: Object-oriented collections vs legacy patterns
- **AI Integration**: Purpose-built MCP server vs no agent support

**📖 See [Why Use This Library](docs/WHY_USE_THIS_LIBRARY.md) for detailed comparison**

## 📖 Documentation

Full documentation is available in the **[docs/](docs/)** directory:

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete beginner's tutorial
- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Hierarchy Features](docs/HIERARCHY_FEATURES.md)** - Multi-sheet design guide
- **[Recipes & Patterns](docs/RECIPES.md)** - Practical examples
- **[Why Use This Library](docs/WHY_USE_THIS_LIBRARY.md)** - Value proposition
- **[Architecture](docs/ARCHITECTURE.md)** - Internal design details
- **[Examples](examples/)** - Code examples and tutorials

## 🤝 Contributing

We welcome contributions! Key areas:

- KiCAD library integration and component validation
- Performance optimizations for large schematics
- Additional MCP tools for AI agents
- Test coverage and format preservation validation

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- **[mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api)** - MCP server for AI agents
- **[circuit-synth](https://github.com/circuit-synth/circuit-synth)** - High-level circuit design automation
- **[Claude Code](https://claude.ai/code)** - AI development environment with MCP support
- **[KiCAD](https://kicad.org/)** - Open source electronics design automation

---

*Made with ❤️ for the open hardware community*
