# PRD: KiCAD Schematic API - Core Building Block

**Version**: 2.0  
**Date**: 2025-08-19  
**Status**: Focused Scope  

## Executive Summary

**"The pandas for KiCAD schematic files"**

Create a focused, professional Python library for KiCAD schematic file manipulation that serves as a building block for other tools. This library provides exact format preservation, component management, and basic KiCAD integration while avoiding feature creep into specialized domains.

## Core Value Proposition

**Focused Building Block**: Professional KiCAD .kicad_sch file manipulation with exact format preservation, designed to be the foundation for other specialized tools.

## Target Users

1. **EDA Tool Developers** - Building automation tools on KiCAD
2. **AI/Agent Developers** - Creating intelligent design assistants  
3. **Circuit Designers** - Who need programmatic schematic control
4. **Python Developers** - Building EDA workflows and automation

## Scope Definition

### ✅ IN SCOPE (Core Building Block)
1. **Professional File Manipulation**
   - Exact format preservation (byte-perfect KiCAD output)
   - S-expression parsing and generation
   - Component placement and property management
   - Hierarchical sheet support

2. **Basic KiCAD Integration**
   - Real KiCAD symbol library access
   - Component validation using actual libraries
   - KiCAD CLI integration (ERC, netlist generation)
   - Pin information from symbol definitions

3. **MCP Server for AI Agents**
   - Tools for schematic creation and editing
   - Component search and validation
   - Professional guidance for AI agents
   - Hierarchical design support

4. **Foundation Features**
   - Object-oriented component collections
   - Professional error handling and reporting
   - Performance optimization (caching, indexing)
   - Comprehensive test suite with format preservation

### ❌ OUT OF SCOPE (Separate Libraries)
- Component sourcing and lifecycle management
- Advanced electrical analysis and simulation
- Manufacturing/DFM checking and optimization
- Standards compliance validation
- Placement optimization algorithms
- Thermal analysis and signal integrity
- Cost analysis and supply chain management

## Core API Design

### Schematic Manipulation
```python
import kicad_sch_api as ksa

# Create and load schematics
sch = ksa.create_schematic('My Circuit')
sch = ksa.load_schematic('existing.kicad_sch')

# Component management
component = sch.components.add(
    lib_id='Device:R',
    reference='R1', 
    value='10k',
    position=(100.0, 100.0),
    footprint='R_0603_1608Metric'
)

# Component search and filtering
resistors = sch.components.find(lib_id_pattern='Device:R*')
components = sch.components.filter(reference_pattern=r'R[0-9]+')

# Exact format preservation
sch.save('output.kicad_sch')  # Byte-perfect KiCAD format
```

### KiCAD Integration
```python
# Real KiCAD library access
symbol_info = ksa.library.get_symbol_info('Device:R')
# Returns: SymbolInfo(pins=[...], footprint_filters=[...])

# KiCAD CLI integration
erc_result = sch.run_erc_check()  # Uses kicad-cli sch erc
netlist = sch.generate_netlist()  # Uses kicad-cli sch export netlist

# Component validation
validation = sch.components.validate_component('Device:R', 'R_0603_1608Metric')
```

### Hierarchical Design
```python
# Add hierarchical sheet
sheet = sch.add_hierarchical_sheet(
    name='Power Supply',
    filename='power.kicad_sch',
    position=(100, 100),
    size=(80, 60)
)

# Add sheet pins for connectivity
sheet.add_pin('VIN', pin_type='input', position=(0, 10))
sheet.add_pin('VOUT', pin_type='output', position=(80, 10))

# In sub-schematic
sub_sch = ksa.create_schematic('Power Supply')
sub_sch.add_hierarchical_label('VIN', label_type='input', position=(50, 25))
```

## Technical Architecture

### Core Library Structure
```
kicad_sch_api/
├── core/
│   ├── schematic.py          # Main schematic class
│   ├── components.py         # Component collection and management
│   ├── parser.py            # S-expression parsing
│   ├── formatter.py         # S-expression generation with format preservation
│   └── types.py             # Data classes for schematic elements
├── library/
│   ├── manager.py           # KiCAD library management
│   ├── cache.py             # Symbol library caching
│   └── validator.py         # Component validation
├── integration/
│   ├── kicad_cli.py         # KiCAD CLI wrapper (ERC, netlist)
│   └── netlist_parser.py    # Parse KiCAD netlist format
└── mcp/
    └── server.py            # MCP server for AI agents
```

### MCP Server Tools
```python
# Essential MCP tools for AI agents
- create_schematic()
- load_schematic()  
- save_schematic()
- add_component()
- list_components()
- search_components() 
- add_hierarchical_sheet()
- add_sheet_pin()
- add_hierarchical_label()
- validate_component()
- get_schematic_info()
```

## Competitive Differentiation

### vs. kicad-skip
- **Format Preservation**: Byte-perfect vs approximate
- **API Design**: Object-oriented collections vs REPL magic
- **Performance**: Production-optimized vs exploration-focused  
- **Validation**: Real KiCAD library integration vs none
- **AI Integration**: Purpose-built MCP server vs none

### vs. Direct S-expression Manipulation
- **Professional API**: High-level operations vs low-level parsing
- **Validation**: Component and library validation vs none
- **Format Preservation**: Guaranteed exact output vs manual formatting
- **Performance**: Optimized collections vs manual iteration

## Success Metrics

### Technical Success
- **Format Preservation**: 100% byte-perfect KiCAD output
- **Performance**: <50ms component operations for typical schematics
- **Library Coverage**: Support for standard KiCAD symbol libraries
- **API Stability**: Semantic versioning with stable public API

### Ecosystem Success  
- **Building Block Adoption**: Other libraries built on this foundation
- **AI Agent Integration**: Multiple agents using MCP server
- **Community Growth**: Active usage in EDA automation projects

## Implementation Plan

### Phase 1: Core Foundation (4 weeks)
- S-expression parser with exact format preservation
- Basic component management and collections
- File I/O with validation
- Comprehensive test suite

### Phase 2: KiCAD Integration (3 weeks)
- Real KiCAD library integration
- KiCAD CLI wrapper (ERC, netlist)  
- Component validation system
- Performance optimization

### Phase 3: MCP Server (2 weeks)
- MCP server implementation
- AI agent tools and guidance
- Professional error handling
- Documentation and examples

## What This Enables

By keeping this library focused as a building block, it enables:

```python
# Other specialized libraries can build on top
import kicad_sch_api as ksa
import kicad_sourcing_tools as sourcing      # Separate library
import kicad_placement_optimizer as placement # Separate library  
import kicad_dfm_checker as dfm              # Separate library

# This library provides the foundation
sch = ksa.load_schematic('project.kicad_sch')

# Specialized libraries extend functionality
sourcing.update_component_sourcing(sch.components)
placement.optimize_layout(sch)
dfm.check_manufacturing_rules(sch)

# All save through this library's format preservation
sch.save()  # Guaranteed exact KiCAD format
```

## Conclusion

By maintaining focus on core schematic manipulation with exact format preservation, this library becomes the reliable foundation that other tools can build upon. It provides the essential "pandas for KiCAD" functionality without bloating into specialized domains that belong in separate libraries.

The MCP server integration makes this foundation immediately useful for AI agents while remaining a focused building block for the broader EDA automation ecosystem.