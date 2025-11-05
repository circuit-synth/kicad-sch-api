# kicad-sch-api Examples

This directory contains practical examples demonstrating kicad-sch-api functionality, organized from beginner to advanced usage.

## Quick Start

Run any example directly:
```bash
python examples/basic_usage.py
```

## Learning Path

### 1. Beginner: Core Functionality

Start here if you're new to kicad-sch-api. These examples cover essential operations.

#### `basic_usage.py` - Your First Schematic
**What it teaches:**
- Creating a new schematic from scratch
- Adding components (resistors, capacitors)
- Setting component properties and footprints
- Adding wire connections
- Component filtering and search
- Bulk property updates
- Validation and error checking
- Saving schematics with format preservation

**Run it:**
```bash
python examples/basic_usage.py
```

**Output:** Creates a voltage divider circuit and demonstrates core API features.

---

#### `parser_demo.py` - Understanding S-Expressions
**What it teaches:**
- How KiCAD schematics are structured (S-expressions)
- Parsing existing KiCAD files
- Inspecting schematic structure
- Understanding the low-level format

**Run it:**
```bash
python examples/parser_demo.py
```

**Use when:** You need to understand KiCAD file format or debug parsing issues.

---

### 2. Intermediate: Connections & Layout

Once comfortable with basics, learn about wiring and component positioning.

#### `simple_circuit_with_pin_wiring.py` - Pin-to-Pin Connections
**What it teaches:**
- Direct pin-to-pin wiring
- Automatic pin position calculation
- Simple component placement
- Creating functional circuits

**Run it:**
```bash
python examples/simple_circuit_with_pin_wiring.py
```

**Output:** Creates a basic circuit with proper pin connections.

---

#### `pin_to_pin_wiring_demo.py` - Advanced Pin Wiring
**What it teaches:**
- Multiple pin-to-pin connections
- Wire routing strategies
- Component positioning for clean layouts
- Handling complex wiring scenarios

**Run it:**
```bash
python examples/pin_to_pin_wiring_demo.py
```

---

#### `simple_two_resistor_routing.py` - Manhattan Routing Basics
**What it teaches:**
- Automatic wire routing between components
- Manhattan (L-shaped) routing algorithms
- Obstacle avoidance basics
- Path optimization

**Run it:**
```bash
python examples/simple_two_resistor_routing.py
```

**Use when:** You need intelligent automatic wire routing.

---

### 3. Advanced: Performance & Integration

Master large schematics, performance optimization, and external tool integration.

#### `advanced_usage.py` - Large Schematics & Performance
**What it teaches:**
- Handling large schematics (100+ components)
- Performance optimization techniques
- Symbol caching and indexing
- Bulk operations at scale
- Memory management
- Performance monitoring

**Run it:**
```bash
python examples/advanced_usage.py
```

**Output:** Creates a 10×10 resistor network (100 components) demonstrating performance.

---

#### `kicad_cli_exports.py` - KiCAD CLI Integration
**What it teaches:**
- Exporting netlists (Spice, KiCAD, etc.)
- Generating BOMs (Bill of Materials)
- Running Electrical Rules Check (ERC)
- Exporting PDFs and SVGs
- Docker fallback for CLI operations

**Run it:**
```bash
python examples/kicad_cli_exports.py
```

**Requirements:** KiCAD CLI installed or Docker available.

---

### 4. Integration: MCP & AI Agents

Learn how to integrate kicad-sch-api with Claude Code and other AI tools.

#### `mcp_basic_example.py` - MCP Server Basics
**What it teaches:**
- Model Context Protocol (MCP) integration
- Exposing schematic operations as MCP tools
- Basic MCP server setup

**Run it:**
```bash
python examples/mcp_basic_example.py
```

---

#### `mcp_integration.py` - Full MCP Implementation
**What it teaches:**
- Complete MCP server implementation
- Tool definitions for AI agents
- Schematic operations via MCP protocol
- Integration with Claude Code

**Run it:**
```bash
python examples/mcp_integration.py
```

**Use when:** Building AI-powered circuit design tools.

---

## Common Patterns

### Creating a Simple Circuit
```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("My Circuit")
r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
sch.save("my_circuit.kicad_sch")
```

### Pin-to-Pin Wiring
```python
# Automatic pin position calculation
sch.add_wire_between_pins("R1", "2", "R2", "1")
```

### Component Search
```python
# Find all resistors
resistors = sch.components.filter(lib_id="Device:R")

# Bulk update
sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%'}}
)
```

## Example Selection Guide

| Your Goal | Recommended Example | Why |
|-----------|-------------------|-----|
| Learn the basics | `basic_usage.py` | Comprehensive introduction |
| Understand file format | `parser_demo.py` | Low-level format details |
| Wire components | `pin_to_pin_wiring_demo.py` | Pin connection techniques |
| Auto-route wires | `simple_two_resistor_routing.py` | Routing algorithms |
| Large schematics | `advanced_usage.py` | Performance optimization |
| KiCAD CLI integration | `kicad_cli_exports.py` | Netlist, BOM, ERC exports |
| AI integration | `mcp_integration.py` | MCP server for Claude Code |

## Tips

**Best Practices:**
- Start with `basic_usage.py` to understand core concepts
- Use `parser_demo.py` when debugging file format issues
- Reference `advanced_usage.py` for performance-critical applications
- Check `kicad_cli_exports.py` for manufacturing preparation

**Common Issues:**
- Missing KiCAD symbols: Install KiCAD and set `KICAD_SYMBOL_DIR` environment variable
- Import errors: Ensure kicad-sch-api is installed (`pip install kicad-sch-api`)
- Performance: Use symbol caching (automatic) for large schematics

## Next Steps

After working through these examples:

1. **Read the full documentation:** https://kicad-sch-api.readthedocs.io/
2. **Explore the API reference:** Understand all available methods
3. **Check out mcp-kicad-sch-api:** Full MCP server for AI agents
4. **Build your own tools:** Use kicad-sch-api as a foundation

## Contributing Examples

Have a useful example? Submit a pull request!

Good examples:
- Demonstrate a specific feature or use case
- Include clear comments explaining each step
- Run without user interaction (automated)
- Show expected output with print statements
- Are self-contained and reproducible

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
