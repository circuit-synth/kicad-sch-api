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
- **📐 Component Bounding Boxes**: Precise component boundary calculation and visualization
- **🎨 Colored Rectangle Graphics**: KiCAD-compatible rectangles with all stroke types and colors
- **🛣️ Manhattan Routing**: Intelligent wire routing with obstacle avoidance
- **🤖 AI Agent Ready**: MCP server for seamless integration with AI development tools
- **📚 Hierarchical Design**: Complete support for multi-sheet schematic projects

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
    footprint="Resistor_SMD:R_0603_1608Metric",
    datasheet="~",
    description="Resistor"
)

capacitor = sch.components.add(
    lib_id="Device:C",
    reference="C1", 
    value="100nF",
    position=(150.0, 100.0),
    footprint="Capacitor_SMD:C_0603_1608Metric"
)

# Add wires for connectivity
sch.wires.add(start=(100, 110), end=(150, 110))

# Pin-to-pin wiring (NEW in v0.3.1)
wire_uuid = sch.add_wire_between_pins("R1", "2", "C1", "1")  # Connect R1 pin 2 to C1 pin 1
external_wire = sch.add_wire_to_pin((50, 100), "R1", "1")   # Connect external point to R1 pin 1

# Add labels for nets
sch.add_label("VCC", position=(125, 110))

# Save with exact format preservation
sch.save("my_circuit.kicad_sch")
```

### Hierarchical Design

```python
# Create main schematic with hierarchical sheet
main_sch = ksa.create_schematic("Main Board")

# Add hierarchical sheet
power_sheet = main_sch.add_hierarchical_sheet(
    name="Power Supply",
    filename="power.kicad_sch",
    position=(100, 100),
    size=(80, 60)
)

# Add sheet pins for connectivity
power_sheet.add_pin("VIN", pin_type="input", position=(0, 10))
power_sheet.add_pin("VOUT", pin_type="output", position=(80, 10))

# Create the sub-schematic
power_sch = ksa.create_schematic("Power Supply")
power_sch.add_hierarchical_label("VIN", label_type="input", position=(50, 25))
power_sch.add_hierarchical_label("VOUT", label_type="output", position=(150, 25))

# Save both schematics
main_sch.save("main.kicad_sch")
power_sch.save("power.kicad_sch")
```

## ⚠️ Critical: KiCAD Coordinate System

### Understanding Symbol vs Schematic Coordinate Spaces

**KiCAD uses TWO different coordinate systems** - this is critical for accurate pin positioning:

#### Symbol Space (Library Definitions)
- Uses **NORMAL Y-axis** (+Y is UP) like standard mathematics
- All component symbols in KiCAD libraries are defined this way
- Example: Resistor pin 1 at `(0, 3.81)`, pin 2 at `(0, -3.81)`

#### Schematic Space (Placed Components)
- Uses **INVERTED Y-axis** (+Y is DOWN) like most computer graphics
- Lower Y values = visually HIGHER on screen (top)
- Higher Y values = visually LOWER on screen (bottom)

#### The Transformation Problem

When placing a symbol on a schematic, **Y coordinates must be negated** to convert between coordinate systems:

```python
# Symbol library defines (normal Y-axis, +Y up):
Pin 1: (0, +3.81)   # Upward from origin
Pin 2: (0, -3.81)   # Downward from origin

# Component placed at (100, 100) in schematic:
# After transformation (inverted Y-axis, +Y down):
Pin 1: (100, 96.52)    # Top (100 + (-3.81))
Pin 2: (100, 103.81)   # Bottom (100 + (+3.81))
```

This transformation happens automatically in `geometry.py:apply_transformation()` before applying rotation and mirroring.

#### Why This Matters

**All pin position calculations depend on this transformation:**
- Wire connectivity analysis
- Pin-to-pin routing
- Component placement
- Hierarchical sheet connections
- ERC (Electrical Rule Check) validation

**Without this transformation**, pin positions would be swapped, breaking all connectivity analysis.

### Grid Alignment Requirement

**All positions in KiCAD schematics MUST be grid-aligned:**

- **Default grid:** 1.27mm (50 mil)
- **Common values:** 0.00, 1.27, 2.54, 3.81, 5.08, 6.35, 7.62, 8.89, 10.16...
- **Required for:** Component positions, wire endpoints, pin positions, junction positions

```python
# Good - grid aligned
sch.components.add('Device:R', 'R1', '10k', position=(100.33, 101.60))

