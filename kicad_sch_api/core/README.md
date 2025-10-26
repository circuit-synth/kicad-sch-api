# Core Module

Core schematic manipulation and manager-based architecture.

## Overview

This module contains the fundamental classes and managers for KiCAD schematic manipulation. The Phase 4 architecture uses a manager-based design pattern where the `Schematic` class coordinates 8 specialized managers.

## Main Classes

### Schematic (`schematic.py`)
- **Lines**: 1,584
- **Purpose**: Main API entry point and manager coordinator
- **Key Methods**:
  - `load()` - Load existing schematic file
  - `save()` - Save with exact format preservation
  - `validate()` - Run validation checks
  - Property accessors: `.components`, `.wires`, `.labels`, etc.

### Parser (`parser.py`)
- **Lines**: 2,351
- **Purpose**: S-expression parser for KiCAD format
- **Responsibility**: Convert KiCAD file text to Python objects
- **Critical for**: Format preservation and parsing accuracy
- **Key Classes**:
  - `KiCADParser` - Main parser class
  - `ParseError` - Custom exception type

### Formatter (`formatter.py`)
- **Lines**: 563
- **Purpose**: Convert Python objects back to KiCAD S-expression format
- **Key Methods**:
  - `format_schematic()` - Generate output text
  - `format_component()` - Format individual elements

### Components (`components.py`)
- **Lines**: 736
- **Purpose**: Component collection management with filtering/bulk operations
- **Key Classes**:
  - `ComponentCollection` - Enhanced list with query methods
  - Filter methods: `filter_by_lib_id()`, `filter_by_value()`, etc.

### Configuration (`config.py`)
- **Lines**: 285
- **Purpose**: Global configuration for KiCAD behavior
- **Instances**: `config` (global singleton)
- **Configurable**: Label positioning, tolerances, import paths

### Types (`types.py`)
- **Lines**: 420
- **Purpose**: Core data type definitions
- **Key Classes**: Point, Component, Wire, Label, Junction, etc.
- **Pattern**: Frozen dataclasses for immutability

## Manager System

Located in `managers/` subdirectory. Each manager handles one responsibility:

| Manager | Purpose |
|---------|---------|
| `file_io.py` | Load/save operations |
| `validation.py` | Error detection and reporting |
| `components.py` | Component CRUD operations |
| `wire.py` | Wire routing and connectivity |
| `text_elements.py` | Text labels and annotations |
| `graphics.py` | Graphical elements (shapes) |
| `metadata.py` | Sheet metadata and properties |
| `format_sync.py` | Format preservation coordination |

## Specialized Modules

### Routing
- **`simple_manhattan.py`** - Simple L-shaped routing (basic use cases)
- **`manhattan_routing.py`** - A* pathfinding routing (complex paths, 430 lines)
- **`wire_routing.py`** - Wire utility functions

### Symbol Management
- **`pin_utils.py`** - Pin parsing and analysis
- **`component_bounds.py`** - Bounding box calculations

### Wiring & Connectivity
- **`wires.py`** - Wire collection management
- **`nets.py`** - Net connectivity analysis
- **`junctions.py`** - Junction point management
- **`no_connects.py`** - No-connect symbol handling

### Text & Labels
- **`texts.py`** - Text element management
- **`labels.py`** - Label-specific handling

### Experimental/Unclear
- **`ic_manager.py`** - Multi-unit IC handling (193 lines)
  - Status: Appears unused, needs clarification
  - Recommendations: Integrate, document, or remove

## Architecture Patterns

### Manager Coordination
```
Schematic (main API)
├── FileIOManager - Load/save
├── ValidationManager - Error checking
├── ComponentManager - Component operations
├── WireManager - Wire operations
├── TextElementManager - Labels
├── GraphicsManager - Shapes
├── MetadataManager - Sheet info
└── FormatSyncManager - Format coordination
```

### Format Preservation Pipeline
1. **Parser** reads .kicad_sch file
2. Preserves all original formatting
3. Python code modifies structure
4. **Formatter** writes back exactly as KiCAD would

## Code Quality

- **Type System**: Strict mypy enabled
- **Format**: Black/isort compliance
- **Lines of Code**: ~9,600 core lines
- **Documentation**: Module/class docstrings throughout

## Known Issues

1. **IC Manager** - Status unclear (experimental or dead code?)
2. **Routing Implementations** - Two different routing algorithms, needs consolidation
3. **Unresolved TODOs** - 4 TODO comments:
   - Component rotation handling
   - Wire connectivity analysis
   - Symbol transformation application
   - PIN text placeholders
4. **Version Mismatch** - Check __init__.py vs pyproject.toml

## Testing

Located in `../tests/`, includes:
- Reference-based format preservation tests
- Component/element removal tests
- Geometry and routing tests
- Integration tests

## Dependencies

- `sexpdata` - S-expression parsing
- `typing-extensions` - Type hint support

## Related Documentation

- See `managers/` for manager-specific details
- See root `CODEBASE_ANALYSIS.md` for architecture diagrams
- See `CLAUDE.md` for development guidelines
