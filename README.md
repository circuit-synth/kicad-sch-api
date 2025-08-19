# KiCAD Schematic API

**Professional Python library for KiCAD schematic file manipulation with exact format preservation**

## Overview

Create and manipulate KiCAD schematic files programmatically with guaranteed exact format preservation. This library serves as the foundation for EDA automation tools and AI agents that need reliable, professional-grade schematic manipulation capabilities.

## 🎯 Core Features

- **📋 Exact Format Preservation**: Byte-perfect KiCAD output that matches native formatting
- **🏗️ Professional Component Management**: Object-oriented collections with search and validation
- **⚡ High Performance**: Optimized for large schematics with intelligent caching
- **🔍 Real KiCAD Library Integration**: Access to actual KiCAD symbol libraries and validation
- **🤖 AI Agent Ready**: MCP server for seamless integration with AI development tools
- **📚 Hierarchical Design**: Complete support for multi-sheet schematic projects

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install kicad-sch-api

# Or install from source
git clone https://github.com/circuit-synth/kicad-sch-api.git
cd kicad-sch-api/python
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

## 🔧 Advanced Features

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

## 🤖 AI Agent Integration (MCP Server)

Use with Claude Code or other AI agents via Model Context Protocol:

### Setup MCP Server

```bash
# Install MCP server
pip install kicad-sch-api[mcp]

# Configure for Claude Code (automatic)
kicad-sch-api --setup-claude-code
```

### Usage with AI Agents

```
# Natural language commands to your AI agent:
"Create a voltage divider with two 10kΩ resistors"
"Add an ESP32 microcontroller with USB connector" 
"Generate a hierarchical schematic with power supply subcircuit"
```

The AI agent will use the MCP server to:
1. Create professional schematics with proper component references
2. Use hierarchical labels instead of messy wires
3. Apply KiCAD design best practices automatically
4. Generate clean, industry-standard layouts

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `create_schematic` | Create new schematic files |
| `add_component` | Add components with validation |
| `search_components` | Find components in KiCAD libraries |
| `add_hierarchical_sheet` | Create multi-sheet designs |
| `validate_component` | Check component/footprint compatibility |
| `list_components` | Get all components in schematic |
| `save_schematic` | Save with exact format preservation |

## 🏗️ Architecture

### Library Structure

```
kicad_sch_api/
├── core/              # Core schematic manipulation
├── library/           # KiCAD library integration
├── integration/       # KiCAD CLI and tool integration
├── mcp/              # MCP server for AI agents
└── utils/            # Validation and utilities
```

### Design Principles

- **Building Block First**: Designed to be the foundation for other tools
- **Exact Format Preservation**: Guaranteed byte-perfect KiCAD output
- **Professional Quality**: Comprehensive error handling and validation
- **AI-Native**: Built specifically for AI agent integration
- **Performance Optimized**: Fast operations on large schematics

## 🧪 Testing & Quality

```bash
# Run all tests
uv run pytest tests/ -v

# Format preservation tests (critical)
uv run pytest tests/reference_tests/ -v

# Code quality checks
uv run black kicad_sch_api/ tests/
uv run mypy kicad_sch_api/
uv run flake8 kicad_sch_api/ tests/
```

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

This library is designed as a building block for specialized tools:

```python
# Foundation library
import kicad_sch_api as ksa

# Specialized libraries (examples of what could be built)
# import kicad_sourcing_tools as sourcing      # Component sourcing
# import kicad_placement_optimizer as placement # Layout optimization  
# import kicad_dfm_checker as dfm              # Manufacturing validation

# Foundation provides reliable schematic manipulation
sch = ksa.load_schematic('project.kicad_sch')

# Specialized tools extend functionality
# sourcing.update_component_sourcing(sch.components)
# placement.optimize_layout(sch)
# dfm.check_manufacturing_rules(sch)

# All save through foundation's format preservation
sch.save()  # Guaranteed exact KiCAD format
```

## 📖 Documentation

- **[API Reference](docs/api.md)**: Complete API documentation
- **[Examples](examples/)**: Code examples and tutorials
- **[MCP Integration](docs/mcp.md)**: AI agent integration guide
- **[Development](docs/development.md)**: Contributing and development setup

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

- **[circuit-synth](https://github.com/circuit-synth/circuit-synth)**: High-level circuit design automation using this library
- **[Claude Code](https://claude.ai/code)**: AI development environment with MCP support
- **[KiCAD](https://kicad.org/)**: Open source electronics design automation suite

---

**Professional KiCAD schematic manipulation for the AI age ⚡**