# Bad - off grid (will cause connectivity issues)
sch.components.add('Device:R', 'R2', '10k', position=(100.5, 101.3))
```

Grid alignment ensures:
- ✅ Proper electrical connectivity
- ✅ Professional schematic appearance
- ✅ Correct ERC validation
- ✅ No floating-point connectivity errors

## 🔧 Advanced Features

### Component Bounding Boxes and Colored Graphics (NEW in v0.3.1)

```python
from kicad_sch_api.core.component_bounds import get_component_bounding_box

# Add components
resistor = sch.components.add("Device:R", "R1", "10k", (100, 100))
opamp = sch.components.add("Amplifier_Operational:LM358", "U1", "LM358", (150, 100))

# Get component bounding boxes
bbox_body = get_component_bounding_box(resistor, include_properties=False)
bbox_full = get_component_bounding_box(resistor, include_properties=True)

# Draw colored bounding box rectangles
sch.draw_bounding_box(bbox_body, stroke_width=0.5, stroke_color="blue", stroke_type="solid")
sch.draw_bounding_box(bbox_full, stroke_width=0.3, stroke_color="red", stroke_type="dash")

# Draw bounding boxes for all components at once
bbox_uuids = sch.draw_component_bounding_boxes(
    include_properties=True,
    stroke_width=0.4,
    stroke_color="green", 
    stroke_type="dot"
)
```

### Manhattan Routing with Obstacle Avoidance

```python
# Automatic routing between component pins
wire_segments = sch.auto_route_pins(
    "R1", "2", "R2", "1",         # From R1 pin 2 to R2 pin 1
    routing_mode="manhattan",      # L-shaped routing
    avoid_components=True          # Avoid component bounding boxes
)

# Manual routing with custom obstacles
from kicad_sch_api.core.manhattan_routing import ManhattanRouter
from kicad_sch_api.core.types import Point

router = ManhattanRouter()
obstacle_bbox = get_component_bounding_box(sch.components.get("C1"))
path = router.route_between_points(
    Point(50, 50), Point(150, 150),
    [obstacle_bbox],
    clearance=2.0
)

# Add wires along the routed path
for i in range(len(path) - 1):
    sch.wires.add(path[i], path[i + 1])
```

### Pin-to-Pin Wiring

```python
# Connect component pins directly - automatically calculates pin positions
wire_uuid = sch.add_wire_between_pins("R1", "2", "R2", "1")  # R1 pin 2 to R2 pin 1

# Connect arbitrary point to component pin
external_wire = sch.add_wire_to_pin((75, 125), "R1", "1")    # External point to R1 pin 1
tuple_wire = sch.add_wire_to_pin(Point(100, 150), "C1", "2") # Using Point object

# Get component pin positions for advanced operations
pin_position = sch.get_component_pin_position("R1", "1")
if pin_position:
    print(f"R1 pin 1 is at ({pin_position.x:.2f}, {pin_position.y:.2f})")

# Error handling - returns None for invalid components/pins
invalid_wire = sch.add_wire_between_pins("R999", "1", "R1", "1")  # Returns None
```

### Connectivity Analysis

```python
# Check if pins are electrically connected
# Traces through wires, junctions, labels, and hierarchical connections
if sch.are_pins_connected("R1", "2", "R2", "1"):
    print("R1 pin 2 and R2 pin 1 are connected")

# Get the electrical net for a pin
net = sch.get_net_for_pin("R1", "2")
if net:
    print(f"Net: {net.name}")
    print(f"Pins on this net: {len(net.pins)}")
    for pin in net.pins:
        print(f"  - {pin.reference}.{pin.pin_number}")

# Get all pins connected to a specific pin
connected_pins = sch.get_connected_pins("R1", "2")
for ref, pin_num in connected_pins:
    print(f"Connected: {ref}.{pin_num}")

# Connectivity analysis includes:
# - Direct wire connections
# - Connections through junctions
# - Local and global labels
# - Hierarchical labels (cross-sheet connections)
# - Power symbols (VCC, GND, etc.)
# - Sheet pins connecting parent/child schematics
```

### Component Bounding Box Visualization (NEW in v0.3.1)

```python
from kicad_sch_api.core.component_bounds import get_component_bounding_box

# Get component bounding box (body only)
resistor = sch.components.get("R1")
bbox = get_component_bounding_box(resistor, include_properties=False)
print(f"R1 body size: {bbox.width:.2f}×{bbox.height:.2f}mm")

# Get bounding box including properties (reference, value, etc.)
bbox_with_props = get_component_bounding_box(resistor, include_properties=True)
print(f"R1 with labels: {bbox_with_props.width:.2f}×{bbox_with_props.height:.2f}mm")

# Draw bounding box as rectangle graphics (for visualization/debugging)
rect_uuid = sch.draw_bounding_box(bbox)
print(f"Drew bounding box rectangle: {rect_uuid}")

# Draw bounding boxes for all components
bbox_uuids = sch.draw_component_bounding_boxes(
    include_properties=False  # True to include reference/value labels
)
print(f"Drew {len(bbox_uuids)} component bounding boxes")

# Expand bounding box for clearance analysis
expanded_bbox = bbox.expand(2.54)  # Expand by 2.54mm (0.1 inch) 
clearance_rect = sch.draw_bounding_box(expanded_bbox)
```

### Component Search and Management

```python
# Search for components
resistors = sch.components.find(lib_id_pattern='Device:R*')
power_components = sch.components.filter(reference_pattern=r'U[0-9]+')

# Bulk updates
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)

# Component validation
validation_result = sch.components.validate_component(
    'Device:R', 
    'Resistor_SMD:R_0603_1608Metric'
)
```

### Component and Element Removal

```python
# Remove components by reference
removed = sch.components.remove("R1")  # Returns True if removed

# Remove wires, labels, and other elements
sch.remove_wire(wire_uuid)
sch.remove_label(label_uuid)
sch.remove_hierarchical_label(label_uuid)

# Remove from collections
sch.wires.remove(wire_uuid)
sch.junctions.remove(junction_uuid)

# lib_symbols are automatically cleaned up when last component of type is removed
```

### Configuration and Customization

```python
import kicad_sch_api as ksa

# Access global configuration
config = ksa.config

# Customize property positioning
config.properties.reference_y = -2.0  # Move reference labels higher
config.properties.value_y = 2.0       # Move value labels lower

# Customize tolerances and precision
config.tolerance.position_tolerance = 0.05  # Tighter position matching
config.tolerance.wire_segment_min = 0.005   # Different wire segment threshold

# Customize defaults
config.defaults.project_name = "my_company_project"
config.defaults.stroke_width = 0.1

# Grid and spacing customization
config.grid.unit_spacing = 10.0       # Tighter multi-unit IC spacing
config.grid.component_spacing = 5.0   # Closer component placement

# Sheet settings for hierarchical designs
config.sheet.name_offset_y = -1.0     # Different sheet label position
config.sheet.file_offset_y = 1.0      # Different file label position
```

### KiCAD Integration

```python
# Run electrical rules check using KiCAD CLI
erc_result = sch.run_erc_check()
print(f"ERC Status: {erc_result.status}")
for violation in erc_result.violations:
    print(f"- {violation.type}: {violation.message}")

# Generate netlist for connectivity analysis
netlist = sch.generate_netlist()
net_info = netlist.analyze_net("VCC")
```

## 🤖 AI Agent Integration

This library serves as the foundation for AI agent integration. For Claude Code or other AI agents, use the **[mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api)** MCP server.

## 🏗️ Architecture

### Library Structure

```
kicad-sch-api/
├── kicad_sch_api/           # Core Python library
│   ├── core/                # Core schematic manipulation
│   ├── library/             # KiCAD library integration
│   ├── discovery/           # Component search and indexing
│   └── utils/              # Validation and utilities
├── tests/                   # Comprehensive test suite
└── examples/               # Usage examples and tutorials
```

### Design Principles

- **Building Block First**: Designed to be the foundation for other tools
- **Exact Format Preservation**: Guaranteed byte-perfect KiCAD output
- **Professional Quality**: Comprehensive error handling and validation
- **MCP Foundation**: Designed as a stable foundation for MCP servers and AI agents
- **Performance Optimized**: Fast operations on large schematics

## 🧪 Testing & Quality

```bash
# Run all tests (29 tests covering all functionality)
uv run pytest tests/ -v

# Format preservation tests (critical - exact KiCAD output matching)
uv run pytest tests/reference_tests/ -v

# Component removal tests (comprehensive removal functionality)
uv run pytest tests/test_*_removal.py -v

# Code quality checks
uv run black kicad_sch_api/ tests/
uv run mypy kicad_sch_api/
uv run flake8 kicad_sch_api/ tests/
```

### Test Categories

- **Format Preservation**: Byte-for-byte compatibility with KiCAD native files
- **Component Management**: Creation, modification, and removal of components
- **Element Operations**: Wires, labels, junctions, hierarchical sheets
- **Configuration**: Customizable settings and behavior
- **Performance**: Large schematic handling and optimization
- **Integration**: Real KiCAD library compatibility

## 🆚 Why This Library?

### vs. Direct KiCAD File Editing
- **Professional API**: High-level operations vs low-level S-expression manipulation
- **Guaranteed Format**: Byte-perfect output vs manual formatting
- **Validation**: Real KiCAD library integration and component validation
- **Performance**: Optimized collections vs manual iteration

### vs. Other Python KiCAD Libraries
- **Format Preservation**: Exact KiCAD compatibility vs approximate output
- **Modern Design**: Object-oriented collections vs legacy patterns
- **AI Integration**: Purpose-built MCP server vs no agent support
- **Professional Focus**: Production-ready vs exploration tools

## 🔗 Ecosystem

This library serves as the foundation for specialized tools and MCP servers:

```python
# Foundation library
import kicad_sch_api as ksa

# MCP servers and specialized libraries built on this foundation:
# - mcp-kicad-sch-api: Full MCP server for AI agents
# - kicad_sourcing_tools: Component sourcing extensions
# - kicad_placement_optimizer: Layout optimization
# - kicad_dfm_checker: Manufacturing validation

# Foundation provides reliable schematic manipulation
sch = ksa.load_schematic('project.kicad_sch')

# All extensions use the same stable API
# mcp_server.use_schematic(sch)      # MCP server integration
# sourcing.update_sourcing(sch)      # Component sourcing
# placement.optimize_layout(sch)     # Layout optimization

# Foundation ensures exact format preservation
sch.save()  # Guaranteed exact KiCAD format
```

## 📖 Documentation

Full documentation is available at **[kicad-sch-api.readthedocs.io](https://kicad-sch-api.readthedocs.io/)**

Quick links:
- **[Getting Started Guide](https://kicad-sch-api.readthedocs.io/en/latest/GETTING_STARTED.html)**: Complete beginner's tutorial
- **[API Reference](https://kicad-sch-api.readthedocs.io/en/latest/API_REFERENCE.html)**: Complete API documentation
- **[Recipes & Patterns](https://kicad-sch-api.readthedocs.io/en/latest/RECIPES.html)**: Practical examples
- **[Why Use This Library?](https://kicad-sch-api.readthedocs.io/en/latest/WHY_USE_THIS_LIBRARY.html)**: Value proposition and use cases
- **[Architecture](https://kicad-sch-api.readthedocs.io/en/latest/ARCHITECTURE.html)**: Internal design details
- **[Examples](examples/)**: Code examples and tutorials

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

- **[mcp-kicad-sch-api](https://github.com/circuit-synth/mcp-kicad-sch-api)**: MCP server for AI agents built on this library
- **[circuit-synth](https://github.com/circuit-synth/circuit-synth)**: High-level circuit design automation using this library
- **[Claude Code](https://claude.ai/code)**: AI development environment with MCP support
- **[KiCAD](https://kicad.org/)**: Open source electronics design automation suite

---

**Professional KiCAD schematic manipulation for the AI age ⚡**